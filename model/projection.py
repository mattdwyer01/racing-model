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
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, verbose=-1, num_threads=4, seed=1)
ROUNDS = 400
K = 8

EXTRA_SQL = """
select r.run_id, r.res_wpr wpr, r.barrier, r.jockey, r.trainer, r.age, ra.track, ra.surface, ra.going_num, ra.rail_m,
  count(*) over (partition by r.race_id) field_n,
  (r.res_pos800 - 1) / greatest(count(*) over (partition by r.race_id) - 1, 1) y_settle,
  ra.res_shape_early y_shape, ra.res_leader_early_rating y_lead_early,
  g.res_gps_extra_m y_gl,
  g.res_gps_rail_m - avg(g.res_gps_rail_m) over (partition by r.race_id) y_rail
from runs r join races ra using (race_id) left join gps_runs g using (run_id)
where not r.is_trial_or_jumpout
"""

SETTLE_X = ["st_mean", "st_last", "st_min3", "st_sd", "st_n", "st_dist", "dist_change", "h_s_early",
            "settle_rank", "early_rank", "inside_faster", "barrier", "barrier_pct", "field_n", "dist",
            "synth", "track_code", "rail_m", "jockey_fwd", "trainer_fwd", "first_up", "log_days",
            "h_none", "ability_rank", "age"]
SETTLE_V1 = ["h_settle", "h_s_early", "settle_rank_v1", "early_rank", "barrier", "barrier_pct", "field_n",
             "dist", "synth", "h_none", "h_settle_miss", "log_n"]
PACE_X = ["n_leaders", "min_settle", "low3_settle", "front3_early", "max_early", "field_n", "dist", "synth",
          "track_code", "going_num", "field_ability"]
GL_X = ["barrier", "barrier_pct", "inside_faster", "proj_settle", "proj_settle_rank", "gl_hist", "rail_hist",
        "gps_n", "jockey_width", "field_n", "dist", "synth", "track_code", "rail_m"]
GL_V1 = ["barrier", "barrier_pct", "field_n", "proj_settle", "proj_settle_rank", "h_gl", "h_gl_miss",
         "dist", "track_code", "synth"]
OUT = ["barrier_pct", "proj_settle", "proj_settle_rank", "proj_shape", "proj_pace", "proj_gl", "proj_adj"]


# ---------------------------------------------------------------- inputs

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

    # GPS width history
    for col, name in [("y_gl", "gl_hist"), ("y_rail", "rail_hist")]:
        v = _lags(x, col)
        okv = ~np.isnan(v)
        wv = np.where(okv, 0.5 ** (np.arange(K) / 3.0), 0)
        x[name] = (wv * np.nan_to_num(v)).sum(1) / (wv.sum(1) + 1.0)
    x["gps_n"] = (~np.isnan(_lags(x, "y_gl"))).sum(1)

    # field context
    x["barrier"] = x["barrier"].where(x["barrier"] > 0)
    g = x.groupby("race_id")
    den = (x["field_n"] - 1).clip(lower=1)
    x["barrier_pct"] = ((g["barrier"].rank(method="average") - 1) / den).fillna(0.5)
    st_fill = x["st_mean"].fillna(0.5)
    x["settle_rank"] = (st_fill.groupby(x["race_id"]).rank() - 1) / den
    hs = x["h_settle"].where(x["h_none"] == 0, 0.5)
    x["settle_rank_v1"] = (hs.groupby(x["race_id"]).rank() - 1) / den
    he = x["h_s_early"].where(x["h_none"] == 0)
    x["early_rank"] = ((he.groupby(x["race_id"]).rank(ascending=False) - 1) / den).fillna(0.5)
    x["ability_rank"] = ((x["h_wpr"].where(x["h_none"] == 0).groupby(x["race_id"]).rank(ascending=False) - 1)
                         / den).fillna(0.5)
    # rivals drawn inside with a more forward settle history
    x = x.sort_values(["race_id", "barrier"]).reset_index(drop=True)
    inside = np.zeros(len(x))
    for _, idx in x.groupby("race_id").indices.items():
        sf = x["st_mean"].to_numpy()[idx]
        sf = np.where(np.isnan(sf), 0.5, sf)
        for a in range(1, len(idx)):
            inside[idx[a]] = (sf[:a] < sf[a]).sum()
    x["inside_faster"] = inside / (x["field_n"] - 1).clip(lower=1)
    x = x.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)

    x["rail_m"] = x["rail_m"].where(x["rail_m"].between(0, 15))
    x["synth"] = x["surface"].isin(["Synthetic", "Sand", "Dirt"]).astype(float)
    x["track_code"] = x["track"].astype("category").cat.codes
    x["log_n"] = np.log1p(x["h_n"])
    x["log_days"] = np.log1p(x["days_since_start"].fillna(0))
    x["first_up"] = (x["days_since_start"].fillna(999) >= 60).astype(float)

    # jockey / trainer tendencies: actual settle minus the horse's own history; jockey width
    x["settle_resid"] = x["y_settle"] - x["st_mean"]
    x["jockey_fwd"] = _rolling_tendency(con, x, "jockey", "settle_resid", 365, 20)
    x["trainer_fwd"] = _rolling_tendency(con, x, "trainer", "settle_resid", 730, 20)
    x["jockey_width"] = _rolling_tendency(con, x, "jockey", "y_rail", 365, 20)
    return x


# ---------------------------------------------------------------- models

def _fit(X, y):
    return lgb.train(PARAMS, lgb.Dataset(X.to_numpy(float), y.to_numpy(float)), ROUNDS)


def _pace_frame(x):
    x = x.assign(_lead=(x["proj_settle"] < 0.15).astype(float), _early=x["h_s_early"].where(x["h_none"] == 0))
    g = x.groupby("race_id")
    srt = x.sort_values("proj_settle")
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


def project(x, train_end, versions=("v2",)):
    """Fit on rows in [2019, train_end), predict all rows. Returns (x with OUT cols, race frame, extras)."""
    train_end = pd.Timestamp(train_end)
    x = x.copy()
    tr = (x["race_date"] < train_end) & (x["race_date"] >= "2019-01-01")
    extras = {}
    m = tr & x["y_settle"].notna()
    x["proj_settle"] = _fit(x.loc[m, SETTLE_X], x.loc[m, "y_settle"]).predict(x[SETTLE_X].to_numpy(float)).clip(0, 1)
    if "v1" in versions:
        x["proj_settle_v1"] = _fit(x.loc[m, SETTLE_V1], x.loc[m, "y_settle"]).predict(
            x[SETTLE_V1].to_numpy(float)).clip(0, 1)
    den = (x["field_n"] - 1).clip(lower=1)
    x["proj_settle_rank"] = (x.groupby("race_id")["proj_settle"].rank() - 1) / den

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
    if "v1" in versions:
        x["proj_gl_v1"] = _fit(x.loc[mg, GL_V1], x.loc[mg, "y_gl"]).predict(x[GL_V1].to_numpy(float))
        x["proj_gl_v1"] -= x.groupby("race_id")["proj_gl_v1"].transform("mean")

    c = cost_coef(x, tr)
    extras["cost"] = c
    adj = c["settle"] * x["proj_settle"] + c["pace"] * x["proj_pace"] + c["gl"] * x["proj_gl"]
    x["proj_adj"] = adj - adj.groupby(x["race_id"]).transform("mean")
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
    acc, ll_rows, per, costs = [], [], {}, {}
    variants = {
        "figure": FIG,
        "figure + barrier": FIG + ["barrier_pct"],
        "figure + projection": FIG + ["barrier_pct", "proj_settle", "proj_pace", "proj_gl", "proj_adj"],
        "SP": ["log_p_sp"],
        "SP + figure": ["log_p_sp"] + FIG,
        "SP + figure + projection": ["log_p_sp"] + FIG + ["barrier_pct", "proj_settle", "proj_pace", "proj_gl",
                                                           "proj_adj"],
    }
    for y in [2023, 2024, 2025, 2026]:
        x, r, ex = project(x0, f"{y}-01-01", versions=("v1", "v2"))
        costs[y] = ex["cost"]
        te = x[(x.race_date.dt.year == y) & x["in_scope"]]
        rt = r[r.index.isin(te.race_id)]
        q = te[te.state == "QLD"]
        acc += [
            {"fold": y, "metric": "settle R2: v2", "v": _r2(te.y_settle, te.proj_settle)},
            {"fold": y, "metric": "settle R2: v1", "v": _r2(te.y_settle, te.proj_settle_v1)},
            {"fold": y, "metric": "settle in-race rank corr: v2", "v": _spearman_in_race(te, "y_settle", "proj_settle")},
            {"fold": y, "metric": "settle in-race rank corr: v1", "v": _spearman_in_race(te, "y_settle", "proj_settle_v1")},
            {"fold": y, "metric": "projected leader led at 800m: v2", "v": _leader_hit(te, "proj_settle")},
            {"fold": y, "metric": "projected leader led at 800m: v1", "v": _leader_hit(te, "proj_settle_v1")},
            {"fold": y, "metric": "pace R2: early shape", "v": _r2(rt.y_shape, rt.proj_shape)},
            {"fold": y, "metric": "pace R2: leader early rating", "v": _r2(rt.y_lead_early, rt.proj_lead_early)},
            {"fold": y, "metric": "ground loss R2 (QLD GPS): v2", "v": _r2(q.y_gl, q.proj_gl)},
            {"fold": y, "metric": "ground loss R2 (QLD GPS): v1", "v": _r2(q.y_gl, q.proj_gl_v1)},
        ]
        e = eval_set(x)
        tr = e[e.race_date < f"{y}-01-01"]
        tt = e[e.race_date.dt.year == y]
        res = {"fold": y, "races": tt.race_id.nunique()}
        for k, cols in variants.items():
            ll = race_ll(fit_eval(tr, tt, cols)[0], tt)
            res[k] = ll.mean()
            per.setdefault(k, []).append(ll)
        ll_rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"}, flush=True)

    a = pd.DataFrame(acc).pivot(index="metric", columns="fold", values="v")
    t = pd.DataFrame(ll_rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    t.loc["pooled"] = [t["races"].sum()] + [pooled[k].mean() for k in per]

    def diff(p, q):
        z = pooled[p] - pooled[q]
        return z.mean(), z.std() / np.sqrt(len(z))
    comps = [("figure + barrier", "figure"), ("figure + projection", "figure + barrier"),
             ("figure + projection", "figure"), ("SP + figure + projection", "SP + figure"),
             ("SP + figure + projection", "SP")]
    _, b = fit_eval(e, e.iloc[:0], variants["figure + projection"])
    L = ["# Race-day projection v2: walk-forward", "",
         "- Every model fitted on 2019 to Y-1 and tested on year Y (VIC/SA/QLD races); v1 = previous version", "",
         "## Projection accuracy", "", a.to_markdown(floatfmt=".3f"), "",
         "## Cost of race shape in WPR points (within-race regression, by fold)", "",
         pd.DataFrame(costs).to_markdown(floatfmt=".3f"),
         "", "settle: per unit of settle share (leader 0 to last 1); pace: per unit of early shape x (1 - settle);"
             " gl: per metre of extra ground", "",
         "## Win model log loss (conditional logit)", "", t.T.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (pooled, negative = first is better)", "", "| model | vs | diff | se |",
         "|---|---|---|---|"]
    L += [f"| {p} | {q} | {diff(p, q)[0]:+.4f} | {diff(p, q)[1]:.4f} |" for p, q in comps]
    L += ["", "## Projection terms in the figure + projection logit (fit on all 2022 on, raw units)", "",
          "| feature | beta |", "|---|---|"] + \
         [f"| {k} | {v:+.4f} |" for k, v in b.items() if k in OUT]
    out = ROOT / "reports/projection_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
