"""What speed map adjustment do winners have? Dashboard pre-race values (tools/dashboard_review.py load()).

    python -W ignore tools/speedmap_winner_test.py --repo ../toprate     # -> reports/speedmap_winner_test.md

SM adj = the dashboard's "SM Adj" column: the Racing Model's race-day adjustment + past ground-loss credit, vs the
field (TopRate's speed_map where ours is missing). Winners vs all runners; win rate and price-matched A/E (wins vs
runners at the same SP) by SM adj band, overall, within Combo gap bands, by state group and distance; the winner's
SM adj rank in its race; TopRate's own speed_map term (22 Aug to 23 Sep, where it exists) for comparison.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import dashboard_review as dr  # noqa: E402

OUT = ROOT / "reports/speedmap_winner_test.md"
BANDS = [-99, -2, -1, -0.5, 0, 0.5, 1, 2, 99]
LAB = ["<= -2", "-2 to -1", "-1 to -0.5", "-0.5 to 0", "0 to 0.5", "0.5 to 1", "1 to 2", "2+"]
rng = np.random.default_rng(5)


def by_band(g, col="sm"):
    g = g.assign(b=pd.cut(g[col], BANDS, labels=LAB))
    nw = g["won"].sum()
    rows = []
    for b, x in g.groupby("b", observed=True):
        rows.append({"SM adj": b, "runners": len(x), "share of runners %": 100 * len(x) / len(g),
                     "share of winners %": 100 * x["won"].sum() / nw, "win %": 100 * x["won"].mean(),
                     "avg SP": x["sp"].median(), "A/E price-matched": x["won"].sum() / x["p_ctl"].sum(),
                     "ROI SP %": 100 * ((x["won"] * x["sp"]).mean() - 1)})
    return pd.DataFrame(rows)


def slope(g, col="sm"):
    """Conditional-logit-free check: win ~ log p_SP + SM adj, pooled logistic within race via clogit."""
    from model import clogit
    g = g.dropna(subset=[col]).sort_values("race_id").copy()
    g["race"] = pd.factorize(g["race_id"])[0]
    g["lp"] = np.log(g["p_sp"])
    b0 = clogit.fit(g[["lp"]].to_numpy(float), g["race"].to_numpy(), g["won"].to_numpy())
    b1 = clogit.fit(g[["lp", col]].to_numpy(float), g["race"].to_numpy(), g["won"].to_numpy())
    # race bootstrap of the SM beta
    races = g["race"].unique()
    bs = []
    for _ in range(200):
        pick = rng.choice(races, len(races))
        idx = np.concatenate([np.flatnonzero(g["race"].to_numpy() == r) for r in pick])
        h = g.iloc[idx].copy()
        h["race"] = np.repeat(np.arange(len(pick)), [np.sum(g["race"].to_numpy() == r) for r in pick])
        bs.append(clogit.fit(h[["lp", col]].to_numpy(float), h["race"].to_numpy(), h["won"].to_numpy())[1])
    return b1[1], np.percentile(bs, [2.5, 97.5]), b0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    a = ap.parse_args()
    sys.path.insert(0, str(ROOT))
    d = dr.load(a.repo)
    d["sm"] = pd.to_numeric(d["sm"], errors="coerce")
    d["sm_tp"] = pd.to_numeric(d["sm_tp"], errors="coerce")
    d["sm_rank"] = d.groupby("race_id")["sm"].rank(ascending=False, method="min")
    d["sm_rank_pct"] = (d["sm_rank"] - 1) / (d.groupby("race_id")["sm"].transform("count") - 1).clip(lower=1)
    w = d[d["won"] == 1]
    L = ["# Speed map adjustment of winners (dashboard pre-race values)", "",
         f"- {d['race_id'].nunique():,} races, {len(d):,} runners, 22 Aug to 30 Sep 2026, all states. SM adj = the"
         " dashboard's SM Adj column (Racing Model race-day adj + past ground loss, vs the field). Tags: favoured >= +0.5,"
         " unfavoured <= -0.5.", "",
         "## Winners vs all runners", "",
         pd.DataFrame({"all runners": d["sm"].describe(percentiles=[.1, .25, .5, .75, .9]),
                       "winners": w["sm"].describe(percentiles=[.1, .25, .5, .75, .9])}).T.to_markdown(floatfmt=".2f"),
         "",
         f"- Winners' SM adj rank in their race: best in the field {100 * (w['sm_rank'] == 1).mean():.1f}%, top 3"
         f" {100 * (w['sm_rank'] <= 3).mean():.1f}%, top half {100 * (w['sm_rank_pct'] <= 0.5).mean():.1f}%, bottom"
         f" quarter {100 * (w['sm_rank_pct'] >= 0.75).mean():.1f}% (random would be about"
         f" {100 * (1 / d.groupby('race_id').size()).mean():.1f}% best, 50% top half, 25% bottom quarter).",
         f"- Tags of winners: favoured {100 * (w['sm_tag'] == 'favoured').mean():.1f}%, neutral"
         f" {100 * (w['sm_tag'] == 'neutral').mean():.1f}%, unfavoured {100 * (w['sm_tag'] == 'unfavoured').mean():.1f}%"
         f" (all runners {100 * (d['sm_tag'] == 'favoured').mean():.1f} / {100 * (d['sm_tag'] == 'neutral').mean():.1f} /"
         f" {100 * (d['sm_tag'] == 'unfavoured').mean():.1f}%).", "",
         "## By SM adj band (all runners)", "", by_band(d).to_markdown(index=False, floatfmt=".2f"), ""]
    b, ci, _ = slope(d)
    L += [f"- Beyond the market (conditional logit on log SP + SM adj): {b:+.3f} per WPR of SM adj"
          f" (95% {ci[0]:+.3f} to {ci[1]:+.3f}). Positive = the market under-rates the speed map.", ""]
    for name, m in [("within 4 of the top Combo", d["gap"] <= 4), ("4 to 10 back", (d["gap"] > 4) & (d["gap"] <= 10)),
                    ("10+ back", d["gap"] > 10)]:
        L += [f"## Inside Combo gap band: {name}", "", by_band(d[m]).to_markdown(index=False, floatfmt=".2f"), ""]
    rows = []
    for gname, g in d.groupby("grp"):
        x = g[g["won"] == 1]
        rows.append({"state group": gname, "races": g["race_id"].nunique(), "winners' median SM adj": x["sm"].median(),
                     "winners favoured %": 100 * (x["sm_tag"] == "favoured").mean(),
                     "winners unfavoured %": 100 * (x["sm_tag"] == "unfavoured").mean(),
                     "A/E favoured": g.loc[g.sm_tag == "favoured", "won"].sum() / g.loc[g.sm_tag == "favoured", "p_ctl"].sum(),
                     "A/E unfavoured": g.loc[g.sm_tag == "unfavoured", "won"].sum() / g.loc[g.sm_tag == "unfavoured", "p_ctl"].sum()})
    d["dist_b"] = pd.cut(pd.to_numeric(d["distance"], errors="coerce"), [0, 1100, 1300, 1700, 9999],
                         labels=["<=1100", "1101-1300", "1301-1700", "1701+"])
    for gname, g in d.groupby("dist_b", observed=True):
        x = g[g["won"] == 1]
        rows.append({"state group": f"distance {gname}", "races": g["race_id"].nunique(),
                     "winners' median SM adj": x["sm"].median(),
                     "winners favoured %": 100 * (x["sm_tag"] == "favoured").mean(),
                     "winners unfavoured %": 100 * (x["sm_tag"] == "unfavoured").mean(),
                     "A/E favoured": g.loc[g.sm_tag == "favoured", "won"].sum() / g.loc[g.sm_tag == "favoured", "p_ctl"].sum(),
                     "A/E unfavoured": g.loc[g.sm_tag == "unfavoured", "won"].sum() / g.loc[g.sm_tag == "unfavoured", "p_ctl"].sum()})
    L += ["## By state group and distance", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".2f"), ""]
    # TopRate's own speed_map term where it exists
    t = d[d["wprp_contrib"].notna()].copy()
    t["sm_toprate"] = t["sm_tp"]
    bt, cit, _ = slope(t, "sm_toprate")
    L += ["## TopRate's own speed_map term (same races, before our adjustment replaced it)", "",
          f"- corr with our SM adj {t[['sm_toprate', 'sm']].corr().iloc[0, 1]:.2f}; beyond the market {bt:+.3f} per WPR"
          f" (95% {cit[0]:+.3f} to {cit[1]:+.3f}).", "", by_band(t, "sm_toprate").to_markdown(index=False, floatfmt=".2f"), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
