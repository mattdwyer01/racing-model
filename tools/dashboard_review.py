"""Dashboard review on what it showed BEFORE each race (tools/dashboard_snapshots.py), 22 Aug 2026 on.

    python -W ignore tools/dashboard_review.py --repo ../toprate     # -> reports/dashboard_review.md

Combo and speed map as the dashboard builds them now (TopRate lib/raceModel.ts compositeScore, lib/racingModel.ts
withModelAdjustments, lib/raceModel.ts SPEED_MAP_TINT_THRESHOLD):
  adjusted projection = TopRate WPR projection - (its speed_map + track_barrier, vs field) + (Racing Model race-day
      adj + past ground-loss credit, vs field). Racing Model part: racing_model.json at the time (24 Sep on), before
      that the out-of-sample scores of tools/combo_redesign_test.py (models trained before 22 Aug / 1 Sep).
  Combo = 2/3 adjusted projection + 1/3 TopRate rating (rescaled to the WPR scale); gap = top Combo - runner's.
  speed map tag = Racing Model part vs field (TopRate's speed_map when ours is missing): favoured >= +0.5,
      unfavoured <= -0.5, else neutral.
Prices: SP (final file) and the dashboard's stored fixed price at the snapshot (>= 10 min before the start; can be
stale). Price-matched A/E: wins / (win rate of all runners at the same SP).
Rule "4 clear": Combo top pick >= 4 WPR clear of the 2nd, its speed map not unfavoured, no first starter in the race.
Quaddies (main = last 4 races of the meeting, early = the 4 before): per leg, every runner within 4 of the top Combo,
  runners 4 to 10 back unless their speed map is unfavoured, and every first starter; played when the combinations
  are <= the cap. No dividends in the data: estimated dividend = (1 - 0.20) / product of the leg winners' normalised
  SP probabilities (a rough guide; real quaddie pools pay differently).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SNAPS = ROOT / "data/interim/dash_snapshots"
OOS = ROOT / "data/interim/combo_gps_scores.csv.gz"
OUT = ROOT / "reports/dashboard_review.md"
WPR_M, WPR_S, TRR_M, TRR_S = 72.57, 10.48, 96.26, 2.71
SM_T = 0.5
TAKE = 0.20
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]
BOOT = 2000
rng = np.random.default_rng(3)


def _c(s, key):
    try:
        v = json.loads(s).get(key) if isinstance(s, str) else None
        return float(v) if v is not None else 0.0
    except (ValueError, TypeError, AttributeError):
        return 0.0


def load(repo):
    s = pd.concat([pd.read_parquet(f) for f in sorted(SNAPS.glob("*.parquet"))], ignore_index=True)
    fin = pd.read_csv(Path(repo) / "toprate_runners.csv", dtype={"run_id": str, "race_id": str},
                      usecols=["run_id", "race_id", "date", "venue", "state", "race", "distance", "has_first_starter",
                               "runs_with_wpr", "form_string", "starting_price_sp", "finish_position", "resulted",
                               "scratched"])
    fin = fin[fin["date"] >= s["date"].min()]
    d = fin.merge(s.drop(columns=["race_id", "date", "scratched"]), on="run_id", how="left")
    d = d[(d["scratched"].fillna(0) == 0) & (d["resulted"].fillna(0) == 1)].copy()
    d["sp"] = pd.to_numeric(d["starting_price_sp"], errors="coerce")
    d["fx"] = pd.to_numeric(d["fixed_win_price"], errors="coerce").where(lambda v: v > 1)
    d["won"] = (pd.to_numeric(d["finish_position"], errors="coerce") == 1).astype(int)
    d["fs"] = (d["runs_with_wpr"].fillna(0) == 0) & d["form_string"].fillna("").str.strip().eq("")
    g = d.groupby("race_id")
    ok = g.agg(n=("run_id", "size"), w=("won", "sum"), p=("wprp_proj", lambda v: v.notna().all()),
               sp=("sp", lambda v: (v > 1).all()))
    keep = ok.index[(ok.n >= 4) & (ok.w == 1) & ok.p & ok.sp]
    d = d[d["race_id"].isin(keep)].copy()
    # Racing Model part: snapshot (24 Sep on) else out-of-sample scores
    oos = pd.read_csv(OOS, dtype={"run_id": str})
    oos["oos_part"] = oos["race-day adj"].fillna(0) + oos["ground loss (past runs)"].fillna(0)
    d = d.merge(oos[["run_id", "oos_part"]], on="run_id", how="left")
    d["ours"] = (d["rm_d"].fillna(0) + d["rm_gl"].fillna(0)).where(d["rm_d"].notna(), d["oos_part"])
    has = d["ours"].notna().groupby(d["race_id"]).transform("all")
    d["ours_d"] = (d["ours"] - d.groupby("race_id")["ours"].transform("mean")).where(has)
    d["tp"] = d["wprp_contrib"].map(lambda v: _c(v, "speed_map")) + d["wprp_contrib"].map(lambda v: _c(v, "track_barrier"))
    d["tp_d"] = d["tp"] - d.groupby("race_id")["tp"].transform("mean")
    d["sm_tp"] = d["wprp_contrib"].map(lambda v: _c(v, "speed_map"))
    d["sm_tp"] -= d.groupby("race_id")["sm_tp"].transform("mean")
    d["proj"] = np.where(has, d["wprp_proj"] - d["tp_d"] + d["ours_d"].fillna(0), d["wprp_proj"])
    trr = WPR_M + (d["toprate_rating"] - TRR_M) / TRR_S * WPR_S
    d["combo"] = np.where(trr.notna(), (2 * d["proj"] + trr) / 3, d["proj"])
    d["sm"] = np.where(has, d["ours_d"], d["sm_tp"])
    d["sm_tag"] = np.select([d["sm"] >= SM_T, d["sm"] <= -SM_T], ["favoured", "unfavoured"], "neutral")
    d["gap"] = d.groupby("race_id")["combo"].transform("max") - d["combo"]
    d["rank"] = d.groupby("race_id")["combo"].rank(ascending=False, method="first")
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d["grp"] = np.where(d["state"].isin(["VIC", "SA", "QLD"]), d["state"].replace({"VIC": "VIC/SA", "SA": "VIC/SA"}),
                        "NSW/WA/other")
    d["ours_src"] = np.where(d["rm_d"].notna(), "dashboard", np.where(d["oos_part"].notna(), "oos", "none"))
    return d


def stats(g, ci=False):
    n = len(g)
    if n == 0:
        return {}
    r = {"bets": n, "wins": int(g["won"].sum()), "win %": 100 * g["won"].mean(), "avg SP": g["sp"].mean(),
         "ROI SP %": 100 * ((g["won"] * g["sp"]).mean() - 1),
         "A/E price-matched": g["won"].sum() / g["p_ctl"].sum()}
    fx = g[g["fx"].notna()]
    r["ROI fixed %"] = 100 * ((fx["won"] * fx["fx"]).mean() - 1) if len(fx) else np.nan
    r["fixed n"] = len(fx)
    if ci:
        ret = (g["won"] * g["sp"] - 1).to_numpy()
        bs = ret[rng.integers(0, n, (BOOT, n))].mean(1)
        r["ROI SP 95%"] = f"{100 * np.percentile(bs, 2.5):+.0f} to {100 * np.percentile(bs, 97.5):+.0f}"
    return r


def table(rows, fmt=".1f"):
    return pd.DataFrame(rows).to_markdown(index=False, floatfmt=fmt)


def quaddies(d, fin_races):
    """Main and early quaddies per meeting; returns a frame of quaddies with combos, hit and estimated dividend."""
    out = []
    sel = (d["gap"] <= 4) | ((d["gap"] <= 10) & (d["sm_tag"] != "unfavoured")) | d["fs"]
    alt = {"within 4 only": d["gap"] <= 4, "within 10 all": d["gap"] <= 10,
           "your rule": sel, "your rule, no first-starter add": (d["gap"] <= 4) | ((d["gap"] <= 10) & (d["sm_tag"] != "unfavoured"))}
    leg = {}
    for name, m in alt.items():
        x = d.assign(sel=m)
        leg[name] = x.groupby("race_id").agg(n=("sel", "sum"), hit=("won", lambda w, s=x["sel"]: bool((w & s[w.index]).any())))
    pw = d[d["won"] == 1].set_index("race_id")["p_sp"]
    for (day, venue), mr in fin_races.groupby(["date", "venue"]):
        nos = sorted(mr["race"].dropna().astype(int).unique())
        if len(nos) < 4:
            continue
        ids = mr.drop_duplicates("race").set_index("race")["race_id"]
        kinds = [("main", nos[-4:])] + ([("early", nos[-8:-4])] if len(nos) >= 8 else [])
        for kind, legs in kinds:
            rids = [ids.get(n) for n in legs]
            if any(r not in pw.index for r in rids):
                continue
            row = {"date": day, "venue": venue, "state": mr["state"].iloc[0], "kind": kind,
                   "est div": (1 - TAKE) / np.prod([pw[r] for r in rids])}
            for name, lg in leg.items():
                row[f"{name}: combos"] = int(np.prod([lg.loc[r, "n"] for r in rids]))
                row[f"{name}: hit"] = all(lg.loc[r, "hit"] for r in rids)
            out.append(row)
    return pd.DataFrame(out)


def q_stats(q, name, cap):
    c, h = q[f"{name}: combos"], q[f"{name}: hit"]
    m = c <= cap if cap else c > 0
    g = q[m]
    if g.empty:
        return {}
    cost, ret = g[f"{name}: combos"], g["est div"] * g[f"{name}: hit"]
    tot = ret.sum() / cost.sum() - 1
    idx = rng.integers(0, len(g), (BOOT, len(g)))
    bs = ret.to_numpy()[idx].sum(1) / cost.to_numpy()[idx].sum(1) - 1
    return {"quaddies": len(g), "share played %": 100 * m.mean(), "hits": int(g[f"{name}: hit"].sum()),
            "hit %": 100 * g[f"{name}: hit"].mean(), "avg combos": cost.mean(),
            "median est div (hits)": g.loc[g[f"{name}: hit"], "est div"].median() if g[f"{name}: hit"].any() else np.nan,
            "est ROI %": 100 * tot,
            "est ROI 95%": f"{100 * np.percentile(bs, 2.5):+.0f} to {100 * np.percentile(bs, 97.5):+.0f}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    a = ap.parse_args()
    d = load(a.repo)
    races = d.drop_duplicates("race_id")
    L = ["# Dashboard review (pre-race values)", "",
         f"- {races.shape[0]:,} races, {races['date'].min()} to {races['date'].max()}, all states on the dashboard"
         f" ({(races['grp'] != 'NSW/WA/other').sum():,} VIC/SA/QLD). Races with >= 4 runners, one winner, SP and a"
         " pre-race projection for every runner.",
         f"- Racing Model part from the dashboard file for {100 * (d['ours_src'] == 'dashboard').mean():.0f}% of runners,"
         f" out-of-sample scores {100 * (d['ours_src'] == 'oos').mean():.0f}%, none (TopRate speed map kept)"
         f" {100 * (d['ours_src'] == 'none').mean():.0f}%.",
         f"- Fixed price at the snapshot for {100 * d['fx'].notna().mean():.0f}% of runners. See the module docstring"
         " for definitions.", ""]

    # 1. top picks
    rows = []
    top = d[d["rank"] == 1]
    rows.append({"pick": "Combo top", **stats(top, True)})
    pt = d.loc[d.groupby("race_id")["proj"].idxmax()]
    rows.append({"pick": "Proj (adjusted) top", **stats(pt, True)})
    tr = d.loc[d.dropna(subset=["toprate_rating"]).groupby("race_id")["toprate_rating"].idxmax()]
    rows.append({"pick": "TopRate rating top", **stats(tr, True)})
    fav = d.loc[d.groupby("race_id")["sp"].idxmin()]
    rows.append({"pick": "SP favourite", **stats(fav, True)})
    rm = d.dropna(subset=["rm_p"])
    if len(rm):
        rmt = rm.loc[rm.groupby("race_id")["rm_p"].idxmax()]
        rows.append({"pick": "Racing Model top (24 Sep on)", **stats(rmt, True)})
    L += ["## 1. Top picks (flat 1 unit)", "", table(rows), ""]
    rows = []
    for gname, g in top.groupby("grp"):
        rows.append({"Combo top": gname, **stats(g, True)})
    L += ["By state group:", "", table(rows), ""]

    # 2. gap bands x speed map
    d["band"] = pd.cut(d["gap"], [-0.01, 0.0001, 2, 4, 6, 10, 99], labels=["top", "0-2", "2-4", "4-6", "6-10", "10+"])
    rows = []
    for (b, t), g in d.groupby(["band", "sm_tag"], observed=True):
        rows.append({"gap from top": b, "speed map": t, **stats(g)})
    L += ["## 2. Combo gap band x speed map tag", "",
          "A/E price-matched > 1 = wins more than runners at the same SP.", "", table(rows), ""]
    rows = []
    for t, g in d.groupby("sm_tag"):
        rows.append({"speed map (all runners)": t, **stats(g)})
    L += [table(rows), ""]

    # 3. the 4-clear rule and variants
    top2 = d[d["rank"] <= 2].sort_values(["race_id", "rank"])
    clear = top2.groupby("race_id")["combo"].agg(lambda v: v.iloc[0] - v.iloc[1] if len(v) == 2 else np.nan)
    top = top.assign(clear=top["race_id"].map(clear))
    rows = []
    for c in [2, 3, 4, 5, 6, 8]:
        for smn, smm in [("any", top["sm_tag"].notna()), ("not unfavoured", top["sm_tag"] != "unfavoured"),
                         ("favoured", top["sm_tag"] == "favoured")]:
            for fsn, fsm in [("no FS in race", ~top["has_first_starter"].fillna(False).astype(bool)),
                             ("FS allowed", top["clear"].notna())]:
                g = top[(top["clear"] >= c) & smm & fsm]
                rows.append({"clear by": c, "speed map": smn, "first starters": fsn, **stats(g, c == 4)})
    rule = top[(top["clear"] >= 4) & (top["sm_tag"] != "unfavoured") & ~top["has_first_starter"].fillna(False).astype(bool)]
    L += ["## 3. Your rule: Combo top pick 4+ clear, speed map not unfavoured, no first starter", "",
          "Main rule:", "", table([{"rule": "4 clear, not unfav, no FS", **stats(rule, True)}]), "",
          "By state group:", "", table([{"group": k, **stats(g, True)} for k, g in rule.groupby("grp")]), "",
          "By SP band:", "", table([{"SP": str(k), **stats(g)} for k, g in
                                    rule.groupby(pd.cut(rule["sp"], [1, 2, 3, 5, 10, 1000]), observed=True)]), "",
          "By week:", "", table([{"week from": str(k.date()), **stats(g)} for k, g in
                                 rule.groupby(pd.to_datetime(rule["date"]).dt.to_period("W").dt.start_time)]), "",
          "Variants:", "", table(rows), ""]

    # 4. quaddies
    q = quaddies(d, d[["date", "venue", "state", "race", "race_id"]].drop_duplicates())
    rows = []
    for kind in ["main", "early", "both"]:
        qq = q if kind == "both" else q[q["kind"] == kind]
        for name in ["your rule", "your rule, no first-starter add", "within 4 only", "within 10 all"]:
            for cap in [500, 600, 1000, None]:
                r = q_stats(qq, name, cap)
                if r:
                    rows.append({"quaddie": kind, "selection": name, "cap": cap or "none", **r})
    L += ["## 4. Quaddies", "",
          f"- {len(q):,} quaddies with complete pre-race data ({(q['kind'] == 'main').sum()} main,"
          f" {(q['kind'] == 'early').sum()} early). Cost = combinations x 1 unit; return = estimated dividend when all"
          " four legs are covered.", "", table(rows), ""]
    qr = q[q["your rule: combos"] <= 600]
    L += ["Your rule at the 600 cap, by state group and leg-miss reasons:", "",
          table([{"group": k, **q_stats(g, "your rule", 600)} for k, g in
                 qr.assign(grp=np.where(qr["state"].isin(["VIC", "SA", "QLD"]), qr["state"], "other")).groupby("grp")]), ""]
    # which leg type loses quaddies: winners outside selections
    w = d[d["won"] == 1]
    rows = [{"winner was": k, "share of winners %": 100 * v} for k, v in
            pd.Series(np.select([w["gap"] <= 4, (w["gap"] <= 10) & (w["sm_tag"] != "unfavoured"), w["fs"],
                                 (w["gap"] <= 10) & (w["sm_tag"] == "unfavoured")],
                                ["within 4", "4-10, speed map ok", "first starter (outside 10)", "4-10, unfavoured"],
                                "outside 10")).value_counts(normalize=True).items()]
    L += ["Where race winners sit (all races):", "", table(rows), ""]
    OUT.write_text("\n".join(L) + "\n")
    q.to_csv(ROOT / "reports/dashboard_review_quaddies.csv.gz", index=False, compression="gzip")
    print("\n".join(L))


if __name__ == "__main__":
    main()
