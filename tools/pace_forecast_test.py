"""Better pace forecasts: new pre-race pace inputs and targets, judged by how well they sort leader value.

    python -W ignore tools/pace_forecast_test.py            # -> reports/pace_forecast_test.md
    python -W ignore tools/pace_forecast_test.py --cached   # reuse data/interim/pace_forecast_races.parquet

Walk-forward (fit on 2019 to Y-1, test Y = 2023 to 2026 YTD, VIC/SA/QLD races), on top of projection v3 settle.
Race-level pace projections compared:
  v3            projection.proj_shape (target TopRate early shape, inputs PACE_X)
  shape+        target early shape, PACE_X + NEW (below)
  gps           target GPS pace (projection_gps: leaders' early speed vs field's late speed), PACE_X
  gps+          target GPS pace, PACE_X + NEW
  lv+           target = the race's realised leader value (within-race slope of WPR - prior WPR on projected
                settle share), PACE_X + NEW, weighted by the race's settle spread. Direct: what we want to know.
NEW inputs (all pre-race):
  horse pace history (decayed, last 8 runs): lead rate, forward rate (settle share <= 0.2), early rating when
  it led, early shape of races where it was forward; race aggregates of these (sum / max / 2nd max, projected
  front three); early speed top two, gap and count within 1.5 of the top; jockey forward tendency and barrier
  of the fastest early horses; class level / maiden; track x distance and track past mean early shape and
  leader value (strictly earlier dates, shrunk).
Judged by:
  - R2 / corr against actual early shape, GPS pace and leader value (test years)
  - leader value sorting: pooled within-race regression perf ~ sd + sd x z, z = the projection standardised
    over test races; the sd x z beta = WPR change in the leader-to-last slope per SD of the projection
    (positive = the projection finds races where forward runners lose value). Race bootstrap 95% CI.
    Also the actual slope in the bottom / top fifth of each projection. Hindsight rows use the actual pace.
"""
import argparse
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, projection  # noqa: E402
from model.projection import K, PACE_X, _fit, _lags, _r2  # noqa: E402
from model.projection_gps import gps_pace  # noqa: E402

CACHE = ROOT / "data/interim/pace_forecast_races.parquet"
RUNNERS = ROOT / "data/interim/pace_forecast_runners.parquet"
OUT = ROOT / "reports/pace_forecast_test.md"
FOLDS = [2023, 2024, 2025, 2026]
BOOT = 1000
rng = np.random.default_rng(11)
NEW = ["es_1", "es_2", "es_gap", "n_es_close", "lead_sum", "lead_max", "lead_2nd", "fwd_sum", "led_early_max",
       "led_early_2nd", "front3_shape_hist", "front3_lead", "front3_jfwd", "fast_bar", "fast_jfwd",
       "class_level", "maiden", "te_td_shape", "te_track_shape", "te_td_lv", "rail_m"]
CLASS_SQL = "select race_id, class_level, (class_type ilike '%maiden%')::double maiden, res_shape_mid y_mid from races"


def decayed(x, v, mask=None):
    """Decayed mean over the horse's last K runs of column v (optionally only runs where mask col is true)."""
    a = _lags(x, v)
    ok = ~np.isnan(a)
    if mask is not None:
        ok &= _lags(x, mask) == 1
    w = np.where(ok, 0.5 ** (np.arange(K) / 3.0), 0)
    return np.where(ok.any(1), (w * np.nan_to_num(a)).sum(1) / np.maximum(w.sum(1), 1e-9), np.nan), ok.sum(1)


def horse_history(x):
    x["_led"] = (x["y_settle"] == 0).astype(float).where(x["y_settle"].notna())
    x["_fwd"] = (x["y_settle"] <= 0.2).astype(float).where(x["y_settle"].notna())
    x["hp_lead_rate"], n = decayed(x, "_led")
    x["hp_fwd_rate"], _ = decayed(x, "_fwd")
    x["hp_led_early"], _ = decayed(x, "y_lead_early", "_led")
    x["hp_shape_fwd"], _ = decayed(x, "y_shape", "_fwd")
    x["hp_n"] = n
    return x.drop(columns=["_led", "_fwd"])


def target_enc(r, key, col, lam):
    """Past mean of col per key, strictly earlier dates, shrunk to 0 with lam pseudo-races."""
    t = r[[*key, "race_date", col]].dropna(subset=[col])
    g = t.groupby([*key, "race_date"])[col].agg(["sum", "count"]).reset_index().sort_values("race_date")
    cs = g.groupby(key)[["sum", "count"]].cumsum() - g[["sum", "count"]].to_numpy()
    g["te"] = cs["sum"] / (cs["count"] + lam)
    return r[[*key, "race_date"]].merge(g[[*key, "race_date", "te"]], on=[*key, "race_date"], how="left")["te"].to_numpy()


def race_features(x, r):
    """NEW race-level inputs from runner rows x (with proj_settle) onto race frame r (index race_id)."""
    x = x[["race_id", "proj_settle", "es_today", "hp_lead_rate", "hp_fwd_rate", "hp_led_early", "hp_shape_fwd",
           "jockey_fwd", "barrier_pct"]].copy()
    g = x.groupby("race_id")
    es = x.sort_values(["race_id", "es_today"], ascending=[True, False])
    top = es.groupby("race_id").head(2)
    rk = top.groupby("race_id").cumcount()
    f = pd.DataFrame(index=r.index)
    f["es_1"] = top[rk == 0].set_index("race_id")["es_today"]
    f["es_2"] = top[rk == 1].set_index("race_id")["es_today"]
    f["es_gap"] = f["es_1"] - f["es_2"]
    x["_close"] = (x["es_today"] >= x["race_id"].map(f["es_1"]) - 1.5).astype(float)
    f["n_es_close"] = x.groupby("race_id")["_close"].sum()
    fast = es.groupby("race_id").head(1).set_index("race_id")
    f["fast_bar"], f["fast_jfwd"] = fast["barrier_pct"], fast["jockey_fwd"]
    lr = x["hp_lead_rate"].fillna(0)
    f["lead_sum"] = lr.groupby(x["race_id"]).sum()
    s = x.assign(_lr=lr).sort_values(["race_id", "_lr"], ascending=[True, False])
    rk = s.groupby("race_id").cumcount()
    f["lead_max"] = s[rk == 0].set_index("race_id")["_lr"]
    f["lead_2nd"] = s[rk == 1].set_index("race_id")["_lr"]
    f["fwd_sum"] = x["hp_fwd_rate"].fillna(0).groupby(x["race_id"]).sum()
    s = x.dropna(subset=["hp_led_early"]).sort_values(["race_id", "hp_led_early"], ascending=[True, False])
    rk = s.groupby("race_id").cumcount()
    f["led_early_max"] = s[rk == 0].set_index("race_id")["hp_led_early"]
    f["led_early_2nd"] = s[rk == 1].set_index("race_id")["hp_led_early"]
    fr = x.sort_values(["race_id", "proj_settle"]).groupby("race_id").head(3).groupby("race_id")
    f["front3_shape_hist"] = fr["hp_shape_fwd"].mean()
    f["front3_lead"] = fr["hp_lead_rate"].mean()
    f["front3_jfwd"] = fr["jockey_fwd"].mean()
    for c in f.columns:
        r[c] = f[c]
    return r


def race_lv(x, col="proj_settle"):
    """Per race: within-race slope of perf on col and its weight (sum of squared deviations)."""
    t = x[(x["h_none"] == 0) & x["wpr"].notna()][["race_id", col, "wpr", "h_wpr"]].copy()
    t["perf"] = t["wpr"] - t["h_wpr"]
    t = t[t.groupby("race_id")["perf"].transform("size") >= 4]
    xd = t[col] - t.groupby("race_id")[col].transform("mean")
    yd = t["perf"] - t.groupby("race_id")["perf"].transform("mean")
    s = pd.DataFrame({"sxy": xd * yd, "sxx": xd * xd, "race_id": t["race_id"]}).groupby("race_id").sum()
    return s


def build():
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = projection.frame(con)
    x0 = horse_history(x0)
    gp = gps_pace(con)
    cl = con.sql(CLASS_SQL).df().set_index("race_id")
    print("frame", len(x0), "gps races", len(gp), flush=True)
    races, runners = [], []
    for y in FOLDS:
        end = pd.Timestamp(f"{y}-01-01")
        x, r, _ = projection.project(x0, end)
        r = r.join(cl).join(gp.rename("gps_pace"))
        r = race_features(x, r)
        lv = race_lv(x)
        r["lv"] = lv["sxy"] / lv["sxx"]
        r["lv_w"] = lv["sxx"]
        r["lv"] = r["lv"].where(r["lv_w"] > 0.05).clip(-40, 40)
        r["dist_b"] = pd.cut(r["dist"], [0, 1050, 1250, 1450, 1700, 2100, 9999], labels=False)
        rr = r.reset_index()
        r["te_td_shape"] = target_enc(rr, ["track_code", "dist_b"], "y_shape", 20)
        r["te_track_shape"] = target_enc(rr, ["track_code"], "y_shape", 20)
        r["te_td_lv"] = target_enc(rr.assign(lv=rr["lv"]), ["track_code", "dist_b"], "lv", 50)
        r["rail_m"] = x.groupby("race_id")["rail_m"].first()
        tr = (r["race_date"] < end) & (r["race_date"] >= "2019-01-01")
        X = PACE_X + NEW
        preds = {"v3": r["proj_shape"]}
        m = tr & r["y_shape"].notna()
        preds["shape+"] = _fit(r.loc[m, X], r.loc[m, "y_shape"]).predict(r[X].to_numpy(float))
        m = tr & r["gps_pace"].notna()
        preds["gps"] = _fit(r.loc[m, PACE_X], r.loc[m, "gps_pace"]).predict(r[PACE_X].to_numpy(float))
        preds["gps+"] = _fit(r.loc[m, X], r.loc[m, "gps_pace"]).predict(r[X].to_numpy(float))
        m = tr & r["lv"].notna()
        cat = [i for i, c in enumerate(X) if c == "track_code"]
        ds = lgb.Dataset(r.loc[m, X].round(6).to_numpy(float), r.loc[m, "lv"].to_numpy(float),
                         weight=r.loc[m, "lv_w"].to_numpy(float), categorical_feature=cat)
        lvm = lgb.train(dict(projection.PARAMS, num_leaves=15, min_data_in_leaf=1000, learning_rate=0.03,
                             cat_smooth=50), ds, 300)
        preds["lv+"] = lvm.predict(r[X].round(6).to_numpy(float))
        imp = pd.Series(lvm.feature_importance("gain"), index=X)
        print(y, "lv+ top inputs", imp.sort_values(ascending=False).head(8).round(0).to_dict(), flush=True)
        te_ids = x.loc[(x.race_date.dt.year == y) & x["core_scope"], "race_id"].unique()
        rt = r.loc[r.index.isin(te_ids)].copy()
        for k, v in preds.items():
            rt[f"p_{k}"] = pd.Series(np.asarray(v), index=r.index).loc[rt.index]
        rt["fold"] = y
        races.append(rt)
        xt = x[x["race_id"].isin(te_ids)][["run_id", "race_id", "proj_settle", "wpr", "h_wpr", "h_none", "y_settle",
                                          "state"]]
        runners.append(xt)
        print(y, "races", len(rt), {k: round(_r2(rt.y_shape, rt[f"p_{k}"]), 3) for k in preds}, flush=True)
        del x
    R = pd.concat(races)
    X_ = pd.concat(runners, ignore_index=True)
    R.to_parquet(CACHE)
    X_.to_parquet(RUNNERS)
    return R, X_


def sort_power(xr, z):
    """perf_d ~ sd + sd x z (pooled within race); returns beta of sd x z and race bootstrap CI."""
    t = xr.dropna(subset=["perf"]).copy()
    t["z"] = t["race_id"].map(z)
    t = t.dropna(subset=["z"])
    t = t[t.groupby("race_id")["perf"].transform("size") >= 4]
    sd = t["proj_settle"] - t.groupby("race_id")["proj_settle"].transform("mean")
    yd = t["perf"] - t.groupby("race_id")["perf"].transform("mean")
    a, b = sd.to_numpy(), (sd * t["z"]).to_numpy()
    y = yd.to_numpy()
    M = pd.DataFrame({"race_id": t["race_id"].to_numpy(), "aa": a * a, "ab": a * b, "bb": b * b, "ay": a * y,
                      "by": b * y}).groupby("race_id").sum().to_numpy()

    def solve(S):
        A = np.array([[S[0], S[1]], [S[1], S[2]]])
        return np.linalg.solve(A, S[3:5])[1]
    est = solve(M.sum(0))
    idx = rng.integers(0, len(M), (BOOT, len(M)))
    bs = [solve(M[i].sum(0)) for i in idx]
    return est, *np.percentile(bs, [2.5, 97.5])


def quint_slopes(xr, v):
    q = pd.qcut(v, 5, labels=False)
    out = []
    for k in [0, 4]:
        t = xr[xr["race_id"].isin(q.index[q == k])].dropna(subset=["perf"])
        t = t[t.groupby("race_id")["perf"].transform("size") >= 4]
        sd = t["proj_settle"] - t.groupby("race_id")["proj_settle"].transform("mean")
        yd = t["perf"] - t.groupby("race_id")["perf"].transform("mean")
        out.append((sd * yd).sum() / (sd * sd).sum())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true")
    a = ap.parse_args()
    if a.cached and CACHE.exists():
        R, X_ = pd.read_parquet(CACHE), pd.read_parquet(RUNNERS)
    else:
        R, X_ = build()
    X_["perf"] = np.where(X_["h_none"] == 0, X_["wpr"] - X_["h_wpr"], np.nan)
    models = ["v3", "shape+", "gps", "gps+", "lv+"]
    L = ["# Pace forecasts: new inputs and targets", "",
         f"- {len(R):,} VIC/SA/QLD test races 2023 to 2026 YTD (walk-forward); GPS pace known for "
         f"{R.gps_pace.notna().sum():,}. See the module docstring for models and inputs.", "",
         "## Accuracy (pooled test races)", "",
         "| projection | R2 early shape | corr early shape | corr GPS pace | corr leader value (weighted) |",
         "|---|---|---|---|---|"]
    ok = R["lv"].notna()
    for m in models:
        p = R[f"p_{m}"]
        w = R.loc[ok, "lv_w"]
        cw = np.cov(R.loc[ok, "lv"], p[ok], aweights=w)
        L.append(f"| {m} | {_r2(R.y_shape, p):.3f} | {R[['y_shape']].corrwith(p).iloc[0]:.3f} | "
                 f"{R[['gps_pace']].corrwith(p).iloc[0]:.3f} | {cw[0, 1] / np.sqrt(cw[0, 0] * cw[1, 1]):.3f} |")
    L += ["", "By fold, R2 early shape:", "",
          R.groupby("fold").apply(lambda g: pd.Series({m: _r2(g.y_shape, g[f"p_{m}"]) for m in models}))
          .to_markdown(floatfmt=".3f"), "",
          "## Leader value sorting", "",
          "beta = change in the within-race WPR slope on projected settle share per SD of the projection (sign set"
          " so positive = races the projection rates faster / worse for leaders have less leader value). Slopes"
          " are WPR per unit settle share (negative = forward runners better).", "",
          "| projection | beta per SD (95% CI) | slope, bottom fifth | slope, top fifth | spread |",
          "|---|---|---|---|---|"]
    rows = [(m, R[f"p_{m}"]) for m in models] + [("hindsight: actual early shape", R["y_shape"]),
                                                  ("hindsight: actual GPS pace", R["gps_pace"])]
    for name, v in rows:
        v = v.dropna()
        z = (v - v.mean()) / v.std()
        est, lo, hi = sort_power(X_, z)
        q1, q5 = quint_slopes(X_, v)
        L.append(f"| {name} | {est:+.3f} ({lo:+.3f} to {hi:+.3f}) | {q1:+.2f} | {q5:+.2f} | {q5 - q1:+.2f} |")
    # combos
    L += ["", "## Combined projections (z-scores averaged)", "", "| combo | beta per SD (95% CI) | spread |",
          "|---|---|---|"]
    zs = {m: (R[f"p_{m}"] - R[f"p_{m}"].mean()) / R[f"p_{m}"].std() for m in models}
    for combo in [("v3", "lv+"), ("shape+", "lv+"), ("gps+", "lv+"), ("shape+", "gps+", "lv+")]:
        v = sum(zs[m] for m in combo) / len(combo)
        z = (v - v.mean()) / v.std()
        est, lo, hi = sort_power(X_, z)
        q1, q5 = quint_slopes(X_, v)
        L.append(f"| {' + '.join(combo)} | {est:+.3f} ({lo:+.3f} to {hi:+.3f}) | {q5 - q1:+.2f} |")
    L += ["", "## Correlations between projections", "",
          pd.DataFrame({m: R[f"p_{m}"] for m in models}).corr().to_markdown(floatfmt=".2f")]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
