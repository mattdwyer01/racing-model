"""Does racing.com (VIC/SA) GPS help? Paired walk-forward comparison of two blend_eval runs that differ only in
whether gps_runs holds the racing.com rows (the 'without' run deletes them from a copy of the database).

    python model/blend_eval.py --variants prodmu --logit-only --tag rcgps_with          # normal database
    (same, on a copy with `delete from gps_runs where source = 'rc'`, --tag rcgps_without)
    python tools/rc_gps_test.py                                                          # -> reports/rc_gps_test.md

racing.com GPS enters training through gps_runs: the ground-loss projection target (projection.py y_gl), the
past ground-loss credit (h_gl, h_gl_miss, h_rail) and the position map's rail distance.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KEY = ["race_id", "race_date", "state", "fold"]
COLS = ["baseline: model logit", "baseline: blend logit", "prodmu: model logit", "prodmu: blend logit",
        "SP calibrated"]
BOOT = 2000


def main(without="rcgps_without", out="rc_gps_test", title="racing.com (VIC/SA) GPS: with vs without",
         what="the racing.com rows of gps_runs (ground-loss projection target, past ground-loss credit)"):
    w = pd.read_csv(ROOT / "reports/blend_per_race_rcgps_with.csv.gz", parse_dates=["race_date"])
    o = pd.read_csv(ROOT / f"reports/blend_per_race_{without}.csv.gz", parse_dates=["race_date"])
    k = [c for c in KEY if c in w and c in o]
    d = w[k + COLS].merge(o[k + COLS], on=k, suffixes=(" with", " without")).dropna()
    rng = np.random.default_rng(0)

    def ci(x):
        x = x.to_numpy()
        m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"
    subsets = [("all", pd.Series(True, index=d.index)), ("VIC/SA", d["state"].isin(["VIC", "SA"])),
               ("VIC", d["state"] == "VIC"), ("SA", d["state"] == "SA"), ("QLD", d["state"] == "QLD")]
    rows = []
    for c in COLS[:4]:
        r = {"model": c}
        for n, s in subsets:
            r[f"{n} (n={int(s.sum()):,})"] = ci(d.loc[s, f"{c} with"] - d.loc[s, f"{c} without"])
        rows.append(r)
    lvl = pd.DataFrame({f"{c} {a}": d.groupby("state")[f"{c} {a}"].mean() for c in COLS for a in ["with", "without"]
                        if not (c == "SP calibrated" and a == "without")}).T
    fold = pd.DataFrame({y: {c: (g[f"{c} with"] - g[f"{c} without"]).mean() for c in COLS[:4]}
                         for y, g in d.groupby("fold")}).T
    L = [f"# {title}", "",
         f"- {len(d):,} VIC/SA/QLD test races, folds 2023 to 2026 YTD, walk-forward (blend_eval, logit). The two runs "
         f"differ only in {what}.",
         "- with minus without; negative = it helps. 95% race bootstrap.", "",
         "## Paired differences", "", pd.DataFrame(rows).to_markdown(index=False), "",
         "## By fold (all races)", "", fold.to_markdown(floatfmt="+.4f"), "",
         "## Log loss by state", "", lvl.to_markdown(floatfmt=".4f"), ""]
    (ROOT / f"reports/{out}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["weights"]:     # carried weights vs every horse at the race average (weight_kg = 57)
        main("noweights", "weights_test", "Carried weight: real vs race average",
             "carried weight (the 'without' run sets runs.weight_kg = 57 for every run: weight vs field = 0, "
             "sectional weight correction off)")
    else:
        main()
