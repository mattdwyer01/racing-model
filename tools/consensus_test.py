"""Win bets on agreement between ratings: top n in Combo / TopRate rating / wpr_nett / Racing Model / form factor.

    python -W ignore tools/consensus_test.py --repo ../toprate [--runners-dir DIR]   # -> reports/consensus_test.md

Data: tools/combo_strike_test.load() (pre-race dashboard values 22 Aug 2026 on, all states). Extra pre-race input:
form factor (`pfm_score`, the dashboard's formFactor) from the 08:00 AEST runners file (git history). Combo is the
CURRENT dashboard Combo (0.3 WPR projection + 0.7 TopRate rating, 3 Oct 2026).
Rule = runner ranks <= n (1, 2, 3) in every rating of a set (any non-empty subset of the five), optionally speed map
not unfavoured (SM > -0.5) and no first starter in the race. Bets one unit at SP (and at the dashboard's stored fixed
price where there is one). 372 rules: chosen on the FIRST half of the dates (best ROI with >= 40 bets), then checked
on the second half. A/E price-matched = wins / win rate of all runners at the same SP.
"""
import argparse
import io
import itertools
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import combo_strike_test as cs  # noqa: E402

CACHE = ROOT / "data/interim/pfm_prerace"
OUT = ROOT / "reports/consensus_test.md"
AEST = timezone(timedelta(hours=10))
RATINGS = {"Combo": "combo70", "TopRate rating": "trr", "wpr_nett": "wpr_nett", "Racing Model": "lrm",
           "form factor": "pfm"}
rng = np.random.default_rng(12)


def pfm_day(repo, d):
    f = CACHE / f"{d}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    t = datetime(d.year, d.month, d.day, 8, tzinfo=AEST).astimezone(timezone.utc)
    sha = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%H", f"--before={t.isoformat()}", "origin/main",
                          "--", "toprate_runners.csv"], capture_output=True, text=True).stdout.strip()
    if not sha:
        return None
    import pyarrow.csv as pc
    data = subprocess.run(["git", "-C", repo, "show", f"{sha}:toprate_runners.csv"], capture_output=True).stdout
    head = data[:data.index(b"\n")].decode().split(",")
    if "pfm_score" not in head:
        return None
    tb = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=["run_id", "date", "pfm_score"], column_types={"run_id": "string", "date": "string"})).to_pandas()
    tb = tb[tb["date"] == str(d)][["run_id", "pfm_score"]]
    tb.to_parquet(f)
    return tb


def load(repo, runners_dir):
    d = cs.load(repo, runners_dir)
    CACHE.mkdir(parents=True, exist_ok=True)
    days = sorted(d["date"].dt.date.unique())
    pf = pd.concat([x for x in (pfm_day(repo, x) for x in days) if x is not None], ignore_index=True)
    d = d.merge(pf.drop_duplicates("run_id"), on="run_id", how="left")
    d["pfm"] = pd.to_numeric(d["pfm_score"], errors="coerce")
    d["combo70"] = np.where(d["trr"].notna(), 0.3 * d["proj"] + 0.7 * d["trr"], d["proj"])
    for name, c in RATINGS.items():
        d["rk_" + c] = d.groupby("race_id")[c].rank(ascending=False, method="min").fillna(99)
    d["sm_ok"] = ~(d["sm"] <= -0.5)
    d["no_fs"] = ~d["fs"].groupby(d["race_id"]).transform("any")
    dates = np.sort(d["date"].unique())
    d["half"] = np.where(d["date"].isin(dates[: len(dates) // 2]), 1, 2)
    return d


def stats(b):
    if len(b) == 0:
        return {"bets": 0}
    roi = 100 * ((b["won"] * b["sp"]).mean() - 1)
    fxb = b[b["fx"] > 1]
    out = {"bets": len(b), "win %": round(100 * b["won"].mean(), 1), "median SP": b["sp"].median(),
           "A/E pm": round(b["won"].sum() / b["p_ctl"].sum(), 3), "ROI SP %": round(roi, 1),
           "ROI fixed %": round(100 * ((fxb["won"] * fxb["fx"]).mean() - 1), 1) if len(fxb) else np.nan}
    if len(b) >= 30:
        r = (b["won"] * b["sp"]).to_numpy()
        m = r[rng.integers(0, len(r), (2000, len(r)))].mean(1)
        out["95% SP"] = f"{100 * (np.percentile(m, 2.5) - 1):+.0f} to {100 * (np.percentile(m, 97.5) - 1):+.0f}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--runners-dir", default=None)
    a = ap.parse_args()
    d = load(a.repo, a.runners_dir)
    rules = []
    names = list(RATINGS)
    for k in range(1, len(names) + 1):
        for subset in itertools.combinations(names, k):
            for n in (1, 2, 3):
                for sm in (False, True):
                    for nofs in (False, True):
                        m = np.ones(len(d), bool)
                        for nm in subset:
                            m &= (d["rk_" + RATINGS[nm]] <= n).to_numpy()
                        if sm:
                            m &= d["sm_ok"].to_numpy()
                        if nofs:
                            m &= d["no_fs"].to_numpy()
                        label = f"top {n} in " + " + ".join(subset) + (", SM not unfav" if sm else "") + \
                            (", no FS" if nofs else "")
                        rules.append((label, m, k, n))
    rows = []
    for label, m, k, n in rules:
        b = d[m]
        h1, h2 = b[b["half"] == 1], b[b["half"] == 2]
        s1, s2, s = stats(h1), stats(h2), stats(b)
        rows.append({"rule": label, "ratings": k, "n": n, "bets": s.get("bets", 0), "win %": s.get("win %"),
                     "A/E pm": s.get("A/E pm"), "ROI SP %": s.get("ROI SP %"), "95% SP": s.get("95% SP", ""),
                     "ROI fixed %": s.get("ROI fixed %"), "h1 bets": s1.get("bets", 0), "h1 ROI": s1.get("ROI SP %"),
                     "h2 bets": s2.get("bets", 0), "h2 ROI": s2.get("ROI SP %"), "h2 A/E pm": s2.get("A/E pm")})
    r = pd.DataFrame(rows)
    base = stats(d[d["rk_combo70"] == 1])
    fav = d.loc[d.groupby("race_id")["sp"].idxmin()]
    L = ["# Agreement between ratings as win bets (pre-race dashboard values)", "",
         f"- {d['race_id'].nunique():,} races, {d['date'].min():%d %b} to {d['date'].max():%d %b %Y}, all states."
         f" Halves: to {d.loc[d['half'] == 1, 'date'].max():%d %b} / after. Form factor filled for"
         f" {100 * d['pfm'].notna().mean():.0f}% of runners, wpr_nett {100 * d['wpr_nett'].notna().mean():.0f}%.",
         f"- Reference: Combo top pick {base['bets']} bets, win {base['win %']}%, ROI SP {base['ROI SP %']}%"
         f" (fixed {base['ROI fixed %']}%); SP favourite win {100 * fav['won'].mean():.1f}%, ROI"
         f" {100 * ((fav['won'] * fav['sp']).mean() - 1):+.1f}%.", "",
         "## Single ratings: top 1", "",
         r[(r["ratings"] == 1) & (r["n"] == 1)].drop(columns=["ratings", "n"]).to_markdown(index=False), "",
         "## Top 10 rules chosen on the FIRST half (>= 40 bets there), and how they did on the second half", ""]
    pick = r[r["h1 bets"] >= 40].sort_values("h1 ROI", ascending=False).head(10)
    L += [pick.drop(columns=["ratings", "n"]).to_markdown(index=False), "",
          f"- Second-half ROI of those 10: mean {pick['h2 ROI'].mean():+.1f}% (first half {pick['h1 ROI'].mean():+.1f}%).",
          "", "## All rules with >= 100 bets, best 20 by whole-window ROI (multiple testing: treat as leads)", "",
          r[r["bets"] >= 100].sort_values("ROI SP %", ascending=False).head(20)
          .drop(columns=["ratings", "n"]).to_markdown(index=False), "",
          "## Does agreement help? Average over rules by number of ratings that must agree (top n = 1)", "",
          r[r["n"] == 1].groupby("ratings").agg(rules=("rule", "size"), bets=("bets", "mean"),
                                                win=("win %", "mean"), ae=("A/E pm", "mean"),
                                                roi=("ROI SP %", "mean")).round(2).to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
