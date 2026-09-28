"""Do forward runners lose their advantage in races projected to be fast? And by track?

    python -W ignore tools/pace_leader_test.py            # -> reports/pace_leader_test.md
    python -W ignore tools/pace_leader_test.py --cached   # reuse data/interim/pace_leader_oos.parquet

Walk-forward race-day projection v3 (projection.project fitted on 2019 to Y-1, tested on Y = 2023 to 2026 YTD,
VIC/SA/QLD races, same as production). Per runner: projected settle share (0 = leader, 1 = last), race projected
early shape (proj_shape, higher = faster early), the model's position adjustment proj_adj (WPR) and track bias
term bias_adj.

Questions:
  1. Actual value of a forward projected position in WPR, by projected pace band: within-race slope of
     (WPR - pre-race ability) on projected settle share. Compared with the slope of the model's own adjustment
     (proj_adj + bias_adj) in the same races. Negative slope = forward runners run better.
     Same by ACTUAL early shape (hindsight upper bound: what a perfect pace forecast would show).
  2. At SP: A/E of the projected leader and the front / back third by projected pace band, and a conditional
     logit log p_SP + settle + settle x projected pace (leave-one-year-out) for whether the interaction adds
     anything the market misses.
  3. By track: actual vs model slope (tracks with >= 150 races), and a track x pace split.
Race bootstrap 95% CIs.
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure, projection  # noqa: E402

CACHE = ROOT / "data/interim/pace_leader_oos.parquet"
OUT = ROOT / "reports/pace_leader_test.md"
KEEP = ["run_id", "race_id", "race_date", "state", "track", "dist", "field_n", "going_num", "sp", "won",
        "wpr", "h_wpr", "h_none", "y_settle", "y_shape", "proj_settle", "proj_settle_rank", "proj_shape",
        "proj_pace", "proj_adj", "bias_adj", "tb_settle_long"]
BOOT = 1000
rng = np.random.default_rng(7)


def build():
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = projection.frame(con)
    print("frame", len(x0), flush=True)
    parts = []
    for y in [2023, 2024, 2025, 2026]:
        x, _, ex = projection.project(x0, f"{y}-01-01")
        te = x[(x.race_date.dt.year == y) & x["core_scope"]]
        parts.append(te[KEEP].assign(fold=y, c_settle=ex["cost"]["settle"], c_pace=ex["cost"]["pace"]))
        print(y, len(te), ex["cost"], flush=True)
        del x
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(CACHE)
    return d


def race_sums(d, y, x):
    """Per-race sums for a pooled within-race slope of y on x (both demeaned by race)."""
    t = d.dropna(subset=[y, x])
    t = t[t.groupby("race_id")[x].transform("size") >= 4]
    xd = t[x] - t.groupby("race_id")[x].transform("mean")
    yd = t[y] - t.groupby("race_id")[y].transform("mean")
    return pd.DataFrame({"sxy": xd * yd, "sxx": xd * xd, "race_id": t["race_id"]}).groupby("race_id").sum()


def slope_ci(s):
    if len(s) == 0:
        return np.nan, np.nan, np.nan
    a, b = s["sxy"].to_numpy(), s["sxx"].to_numpy()
    est = a.sum() / b.sum()
    idx = rng.integers(0, len(a), (BOOT, len(a)))
    bs = a[idx].sum(1) / b[idx].sum(1)
    return est, *np.percentile(bs, [2.5, 97.5])


def ae_ci(t):
    """Actual / expected wins at normalised SP, race bootstrap CI."""
    g = t.groupby("race_id").agg(w=("won", "sum"), e=("p_sp", "sum"))
    w, e = g["w"].to_numpy(), g["e"].to_numpy()
    idx = rng.integers(0, len(w), (BOOT, len(w)))
    bs = w[idx].sum(1) / e[idx].sum(1)
    return len(t), w.sum() / len(t), w.sum() / e.sum(), *np.percentile(bs, [2.5, 97.5])


def fmt(v):
    return f"{v[0]:+.2f} ({v[1]:+.2f} to {v[2]:+.2f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cached", action="store_true")
    a = ap.parse_args()
    d = pd.read_parquet(CACHE) if a.cached and CACHE.exists() else build()
    d["race_date"] = pd.to_datetime(d["race_date"])
    d["won"] = d["won"].fillna(0).astype(int)
    r = d.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ok=("sp", lambda s: (s > 1).all()))
    d = d[d["race_id"].isin(r.index[(r.n >= 4) & (r.w == 1) & r.ok])].copy()
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["perf"] = np.where(d["h_none"] == 0, d["wpr"] - d["h_wpr"], np.nan)
    d["model_adj"] = d["proj_adj"] + d["bias_adj"].fillna(0)

    R = d.groupby("race_id").agg(proj_shape=("proj_shape", "first"), y_shape=("y_shape", "first"),
                                 track=("track", "first"), state=("state", "first"), dist=("dist", "first"),
                                 fold=("fold", "first"))
    q = np.quantile(R["proj_shape"], [0.2, 0.4, 0.6, 0.8])
    lab = ["1 slowest", "2", "3", "4", "5 fastest"]
    R["pband"] = pd.cut(R["proj_shape"], [-np.inf, *q, np.inf], labels=lab)
    R["aband"] = pd.qcut(R["y_shape"], 5, labels=lab)
    R["dband"] = pd.cut(R["dist"], [0, 1100, 1300, 1700, 9999], labels=["<=1100", "1101-1300", "1301-1700", "1701+"])
    d = d.join(R[["pband", "aband", "dband"]], on="race_id")
    corr = R[["proj_shape", "y_shape"]].corr().iloc[0, 1]

    L = ["# Leader value by projected pace and track", "",
         f"- {R.shape[0]:,} VIC/SA/QLD races, 2023 to {d.race_date.max():%d %b %Y}, walk-forward projection v3"
         " (fitted on 2019 to Y-1, tested on Y). Races with >= 4 runners, one winner, SP for all.",
         "- Slope = within-race WPR per unit projected settle share (0 = leader, 1 = last). Negative = forward"
         " runners better. Actual = WPR minus pre-race ability (runners with form). Model = proj_adj + bias_adj.",
         f"- Projected vs actual early shape: corr {corr:.2f} (R2 {corr**2:.2f}).",
         f"- Cost coefficients by fold (WPR): " + ", ".join(
             f"{y}: settle {g.c_settle.iloc[0]:.2f}, pace {g.c_pace.iloc[0]:.2f}" for y, g in d.groupby("fold")), ""]

    def slope_table(band, title):
        rows = []
        for b, g in d.groupby(band, observed=True):
            act = slope_ci(race_sums(g, "perf", "proj_settle"))
            mod = slope_ci(race_sums(g, "model_adj", "proj_settle"))
            rows.append({band: b, "races": g.race_id.nunique(),
                         "mean proj shape": R.loc[R[band] == b, "proj_shape"].mean(),
                         "mean actual shape": R.loc[R[band] == b, "y_shape"].mean(),
                         "actual slope (95% CI)": fmt(act), "model slope": f"{mod[0]:+.2f}",
                         "actual - model": f"{act[0] - mod[0]:+.2f}"})
        allr = (slope_ci(race_sums(d, "perf", "proj_settle")), slope_ci(race_sums(d, "model_adj", "proj_settle")))
        rows.append({band: "all", "races": d.race_id.nunique(), "mean proj shape": R.proj_shape.mean(),
                     "mean actual shape": R.y_shape.mean(), "actual slope (95% CI)": fmt(allr[0]),
                     "model slope": f"{allr[1][0]:+.2f}", "actual - model": f"{allr[0][0] - allr[1][0]:+.2f}"})
        return [f"## {title}", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".2f"), ""]

    L += slope_table("pband", "1. Leader value by PROJECTED pace (what the model can use)")
    L += slope_table("aband", "1b. Leader value by ACTUAL early shape (hindsight: a perfect pace forecast)")
    L += slope_table("dband", "1c. Leader value by distance")

    # projected pace x distance
    rows = []
    for (db, pb), g in d.groupby(["dband", "pband"], observed=True):
        rows.append({"dist": db, "pace": pb, "races": g.race_id.nunique(),
                     "actual": slope_ci(race_sums(g, "perf", "proj_settle"))[0],
                     "model": slope_ci(race_sums(g, "model_adj", "proj_settle"))[0]})
    t = pd.DataFrame(rows)
    L += ["## 1d. Actual slope by distance x projected pace (model slope in brackets)", "",
          t.assign(v=[f"{a_:+.2f} ({m_:+.2f})" for a_, m_ in zip(t.actual, t.model)])
          .pivot(index="dist", columns="pace", values="v").to_markdown(), ""]

    # 2. at SP
    d["front"] = np.select([d.proj_settle_rank <= 1 / 3, d.proj_settle_rank >= 2 / 3], ["front third", "back third"],
                           "middle")
    lead = d.loc[d.groupby("race_id")["proj_settle"].idxmin()]
    rows = []
    for b in lab + ["all"]:
        gl = lead if b == "all" else lead[lead.pband == b]
        gd = d if b == "all" else d[d.pband == b]
        row = {"projected pace": b}
        for name, t in [("proj leader", gl), ("front third", gd[gd.front == "front third"]),
                        ("back third", gd[gd.front == "back third"])]:
            n, sr, ae, lo, hi = ae_ci(t)
            row[f"{name} A/E"] = f"{ae:.3f} ({lo:.2f}-{hi:.2f})"
        n, sr, *_ = ae_ci(gl)
        row["leader win %"] = f"{100 * sr:.1f}"
        rows.append(row)
    L += ["## 2. At SP: A/E (actual / expected wins at normalised SP) by projected pace", "",
          pd.DataFrame(rows).to_markdown(index=False), ""]

    # conditional logit, leave one year out: does settle x projected pace add over SP (+ settle)?
    e = d.sort_values(["race_date", "race_id"]).reset_index(drop=True)
    e["race"] = pd.factorize(e["race_id"])[0]
    e["log_p_sp"] = np.log(e["p_sp"])
    e["sd"] = e["proj_settle"] - e.groupby("race_id")["proj_settle"].transform("mean")
    zs = (e["proj_shape"] - R.proj_shape.mean()) / R.proj_shape.std()
    e["sd_x_pace"] = e["sd"] * zs
    e["adj"] = e["model_adj"] - e.groupby("race_id")["model_adj"].transform("mean")
    variants = {"SP": ["log_p_sp"], "SP + model adj": ["log_p_sp", "adj"],
                "SP + model adj + settle": ["log_p_sp", "adj", "sd"],
                "SP + model adj + settle + settle x pace": ["log_p_sp", "adj", "sd", "sd_x_pace"]}
    ll = {k: [] for k in variants}
    betas = {}
    for y in sorted(e.fold.unique()):
        tr, te = e[e.fold != y].copy(), e[e.fold == y].copy()
        tr["race"] = pd.factorize(tr["race_id"])[0]
        te["race"] = pd.factorize(te["race_id"])[0]
        for k, cols in variants.items():
            b = clogit.fit(tr[cols].to_numpy(float), tr["race"].to_numpy(), tr["won"].to_numpy())
            p = clogit.probs(te[cols].to_numpy(float), te["race"].to_numpy(), b)
            ll[k].append(-np.log(np.clip(p[te["won"].to_numpy() == 1], 1e-12, 1)))
            betas[(k, y)] = b
    ll = {k: np.concatenate(v) for k, v in ll.items()}
    ball = {k: clogit.fit(e[c].to_numpy(float), e["race"].to_numpy(), e["won"].to_numpy()) for k, c in variants.items()}
    rows = []
    prev = None
    for k in variants:
        row = {"variant": k, "log loss": f"{ll[k].mean():.5f}"}
        if prev is not None:
            z = ll[k] - ll[prev]
            idx = rng.integers(0, len(z), (BOOT, len(z)))
            lo, hi = np.percentile(z[idx].mean(1), [2.5, 97.5])
            row["vs previous row"] = f"{z.mean():+.5f} ({lo:+.5f} to {hi:+.5f})"
        row["betas (all years)"] = ", ".join(f"{c} {v:+.3f}" for c, v in zip(variants[k], ball[k]))
        rows.append(row)
        prev = k
    L += ["## 2b. Conditional logit at SP, leave one year out", "",
          "sd = projected settle share minus race mean; sd x pace = sd times standardised projected shape"
          " (a positive beta = forward runners lose value in races projected fast).", "",
          pd.DataFrame(rows).to_markdown(index=False), ""]

    # 3. by track
    rows = []
    for (tk, st), g in d.groupby(["track", "state"]):
        nr = g.race_id.nunique()
        if nr < 150:
            continue
        act = slope_ci(race_sums(g, "perf", "proj_settle"))
        mod = slope_ci(race_sums(g, "model_adj", "proj_settle"))
        fast = g[g.pband.isin(["4", "5 fastest"])]
        slow = g[g.pband.isin(["1 slowest", "2"])]
        rows.append({"track": tk, "state": st, "races": nr, "actual": act[0], "lo": act[1], "hi": act[2],
                     "model": mod[0], "actual slow pace": slope_ci(race_sums(slow, "perf", "proj_settle"))[0],
                     "actual fast pace": slope_ci(race_sums(fast, "perf", "proj_settle"))[0],
                     "model fast pace": slope_ci(race_sums(fast, "model_adj", "proj_settle"))[0]})
    T = pd.DataFrame(rows).sort_values("actual")
    c1 = T[["actual", "model"]].corr().iloc[0, 1]
    # split-half reliability of the track actual slopes (odd vs even races)
    d["half"] = d["race_id"].map(lambda v: hash(v) % 2)
    halves = []
    for tk in T.track:
        g = d[d.track == tk]
        halves.append([slope_ci(race_sums(g[g.half == h], "perf", "proj_settle"))[0] for h in (0, 1)])
    hv = np.array(halves)
    rel = np.corrcoef(hv[:, 0], hv[:, 1])[0, 1]
    wrong = T[(T.hi < T.model) | (T.lo > T.model)]
    pos = T[T.hi < 0]
    L += ["## 3. By track (>= 150 races)", "",
          f"- {len(T)} tracks. Corr actual vs model slope across tracks {c1:.2f}; split-half reliability of the"
          f" actual track slopes {rel:.2f}.",
          f"- Tracks where forward runners are significantly better (CI below 0): {len(pos)} of {len(T)}."
          f" Tracks with any CI above 0 (back-markers better): {(T.lo > 0).sum()}.",
          f"- Tracks where the model slope is outside the actual 95% CI: {len(wrong)}"
          + (f" ({', '.join(wrong.track)})" if len(wrong) else ""), "",
          T.assign(**{"actual (95% CI)": [fmt((a_, l_, h_)) for a_, l_, h_ in zip(T.actual, T.lo, T.hi)]})
          [["track", "state", "races", "actual (95% CI)", "model", "actual slow pace", "actual fast pace",
            "model fast pace"]].to_markdown(index=False, floatfmt="+.2f"), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
