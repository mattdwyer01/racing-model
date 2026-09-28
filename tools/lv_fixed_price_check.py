"""Leader value signal at captured fixed prices (indicative): 2026 runners from the --lv disagreement test.

    python -W ignore tools/lv_fixed_price_check.py      # needs reports/disagreement_per_runner_lv.csv.gz
                                                         # -> reports/lv_fixed_price_check.md

Price = the last git snapshot of the dashboard runners file (tools/extract_prices_from_git.py) at least 10 minutes
before the start (race_times.start_utc). These snapshots are often 1.5 to 3 hours old and are what the dashboard
showed, not necessarily what TAB offered (reports/price_timing.md), so this is indicative only.
Groups: runners the leader value pushes UP (top 5% / 10% of d) and DOWN (bottom 10% / 5%), thresholds from all
test years. Per group: flat 1-unit ROI at the fixed price and at SP; control = all 2026 runners with a fixed
price in the same fixed-price bands, reweighted to the group's price mix. Race bootstrap 95% ranges.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402

RUNNERS = ROOT / "reports/disagreement_per_runner_lv.csv.gz"
PRICES = ROOT / "data/interim/tab_price_history_from_git.csv.gz"
OUT = ROOT / "reports/lv_fixed_price_check.md"
BANDS = [1, 2, 3.5, 6, 11, 21, 51, 10000]
LEAD_MIN = 10
BOOT = 2000


def main():
    d = pd.read_csv(RUNNERS)
    x = d["d leader value"]
    thr = {q: x.quantile(q) for q in (0.05, 0.10, 0.90, 0.95)}
    d = d[d["fold"] == 2026].copy()
    con = duckdb.connect(str(figure.DB), read_only=True)
    st = con.sql("select race_id, start_utc from race_times").df()
    st["start_utc"] = pd.to_datetime(st["start_utc"], utc=True)
    h = pd.read_csv(PRICES)
    h = h[(h["scratched"].fillna(0) == 0) & h["fixed_win_price"].gt(1)]
    h["commit_utc"] = pd.to_datetime(h["commit_utc"], utc=True)
    h = h.merge(st, on="race_id")
    h = h[h["commit_utc"] <= h["start_utc"] - pd.Timedelta(minutes=LEAD_MIN)]
    last = h.sort_values("commit_utc").groupby("run_id").tail(1)
    last["age_min"] = (last["start_utc"] - last["commit_utc"]).dt.total_seconds() / 60
    d = d.merge(last[["run_id", "fixed_win_price", "age_min"]], on="run_id", how="inner")
    d["band"] = pd.cut(d["fixed_win_price"], BANDS)
    d["ret_fx"] = d["won"] * d["fixed_win_price"] - 1
    d["ret_sp"] = d["won"] * d["sp"] - 1
    d["ctrl"] = d["band"].map(d.groupby("band", observed=False)["ret_fx"].mean()).astype(float)
    rng = np.random.default_rng(0)
    rows = []
    v = d["d leader value"]
    groups = [("UP top 5%", v >= thr[0.95]), ("UP top 10%", v >= thr[0.90]), ("DOWN bottom 10%", v <= thr[0.10]),
              ("DOWN bottom 5%", v <= thr[0.05]), ("all 2026 runners with a price", v.notna())]
    for name, m in groups:
        for stn, sm in [("all", d["state"].notna()), ("QLD", d["state"] == "QLD"), ("VIC/SA", d["state"] != "QLD")]:
            g = d[m & sm]
            if len(g) < 100:
                continue
            w = g.groupby("race_id")[["ret_fx", "ret_sp", "ctrl", "won", "p_sp"]].sum()
            W = w.to_numpy()[rng.integers(0, len(w), (BOOT, len(w)))].sum(1)
            n = len(g)
            ex = (W[:, 0] - W[:, 2]) / n
            rows.append({"group": name, "races": stn, "runners": n, "wins": int(g["won"].sum()),
                         "median fixed price": g["fixed_win_price"].median(),
                         "ROI fixed": g["ret_fx"].mean(), "ROI SP": g["ret_sp"].mean(),
                         "control ROI fixed": g["ctrl"].mean(),
                         "ROI fixed - control 95%": f"{np.percentile(ex, 2.5):+.3f} to {np.percentile(ex, 97.5):+.3f}",
                         "A/E SP": g["won"].sum() / g["p_sp"].sum()})
    t = pd.DataFrame(rows)
    L = ["# Leader value at captured fixed prices (2026, indicative)", "",
         f"- {d.race_id.nunique():,} 2026 VIC/SA/QLD races, {len(d):,} runners with a snapshot price >= {LEAD_MIN} min"
         f" before the start; median snapshot age {d['age_min'].median():.0f} min (IQR {d['age_min'].quantile(.25):.0f}"
         f" to {d['age_min'].quantile(.75):.0f})",
         "- Snapshots are the dashboard's stored prices from git history, not a TAB log: indicative only", "",
         t.to_markdown(index=False, floatfmt=".3f")]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
