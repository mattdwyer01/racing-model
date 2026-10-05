"""Placing each horse more precisely: settle (800m position share) forecast variants.

    python -W ignore tools/settle_test.py      # -> reports/settle_test.md, data/interim/settle_test_oos.parquet

Walk-forward by year (fit on races 2019 to Y-1, score Y = 2023 to 2026), the v3 settle model (projection.SETTLE_X,
LightGBM) against:
  slow       + slow-away history: share of the last 5 runs with a slow / awkward start in stewards / video comments,
               last start slow
  early200   + GPS position at 200m history (decayed, as early_hist uses 400m)
  both       slow + early200
  rank       LambdaRank on the within-race settle order (both feature sets), mapped to a share by its rank in the race
  spread     LightGBM on |error| of 'both' (later 25% of training): calibration of the per-horse uncertainty
TopRate pre-race fields (Apr 2026 on only): avg_settled_pos, avg_800m_pos, early_speed_score, speed_rank_in_race and
the settling label vs the field, as extra settle inputs; fit on 26 Apr to 31 Jul 2026, score 1 Aug on (same split for
the baseline).
Scored: R2 on the settle share, within-race Spearman, projected leader leads at the 800m (%).
"""
import re
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, projection as P  # noqa: E402

OUT = ROOT / "reports/settle_test.md"
OOS = ROOT / "data/interim/settle_test_oos.parquet"
SLOW = re.compile(r"slow|dwelt|missed the start|began awkwardly|jumped awkwardly|flat[- ]footed|blundered|reared|"
                  r"crowded at the start|bumped at the start|awkwardly", re.I)
NEW_SLOW, NEW_E2 = ["slow_rate", "slow_last"], ["e200_hist"]
TR = ["tr_avg_settled", "tr_avg_800", "tr_early", "tr_speed_rank", "tr_settling"]


def features(con, x):
    c = con.sql("""select cast(u.run_id as varchar) run_id, u.res_stewards, u.res_video, g.res_gps_early200
                   from runs u left join gps_runs g using (run_id)""").df()
    x["run_id"] = x["run_id"].astype(str)
    x = x.merge(c, on="run_id", how="left")
    txt = x["res_stewards"].fillna("") + " " + x["res_video"].fillna("")
    ran = x["y_settle"].notna()
    x["_slow"] = np.where(ran, txt.str.contains(SLOW).astype(float), np.nan)
    v = P._lags(x, "_slow")
    ok = ~np.isnan(v)
    x["slow_rate"] = np.where(ok[:, :5].any(1), np.nansum(v[:, :5], 1) / np.maximum(ok[:, :5].sum(1), 1), np.nan)
    x["slow_last"] = v[:, 0]
    x["_e2"] = x["res_gps_early200"].where(ran)
    e = P._lags(x, "_e2")
    ok = ~np.isnan(e)
    w = np.where(ok, 0.5 ** (np.arange(P.K) / 3.0), 0)
    x["e200_hist"] = np.where(ok.any(1), (w * np.nan_to_num(e)).sum(1) / np.maximum(w.sum(1), 1e-9), np.nan)
    return x.drop(columns=["res_stewards", "res_video", "res_gps_early200", "_slow", "_e2"])


def metrics(t, p):
    ok = t["y_settle"].notna()
    t, p = t[ok], pd.Series(np.asarray(p)[ok.to_numpy()], index=t.index)
    r2 = 1 - ((t["y_settle"] - p) ** 2).sum() / ((t["y_settle"] - t["y_settle"].mean()) ** 2).sum()
    rp = p.groupby(t["race_id"]).rank()
    ry = t["y_settle"].groupby(t["race_id"]).rank()
    sp = np.corrcoef(rp - rp.groupby(t["race_id"]).transform("mean"), ry - ry.groupby(t["race_id"]).transform("mean"))[0, 1]
    lead = t.loc[p.groupby(t["race_id"]).idxmin(), "y_settle"].eq(0).mean()
    return round(r2, 4), round(sp, 4), round(100 * lead, 1)


def to_share(score, t, higher_forward=True):
    s = pd.Series(score, index=t.index)
    rk = s.groupby(t["race_id"]).rank(ascending=not higher_forward, method="average")
    n = t.groupby("race_id")["race_id"].transform("count")
    return ((rk - 1) / (n - 1).clip(lower=1)).to_numpy()


def rank_model(tr, te, feats):
    tr = tr[tr["y_settle"].notna()].sort_values(["race_id"])
    rel = np.clip(np.round((1 - tr["y_settle"]) * 10), 0, 10).astype(int)
    grp = tr.groupby("race_id", sort=False).size().to_numpy()
    m = lgb.train(dict(objective="lambdarank", learning_rate=0.05, num_leaves=63, min_data_in_leaf=200, verbose=-1,
                       label_gain=list(range(11)), deterministic=True, force_row_wise=True, seed=7),
                  lgb.Dataset(tr[feats].astype(float).round(6), rel, group=grp), 400)
    return to_share(m.predict(te[feats].astype(float).round(6)), te)


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    x = features(con, P.frame(con))
    print("frame", x.shape, flush=True)
    sets = {"v3 (live)": P.SETTLE_X, "slow": P.SETTLE_X + NEW_SLOW, "early200": P.SETTLE_X + NEW_E2,
            "both": P.SETTLE_X + NEW_SLOW + NEW_E2}
    rows, parts = [], []
    for y in (2023, 2024, 2025, 2026):
        tr = x[(x["race_date"] >= "2019-01-01") & (x["race_date"] < f"{y}-01-01") & x["y_settle"].notna()]
        te = x[(x["race_date"].dt.year == y) & x["y_settle"].notna()].copy()
        keep = te[["run_id", "race_id", "race_date", "y_settle"]].copy()
        for name, f in sets.items():
            keep[name] = P._fit(tr[f], tr["y_settle"]).predict(te[f].to_numpy(float)).clip(0, 1)
        keep["v3 as rank"] = to_share(-keep["v3 (live)"].to_numpy(), te)
        keep["both as rank"] = to_share(-keep["both"].to_numpy(), te)
        keep["rank (both)"] = rank_model(tr, te, sets["both"])
        # spread: |error| of 'both' learned on the later 25% of training
        cut = tr["race_date"].quantile(0.75)
        a, b = tr[tr["race_date"] <= cut], tr[tr["race_date"] > cut]
        mb = P._fit(a[sets["both"]], a["y_settle"])
        res = (b["y_settle"] - mb.predict(b[sets["both"]].to_numpy(float))).abs()
        sm = lgb.train(dict(objective="l1", num_leaves=31, learning_rate=0.05, min_data_in_leaf=200, verbose=-1),
                       lgb.Dataset(b[sets["both"]].astype(float), res), 300)
        keep["spread"] = sm.predict(te[sets["both"]].astype(float))
        parts.append(keep)
        for v in [c for c in keep if c not in ("run_id", "race_id", "race_date", "y_settle", "spread")]:
            r2, sp, ld = metrics(keep, keep[v])
            rows.append({"fold": y, "variant": v, "R2": r2, "Spearman in race": sp, "leader leads %": ld})
        print(y, "done", flush=True)
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(OOS)
    t = pd.DataFrame(rows)
    piv = t.pivot_table(index="variant", values=["R2", "Spearman in race", "leader leads %"], aggfunc="mean").round(4)
    byy = t.pivot_table(index="variant", columns="fold", values="R2").round(4)
    # spread calibration: share of actual within +/- predicted spread x 1.25 (mean abs to sd), by spread quintile
    d["err"] = (d["y_settle"] - d["both"]).abs()
    d["q"] = pd.qcut(d["spread"], 5, labels=False)
    cal = d.groupby("q").agg(spread=("spread", "mean"), mean_abs_error=("err", "mean"), runners=("err", "size")).round(3)
    # TopRate pre-race fields, 2026 only
    tr_rows = []
    try:
        S = Path("/tmp/claude-0/-home-user-racing-model/9a9ae262-cc87-5934-9222-4ece5edef6b6/scratchpad/runners_all.pkl")
        rf = pd.read_pickle(S) if S.exists() else pd.read_csv(ROOT.parent / "toprate/toprate_runners_archive.csv.gz", low_memory=False)
        rf = rf.copy()
        rf["run_id"] = rf["run_id"].astype(str)
        g = rf.groupby("race_id")
        n = g["run_id"].transform("count")
        for src, dst in (("avg_settled_pos", "tr_avg_settled"), ("avg_800m_pos", "tr_avg_800"),
                         ("early_speed_score", "tr_early"), ("speed_rank_in_race", "tr_speed_rank")):
            rf[dst] = pd.to_numeric(rf[src], errors="coerce") / (n if dst != "tr_early" else 1)
        rf["tr_settling"] = rf["_settling"].map({"leader": 0, "on pace": 1, "on-pace": 1, "midfield": 2, "back": 3,
                                                "backmarker": 3}).astype(float)
        z = x.merge(rf[["run_id"] + TR], on="run_id", how="inner")
        z = z[z["y_settle"].notna()]
        a, b = z[z["race_date"] < "2026-08-01"], z[z["race_date"] >= "2026-08-01"]
        for name, f in (("v3 (live)", P.SETTLE_X), ("both", sets["both"]), ("both + TopRate", sets["both"] + TR)):
            p = P._fit(a[f], a["y_settle"]).predict(b[f].to_numpy(float)).clip(0, 1)
            r2, sp, ld = metrics(b, p)
            tr_rows.append({"variant": name, "R2": r2, "Spearman in race": sp, "leader leads %": ld, "train runs": len(a),
                            "test runs": len(b)})
    except Exception as e:  # noqa: BLE001
        tr_rows.append({"variant": f"TopRate test failed: {type(e).__name__}: {str(e)[:100]}"})
    L = ["# Settle forecast: placing each horse more precisely (walk-forward 2023 to Sep 2026)", "",
         f"- {d['race_id'].nunique():,} races, {len(d):,} runs with an 800m position (all states in the frame).",
         "- R2 on the 800m settle share; Spearman = within-race rank correlation; leader leads % = the projected leader is",
         "  first at the 800m. 'as rank' = the same forecast turned into its rank share within the race.", "",
         "## Mean over folds", "", piv.to_markdown(), "", "## R2 by year", "", byy.to_markdown(), "",
         "## Spread model (per-horse uncertainty of 'both'), by predicted-spread fifth", "", cal.to_markdown(), "",
         "## TopRate pre-race fields (fit 26 Apr to 31 Jul 2026, score 1 Aug on)", "", pd.DataFrame(tr_rows).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
