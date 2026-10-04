"""Search for win-bet rules that hold up out of sample (walk-forward Racing Model, VIC/SA/QLD, 2023 to Sep 2026).

    python -W ignore tools/strategy_search.py        # -> reports/strategy_search.md

Per runner (all walk-forward, models fitted before each year): Racing Model chance (`model %`, market-free) and its
blend with SP (`blend %`; tools/clear_test.py scores), race-day projection adj vs field (`sm`, v3 proj_adj + bias_adj),
model rank, clear (6.843 x ln(p1 / p2) for the top pick), overlay = blend x SP, SP rank, state, field size, going,
distance, prep run (DB runs). Bets 1 unit at SP (the only price for 2023-2025; blend / overlay use SP, so a live rule
would need a bet-time price close to SP).
Every combination of the filters below is a rule. Rules are CHOSEN on 2023-2024 (>= 150 bets) and then scored on
2025 to Sep 2026, which the choice never saw. A/E pm = wins / win rate of all runners at the same SP.
"""
from itertools import product
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/strategy_search.md"
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]
rng = np.random.default_rng(23)


def load():
    sc = pd.concat([pd.read_csv(ROOT / f"data/interim/clear_test_scores_{y}.csv.gz", dtype={"run_id": str, "race_id": str})
                    for y in (2023, 2024, 2025, 2026)], ignore_index=True)
    p = pd.read_parquet(ROOT / "data/interim/pace_leader_oos.parquet")
    p["run_id"] = p["run_id"].astype(str)
    p["race_id"] = p["race_id"].astype(str)
    d = p.merge(sc[["run_id", "model %", "blend %"]], on="run_id", how="inner")
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    x = con.sql("select cast(run_id as varchar) run_id, prep_run, days_since_start from runs where race_date >= date '2023-01-01'").df()
    d = d.merge(x, on="run_id", how="left")
    d = d[(d["race_date"] < "2026-10-01") & d["won"].notna() & (d["sp"] > 1)].copy()
    d["won"] = d["won"].astype(int)
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ovr=("sp", lambda s: (1 / s).sum()),
                                  p=("model %", lambda s: s.notna().all()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & (ok.ovr >= 1.08) & (ok.ovr <= 1.6) & ok.p])].copy()
    g = d.groupby("race_id")
    d["adj"] = d["proj_adj"].fillna(0) + d["bias_adj"].fillna(0)
    d["sm"] = d["adj"] - g["adj"].transform("mean")
    d["rk"] = g["model %"].rank(ascending=False, method="first")
    d["brk"] = g["blend %"].rank(ascending=False, method="first")
    d["spr"] = g["sp"].rank(method="first")
    p2 = g["model %"].transform(lambda s: s.nlargest(2).iloc[-1])
    d["clear"] = np.where(d["rk"] == 1, 6.843 * np.log(d["model %"] / p2), np.nan)
    d["ov"] = d["blend %"] / 100 * d["sp"]
    d["mov"] = d["model %"] / 100 * d["sp"]
    d["n"] = g["run_id"].transform("size")
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d["year"] = pd.to_datetime(d["race_date"]).dt.year
    d["train"] = d["year"] <= 2024
    return d


SEL = {"model top": lambda d: d["rk"] == 1, "model top 2": lambda d: d["rk"] <= 2,
       "model top, not SP fav": lambda d: (d["rk"] == 1) & (d["spr"] > 1), "model top 4+ clear": lambda d: d["clear"] >= 4,
       "blend overlay 1.0+": lambda d: d["ov"] >= 1.0, "blend overlay 1.1+": lambda d: d["ov"] >= 1.1,
       "model overlay 1.2+": lambda d: d["mov"] >= 1.2, "model overlay 1.5+": lambda d: d["mov"] >= 1.5,
       "any runner": lambda d: d["rk"] > 0}
PRICE = {"any": (1, 1000), "$1-2": (1, 2), "$2-3": (2, 3), "$3-5": (3, 5), "$5-8": (5, 8), "$8-15": (8, 15),
         "$2-5": (2, 5), "$3-8": (3, 8), "$15+": (15, 1000)}
STATE = {"all": None, "QLD": ["QLD"], "VIC": ["VIC"], "SA": ["SA"]}
SMF = {"any": None, "sm >= 0.5": 0.5, "sm >= 1": 1.0}
FIELD = {"any": (0, 99), "<= 8": (0, 8), "9-12": (9, 12), "13+": (13, 99)}
EXTRA = {"none": None, "good 1-6": lambda d: d["going_num"].fillna(4) <= 6, "wet 7+": lambda d: d["going_num"].fillna(4) >= 7,
         "first-up": lambda d: d["prep_run"] == 1, "not first-up": lambda d: d["prep_run"] > 1,
         "sprint < 1200": lambda d: d["dist"] < 1200, "1200-1599": lambda d: (d["dist"] >= 1200) & (d["dist"] < 1600),
         "1600+": lambda d: d["dist"] >= 1600}


def stats(b):
    if len(b) == 0:
        return dict(bets=0, roi=np.nan, ae=np.nan, win=np.nan)
    return dict(bets=len(b), roi=100 * ((b["won"] * b["sp"]).mean() - 1), ae=b["won"].sum() / b["p_ctl"].sum(),
                win=100 * b["won"].mean())


def ci(b):
    r = (b["won"] * b["sp"]).to_numpy()
    m = r[rng.integers(0, len(r), (2000, len(r)))].mean(1)
    return f"{100 * (np.percentile(m, 2.5) - 1):+.0f} to {100 * (np.percentile(m, 97.5) - 1):+.0f}"


def main():
    d = load()
    masks = {}
    for k, f in SEL.items():
        masks[("sel", k)] = f(d).to_numpy()
    rows = []
    for (sk, pk, stk, smk, fk, ek) in product(SEL, PRICE, STATE, SMF, FIELD, EXTRA):
        m = masks[("sel", sk)].copy()
        lo, hi = PRICE[pk]
        m &= ((d["sp"] >= lo) & (d["sp"] < hi)).to_numpy()
        if STATE[stk]:
            m &= d["state"].isin(STATE[stk]).to_numpy()
        if SMF[smk] is not None:
            m &= (d["sm"] >= SMF[smk]).to_numpy()
        lo, hi = FIELD[fk]
        m &= ((d["n"] >= lo) & (d["n"] <= hi)).to_numpy()
        if EXTRA[ek] is not None:
            m &= EXTRA[ek](d).fillna(False).to_numpy()
        tr, te = d[m & d["train"].to_numpy()], d[m & ~d["train"].to_numpy()]
        if len(tr) < 150:
            continue
        a, b = stats(tr), stats(te)
        rows.append({"selection": sk, "price": pk, "state": stk, "sm": smk, "field": fk, "extra": ek,
                     "train bets": a["bets"], "train ROI %": a["roi"], "train A/E": a["ae"],
                     "test bets": b["bets"], "test ROI %": b["roi"], "test A/E": b["ae"], "_m": m})
    r = pd.DataFrame(rows)
    n_rules = len(r)
    top = r.sort_values("train ROI %", ascending=False).head(30).copy()
    top["test 95%"] = [ci(d[m & ~d["train"].to_numpy()]) if m[~d["train"].to_numpy()].sum() >= 30 else "" for m in top["_m"]]
    fam = r.copy()
    fam["train decile"] = pd.qcut(fam["train ROI %"].rank(method="first"), 10, labels=False)
    dec = fam.groupby("train decile").agg(rules=("selection", "size"), train_roi=("train ROI %", "mean"),
                                          test_roi=("test ROI %", "mean"), test_ae=("test A/E", "mean")).round(2)
    # rules positive in BOTH periods with decent volume, and robust: positive in each of the 4 years
    yr = d["year"].to_numpy()
    def by_year(m):
        return [100 * ((d["won"][m & (yr == y)] * d["sp"][m & (yr == y)]).mean() - 1) if (m & (yr == y)).sum() >= 30 else np.nan
                for y in (2023, 2024, 2025, 2026)]
    both = r[(r["train ROI %"] > 0) & (r["test ROI %"] > 0) & (r["test bets"] >= 100)].copy()
    both[["2023", "2024", "2025", "2026"]] = [by_year(m) for m in both["_m"]]
    both["years +"] = (both[["2023", "2024", "2025", "2026"]] > 0).sum(1)
    both = both.sort_values(["years +", "test ROI %"], ascending=False).head(25)
    both["all 95%"] = [ci(d[m]) for m in both["_m"]]
    base = stats(d[d["rk"] == 1])
    L = ["# Strategy search: win rules chosen on 2023-2024, scored on 2025 to Sep 2026 (walk-forward RM, SP)", "",
         f"- {d['race_id'].nunique():,} VIC/SA/QLD races ({d.loc[d.train, 'race_id'].nunique():,} train /"
         f" {d.loc[~d.train, 'race_id'].nunique():,} test), {n_rules:,} rules with >= 150 train bets. Model top pick: train"
         f" {stats(d[(d.rk == 1) & d.train])['roi']:+.1f}%, test {stats(d[(d.rk == 1) & ~d.train])['roi']:+.1f}%."
         " All bets at SP; every runner loses ~-20% at SP on average here.", "",
         "## Do good training rules stay good? Rules grouped by training ROI decile", "", dec.to_markdown(), "",
         "## Best 30 rules on 2023-2024 and what they did on 2025-2026", "",
         top.drop(columns="_m").round(2).to_markdown(index=False), "",
         f"- Mean test ROI of these 30: {top['test ROI %'].mean():+.1f}% (train {top['train ROI %'].mean():+.1f}%).", "",
         "## Rules profitable in both periods (>= 100 test bets), most consistent first", "",
         both.drop(columns="_m").round(1).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
