"""Filter screen, batch 2: last-start comments, GPS ground covered, closing sectional, sire suitability, form trend.

    python -W ignore tools/filter_screen2.py        # -> reports/filter_screen2.md

Same pools and measure as tools/filter_screen.py (price-matched A/E at SP in 2023-24 and 2025-26). All inputs are from
the horse's PREVIOUS starts or from sire progeny on earlier dates:
  stewards / video   keyword flags on the last start's stewards report and video comment
  GPS                last start's extra metres vs the field of that race (gps_runs, QLD from Oct 2022, VIC/SA rc)
  closing            last start's L600 sectional vs that race's field
  sire               progeny strike rate on wet (7+) / 1600m+ vs the sire's own overall, earlier dates only (50+ runs)
  trend              last start WPR vs the horse's prior average
"""
import re
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import strategy_search as ss  # noqa: E402

OUT = ROOT / "reports/filter_screen2.md"
STEW = {"slowly away / began awkwardly": r"slowly away|began awkwardly|slow to begin|missed the start",
        "held up / checked / hampered": r"held up|checked|hampered|crowded|struck interference|inconvenienced|blocked|steadied",
        "raced wide / without cover": r"wide throughout|raced wide|without cover|three wide|four wide|3 wide|4 wide",
        "overraced / pulled": r"overrac|over-rac|pulled hard|raced keenly|fractious",
        "laid / hung / shifted": r"laid in|laid out|hung out|hung in|shifted",
        "vet issue (lame, bled, heart)": r"lame|bled|blood|heart|cardiac|respirat|soreness|sore ",
        "eased / not persevered": r"eased|not persevered|failed to handle",
        "no stewards comment": None}
VID = {"video: eye catcher / ran on well": r"eye catch|ran on well|finished off well|good late|strong late",
       "video: poor / never likely": r"\[poor\]|never likely|weak run home|couldn't finish off|didn't finish off",
       "video: every chance": r"every chance|had its chance"}


def facts(con):
    r = con.sql("""select cast(u.run_id as varchar) run_id, u.race_id, u.horse_id, u.race_date, u.sire_id, u.res_won won_all,
                          u.res_wpr, u.res_s_l600, u.res_finish, u.res_stewards, u.res_video, r.going_num, r.distance
                   from runs u join races r using (race_id)
                   where u.race_date >= date '2018-01-01' and not coalesce(u.is_trial_or_jumpout, false)""").df()
    r["race_date"] = pd.to_datetime(r["race_date"])
    r["won_all"] = r["won_all"].astype(float).fillna(0)
    gx = con.sql("select cast(run_id as varchar) run_id, res_gps_extra_m from gps_runs").df()
    r = r.merge(gx.drop_duplicates("run_id"), on="run_id", how="left")
    g = r.groupby("race_id")
    r["gps_rel"] = r["res_gps_extra_m"] - g["res_gps_extra_m"].transform("mean")
    l6 = pd.to_numeric(r["res_s_l600"], errors="coerce")
    r["l600_rel"] = l6 - l6.groupby(r["race_id"]).transform("mean")
    # direction: whichever way correlates with finishing ahead
    c = np.corrcoef(r["l600_rel"].fillna(0), -pd.to_numeric(r["res_finish"], errors="coerce").fillna(10))[0, 1]
    if c < 0:
        r["l600_rel"] = -r["l600_rel"]
    stew = r["res_stewards"].fillna("").str.lower()
    vid = r["res_video"].fillna("").str.lower()
    for k, pat in STEW.items():
        r["cs_" + k] = (stew.str.strip() == "") if pat is None else stew.str.contains(pat, regex=True)
    for k, pat in VID.items():
        r["cs_" + k] = vid.str.contains(pat, regex=True)
    r = r.sort_values(["horse_id", "race_date", "run_id"])
    h = r.groupby("horse_id")
    keep = ["gps_rel", "l600_rel"] + [c for c in r if c.startswith("cs_")]
    for c in keep:
        r["last_" + c] = h[c].shift(1)
    r["last_wpr"] = h["res_wpr"].shift(1)
    r["prior_avg_wpr"] = h["res_wpr"].transform(lambda s: s.expanding().mean().shift(1))
    # sire progeny strike rates on earlier dates
    r = r.sort_values("race_date")
    for tag, m in (("wet", r["going_num"] >= 7), ("stay", r["distance"] >= 1600), ("all", pd.Series(True, index=r.index))):
        x = r[m.fillna(False)].groupby(["sire_id", "race_date"]).agg(w=("won_all", "sum"), n=("won_all", "size")).reset_index()
        x = x.sort_values(["sire_id", "race_date"])
        gg = x.groupby("sire_id")
        x[f"sw_{tag}"] = gg["w"].cumsum() - x["w"]
        x[f"sn_{tag}"] = gg["n"].cumsum() - x["n"]
        r = pd.merge_asof(r.sort_values("race_date"), x[["sire_id", "race_date", f"sw_{tag}", f"sn_{tag}"]].sort_values("race_date"),
                          on="race_date", by="sire_id", direction="backward", allow_exact_matches=False)
    for tag in ("wet", "stay"):
        r[f"sire_{tag}_idx"] = (r[f"sw_{tag}"] / r[f"sn_{tag}"]) / (r["sw_all"] / r["sn_all"])
        r.loc[r[f"sn_{tag}"] < 50, f"sire_{tag}_idx"] = np.nan
    cols = ["run_id"] + ["last_" + c for c in keep] + ["last_wpr", "prior_avg_wpr", "sire_wet_idx", "sire_stay_idx"]
    return r[r["race_date"] >= "2023-01-01"][cols]


def main():
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    d = ss.load()
    d = d.merge(facts(con), on="run_id", how="left")
    g = d.groupby("race_id")
    d["gap"] = 6.843 * np.log(g["model %"].transform("max") / d["model %"])
    d["fs_race"] = g["h_none"].transform("max").fillna(0) > 0
    wet, stay = d["going_num"] >= 7, d["dist"] >= 1600
    F = {k.replace("last_cs_", "last start: "): d[k].astype("boolean") for k in d if k.startswith("last_cs_")}
    F.update({
        "GPS: covered most ground last start (top 20%)": d["last_gps_rel"] >= d["last_gps_rel"].quantile(0.8),
        "GPS: saved ground last start (bottom 20%)": d["last_gps_rel"] <= d["last_gps_rel"].quantile(0.2),
        "closing: best L600 fifth last start": d["last_l600_rel"] >= d["last_l600_rel"].quantile(0.8),
        "closing: worst L600 fifth last start": d["last_l600_rel"] <= d["last_l600_rel"].quantile(0.2),
        "last start WPR 5+ above prior average": d["last_wpr"] >= d["prior_avg_wpr"] + 5,
        "last start WPR 5+ below prior average": d["last_wpr"] <= d["prior_avg_wpr"] - 5,
        "wet race, sire wet index >= 1.2": wet & (d["sire_wet_idx"] >= 1.2),
        "wet race, sire wet index <= 0.8": wet & (d["sire_wet_idx"] <= 0.8),
        "1600m+ race, sire staying index >= 1.2": stay & (d["sire_stay_idx"] >= 1.2),
        "1600m+ race, sire staying index <= 0.8": stay & (d["sire_stay_idx"] <= 0.8),
    })
    pools = {"all runners": np.ones(len(d), bool),
             "within 4, SP $2+, no first starter": ((d["gap"] <= 4) & (d["sp"] >= 2) & ~d["fs_race"]).to_numpy()}
    tr = d["train"].to_numpy()
    out = []
    for pname, pm in pools.items():
        for name, fm in F.items():
            m = pm & fm.fillna(False).to_numpy(bool)
            row = {"pool": pname, "filter": name, "share %": round(100 * m.sum() / pm.sum(), 1)}
            for lab, per in (("23-24", tr), ("25-26", ~tr)):
                b = d[m & per]
                row[f"A/E {lab}"] = round(b["won"].sum() / b["p_ctl"].sum(), 3) if len(b) else np.nan
                row[f"ROI {lab} %"] = round(100 * ((b["won"] * b["sp"]).mean() - 1), 1) if len(b) else np.nan
            row["bets"] = int(m.sum())
            row["both > 1.02"] = "yes" if row["A/E 23-24"] > 1.02 and row["A/E 25-26"] > 1.02 else \
                ("both < 0.98" if row["A/E 23-24"] < 0.98 and row["A/E 25-26"] < 0.98 else "")
            out.append(row)
    t = pd.DataFrame(out)
    L = ["# Filter screen batch 2 (walk-forward, VIC/SA/QLD 2023 to Sep 2026, SP)", "",
         f"- {d['race_id'].nunique():,} races. GPS last start filled for {100 * d['last_gps_rel'].notna().mean():.0f}% of runners,"
         f" L600 {100 * d['last_l600_rel'].notna().mean():.0f}%, sire wet index {100 * d['sire_wet_idx'].notna().mean():.0f}%.", ""]
    for p in pools:
        L += [f"## {p}", "", t[t.pool == p].drop(columns="pool").sort_values("A/E 25-26", ascending=False).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    d.to_parquet(ROOT / "data/interim/filter_screen2_runs.parquet")


if __name__ == "__main__":
    main()
