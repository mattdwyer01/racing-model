"""Figure diagnostic: does the per-run figure predict the next run better than WPR, and where is it biased?

    python model/figure_diagnostic.py      # -> reports/figure_diagnostic.md

Figure weights fitted on races before 2025 (ability.fit_coef); everything below is measured on 2025-26 runs.
1. Next-run prediction: for each start with a later start, predict the next start's WPR from
   (a) this run's WPR, (b) this run's figure, (c) decayed mean WPR, (d) decayed mean figure (pre-race of
   the next start). Linear fits on pre-2025 pairs; R2 and within-race rank correlation on 2025-26 pairs.
2. Bias: mean residual of next WPR (actual - predicted from (a) and from (b)), grouped by conditions of
   this run. A good figure flattens the patterns WPR leaves (e.g. leaders in fast-early races).
3. Stability: figure weights refitted with training cut-offs 2023 to 2026.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import ability, figure  # noqa: E402

TEST_FROM = "2025-01-01"

EXTRA_SQL = """
select r.run_id, ra.location_class, ra.going_num, r.res_wpr_status wpr_status, r.res_margin_l margin, r.age,
  ra.class_type
from runs r join races ra using (race_id) where not r.is_trial_or_jumpout
"""


def _r2(y, p):
    return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def _rank_corr(df, a, b):
    t = df[["race_id", a, b]].dropna()
    t = t[t.groupby("race_id")["race_id"].transform("size") >= 3]
    ra, rb = t.groupby("race_id")[a].rank(), t.groupby("race_id")[b].rank()
    return pd.concat([t["race_id"], ra.rename("x"), rb.rename("y")], axis=1).groupby("race_id")[["x", "y"]] \
        .corr().unstack().iloc[:, 1].mean()


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    d = ability.load(con)
    h = figure.history(d)
    coef = ability.fit_coef(h, TEST_FROM)
    a = ability.features(d, coef)          # adds fig and dm (decayed mean figure, pre-race)
    a = a.merge(h[["run_id", "h_wpr", "h_none"]], on="run_id").merge(con.sql(EXTRA_SQL).df(), on="run_id", how="left")
    a = a.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    g = a.groupby("horse_id", sort=False)
    # next start's actual WPR and its pre-race decayed means
    for c in ["wpr", "race_id", "race_date", "dm", "h_wpr", "h_none", "in_scope"]:
        a["next_" + c] = g[c].shift(-1)
    p = a[a["wpr"].notna() & a["next_wpr"].notna() & a["fig"].notna()].copy()
    p["gap_days"] = (p["next_race_date"] - p["race_date"]).dt.days
    tr = p[(p["next_race_date"] < TEST_FROM) & (p["race_date"] >= "2022-01-01")]
    te = p[(p["next_race_date"] >= TEST_FROM) & p["next_in_scope"].fillna(False).astype(bool)]

    preds = {"this run WPR": "wpr", "this run figure": "fig",
             "decayed mean WPR (pre-race)": "next_h_wpr", "decayed mean figure (pre-race)": "next_dm"}
    rows, fitted = [], {}
    for lab, col in preds.items():
        m = tr[col].notna() & ((tr["next_h_none"] == 0) if col.startswith("next_") else True)
        b = np.polyfit(tr.loc[m, col], tr.loc[m, "next_wpr"], 1)
        mt = te[col].notna() & ((te["next_h_none"] == 0) if col.startswith("next_") else True)
        yhat = np.polyval(b, te.loc[mt, col])
        fitted[col] = b
        rows.append({"predictor": lab, "slope": b[0], "R2 on 2025-26": _r2(te.loc[mt, "next_wpr"], yhat),
                     "within-race rank corr": np.nan, "pairs": int(mt.sum())})
    # within-race rank corr on the NEXT race (compare predictors on the same runners)
    q = te[te["next_h_none"] == 0].copy()
    for lab, col in preds.items():
        q["_p_" + col] = np.polyval(fitted[col], q[col])
    q["race_id"] = q["next_race_id"]
    for r in rows:
        col = preds[r["predictor"]]
        r["within-race rank corr"] = _rank_corr(q, "_p_" + col, "next_wpr")
    pred_tab = pd.DataFrame(rows)

    # year-by-year for the two decayed-mean predictors
    yr = []
    for y in [2025, 2026]:
        qy = q[q["next_race_date"].dt.year == y]
        yr.append({"year": y, "pairs": len(qy),
                   "R2 decayed mean WPR": _r2(qy["next_wpr"], qy["_p_next_h_wpr"]),
                   "R2 decayed mean figure": _r2(qy["next_wpr"], qy["_p_next_dm"]),
                   "rank corr WPR": _rank_corr(qy, "_p_next_h_wpr", "next_wpr"),
                   "rank corr figure": _rank_corr(qy, "_p_next_dm", "next_wpr")})

    # bias by conditions of this run: residual of next WPR predicted from this run's WPR vs figure
    te = te.copy()
    te["res_wpr"] = te["next_wpr"] - np.polyval(fitted["wpr"], te["wpr"])
    te["res_fig"] = te["next_wpr"] - np.polyval(fitted["fig"], te["fig"])
    te["settle_q"] = pd.cut(te["settle"].where(te["settle_miss"] == 0), [-0.01, 0.1, 0.3, 0.5, 0.7, 1.0],
                            labels=["leader (0-0.1)", "0.1-0.3", "0.3-0.5", "0.5-0.7", "back (0.7-1)"])
    te["shape_q"] = pd.cut(te["shape"], [-99, -3, -1, 1, 3, 99], labels=["slow <-3", "-3 to -1", "-1 to 1", "1 to 3", "fast >3"])
    te["lead_fast"] = np.where((te["settle"] <= 0.2) & (te["settle_miss"] == 0),
                               pd.cut(te["shape"], [-99, -2, 2, 99], labels=["on pace, slow early", "on pace, even", "on pace, fast early"]).astype(str),
                               "not on pace")
    te["dist_b"] = pd.cut(te["dist"], [0, 1100, 1300, 1600, 2000, 4000], labels=["<=1100", "1101-1300", "1301-1600", "1601-2000", "2000+"])
    te["going_b"] = pd.cut(te["going_num"].fillna(4), [0, 4, 6, 8, 11], labels=["good (<=4)", "soft 5-6", "soft 7-heavy 8", "heavy 9-10"])
    te["gap_b"] = pd.cut(te["gap_days"], [0, 14, 28, 60, 120, 10000], labels=["<=14d", "15-28d", "29-60d", "61-120d", "120d+"])
    te["age_b"] = te["age"].clip(2, 7).astype("Int64").astype(str).replace({"7": "7+"})
    te["field_b"] = pd.cut(te["field_size"], [0, 7, 10, 13, 30], labels=["<=7", "8-10", "11-13", "14+"])
    te["margin_b"] = pd.cut(te["margin"].fillna(0), [-0.01, 0.5, 2, 5, 10, 999], labels=["won/<=0.5L", "0.5-2L", "2-5L", "5-10L", "10L+"])
    te["sect_b"] = np.where(te["s_early_miss"] == 1, "sectionals missing", "sectionals present")
    te["status_b"] = te["wpr_status"].fillna("none")
    groups = [("settle position (share of field)", "settle_q"), ("race early shape", "shape_q"),
              ("on-pace runners by early shape", "lead_fast"), ("distance", "dist_b"), ("going", "going_b"),
              ("state", "state"), ("location class", "location_class"), ("class type", "class_type"),
              ("days to next start", "gap_b"), ("age", "age_b"), ("field size", "field_b"),
              ("beaten margin", "margin_b"), ("sectionals", "sect_b"), ("WPR status", "status_b")]
    bias = []
    for lab, col in groups:
        t = te.groupby(col, observed=True).agg(n=("res_wpr", "size"), wpr_resid=("res_wpr", "mean"),
                                              fig_resid=("res_fig", "mean"), se=("res_fig", "sem"))
        t = t[t["n"] >= 200]
        for k, r in t.iterrows():
            bias.append({"condition": lab, "group": k, "n": int(r.n), "resid, WPR-based": r.wpr_resid,
                         "resid, figure-based": r.fig_resid, "se": r.se})
    bias = pd.DataFrame(bias)
    spread = bias.groupby("condition").agg(wpr_spread=("resid, WPR-based", lambda s: s.max() - s.min()),
                                           fig_spread=("resid, figure-based", lambda s: s.max() - s.min()))

    stab = pd.DataFrame({y: ability.fit_coef(h, f"{y}-01-01") for y in [2023, 2024, 2025, 2026]})

    L = ["# Figure diagnostic", "",
         f"- Figure weights fitted on races before {TEST_FROM}; all tests on runs whose next start is in 2025-26"
         " (VIC/SA/QLD next races)",
         "- Next-run target: WPR of the horse's next start. Linear predictors fitted on 2022-2024 pairs", "",
         "## 1. Predicting the next start's WPR", "", pred_tab.to_markdown(index=False, floatfmt=".3f"), "",
         "Rank corr = mean within-race Spearman correlation between the prediction and the next race's WPR.", "",
         pd.DataFrame(yr).to_markdown(index=False, floatfmt=".3f"), "",
         "## 2. Bias by conditions of this run (mean residual of next WPR, WPR points)", "",
         "Positive = the horse ran better next time than predicted (the run was under-rated).", "",
         "Spread (max group minus min group) per condition:", "", spread.to_markdown(floatfmt=".2f"), "",
         bias.to_markdown(index=False, floatfmt=".2f"), "",
         "## 3. Figure weights by training cut-off (WPR points per unit)", "", stab.to_markdown(floatfmt=".3f")]
    out = ROOT / "reports/figure_diagnostic.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
