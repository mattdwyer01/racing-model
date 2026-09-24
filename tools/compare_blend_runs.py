"""Paired comparison of two blend_eval runs on the races they share (e.g. NSW/WA added to training vs not).

    python tools/compare_blend_runs.py nswwa mu --cols "prodmu: model logit" "prodmu: blend logit" \
        --out reports/blend_eval_nswwa_vs_mu.md

Reads reports/blend_per_race_{tag}.csv.gz for both tags, keeps races present in both, and reports
first minus second per column (95% race bootstrap), overall and by state group, pooled and by fold.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BOOT = 2000


def load(tag):
    return pd.read_csv(ROOT / f"reports/blend_per_race_{tag}.csv.gz", parse_dates=["race_date"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--cols", nargs="+", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    a, b = load(args.a), load(args.b)
    m = a.merge(b, on="race_id", suffixes=(" A", " B"))
    m["group"] = np.where(m["state A"] == "QLD", "QLD", "VIC/SA")
    rng = np.random.default_rng(0)
    rows = []
    for c in args.cols + ["SP calibrated"]:
        x_all = (m[f"{c} A"] - m[f"{c} B"]).to_numpy()
        for gname, mask in [("all", np.ones(len(m), bool)), ("QLD", m["group"] == "QLD"),
                            ("VIC/SA", m["group"] == "VIC/SA")]:
            x = x_all[np.asarray(mask)]
            mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
            rows.append({"column": c, "races": gname, "n": len(x), f"{args.a} - {args.b}": x.mean(),
                         "95% lo": np.percentile(mm, 2.5), "95% hi": np.percentile(mm, 97.5),
                         f"{args.a} mean": m.loc[np.asarray(mask), f"{c} A"].mean(),
                         f"{args.b} mean": m.loc[np.asarray(mask), f"{c} B"].mean()})
    fold = m.groupby("fold A").apply(lambda g: pd.Series({c: (g[f"{c} A"] - g[f"{c} B"]).mean() for c in args.cols}),
                                        include_groups=False)
    L = [f"# {args.a} vs {args.b}: same races, paired", "",
         f"- Races in both runs: {len(m):,} (of {len(a):,} in {args.a}, {len(b):,} in {args.b})",
         "- Negative = first run better. 95% ranges: 2,000 race bootstrap resamples", "",
         pd.DataFrame(rows).to_markdown(index=False, floatfmt=".4f"), "", "## By fold (mean difference)", "",
         fold.to_markdown(floatfmt=".4f")]
    text = "\n".join(L) + "\n"
    if args.out:
        Path(args.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
