"""Race-day projection: settle position, race early pace, ground loss, and their cost in WPR.

    python model/projection.py      # walk-forward evaluation -> reports/projection_validation.md

All inputs are known before the race. Per fold (test year Y) every model is fitted on 2019..Y-1.

settle   target: position at the 800m as a share of the field (0 = leader)
         inputs: horse's settle history (decayed mean over runs with a position, last, most forward of
                 last 3, spread, at similar distances, count), distance change, past early sectional,
                 today's field: settle / early-speed rank, faster rivals drawn inside, barrier (raw and
                 share), field size, distance, surface, track, rail setting, jockey and trainer
                 forward-ride tendency (rolling mean of actual minus expected settle), first up, days
                 since last start, ability rank in the field
pace     target: race early shape (TopRate raceShapeEarly, + = fast early), one row per race
         inputs: projected leaders, the early speed of the 3 horses projected to be most forward,
                 fastest early rating, field size, distance, surface, track, going, field ability
gl       target: GPS extra ground vs field mean (m), QLD GPS runs only
         inputs: barrier, barrier share, faster rivals inside, projected settle and rank, the horse's
                 past extra ground and width from the rail, jockey width tendency, field size,
                 distance, surface, track, rail setting
cost     linear, within race: (WPR today - pre-race ability) on actual settle, pace and ground loss.
         proj_adj = the same coefficients applied to the projected values (WPR points).

Outputs per run: barrier_pct, proj_settle, proj_settle_rank, proj_shape, proj_pace, proj_gl, proj_adj.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure  # noqa: E402

PARAMS = dict(objective="regression", num_leaves=63, learning_rate=0.05, min_data_in_leaf=200,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, num_threads=4, seed=1,
              deterministic=True, force_row_wise=True)   # identical results run to run
ROUNDS = 400
K = 8

EXTRA_SQL = """
select r.run_id, r.res_wpr wpr, r.res_s_early s_early_raw, coalesce(r.weight_claim_kg, 0) claim, r.barrier, r.jockey, r.trainer, r.age, ra.track, ra.surface, ra.going_num, ra.rail_m,
  count(*) over (partition by r.race_id) field_n,
  (r.res_pos800 - 1) / greatest(count(*) over (partition by r.race_id) - 1, 1) y_settle,
  ra.res_shape_early y_shape, ra.res_leader_early_rating y_lead_early,
  g.res_gps_extra_m y_gl,
  g.res_gps_rail_m - avg(g.res_gps_rail_m) over (partition by r.race_id) y_rail,
  g.res_gps_early400 y_early
from runs r join races ra using (race_id) left join gps_runs g using (run_id)
where not r.is_trial_or_jumpout
"""

SETTLE_OLD = ["st_mean", "st_last", "st_min3", "st_sd", "st_n", "st_dist", "dist_change", "h_s_early",
              "settle_rank", "early_rank", "inside_faster", "barrier", "barrier_pct", "field_n", "dist",
              "synth", "track_code", "rail_m", "jockey_fwd", "trainer_fwd", "first_up", "log_days",
              "h_none", "ability_rank", "age", "early_hist", "early_n"]
SPEED = ["early_rank2", "wide_x_slow", "nb_diff_in", "nb_diff_out", "inside_faster_es"]
SETTLE_X = SETTLE_OLD + ["es_mean", "es_last", "es_dist", "es_fu", "es_going", "es_n"] + SPEED + \
    ["td_bar_settle", "wt_rel_today", "claim", "t_trial_since", "t_trial_pos", "t_trial_marg"]
PACE_X = ["n_leaders", "min_settle", "low3_settle", "front3_early", "max_early", "field_n", "dist", "synth",
          "track_code", "going_num", "field_ability"]
GL_X = ["barrier", "barrier_pct", "inside_faster", "proj_settle", "proj_settle_rank", "gl_hist", "rail_hist",
        "gps_n", "jockey_width", "field_n", "dist", "synth", "track_code", "rail_m", "td_bar_settle"] + SPEED
BIAS = ["tbx_settle_long", "tbx_settle_recent", "tbx_bar_long", "tbx_bar_recent", "bias_adj"]
TD = ["tdx_settle", "tdx_perf"]
SPEED_WIN = ["early_rank2", "wide_x_slow", "nb_diff_in", "nb_diff_out"]
OUT = ["barrier_pct", "proj_settle", "proj_settle_rank", "proj_shape", "proj_pace", "proj_gl", "proj_adj"] + \
    BIAS + TD + SPEED_WIN
BIAS_LAMBDA_LONG, BIAS_LAMBDA_RECENT, BIAS_DAYS = 30.0, 10.0, 35
TD_LAMBDA = 10.0
GLOBALS = {}   # global slopes fitted on 2019-2021 (set by frame)


# ---------------------------------------------------------------- inputs

def _rank(v, by, ascending=True):
    """Rank within race on values rounded to 1e-6, so float noise in near-ties cannot flip the order."""
    return v.round(6).groupby(by).rank(ascending=ascending)


def _lags(d, col, k=K):
    g = d.groupby("horse_id", sort=False)[col]
    return np.stack([g.shift(j).to_numpy(float) for j in range(1, k + 1)], 1)


def _rolling_tendency(con, df, key, col, days, prior_n):
    """Pre-race rolling mean of `col` per `key` over the last `days` (windows end the day before), shrunk."""
    con.register("tend_df", df[["run_id", "race_date", key, col]])
    out = con.sql(f"""
        select run_id,
          coalesce(sum({col}) over w, 0) / (coalesce(count({col}) over w, 0) + {prior_n}) v
        from tend_df
        window w as (partition by {key} order by race_date
                     range between interval {days} days preceding and interval 1 day preceding)""").df()
    con.unregister("tend_df")
    return df[["run_id"]].merge(out, on="run_id", how="left")["v"].fillna(0).to_numpy()


def frame(con, h=None):
    """All runs with every projection input and target. h = figure.history(...) (computed if None)."""
    d = figure.components(con)
    h = figure.history(d) if h is None else h
    x = h.merge(con.sql(EXTRA_SQL).df(), on="run_id", how="left")
    x = x.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    x["race_date"] = pd.to_datetime(x["race_date"])

    # settle history over runs that have a position
    s = _lags(x, "y_settle")
    dl = _lags(x, "dist")
    ok = ~np.isnan(s)
    w = np.where(ok, 0.5 ** (np.arange(K) / 3.0), 0)
    wsum = w.sum(1)
    has = wsum > 0
    sv = np.nan_to_num(s)
    x["st_n"] = ok.sum(1)
    x["st_mean"] = np.where(has, (w * sv).sum(1) / np.where(has, wsum, 1), np.nan)
    first = np.argmax(ok, 1)
    x["st_last"] = np.where(has, sv[np.arange(len(x)), first], np.nan)
    with np.errstate(all="ignore"):
        s3 = np.where(ok & (np.cumsum(ok, 1) <= 3), s, np.nan)
        x["st_min3"] = np.nanmin(s3, 1)
        x["st_sd"] = np.nanstd(np.where(ok, s, np.nan), 1)
    near = ok & (np.abs(np.log(np.nan_to_num(dl, nan=1.0) / x["dist"].to_numpy()[:, None])) < 0.15)
    wn = np.where(near, w, 0)
    x["st_dist"] = np.where(has, ((wn * sv).sum(1) + 2 * x["st_mean"].fillna(0.5)) / (wn.sum(1) + 2), np.nan)
    x["dist_change"] = np.log(x["dist"] / x.groupby("horse_id")["dist"].shift(1))

    # early speed history (actual early sectional ratings only), matched to today's conditions
    x["wet"] = (x["going_num"].fillna(4) >= 7).astype(float)
    x["first_up"] = (x["days_since_start"].fillna(999) >= 60).astype(float)
    x["s_early_raw"] = x["s_early_raw"].where(x["s_early_raw"].between(-25, 15))
    e = _lags(x, "s_early_raw")
    oke = ~np.isnan(e)
    we = np.where(oke, 0.5 ** (np.arange(K) / 3.0), 0)
    ev = np.nan_to_num(e)
    hase = we.sum(1) > 0
    x["es_n"] = oke.sum(1)
    es_mean = np.where(hase, (we * ev).sum(1) / np.maximum(we.sum(1), 1e-9), np.nan)
    x["es_mean"] = es_mean
    x["es_last"] = np.where(hase, ev[np.arange(len(x)), np.argmax(oke, 1)], np.nan)
    base = np.nan_to_num(es_mean)

    def matched(mask):
        wm = np.where(mask & oke, we, 0)
        return np.where(hase, ((wm * ev).sum(1) + 2 * base) / (wm.sum(1) + 2), np.nan)
    x["es_dist"] = matched(np.abs(np.log(np.nan_to_num(dl, nan=1.0) / x["dist"].to_numpy()[:, None])) < 0.15)
    fu_l = _lags(x, "first_up")
    x["es_fu"] = np.where(x["first_up"] == 1, matched(fu_l == 1), es_mean)
    x["es_going"] = matched(_lags(x, "wet") == x["wet"].to_numpy()[:, None])

    # GPS width history
    for col, name in [("y_gl", "gl_hist"), ("y_rail", "rail_hist")]:
        v = _lags(x, col)
        okv = ~np.isnan(v)
        wv = np.where(okv, 0.5 ** (np.arange(K) / 3.0), 0)
        x[name] = (wv * np.nan_to_num(v)).sum(1) / (wv.sum(1) + 1.0)
    x["gps_n"] = (~np.isnan(_lags(x, "y_gl"))).sum(1)
    v = _lags(x, "y_early")
    okv = ~np.isnan(v)
    wv = np.where(okv, 0.5 ** (np.arange(K) / 3.0), 0)
    x["early_n"] = okv.sum(1)
    x["early_hist"] = np.where(okv.any(1), (wv * np.nan_to_num(v)).sum(1) / np.maximum(wv.sum(1), 1e-9), np.nan)

    # field context
    x["barrier"] = x["barrier"].where(x["barrier"] > 0)
    g = x.groupby("race_id")
    den = (x["field_n"] - 1).clip(lower=1)
    x["barrier_pct"] = ((g["barrier"].rank(method="average") - 1) / den).fillna(0.5)
    st_fill = x["st_mean"].fillna(0.5)
    x["settle_rank"] = (_rank(st_fill, x["race_id"]) - 1) / den
    he = x["h_s_early"].where(x["h_none"] == 0)
    x["early_rank"] = ((_rank(he, x["race_id"], ascending=False) - 1) / den).fillna(0.5)
    x["ability_rank"] = ((_rank(x["h_wpr"].where(x["h_none"] == 0), x["race_id"], ascending=False) - 1)
                         / den).fillna(0.5)
    # early speed for today (first-up history when first up, else distance-matched), field rank
    es_today = x["es_fu"].where(x["first_up"] == 1, x["es_dist"])
    es_fill = es_today.fillna(es_today.groupby(x["race_id"]).transform("median")).fillna(-6.0)
    x["es_today"] = es_fill
    x["early_rank2"] = (_rank(es_fill, x["race_id"], ascending=False) - 1) / den
    x["wide_x_slow"] = x["barrier_pct"] * x["early_rank2"]
    # speed map: rivals drawn inside, neighbours' early speed
    x = x.sort_values(["race_id", "barrier", "run_id"], kind="mergesort").reset_index(drop=True)
    inside = np.zeros(len(x))
    inside_es = np.zeros(len(x))
    stv, esv = x["st_mean"].round(6).to_numpy(), x["es_today"].round(6).to_numpy()
    for _, idx in x.groupby("race_id").indices.items():
        sf = np.where(np.isnan(stv[idx]), 0.5, stv[idx])
        ef = esv[idx]
        for a in range(1, len(idx)):
            inside[idx[a]] = (sf[:a] < sf[a]).sum()
            inside_es[idx[a]] = (ef[:a] > ef[a]).sum()
    x["inside_faster"] = inside / (x["field_n"] - 1).clip(lower=1)
    x["inside_faster_es"] = inside_es / (x["field_n"] - 1).clip(lower=1)
    gb = x.groupby("race_id")["es_today"]
    x["nb_diff_in"] = (x["es_today"] - gb.shift(1)).fillna(0)
    x["nb_diff_out"] = (x["es_today"] - gb.shift(-1)).fillna(0)
    x = x.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)

    x["rail_m"] = x["rail_m"].where(x["rail_m"].between(0, 15))
    x["synth"] = x["surface"].isin(["Synthetic", "Sand", "Dirt"]).astype(float)
    x["track_code"] = x["track"].astype("category").cat.codes
    x["log_n"] = np.log1p(x["h_n"])
    x["log_days"] = np.log1p(x["days_since_start"].fillna(0))

    x = track_bias(x)
    x = td_barrier(x)
    from model.ability import TRIAL_SQL
    x = x.merge(con.sql(TRIAL_SQL).df(), on="run_id", how="left")
    x["t_trial_since"] = x["t_trial_since"].fillna(0)
    x["t_trial_pos"] = x["t_trial_pos"].where(x["t_trial_since"] > 0)
    x["t_trial_marg"] = x["t_trial_marg"].where(x["t_trial_since"] > 0)

    # jockey / trainer tendencies: actual settle minus the horse's own history; jockey width
    x["settle_resid"] = x["y_settle"] - x["st_mean"]
    x["jockey_fwd"] = _rolling_tendency(con, x, "jockey", "settle_resid", 365, 20)
    x["trainer_fwd"] = _rolling_tendency(con, x, "trainer", "settle_resid", 730, 20)
    x["jockey_width"] = _rolling_tendency(con, x, "jockey", "y_rail", 365, 20)
    return x


def track_bias(x):
    """Settle and barrier bias at each track from PAST meetings only.

    Per meeting: within-race slopes of (WPR - pre-race ability) on actual settle share and barrier share,
    pooled over the meeting's races. For a race: long-run = all prior meetings at the track (shrunk);
    recent = the previous 1-2 meetings at the same track and rail setting within 35 days (shrunk).
    Stored as deviations from the global slope (fitted on 2019-2021), and interacted with the runner's
    projected settle / barrier vs the field (tbx_*). bias_adj = long-run deviations x those (WPR points).
    """
    # every run (incl. race days without results yet) so each meeting gets its prior history;
    # runs without a result contribute nothing to the sums
    t = x.copy()
    valid = (t["h_none"] == 0) & t["wpr"].notna() & t["y_settle"].notna()
    t["res"] = t["wpr"] - t["h_wpr"]
    for c in ["res", "y_settle", "barrier_pct"]:
        v = t[c].where(valid)
        t[c + "_dm"] = v - v.groupby(t["race_id"]).transform("mean")
    t["sxy"], t["sxx"] = t["res_dm"] * t["y_settle_dm"], t["y_settle_dm"] ** 2
    t["bxy"], t["bxx"] = t["res_dm"] * t["barrier_pct_dm"], t["barrier_pct_dm"] ** 2
    m = t.groupby(["track", "race_date"]).agg(sxy=("sxy", "sum"), sxx=("sxx", "sum"), bxy=("bxy", "sum"),
                                               bxx=("bxx", "sum"), rail=("rail_m", "first")).reset_index()
    m["rail"] = m["rail"].round(1).fillna(-1)
    early = m["race_date"].dt.year.between(2019, 2021)
    gs = m.loc[early, "sxy"].sum() / m.loc[early, "sxx"].sum()
    gb = m.loc[early, "bxy"].sum() / m.loc[early, "bxx"].sum()
    m = m.sort_values(["track", "race_date"]).reset_index(drop=True)
    g = m.groupby("track")
    for c, xy, xx, glob in [("settle", "sxy", "sxx", gs), ("bar", "bxy", "bxx", gb)]:
        cxy, cxx = g[xy].cumsum() - m[xy], g[xx].cumsum() - m[xx]
        m[f"tb_{c}_long"] = cxy / (cxx + BIAS_LAMBDA_LONG) - glob * cxx / (cxx + BIAS_LAMBDA_LONG)
        gr = m.groupby(["track", "rail"])
        gap = (m["race_date"] - gr["race_date"].shift(1)).dt.days
        rxy = gr[xy].shift(1).fillna(0) + gr[xy].shift(2).fillna(0).where(
            (m["race_date"] - gr["race_date"].shift(2)).dt.days <= 2 * BIAS_DAYS, 0)
        rxx = gr[xx].shift(1).fillna(0) + gr[xx].shift(2).fillna(0).where(
            (m["race_date"] - gr["race_date"].shift(2)).dt.days <= 2 * BIAS_DAYS, 0)
        rec = rxy / (rxx + BIAS_LAMBDA_RECENT) - glob * rxx / (rxx + BIAS_LAMBDA_RECENT)
        m[f"tb_{c}_recent"] = rec.where(gap <= BIAS_DAYS, 0.0).fillna(0.0)
    cols = ["tb_settle_long", "tb_settle_recent", "tb_bar_long", "tb_bar_recent"]
    x = x.merge(m[["track", "race_date"] + cols], on=["track", "race_date"], how="left")
    x[cols] = x[cols].fillna(0.0)
    GLOBALS["bias"] = (gs, gb)
    return x


def td_barrier(x):
    """Barrier effect by track and distance from PAST race days only (same-day excluded).

    Within-race slopes of actual settle share and of (WPR - pre-race ability) on barrier share, pooled over
    all prior days at the same track and distance, shrunk toward the global slope (2019-2021).
    td_bar_settle / td_bar_perf are the slopes; tdx_* = slope x the runner's barrier share vs the field.
    """
    t = x.copy()   # all runs, so race days without results still get their prior history
    valid = t["y_settle"].notna()
    t["res"] = (t["wpr"] - t["h_wpr"]).where(t["h_none"] == 0)
    for c in ["y_settle", "barrier_pct", "res"]:
        v = t[c].where(valid)
        t[c + "_dm"] = v - v.groupby(t["race_id"]).transform("mean")
    t["sxy"], t["xx"] = t["y_settle_dm"] * t["barrier_pct_dm"], t["barrier_pct_dm"] ** 2
    t["pxy"] = t["res_dm"] * t["barrier_pct_dm"]
    t["pxx"] = t["xx"].where(t["res_dm"].notna())
    t["td"] = t["track"].astype(str) + "_" + t["dist"].astype(str)
    m = t.groupby(["td", "race_date"])[["sxy", "xx", "pxy", "pxx"]].sum().reset_index()
    early = m["race_date"].dt.year.between(2019, 2021)
    g_s = m.loc[early, "sxy"].sum() / m.loc[early, "xx"].sum()
    g_p = m.loc[early, "pxy"].sum() / m.loc[early, "pxx"].sum()
    m = m.sort_values(["td", "race_date"])
    cum = m.groupby("td")[["sxy", "xx", "pxy", "pxx"]].cumsum() - m[["sxy", "xx", "pxy", "pxx"]]
    m["td_bar_settle"] = (cum["sxy"] + TD_LAMBDA * g_s) / (cum["xx"] + TD_LAMBDA)
    m["td_bar_perf"] = (cum["pxy"] + TD_LAMBDA * g_p) / (cum["pxx"] + TD_LAMBDA)
    x["td"] = x["track"].astype(str) + "_" + x["dist"].astype(str)
    x = x.merge(m[["td", "race_date", "td_bar_settle", "td_bar_perf"]], on=["td", "race_date"], how="left")
    x["td_bar_settle"] = x["td_bar_settle"].fillna(g_s)
    x["td_bar_perf"] = x["td_bar_perf"].fillna(g_p)
    bd = x["barrier_pct"] - x.groupby("race_id")["barrier_pct"].transform("mean")
    x["tdx_settle"] = (x["td_bar_settle"] - g_s) * bd
    x["tdx_perf"] = (x["td_bar_perf"] - g_p) * bd
    GLOBALS["td"] = (g_s, g_p)
    return x


# ---------------------------------------------------------------- models

class _Model:
    """LightGBM regressor on inputs rounded to 1e-6, so float noise far below any real difference
    (e.g. 1e-14 from upstream fits) cannot move a value across a bin edge and change the trees."""

    def __init__(self, X, y):
        cat = [i for i, c in enumerate(X.columns) if c == "track_code"]
        self.m = lgb.train(dict(PARAMS, cat_smooth=20, max_cat_to_onehot=4),
                           lgb.Dataset(X.round(6).to_numpy(float), y.to_numpy(float), categorical_feature=cat), ROUNDS)

    def predict(self, X):
        return self.m.predict(np.round(np.asarray(X, dtype=float), 6))


def _fit(X, y):
    return _Model(X, y)


def _pace_frame(x):
    x = x.assign(_lead=(x["proj_settle"] < 0.15).astype(float), _early=x["es_today"])
    g = x.groupby("race_id")
    srt = x.assign(_k=x["proj_settle"].round(6)).sort_values(["race_id", "_k", "run_id"], kind="mergesort")
    front3 = srt.groupby("race_id").head(3)
    r = pd.DataFrame({
        "n_leaders": g["_lead"].sum(), "min_settle": g["proj_settle"].min(),
        "low3_settle": front3.groupby("race_id")["proj_settle"].mean(),
        "front3_early": front3.groupby("race_id")["_early"].mean(),
        "max_early": g["_early"].max(), "field_ability": g["h_wpr"].mean(),
        "field_n": g["field_n"].first(), "dist": g["dist"].first(), "synth": g["synth"].first(),
        "track_code": g["track_code"].first(), "going_num": g["going_num"].first(),
        "y_shape": g["y_shape"].first(), "y_lead_early": g["y_lead_early"].first(),
        "race_date": g["race_date"].first()})
    return r


def cost_coef(x, mask):
    """Within-race regression of (WPR - pre-race ability) on actual settle, pace and ground loss."""
    t = x[mask & (x["h_none"] == 0) & x["y_settle"].notna() & x["y_shape"].notna()].copy()
    t["pace"] = t["y_shape"] * (1 - t["y_settle"])
    t["gl"] = t["y_gl"].fillna(0)
    t["gl_miss"] = t["y_gl"].isna().astype(float)
    t["perf"] = t["wpr"] - t["h_wpr"]
    cols = ["y_settle", "pace", "gl", "gl_miss"]
    dm = t[cols + ["perf"]] - t.groupby("race_id")[cols + ["perf"]].transform("mean")
    b = np.linalg.lstsq(dm[cols].to_numpy(float), dm["perf"].to_numpy(float), rcond=None)[0]
    return dict(zip(["settle", "pace", "gl"], b[:3]))


def project(x, train_end, versions=("v2",), settle_fn=None):
    """Fit on rows in [2019, train_end), predict all rows. Returns (x with OUT cols, race frame, extras).
    settle_fn(x, train_end) -> projected settle per row, replacing the v3 settle model (e.g. projection_v4.settle)."""
    train_end = pd.Timestamp(train_end)
    x = x.copy()
    tr = (x["race_date"] < train_end) & (x["race_date"] >= "2019-01-01")
    extras = {}
    m = tr & x["y_settle"].notna()
    if settle_fn is None:
        x["proj_settle"] = _fit(x.loc[m, SETTLE_X], x.loc[m, "y_settle"]).predict(x[SETTLE_X].to_numpy(float)).clip(0, 1)
    else:
        x["proj_settle"] = np.asarray(settle_fn(x, train_end), float).clip(0, 1)
    if "old" in versions:
        x["proj_settle_old"] = _fit(x.loc[m, SETTLE_OLD], x.loc[m, "y_settle"]).predict(
            x[SETTLE_OLD].to_numpy(float)).clip(0, 1)
    den = (x["field_n"] - 1).clip(lower=1)
    x["proj_settle_rank"] = (_rank(x["proj_settle"], x["race_id"]) - 1) / den

    r = _pace_frame(x)
    rm = (r["race_date"] < train_end) & (r["race_date"] >= "2019-01-01")
    ok = rm & r["y_shape"].notna()
    r["proj_shape"] = _fit(r.loc[ok, PACE_X], r.loc[ok, "y_shape"]).predict(r[PACE_X].to_numpy(float))
    ok = rm & r["y_lead_early"].notna()
    r["proj_lead_early"] = _fit(r.loc[ok, PACE_X], r.loc[ok, "y_lead_early"]).predict(r[PACE_X].to_numpy(float))
    x = x.join(r[["proj_shape", "proj_lead_early"]], on="race_id")
    x["proj_pace"] = x["proj_shape"] * (1 - x["proj_settle"])

    mg = tr & x["y_gl"].notna()
    x["proj_gl"] = _fit(x.loc[mg, GL_X], x.loc[mg, "y_gl"]).predict(x[GL_X].to_numpy(float))
    x["proj_gl"] -= x.groupby("race_id")["proj_gl"].transform("mean")

    c = cost_coef(x, tr)
    extras["cost"] = c
    adj = c["settle"] * x["proj_settle"] + c["pace"] * x["proj_pace"] + c["gl"] * x["proj_gl"]
    x["proj_adj"] = adj - adj.groupby(x["race_id"]).transform("mean")
    sd = x["proj_settle"] - x.groupby("race_id")["proj_settle"].transform("mean")
    bd = x["barrier_pct"] - x.groupby("race_id")["barrier_pct"].transform("mean")
    x["tbx_settle_long"], x["tbx_settle_recent"] = x["tb_settle_long"] * sd, x["tb_settle_recent"] * sd
    x["tbx_bar_long"], x["tbx_bar_recent"] = x["tb_bar_long"] * bd, x["tb_bar_recent"] * bd
    x["bias_adj"] = x["tbx_settle_long"] + x["tbx_bar_long"]
    return x, r, extras


# ---------------------------------------------------------------- evaluation

def _r2(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    ok = ~(np.isnan(y) | np.isnan(p))
    y, p = y[ok], p[ok]
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def _spearman_in_race(df, a, b):
    t = df.dropna(subset=[a, b])
    ra = t.groupby("race_id")[a].rank()
    rb = t.groupby("race_id")[b].rank()
    t = t.assign(ra=ra, rb=rb)
    c = t.groupby("race_id")[["ra", "rb"]].corr().unstack().iloc[:, 1]
    return c.mean()


def _leader_hit(df, p):
    t = df.dropna(subset=["y_settle"])
    t = t[t.groupby("race_id")["y_settle"].transform("min") == 0]
    top = t.loc[t.groupby("race_id")[p].idxmin()]
    return (top["y_settle"] == 0).mean()


def main():
    from model.validate_figure import FIG, eval_set, fit_eval, race_ll
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = frame(con)
    print("frame", len(x0), flush=True)
    BASE = FIG + ["barrier_pct", "proj_settle", "proj_pace", "proj_gl", "proj_adj"] + BIAS
    variants = {
        "figure": FIG,
        "projection v3 + track bias": BASE,
        "+ track x distance barrier": BASE + TD,
        "+ speed map": BASE + SPEED_WIN,
        "+ both": BASE + TD + SPEED_WIN,
        "SP": ["log_p_sp"],
        "SP + projection v3 + track bias": ["log_p_sp"] + BASE,
        "SP + all": ["log_p_sp"] + BASE + TD + SPEED_WIN,
    }
    acc, ll_rows, per, per_qld, costs = [], [], {}, {}, {}
    for y in [2023, 2024, 2025, 2026]:
        x, r, ex = project(x0, f"{y}-01-01", versions=("old",))
        costs[y] = ex["cost"]
        te = x[(x.race_date.dt.year == y) & x["in_scope"]]
        rt = r[r.index.isin(te.race_id)]
        q = te[te.state == "QLD"]
        deb = te[te["h_none"] == 1]
        fu = te[te["first_up"] == 1]
        for lab, col in [("v3", "proj_settle"), ("previous", "proj_settle_old")]:
            acc += [
                {"fold": y, "metric": f"settle R2: {lab}", "v": _r2(te.y_settle, te[col])},
                {"fold": y, "metric": f"settle in-race rank corr: {lab}", "v": _spearman_in_race(te, "y_settle", col)},
                {"fold": y, "metric": f"projected leader led at 800m: {lab}", "v": _leader_hit(te, col)},
                {"fold": y, "metric": f"settle R2, first-up runners: {lab}", "v": _r2(fu.y_settle, fu[col])},
                {"fold": y, "metric": f"settle R2, debutants: {lab}", "v": _r2(deb.y_settle, deb[col])},
            ]
        acc += [{"fold": y, "metric": "pace R2: early shape", "v": _r2(rt.y_shape, rt.proj_shape)},
                {"fold": y, "metric": "ground loss R2 (QLD GPS)", "v": _r2(q.y_gl, q.proj_gl)}]
        e = eval_set(x)
        tr = e[e.race_date < f"{y}-01-01"]
        tt = e[e.race_date.dt.year == y]
        isq = (tt.loc[tt.won == 1, "state"] == "QLD").to_numpy()
        res = {"fold": y, "races": tt.race_id.nunique()}
        for k, cols in variants.items():
            ll = race_ll(fit_eval(tr, tt, cols)[0], tt)
            res[k] = ll.mean()
            per.setdefault(k, []).append(ll)
            per_qld.setdefault(k, []).append(ll[isq])
        ll_rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"}, flush=True)

    a = pd.DataFrame(acc).pivot(index="metric", columns="fold", values="v")
    t = pd.DataFrame(ll_rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    pq = {k: np.concatenate(v) for k, v in per_qld.items()}
    t.loc["pooled"] = [t["races"].sum()] + [pooled[k].mean() for k in per]

    def diff(p_, q_, src):
        z = src[p_] - src[q_]
        return z.mean(), z.std() / np.sqrt(len(z))
    comps = [("projection v3 + track bias", "figure"),
             ("+ track x distance barrier", "projection v3 + track bias"),
             ("+ speed map", "projection v3 + track bias"), ("+ both", "projection v3 + track bias"),
             ("SP + projection v3 + track bias", "SP"), ("SP + all", "SP + projection v3 + track bias"),
             ("SP + all", "SP")]
    _, b = fit_eval(e, e.iloc[:0], variants["+ both"])
    gs, gb = GLOBALS["bias"]
    ts, tp = GLOBALS["td"]
    L = ["# Race-day projection v3: walk-forward", "",
         "- Every model fitted on 2019 to Y-1 and tested on year Y (VIC/SA/QLD races)",
         "- v3 settle model adds: early-speed history matched to distance / first-up / going, speed map (early speed"
         " vs neighbours, faster rivals inside, wide x slow), barrier effect by track and distance, trials,"
         " weight and apprentice claim; track as a categorical. 'previous' = the v2 settle model", "",
         "## Projection accuracy", "", a.to_markdown(floatfmt=".3f"), "",
         "## Cost of race shape in WPR points (within-race regression, by fold)", "",
         pd.DataFrame(costs).to_markdown(floatfmt=".3f"), "",
         f"Global slopes (2019-2021), WPR per unit share: settle {gs:.2f}, barrier {gb:.2f}; barrier on settle"
         f" share {ts:.3f}, barrier on performance {tp:.2f}", "",
         "## Win model log loss (conditional logit)", "", t.T.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (pooled; negative = first is better)", "",
         "| model | vs | all: diff | se | QLD only: diff | se |", "|---|---|---|---|---|---|"]
    for p_, q_ in comps:
        d1, d2 = diff(p_, q_, pooled), diff(p_, q_, pq)
        L.append(f"| {p_} | {q_} | {d1[0]:+.4f} | {d1[1]:.4f} | {d2[0]:+.4f} | {d2[1]:.4f} |")
    L += ["", "## Projection terms in the '+ both' logit (fit on all 2022 on, raw units)", "",
          "| feature | beta |", "|---|---|"] + [f"| {k} | {v:+.4f} |" for k, v in b.items() if k in OUT]
    out = ROOT / "reports/projection_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
