"""Position value map: what each running position is worth, by pace, track, distance, going and rail.

Past runs (fitted on races before train_end only):
  position  at the 800m, from position and margin: lead, <=1.5L, 1.5-3L, 3-5L, 5-8L, 8L+ back (all states)
  width     QLD: mean GPS distance from the rail 800m to 200m from home; VIC/SA: racing.com whole-race average
            (Triple S only): fence (<2m), 1 wide (2-3.5m), 2 wide (3.5-5m), 3+ wide (5m+)
  pace      race early shape: slow (< -2), even, fast (> 2)
  value     WPR minus the horse's pre-race decayed WPR, demeaned within the race; recency weight half-life 2 years
  pooling   V = global[pos, pace] + track + track x distance band + going band + track x rail band, each level fitted
            on what the levels above leave, shrunk as sum / (weight + LAMBDA); width map likewise (global, track,
            track x distance) on what the position map leaves
Pre-race:
  P(position) and P(width) from LightGBM multiclass models on the projection's settle / ground-loss inputs;
  P(pace) from the projected early shape with the training residual spread (normal)
  pv_adj = sum over position, pace of P(position) P(pace) V(race context, position, pace), demeaned in race
  pw_adj = same for width (0 when the race has no width model coverage)
"""
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import norm

from model import projection

POS = ["lead", "<=1.5L", "1.5-3L", "3-5L", "5-8L", "8L+"]
WID = ["fence", "1 wide", "2 wide", "3+ wide"]
PACE = ["slow", "even", "fast"]
LAMBDA = 30.0
HALF_LIFE_DAYS = 730
FEATS = ["pv_adj", "pw_adj"]
# columns features() reads from the projection frame (pass px[NEEDS] to keep memory down)
NEEDS = list(dict.fromkeys(["run_id", "race_id", "race_date", "y_shape", "proj_shape", "dist", "going_num", "rail_m", "track",
                            "wpr", "h_wpr", "h_none"] + projection.SETTLE_X + projection.GL_X))
CLF = dict(objective="multiclass", num_leaves=31, learning_rate=0.05, min_data_in_leaf=200, feature_fraction=0.8,
           bagging_fraction=0.8, bagging_freq=1, verbose=-1, num_threads=4, seed=1, deterministic=True,
           force_row_wise=True)
ROUNDS = 250
MAPS = {}   # fitted maps by train_end, for reports

SQL = """
select r.run_id, r.res_pos800 pos800, r.res_marg800 marg800, ra.going_num, ra.rail_m r_rail
from runs r join races ra using (race_id) where not r.is_trial_or_jumpout
"""


def _pos_bucket(pos, marg):
    m = np.where(pos == 1, -1.0, marg)
    return pd.cut(pd.Series(m), [-2, -0.5, 1.5, 3, 5, 8, 999], labels=False).to_numpy(float)


def _width(con, runs):
    """Width per run_id: QLD = mean GPS distance from the rail 800m to 200m from home; VIC/SA (racing.com Triple S)
    = the whole-race average distance from the rail (the only width measure it gives)."""
    rc = con.sql("select run_id, res_gps_rail_m from gps_runs where source = 'rc' and res_gps_rail_m is not null").df()
    rc = rc.set_index("run_id")["res_gps_rail_m"]
    return pd.concat([_width_rq(con), rc])


def _width_rq(con):
    from model.extra_history import SECTIONS, read_rq_sections
    if not SECTIONS.exists():
        return pd.Series(dtype=float)
    s = read_rq_sections(columns=["race_code", "tab_no", "cum_dist_m", "rail_m"])
    s = s[s["rail_m"].notna()]
    s["race_code"] = s["race_code"].astype(str)
    key = con.sql("select run_id, src_race race_code, tab_no from gps_runs where source = 'rq'").df()
    key["race_code"] = key["race_code"].astype(str)
    s = s.merge(key, on=["race_code", "tab_no"])
    last = s.groupby("run_id")["cum_dist_m"].transform("max")
    turn = s[(s["cum_dist_m"] > last - 800) & (s["cum_dist_m"] <= last - 200)]
    return turn.groupby("run_id")["rail_m"].mean()


def _context(x):
    dist_b = pd.cut(x["dist"], [0, 1100, 1300, 1600, 2000, 9999], labels=False).astype(str)
    going_b = pd.cut(x["going_num"].fillna(4), [0, 4, 6, 20], labels=False).astype(str)
    rail_b = pd.cut(x["rail_m"].fillna(-1), [-9, -0.5, 0.5, 3.5, 6.5, 99], labels=False).astype(str)
    trk = x["track"].astype(str)
    return pd.DataFrame({"cx_g": "all", "cx_t": trk, "cx_td": trk + "|" + dist_b, "cx_go": going_b,
                         "cx_tr": trk + "|" + rail_b}, index=x.index)


def _fit_levels(df, cell_cols, levels, lam=LAMBDA):
    """Sequential shrunk cell means. df has r (target), w (weight), context columns, cell columns."""
    r = df["r"].to_numpy(float).copy()
    tables = []
    for lev in levels:
        keys = [lev] + cell_cols
        t = pd.DataFrame({k: df[k].to_numpy() for k in keys}).assign(wr=df["w"].to_numpy() * r, w=df["w"].to_numpy())
        agg = t.groupby(keys)[["wr", "w"]].sum()
        eff = (agg["wr"] / (agg["w"] + (0 if lev == "cx_g" else lam))).rename("v").reset_index()
        tables.append((lev, eff))
        r = r - pd.DataFrame({k: df[k].to_numpy() for k in keys}).merge(eff, on=keys, how="left")["v"].fillna(0).to_numpy()
    return tables


def _lookup(tables, ctx, cell_cols, cells):
    """Value for every row x every cell combination: array (n_rows, n_cells)."""
    out = np.zeros((len(ctx), len(cells)))
    for lev, eff in tables:
        m = eff.set_index([lev] + cell_cols)["v"]
        for j, cell in enumerate(cells):
            idx = pd.MultiIndex.from_arrays([ctx[lev].to_numpy()] + [np.full(len(ctx), c) for c in cell])
            out[:, j] += m.reindex(idx).fillna(0).to_numpy()
    return out


def _clf(X, y, n):
    return lgb.train(dict(CLF, num_class=n), lgb.Dataset(np.round(X.to_numpy(float), 6), y.astype(int)), ROUNDS)


def features(con, px, train_end):
    """pv_adj / pw_adj for every run. px = projection.project(...) output (full frame incl. proj_* and inputs)."""
    train_end = pd.Timestamp(train_end)
    x = px.merge(con.sql(SQL).df().drop(columns=["going_num"], errors="ignore"), on="run_id", how="left")
    x["pos_b"] = _pos_bucket(x["pos800"].to_numpy(float), x["marg800"].to_numpy(float))
    x["width_m"] = x["run_id"].map(_width(con, x))
    x["wid_b"] = pd.cut(x["width_m"], [-1, 2, 3.5, 5, 99], labels=False)
    x["pace_b"] = pd.cut(x["y_shape"], [-99, -2, 2, 99], labels=False)
    ctx = _context(x)
    x = pd.concat([x, ctx], axis=1)
    age = (train_end - x["race_date"]).dt.days.clip(lower=0)
    tr = (x["race_date"] < train_end) & (x["race_date"] >= "2019-01-01")
    res = (x["wpr"] - x["h_wpr"]).where((x["h_none"] == 0) & x["wpr"].notna())
    x["r"] = res - res.groupby(x["race_id"]).transform("mean")
    x["w"] = 0.5 ** (age / HALF_LIFE_DAYS)

    # value maps
    fm = tr & x["r"].notna() & x["pos_b"].notna() & x["pace_b"].notna()
    pos_tabs = _fit_levels(x[fm], ["pos_b", "pace_b"], ["cx_g", "cx_t", "cx_td", "cx_go", "cx_tr"])
    cells_p = [(p, q) for p in range(len(POS)) for q in range(len(PACE))]
    fw = fm & x["wid_b"].notna()
    xw = x[fw].copy()
    # residual after the position map for the width map
    own = np.zeros(len(xw))
    for lev, eff in pos_tabs:
        own += xw[[lev, "pos_b", "pace_b"]].merge(eff, on=[lev, "pos_b", "pace_b"], how="left")["v"].fillna(0).to_numpy()
    xw["r"] = xw["r"] - own
    wid_tabs = _fit_levels(xw, ["wid_b", "pace_b"], ["cx_g", "cx_t", "cx_td"])
    cells_w = [(k, q) for k in range(len(WID)) for q in range(len(PACE))]
    MAPS[str(train_end.date())] = {"pos": pos_tabs, "wid": wid_tabs}

    # pre-race probabilities
    ms = tr & x["pos_b"].notna()
    clf_p = _clf(x.loc[ms, projection.SETTLE_X], x.loc[ms, "pos_b"].to_numpy(), len(POS))
    P_pos = clf_p.predict(np.round(x[projection.SETTLE_X].to_numpy(float), 6))
    gx = [c for c in projection.GL_X]
    mw = tr & x["wid_b"].notna()
    clf_w = _clf(x.loc[mw, gx], x.loc[mw, "wid_b"].to_numpy(), len(WID))
    P_wid = clf_w.predict(np.round(x[gx].to_numpy(float), 6))
    race_rows = tr & x["y_shape"].notna()
    sd = float((x.loc[race_rows, "y_shape"] - x.loc[race_rows, "proj_shape"]).std())
    mu = x["proj_shape"].fillna(0).to_numpy(float)
    cdf_lo, cdf_hi = norm.cdf((-2 - mu) / sd), norm.cdf((2 - mu) / sd)
    P_pace = np.c_[cdf_lo, cdf_hi - cdf_lo, 1 - cdf_hi]

    # expected values
    Vp = _lookup(pos_tabs, x, ["pos_b", "pace_b"], cells_p)          # (n, 6*3)
    joint_p = (P_pos[:, :, None] * P_pace[:, None, :]).reshape(len(x), -1)
    pv = (Vp * joint_p).sum(1)
    Vw = _lookup(wid_tabs, x, ["wid_b", "pace_b"], cells_w)
    joint_w = (P_wid[:, :, None] * P_pace[:, None, :]).reshape(len(x), -1)
    pw = (Vw * joint_w).sum(1)
    covered = x["track"].isin(x.loc[mw, "track"].unique())          # tracks with GPS width history
    pw = np.where(covered, pw, 0.0)
    out = pd.DataFrame({"run_id": x["run_id"], "race_id": x["race_id"], "pv": pv, "pw": pw})
    for c in ["pv", "pw"]:
        out[c + "_adj"] = out[c] - out.groupby("race_id")[c].transform("mean")
    return out[["run_id"] + FEATS]


def map_table(train_end, track=None, dist_band=None, going_band="0", rail_band="1"):
    """Readable position x pace map (WPR points) for a context, from a fitted map."""
    tabs = MAPS[train_end]["pos"]
    ctx = pd.DataFrame({"cx_g": ["all"], "cx_t": [track or ""], "cx_td": [f"{track}|{dist_band}"],
                        "cx_go": [going_band], "cx_tr": [f"{track}|{rail_band}"]})
    cells = [(p, q) for p in range(len(POS)) for q in range(len(PACE))]
    v = _lookup(tabs, ctx, ["pos_b", "pace_b"], cells)[0]
    return pd.DataFrame(v.reshape(len(POS), len(PACE)), index=POS, columns=PACE)
