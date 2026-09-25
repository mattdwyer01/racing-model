"""Racing Model rating blended with TopRate's rating and form factor (TopRate's Combo with our rating in place
of its WPR projection).

    python -W ignore tools/rm_toprate_blend_test.py            # -> reports/rm_toprate_blend_test.md
    python -W ignore tools/rm_toprate_blend_test.py --prerace  # -> reports/rm_toprate_blend_test_prerace.md

--prerace: TopRate rating and form factor as they stood before each race (tools/toprate_rating_snapshots.py,
git history of the runners file), not the runners file's final values, which follow the market to the jump
and beyond. Same races either way.

Same races and out-of-sample Racing Model scores as tools/compare_toprate_combo.py (VIC/SA/QLD, 26 Apr 2026 on,
monthly retrain). Racing Model rating on the WPR scale = 6.843 x log model probability (+ a per-race constant,
which drops out). Variants:
  fixed      Combo weights 0.50 / 0.25 / 0.25 with our rating in place of wprp_proj (TopRate rating and form
             factor rescaled onto the WPR scale exactly as Combo does)
  fitted     conditional logit on our log probability, TopRate rating and form factor (missing = race mean, with
             flags), fitted on one half of the dates and tested on the other (swapped)
Each alone and with log SP. Race bootstrap 95% ranges on the paired log loss differences.
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure  # noqa: E402
import compare_toprate_combo as ctc  # noqa: E402

WPR_PER_LOGP = 6.843
BOOT = 2000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prerace", action="store_true")
    a = ap.parse_args()
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql("""select l.run_id, l.race_id, l.date race_date, l.state, l.finish_position fp,
                             l.starting_price_sp sp, l.wprp_proj, l.toprate_rating, l.pfm_score
                      from live_runners l
                      where l.resulted = 1 and l.state in ('VIC','SA','QLD') and coalesce(l.scratched,0) = 0
                        and l.date >= date '2026-04-26'""").df()
    sc = pd.read_csv(ctc.OUT)
    d = live.merge(sc[["run_id", "model %"]], on="run_id", how="inner")
    d = d[d["sp"] > 1]
    if a.prerace:
        pre = pd.read_csv(ROOT / "data/interim/toprate_rating_prerace.csv.gz", dtype={"run_id": str})
        d["run_id"] = d["run_id"].astype(str)
        d = d.merge(pre[["run_id", "trr_pre", "pfm_pre"]], on="run_id", how="left")
        d["toprate_rating"], d["pfm_score"] = d["trr_pre"], d["pfm_pre"]
    d["combo"] = ctc.combo(d)
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()),
                                  m=("model %", lambda s: s.notna().all()), c=("combo", lambda s: s.notna().all()))
    full = live.groupby("race_id").size()
    ok = ok[(ok.n >= 4) & (ok.w == 1) & ok.m & ok.c & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["won"] = (d["fp"] == 1).astype(int)
    g = d.groupby("race_id")
    inv = 1 / d["sp"]
    d["lp_sp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    d["lp_model"] = np.log((d["model %"] / g["model %"].transform("sum")).clip(1e-9))
    d["rm_wpr"] = WPR_PER_LOGP * d["lp_model"]
    d["rm_wpr"] += ctc.WPR_M - d.groupby("race_id")["rm_wpr"].transform("mean")   # onto the WPR level (drops out)
    # fixed Combo weights with our rating in place of wprp_proj
    d["swap"] = ctc.combo(d.assign(wprp_proj=d["rm_wpr"]))
    for c in ["toprate_rating", "pfm_score"]:
        d[c + "_miss"] = d[c].isna().astype(float)
        d[c + "_f"] = d[c].fillna(d.groupby("race_id")[c].transform("mean")).fillna(0)
    TR, PF = ["toprate_rating_f", "toprate_rating_miss"], ["pfm_score_f", "pfm_score_miss"]
    V = {"Racing Model": ["lp_model"], "TopRate Combo": ["combo"], "TopRate rating": TR, "form factor": PF,
         "TopRate rating + form factor": TR + PF,
         "RM + TopRate rating + form factor, fixed Combo weights": ["swap"],
         "RM + TopRate rating + form factor, fitted": ["lp_model"] + TR + PF,
         "RM + TopRate rating, fitted": ["lp_model"] + TR, "RM + form factor, fitted": ["lp_model"] + PF,
         "SP (calibrated)": ["lp_sp"]}
    for k in ["Racing Model", "TopRate Combo", "RM + TopRate rating + form factor, fixed Combo weights",
              "RM + TopRate rating + form factor, fitted", "TopRate rating + form factor"]:
        V[k + " + SP"] = V[k] + ["lp_sp"]
    P = {k: ctc.fit_prob(d, v) for k, v in V.items()}
    w = d["won"] == 1
    L = pd.DataFrame({k: -np.log(p[w].clip(1e-12)).to_numpy() for k, p in P.items()})
    rng = np.random.default_rng(0)

    def ci(x):
        x = np.asarray(x)
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    rows = []
    for k, p in P.items():
        rank = p.groupby(d["race_id"]).rank(ascending=False, method="first")
        top = d[rank == 1]
        rows.append({"model": k, "log loss": L[k].mean(), "top pick won": f"{top['won'].mean():.1%}",
                     "ROI top pick at SP": f"{(top['won'] * top['sp']).mean() - 1:+.1%}"})
    best = "RM + TopRate rating + form factor, fitted"
    pairs = [(best, "Racing Model"), (best, "TopRate Combo"),
             ("RM + TopRate rating + form factor, fixed Combo weights", "TopRate Combo"),
             ("RM + TopRate rating, fitted", "Racing Model"), ("RM + form factor, fitted", "Racing Model"),
             (best + " + SP", "Racing Model + SP"), (best + " + SP", "SP (calibrated)"),
             ("Racing Model + SP", "SP (calibrated)"), ("TopRate Combo + SP", "SP (calibrated)"),
             ("TopRate rating + form factor + SP", "SP (calibrated)")]
    st = d.loc[w, "state"].to_numpy()
    qld = st == "QLD"
    prs = [{"first": a, "minus": b, "all": ci(L[a] - L[b]), "QLD": ci((L[a] - L[b])[qld]),
            "VIC/SA": ci((L[a] - L[b])[~qld])} for a, b in pairs]
    Lines = ["# Racing Model + TopRate rating + form factor" + (" (pre-race TopRate values)" if a.prerace else ""), "",
             f"- {int(w.sum()):,} VIC/SA/QLD races, {d['race_date'].min():%d %b} to {d['race_date'].max():%d %b %Y}; "
             "Racing Model out of sample (monthly retrain). Fitted blends: conditional logit, half-window swap.",
             "", "## Log loss and top pick", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".4f"), "",
             "## Paired differences (negative = first is better; 95% race bootstrap)", "",
             pd.DataFrame(prs).to_markdown(index=False), ""]
    (ROOT / f"reports/rm_toprate_blend_test{'_prerace' if a.prerace else ''}.md").write_text("\n".join(Lines) + "\n")
    print("\n".join(Lines))


if __name__ == "__main__":
    main()
