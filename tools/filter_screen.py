"""Which pre-race filters pick runners the market under-prices? Screen on three years of walk-forward data.

    python -W ignore tools/filter_screen.py        # -> reports/filter_screen.md

Runners: tools/strategy_search.load() (VIC/SA/QLD 2023 to Sep 2026, Racing Model walk-forward scores, race-day adj) plus
pre-race facts from the DB: class / jockey / weight / distance change vs the horse's last start, last-start result,
spell, trials, barrier, age / sex, jockey and trainer strike rate over the previous 365 days (to the day before).
Per filter: price-matched A/E (wins / win rate of all runners at the same SP) and ROI at SP, in 2023-24 and 2025-26
separately, among (a) all runners and (b) the dashboard-style pool: within 4 of the model's top pick, SP $2+, no
first starter. A filter is worth keeping when A/E > 1 in both periods.
"""
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

import strategy_search as ss

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/filter_screen.md"
rng = np.random.default_rng(5)


def strike(r, key, days=365):
    """Prior-365-day wins / rides for jockey or trainer, using races strictly before the date."""
    x = r[[key, "race_date", "won_all"]].dropna(subset=[key])
    day = x.groupby([key, "race_date"]).agg(w=("won_all", "sum"), n=("won_all", "size")).reset_index()
    day = day.sort_values([key, "race_date"])
    out = []
    for k, g in day.groupby(key, sort=False):
        t = g.set_index("race_date")[["w", "n"]]
        roll = t.rolling(f"{days}D").sum().shift(1)          # windows end the day before
        roll[key] = k
        out.append(roll.reset_index())
    s = pd.concat(out, ignore_index=True)
    s[key + "_sr"] = s["w"] / s["n"]
    s[key + "_n"] = s["n"]
    return s[[key, "race_date", key + "_sr", key + "_n"]]


def facts():
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    r = con.sql("""select cast(u.run_id as varchar) run_id, u.horse_id, u.race_date, u.barrier, u.weight_kg, u.weight_claim_kg,
                          u.jockey, u.trainer, u.age, u.sex, u.prep_run, u.days_since_start, u.trials_since_last_start,
                          u.res_finish, u.res_margin_l, u.res_won won_all, r.class_level, r.location_class, r.distance
                   from runs u join races r using (race_id)
                   where u.race_date >= date '2021-06-01' and not coalesce(u.is_trial_or_jumpout, false)""").df()
    r["race_date"] = pd.to_datetime(r["race_date"])
    r = r.sort_values(["horse_id", "race_date"])
    g = r.groupby("horse_id")
    for c in ("class_level", "jockey", "weight_kg", "distance", "res_finish", "res_margin_l", "location_class"):
        r["last_" + c] = g[c].shift(1)
    r["won_all"] = r["won_all"].astype(float).fillna(0)
    for k in ("jockey", "trainer"):
        r = r.merge(strike(r, k), on=[k, "race_date"], how="left")
    return r[r["race_date"] >= "2023-01-01"]


def main():
    d = ss.load()
    f = facts()
    d = d.merge(f.drop(columns=["race_date", "won_all", "prep_run", "days_since_start"]), on="run_id", how="left")
    g = d.groupby("race_id")
    d["gap"] = 6.843 * np.log(g["model %"].transform("max") / d["model %"])
    d["fs_race"] = g["h_none"].transform("max").fillna(0) > 0
    d["bar_pct"] = (d["barrier"] - 1) / (d["n"] - 1).clip(lower=1)
    d["sm_hi"] = d["sm"] >= d["sm"].quantile(0.82)
    F = {
        "speed map favoured (top 18%)": d["sm_hi"],
        "projected leader": d["proj_settle_rank"] == 1,
        "projected back third": d["proj_settle"] >= 0.67,
        "track bias helps (bias_adj top 20%)": d["bias_adj"] >= d["bias_adj"].quantile(0.8),
        "track bias hurts (bottom 20%)": d["bias_adj"] <= d["bias_adj"].quantile(0.2),
        "barrier 1-3": d["barrier"] <= 3, "barrier 10+": d["barrier"] >= 10,
        "first-up": d["prep_run"] == 1, "second-up": d["prep_run"] == 2, "4th+ up": d["prep_run"] >= 4,
        "back within 14 days": d["days_since_start"] <= 14, "trialled since last start": d["trials_since_last_start"] > 0,
        "dropping in class": d["class_level"] < d["last_class_level"], "rising in class": d["class_level"] > d["last_class_level"],
        "metro last start, not metro today": (d["last_location_class"] == "Metro") & (d["location_class"] != "Metro"),
        "jockey change": d["jockey"] != d["last_jockey"],
        "apprentice claiming": d["weight_claim_kg"] > 0,
        "weight down 2kg+ vs last": d["weight_kg"] <= d["last_weight_kg"] - 2,
        "weight up 2kg+ vs last": d["weight_kg"] >= d["last_weight_kg"] + 2,
        "distance up 200m+": d["distance"] >= d["last_distance"] + 200, "distance down 200m+": d["distance"] <= d["last_distance"] - 200,
        "won last start": d["last_res_finish"] == 1, "placed 2-3 last start": d["last_res_finish"].isin([2, 3]),
        "beaten 6L+ last start": d["last_res_margin_l"] >= 6,
        "top jockey (365d strike 18%+, 50+ rides)": (d["jockey_sr"] >= 0.18) & (d["jockey_n"] >= 50),
        "weak jockey (strike < 7%)": (d["jockey_sr"] < 0.07) & (d["jockey_n"] >= 50),
        "top trainer (strike 18%+, 50+ runners)": (d["trainer_sr"] >= 0.18) & (d["trainer_n"] >= 50),
        "age 2-3": d["age"] <= 3, "age 6+": d["age"] >= 6,
        "mare / filly": d["sex"].astype(str).str.lower().str[0].isin(["m", "f"]),
        "wet track (7+)": d["going_num"] >= 7, "field 13+": d["n"] >= 13, "field <= 8": d["n"] <= 8,
        "model overlay (model % x SP >= 1.2)": d["mov"] >= 1.2, "blend overlay (>= 1.1)": d["ov"] >= 1.1,
        "SP favourite": d["spr"] == 1,
    }
    pools = {"all runners": np.ones(len(d), bool),
             "within 4, SP $2+, no first starter": ((d["gap"] <= 4) & (d["sp"] >= 2) & ~d["fs_race"]).to_numpy()}
    tr = d["train"].to_numpy()
    out = []
    for pname, pm in pools.items():
        for name, fm in F.items():
            m = pm & fm.fillna(False).to_numpy()
            row = {"pool": pname, "filter": name, "share %": round(100 * m.sum() / pm.sum(), 1)}
            for lab, per in (("23-24", tr), ("25-26", ~tr)):
                b = d[m & per]
                row[f"A/E {lab}"] = round(b["won"].sum() / b["p_ctl"].sum(), 3) if len(b) else np.nan
                row[f"ROI {lab} %"] = round(100 * ((b["won"] * b["sp"]).mean() - 1), 1) if len(b) else np.nan
            b = d[m]
            x = (b["won"] / b["p_ctl"].mean()).to_numpy()
            row["bets"] = int(m.sum())
            row["both > 1"] = "yes" if row["A/E 23-24"] > 1.02 and row["A/E 25-26"] > 1.02 else ""
            out.append(row)
    t = pd.DataFrame(out)
    base = {p: (d[pm]["won"].sum() / d[pm]["p_ctl"].sum(), 100 * ((d[pm]["won"] * d[pm]["sp"]).mean() - 1)) for p, pm in pools.items()}
    L = ["# Filter screen (walk-forward, VIC/SA/QLD 2023 to Sep 2026, SP)", "",
         f"- {d['race_id'].nunique():,} races. Pools: " + "; ".join(f"{p}: A/E {a:.3f}, ROI {r:+.1f}%" for p, (a, r) in base.items()),
         "- A/E = price-matched (1.00 = exactly what the price says). 'both > 1' = above 1.02 in 2023-24 AND 2025-26.", ""]
    for p in pools:
        L += [f"## {p}", "", t[t.pool == p].drop(columns="pool").sort_values("A/E 25-26", ascending=False).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    main()
