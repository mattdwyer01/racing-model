"""Win rule on three years of walk-forward Racing Model output: top pick + favoured race-day projection + price band.

    python -W ignore tools/topsm_test.py        # -> reports/topsm_test.md

Stands in for the dashboard rule "Combo top pick, SM >= +1, $3 to $6" (pre-race dashboard data exists only from 22 Aug
2026). Here, all walk-forward (models fitted before each year):
  top pick   Racing Model `model %` (tools/clear_test.py scores, market-free, yearly retrain)
  SM         race-day projection v3 adj (proj_adj + bias_adj, WPR) vs the race mean (data/interim/pace_leader_oos.parquet);
             the dashboard's SM column is the Racing Model's race-day part + past ground loss, also vs the field
  clear      gap to the 2nd pick on the WPR scale, 6.843 x ln(p1 / p2)
Prices: SP only (filter and returns at SP; no bet-time prices before 2026). VIC/SA/QLD, 2023 to Sep 2026.
A/E pm = wins / win rate of all runners at the same SP. Race bootstrap 95% on ROI.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/topsm_test.md"
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]
rng = np.random.default_rng(17)


def load():
    sc = pd.concat([pd.read_csv(ROOT / f"data/interim/clear_test_scores_{y}.csv.gz", dtype={"run_id": str, "race_id": str})
                    for y in (2023, 2024, 2025, 2026)], ignore_index=True)
    p = pd.read_parquet(ROOT / "data/interim/pace_leader_oos.parquet")
    p["run_id"] = p["run_id"].astype(str)
    p["race_id"] = p["race_id"].astype(str)
    d = p.merge(sc[["run_id", "model %"]], on="run_id", how="inner")
    d = d[(d["race_date"] < "2026-10-01") & d["won"].notna() & (d["sp"] > 1)].copy()
    d["won"] = d["won"].astype(int)
    full = d.groupby("race_id")["run_id"].transform("size") == d["field_n"]
    d = d[full | d["field_n"].isna()]
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ovr=("sp", lambda s: (1 / s).sum()),
                                  p=("model %", lambda s: s.notna().all()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & (ok.ovr >= 1.0) & ok.p])].copy()
    g = d.groupby("race_id")
    d["adj"] = d["proj_adj"].fillna(0) + d["bias_adj"].fillna(0)
    d["sm"] = d["adj"] - g["adj"].transform("mean")
    d["rk"] = g["model %"].rank(ascending=False, method="first")
    p2 = g["model %"].transform(lambda s: s.nlargest(2).iloc[-1])
    d["clear"] = np.where(d["rk"] == 1, 6.843 * np.log(d["model %"] / p2), 0.0)
    d["fs_race"] = g["h_none"].transform("max").fillna(0) > 0
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d["year"] = pd.to_datetime(d["race_date"]).dt.year
    return d


def st(b, name):
    if len(b) < 20:
        return {"rule": name, "bets": len(b)}
    r = (b["won"] * b["sp"]).to_numpy()
    m = r[rng.integers(0, len(r), (2000, len(r)))].mean(1)
    yrs = {f"ROI {y}": round(100 * ((t["won"] * t["sp"]).mean() - 1), 1) for y, t in b.groupby("year")}
    return {"rule": name, "bets": len(b), "per day": round(len(b) / b["race_date"].nunique(), 1),
            "win %": round(100 * b["won"].mean(), 1), "median SP": b["sp"].median(),
            "A/E pm": round(b["won"].sum() / b["p_ctl"].sum(), 3), "ROI %": round(100 * (r.mean() - 1), 1),
            "95%": f"{100 * (np.percentile(m, 2.5) - 1):+.0f} to {100 * (np.percentile(m, 97.5) - 1):+.0f}", **yrs}


def main():
    d = load()
    q = (d["sm"] >= 1).mean()
    top = d[d["rk"] == 1]
    t1 = top[top["sm"] >= 1]
    band = lambda b, lo, hi: b[(b["sp"] >= lo) & (b["sp"] <= hi)]  # noqa: E731
    rows = [st(top, "top pick (all)"), st(band(top, 3, 6), "top pick, SP $3-6 (no SM filter)"),
            st(t1, "top pick, SM >= +1"), st(band(t1, 2, 6), "top pick, SM >= +1, SP $2-6"),
            st(band(t1, 3, 6), "top pick, SM >= +1, SP $3-6  << the rule"),
            st(t1[t1["sp"] >= 3], "top pick, SM >= +1, SP $3+"),
            st(band(t1, 6, 1000), "top pick, SM >= +1, SP over $6"),
            st(band(t1[~t1["fs_race"]], 3, 6), "the rule, no first starter in the race"),
            st(band(top[top["sm"] > 0], 3, 6), "top pick, SM > 0, SP $3-6"),
            st(band(top[top["sm"] >= 2], 3, 6), "top pick, SM >= +2, SP $3-6"),
            st(t1[t1["clear"] >= 4], "top pick 4+ clear, SM >= +1 (current win rule analogue)"),
            st(band(t1[t1["clear"] >= 4], 2, 1000), "top pick 4+ clear, SM >= +1, SP $2+")]
    r = band(t1, 3, 6)
    st_rows = [st(t, f"the rule, {s}") for s, t in r.groupby("state")]
    L = ["# Top pick + favoured race-day projection + price band (walk-forward Racing Model, 2023 to Sep 2026)", "",
         f"- {d['race_id'].nunique():,} VIC/SA/QLD races, {d['race_date'].nunique():,} race days. SM >= +1 covers"
         f" {100 * q:.0f}% of runners here (the dashboard's SM >= +1: 18%). SP filter and returns.", "",
         pd.DataFrame(rows).to_markdown(index=False), "", "## The rule by state", "",
         pd.DataFrame(st_rows).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
