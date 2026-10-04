"""Speed map (race-day projection) checks: wide leaders, track-level leader bias, going.

    python -W ignore tools/speedmap_check.py        # -> reports/speedmap_check.md

Data: data/interim/pace_leader_oos.parquet (tools/pace_leader_test.py: walk-forward race-day projection v3, fitted on
2019 to Y-1, scored on Y = 2023 to 2026, VIC/SA/QLD) + barrier from the DB. Per runner: projected settle share
(0 leader, 1 last), the model's position adjustment adj = proj_adj + bias_adj (WPR), actual WPR and pre-race ability
h_wpr. "Surprise" = (WPR - h_wpr) - adj, demeaned within the race: > 0 = ran better than the projection allowed.
  1. Wide leaders: surprise and A/E at SP by projected settle third x barrier band; and how often each actually led.
  2. Track leader level: per track, actual within-race slope of (WPR - h_wpr) on settle vs the model's adj slope, from
     PRIOR years only; correction = shrunk gap x settle vs race mean. Does it help on the next year (conditional
     logit with log SP; and h_wpr + adj model-alone)?
  3. Going: actual vs model leader slope by going band.
Race bootstrap 95% CIs.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit  # noqa: E402

OUT = ROOT / "reports/speedmap_check.md"
BOOT = 1000
rng = np.random.default_rng(31)
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]


def load():
    p = pd.read_parquet(ROOT / "data/interim/pace_leader_oos.parquet")
    p = p[p["race_date"] < "2026-10-01"]
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    b = con.sql("select run_id, barrier from runs where race_date >= date '2023-01-01'").df()
    p = p.merge(b, on="run_id", how="left")
    p = p[p["wpr"].notna() & p["h_wpr"].notna() & (p["h_none"] == 0) & p["proj_settle"].notna() & (p["sp"] > 1)
          & p["won"].notna()].copy()
    p["won"] = p["won"].astype(int)
    ok = p.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ovr=("sp", lambda s: (1 / s).sum()))
    p = p[p["race_id"].isin(ok.index[(ok.n >= 5) & (ok.w == 1) & (ok.ovr >= 1.0)])].copy()
    g = p.groupby("race_id")
    p["adj"] = p["proj_adj"].fillna(0) + p["bias_adj"].fillna(0)
    p["perf"] = p["wpr"] - p["h_wpr"]
    for c in ("perf", "adj", "proj_settle"):
        p[c + "_d"] = p[c] - g[c].transform("mean")
    p["surprise"] = p["perf_d"] - p["adj_d"]
    n = g["run_id"].transform("size")
    p["bar_pct"] = (p["barrier"] - 1) / (n - 1).clip(lower=1)
    inv = 1 / p["sp"]
    p["p_sp"] = inv / inv.groupby(p["race_id"]).transform("sum")
    p["lsp"] = np.log(p["p_sp"])
    p["p_ctl"] = p.groupby(pd.cut(p["sp"], SP_BINS), observed=True)["won"].transform("mean")
    p["year"] = pd.to_datetime(p["race_date"]).dt.year
    p["settle3"] = pd.cut(p["proj_settle"], [-0.01, 1 / 3, 2 / 3, 1.01], labels=["front", "middle", "back"])
    p["bar3"] = pd.cut(p["barrier"], [0, 4, 9, 99], labels=["1-4", "5-9", "10+"])
    p["led"] = (p["y_settle"] <= 0.05).astype(float)
    p["going"] = pd.cut(p["going_num"], [0, 4, 6, 8, 11], labels=["good 1-4", "soft 5-6", "soft 7-8", "heavy 9-10"])
    return p


def boot_mean(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if len(x) < 30:
        return ""
    m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
    return f"{np.percentile(m, 2.5):+.2f} to {np.percentile(m, 97.5):+.2f}"


def slope(g, y):
    x = g["proj_settle_d"].to_numpy()
    v = g[y].to_numpy()
    return (x * v).sum() / (x * x).sum()


def logit_ll(tr, te, cols):
    tr = tr.sort_values("race_id")
    b = clogit.fit(tr[cols].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
    z = pd.Series(te[cols].to_numpy(float) @ b, index=te.index)
    e = np.exp(z - z.groupby(te["race_id"]).transform("max"))
    pr = e / e.groupby(te["race_id"]).transform("sum")
    w = te["won"] == 1
    return pd.Series(-np.log(pr[w].clip(1e-12)).to_numpy(), index=te.loc[w, "race_id"].to_numpy()), b


def main():
    p = load()
    L = ["# Speed map checks (walk-forward race-day projection, 2023 to Sep 2026, VIC/SA/QLD)", "",
         f"- {p['race_id'].nunique():,} races, {len(p):,} runners with form. Surprise = (WPR - prior ability) - the"
         " model's position adjustment, vs the race: > 0 = ran better than the projection allowed.", ""]
    # 1. wide leaders
    t = p.groupby(["settle3", "bar3"], observed=True).apply(lambda g: pd.Series({
        "runners": len(g), "model adj (WPR)": g["adj_d"].mean(), "actual (WPR)": g["perf_d"].mean(),
        "surprise": g["surprise"].mean(), "surprise 95%": boot_mean(g["surprise"]),
        "actually led %": 100 * g["led"].mean(), "A/E at SP": g["won"].sum() / g["p_sp"].sum(),
        "A/E price-matched": g["won"].sum() / g["p_ctl"].sum()}))
    L += ["## 1. Projected position x barrier", "", t.round(3).to_markdown(), ""]
    lead = p[p["proj_settle"] == p.groupby("race_id")["proj_settle"].transform("min")]
    t = lead.groupby("bar3", observed=True).apply(lambda g: pd.Series({
        "projected leaders": len(g), "actually led %": 100 * g["led"].mean(), "model adj": g["adj_d"].mean(),
        "actual": g["perf_d"].mean(), "surprise": g["surprise"].mean(), "surprise 95%": boot_mean(g["surprise"]),
        "A/E price-matched": g["won"].sum() / g["p_ctl"].sum()}))
    L += ["Projected leader (rank 1) by barrier:", "", t.round(3).to_markdown(), ""]
    # 2. corrections, walk-forward by year: fitted on earlier years (2023 needs 2022: start at 2024), scored on Y
    p["h_d"] = p["h_wpr"] - p.groupby("race_id")["h_wpr"].transform("mean")
    p["x_wet"] = p["proj_settle_d"] * (p["going_num"].fillna(4) - 4).clip(lower=0)      # settle x wetness
    p["x_wide_front"] = p["adj_d"].clip(lower=0) * p["bar_pct"].fillna(0.5)               # credit given wide
    res = []
    for y in sorted(p["year"].unique())[1:]:
        prior, cur = p[p["year"] < y], p[p["year"] == y].copy()
        st = prior.groupby("track").apply(lambda g: pd.Series({
            "races": float(g["race_id"].nunique()), "gap": slope(g, "perf_d") - slope(g, "adj_d")}))
        st["corr"] = st["gap"] * st["races"] / (st["races"] + 150.0)
        cur["x_track"] = cur["track"].map(st["corr"]).astype(float).fillna(0.0) * cur["proj_settle_d"]
        res.append(cur)
    c = pd.concat(res)
    L += [f"- Corrections tested on {c['race_id'].nunique():,} races 2024 to Sep 2026; x_track nonzero for"
          f" {100 * (c['x_track'] != 0).mean():.0f}% of runners.", ""]
    years = sorted(c["year"].unique())
    variants = {"ability + adj": ["h_d", "adj_d"], "+ wet": ["h_d", "adj_d", "x_wet"],
                "+ wide front": ["h_d", "adj_d", "x_wide_front"], "+ track": ["h_d", "adj_d", "x_track"],
                "+ all three": ["h_d", "adj_d", "x_wet", "x_wide_front", "x_track"],
                "SP + adj": ["lsp", "adj_d"], "SP + adj + wet": ["lsp", "adj_d", "x_wet"],
                "SP + adj + wide front": ["lsp", "adj_d", "x_wide_front"], "SP + adj + track": ["lsp", "adj_d", "x_track"],
                "SP + adj + all three": ["lsp", "adj_d", "x_wet", "x_wide_front", "x_track"]}
    out = {}
    for name, cols in variants.items():
        parts, bs = [], []
        for y in years:                       # leave-one-year-out within 2024-2026 (corrections already prior-only)
            ll, b = logit_ll(c[c["year"] != y], c[c["year"] == y], cols)
            parts.append(ll)
            bs.append(b)
        out[name] = (pd.concat(parts), np.mean(bs, axis=0), cols)

    def ci(a, b, mask=None):
        x = (out[a][0] - out[b][0].reindex(out[a][0].index)).dropna()
        if mask is not None:
            x = x[x.index.isin(mask)]
        x = x.to_numpy()
        m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"
    wet_races = set(c.loc[c["going_num"] >= 7, "race_id"])
    rows = []
    for a, b in (("+ wet", "ability + adj"), ("+ wide front", "ability + adj"), ("+ track", "ability + adj"),
                 ("+ all three", "ability + adj"), ("SP + adj + wet", "SP + adj"),
                 ("SP + adj + wide front", "SP + adj"), ("SP + adj + track", "SP + adj"),
                 ("SP + adj + all three", "SP + adj")):
        rows.append({"variant": a, "vs": b, "all races": ci(a, b), "soft 7+ / heavy": ci(a, b, wet_races),
                     "weights": ", ".join(f"{k} {v:+.3f}" for k, v in zip(out[a][2], out[a][1]))})
    L += ["## 2. Corrections in a conditional logit (leave-one-year-out, 2024 to 2026; negative = better)", "",
          pd.DataFrame(rows).to_markdown(index=False), ""]
    last = p[p["year"] < 2026]
    tr = last.groupby("track").apply(lambda g: pd.Series({
        "races": g["race_id"].nunique(), "actual slope": slope(g, "perf_d"), "model slope": slope(g, "adj_d")}))
    tr["gap"] = tr["actual slope"] - tr["model slope"]
    tr = tr[tr["races"] >= 150].sort_values("gap")
    L += ["Tracks (2023-2025, >= 150 races): slope of WPR on settle share (negative = leaders favoured).",
          "gap > 0 = model more pro-leader than results.", "",
          pd.concat([tr.head(8), tr.tail(8)]).round(2).to_markdown(), ""]
    # 3. going
    t = p.groupby("going", observed=True).apply(lambda g: pd.Series({
        "races": g["race_id"].nunique(), "actual slope": slope(g, "perf_d"), "model slope": slope(g, "adj_d"),
        "projected leader A/E pm": g.loc[g["proj_settle"] <= 0.05, "won"].sum()
        / max(g.loc[g["proj_settle"] <= 0.05, "p_ctl"].sum(), 1e-9),
        "front third surprise": g.loc[g["settle3"] == "front", "surprise"].mean(),
        "back third surprise": g.loc[g["settle3"] == "back", "surprise"].mean()}))
    L += ["## 3. By going: leader value actual vs model", "", t.round(3).to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
