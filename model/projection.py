"""Race-day projection: settle position, race early pace, ground loss. Pre-race inputs only.

    python model/projection.py      # walk-forward R2 by fold -> reports/projection_validation.md

Three LightGBM regressors, each trained on races before the fold start:
    settle   target: position at the 800m as a share of the field (0 = leader)
             inputs: horse's decayed past settle and early sectional, both ranked within today's
                     field, barrier (raw and as a share of the field), field size, distance, surface
    pace     target: race early shape (TopRate raceShapeEarly, + = fast early), one row per race
             inputs: field make-up: projected leaders, mean of the 3 lowest projected settles,
                     mean of the 3 best past early sectionals, field size, distance, state
    gl       target: GPS extra ground vs field mean (m), QLD GPS runs only
             inputs: barrier, barrier share, field size, projected settle and its rank, horse's past
                     ground loss, distance, track
Outputs per run: proj_settle, proj_settle_rank, proj_shape, proj_pace (shape x (1 - settle)),
proj_gl, plus barrier and barrier_pct.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402

PARAMS = dict(objective="regression", num_leaves=31, learning_rate=0.05, min_data_in_leaf=200,
              feature_fraction=0.9, verbose=-1, num_threads=4, seed=1)
ROUNDS = 300

EXTRA_SQL = """
select r.run_id, r.barrier, ra.track, ra.surface,
  count(*) over (partition by r.race_id) field_n,
  (r.res_pos800 - 1) / greatest(count(*) over (partition by r.race_id) - 1, 1) y_settle,
  ra.res_shape_early y_shape, g.res_gps_extra_m y_gl
from runs r join races ra using (race_id) left join gps_runs g using (run_id)
where not r.is_trial_or_jumpout
"""
SETTLE_X = ["h_settle", "h_s_early", "settle_rank", "early_rank", "barrier", "barrier_pct", "field_n",
            "dist", "synth", "h_none", "h_settle_miss", "log_n"]
PACE_X = ["n_leaders", "low3_settle", "top3_early", "field_n", "dist", "synth", "is_qld", "is_vic", "is_sa"]
GL_X = ["barrier", "barrier_pct", "field_n", "proj_settle", "proj_settle_rank", "h_gl", "h_gl_miss",
        "dist", "track_code", "synth"]
OUT = ["barrier", "barrier_pct", "proj_settle", "proj_settle_rank", "proj_shape", "proj_pace", "proj_gl"]


def frame(con, h):
    """h = figure.history(...) output (all runs). Adds the inputs used by the projection models."""
    x = h.merge(con.sql(EXTRA_SQL).df(), on="run_id", how="left")
    g = x.groupby("race_id")
    x["barrier"] = x["barrier"].where(x["barrier"] > 0)
    x["barrier_pct"] = (g["barrier"].rank(method="average") - 1) / (x["field_n"] - 1).clip(lower=1)
    x["barrier_pct"] = x["barrier_pct"].fillna(0.5)
    # rivals without history get a neutral settle/early value before ranking
    hs = x["h_settle"].where(x["h_none"] == 0, 0.5)
    he = x["h_s_early"].where(x["h_none"] == 0, np.nan)
    x["settle_rank"] = (hs.groupby(x["race_id"]).rank() - 1) / (x["field_n"] - 1).clip(lower=1)
    x["early_rank"] = (he.groupby(x["race_id"]).rank(ascending=False) - 1) / (x["field_n"] - 1).clip(lower=1)
    x["early_rank"] = x["early_rank"].fillna(0.5)
    x["synth"] = x["surface"].isin(["Synthetic", "Sand", "Dirt"]).astype(float)
    x["log_n"] = np.log1p(x["h_n"])
    x["track_code"] = x["track"].astype("category").cat.codes
    x["is_qld"], x["is_vic"], x["is_sa"] = [(x["state"] == s).astype(float) for s in ["QLD", "VIC", "SA"]]
    return x


def _fit(X, y):
    return lgb.train(PARAMS, lgb.Dataset(X.to_numpy(float), y.to_numpy(float)), ROUNDS)


def _race_pace_frame(x):
    x = x.assign(_lead=(x["proj_settle"] < 0.2).astype(float),
                 _early=x["h_s_early"].where(x["h_none"] == 0))
    g = x.groupby("race_id")
    low3 = x.sort_values("proj_settle").groupby("race_id").head(3).groupby("race_id")["proj_settle"].mean()
    top3 = x.dropna(subset=["_early"]).sort_values("_early", ascending=False).groupby("race_id").head(3) \
        .groupby("race_id")["_early"].mean()
    r = pd.DataFrame({
        "n_leaders": g["_lead"].sum(),
        "low3_settle": low3,
        "top3_early": top3,
        "field_n": g["field_n"].first(), "dist": g["dist"].first(), "synth": g["synth"].first(),
        "is_qld": g["is_qld"].first(), "is_vic": g["is_vic"].first(), "is_sa": g["is_sa"].first(),
        "y_shape": g["y_shape"].first(), "race_date": g["race_date"].first()})
    return r


def project(x, train_end):
    """Fit on rows before train_end, predict every row. Returns run_id + OUT columns and the fitted models."""
    train_end = pd.Timestamp(train_end)
    tr = (x["race_date"] < train_end) & (x["race_date"] >= "2019-01-01")
    m = tr & x["y_settle"].notna()
    ms = _fit(x.loc[m, SETTLE_X], x.loc[m, "y_settle"])
    x = x.copy()
    x["proj_settle"] = ms.predict(x[SETTLE_X].to_numpy(float)).clip(0, 1)
    x["proj_settle_rank"] = (x.groupby("race_id")["proj_settle"].rank() - 1) / (x["field_n"] - 1).clip(lower=1)

    r = _race_pace_frame(x)
    rm = (r["race_date"] < train_end) & (r["race_date"] >= "2019-01-01") & r["y_shape"].notna()
    mp = _fit(r.loc[rm, PACE_X], r.loc[rm, "y_shape"])
    r["proj_shape"] = mp.predict(r[PACE_X].to_numpy(float))
    x = x.join(r["proj_shape"], on="race_id")
    x["proj_pace"] = x["proj_shape"] * (1 - x["proj_settle"])

    mg_rows = tr & x["y_gl"].notna()
    mg = _fit(x.loc[mg_rows, GL_X], x.loc[mg_rows, "y_gl"])
    x["proj_gl"] = mg.predict(x[GL_X].to_numpy(float))
    x["proj_gl"] = x["proj_gl"] - x.groupby("race_id")["proj_gl"].transform("mean")
    return x, r


def _r2(y, p):
    ok = ~(np.isnan(y) | np.isnan(p))
    y, p = y[ok], p[ok]
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum(), ok.sum()


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = frame(con, figure.history(figure.components(con)))
    rows = []
    for y in [2023, 2024, 2025, 2026]:
        x, r = project(x0, f"{y}-01-01")
        te = x[(x.race_date.dt.year == y) & x["in_scope"]]
        rt = r[(r.race_date.dt.year == y) & r.index.isin(te.race_id)]
        naive_settle = te["settle_rank"].to_numpy()
        gl_te = te[te.state == "QLD"]
        naive_gl = (2 * gl_te["barrier_pct"] - 1).to_numpy()
        for name, yv, pv in [
            ("settle: projection", te["y_settle"], te["proj_settle"]),
            ("settle: past-settle rank only", te["y_settle"], pd.Series(naive_settle, index=te.index)),
            ("race pace: projection", rt["y_shape"], rt["proj_shape"]),
            ("ground loss: projection (QLD GPS)", gl_te["y_gl"], gl_te["proj_gl"]),
        ]:
            r2, n = _r2(yv.to_numpy(float), pv.to_numpy(float))
            rows.append({"fold": y, "target": name, "R2": r2, "n": n})
        # barrier-only ground-loss baseline, scaled by OLS on test (upper bound for a linear barrier rule)
        yy, bb = gl_te["y_gl"].to_numpy(float), naive_gl
        ok = ~np.isnan(yy)
        b = np.polyfit(bb[ok], yy[ok], 1)
        rows.append({"fold": y, "target": "ground loss: barrier share only (best linear fit)",
                     "R2": _r2(yy[ok], np.polyval(b, bb[ok]))[0], "n": ok.sum()})
        print(y, "done", flush=True)
    t = pd.DataFrame(rows).pivot(index="target", columns="fold", values="R2")
    n = pd.DataFrame(rows).groupby("target")["n"].sum()
    t["test n (all folds)"] = n
    L = ["# Race-day projection: walk-forward R2 (VIC/SA/QLD test races)", "",
         "- Each model trained on 2019 to Y-1 (all AU; ground loss on QLD GPS runs), tested on year Y", "",
         t.to_markdown(floatfmt=".3f")]
    out = ROOT / "reports/projection_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
