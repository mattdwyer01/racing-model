"""Proj rebuild: the WPR each horse runs (same inputs as model/wpr_model.py), trained to put more WINNERS inside the
n-point line from the top projection, while staying a WPR number.

    python -W ignore tools/proj_rebuild_test.py          # walk-forward 2023 to 2026 -> reports/proj_rebuild_test.md
    python -W ignore tools/proj_rebuild_test.py --report # rebuild the report from data/interim/proj_rebuild_oos.parquet

Variants (per fold Y: fit on races before Y, score Y; VIC/SA/QLD):
  base      current Proj: LightGBM l2 on the run's WPR
  rel       target = WPR vs the race's mean WPR (race-level noise removed); level from base (race mean of base)
  front     base with sample weights on runners near the race's best WPR (within 5: x4, within 10: x2)
  rel_front rel + front weights
  q60/q70   quantile regression (the 60th / 70th percentile of the WPR it runs: credits upside)
  sd03/sd05 base mean + 0.3 / 0.5 x predicted sd (upside from the spread model)
  rank      LambdaRank on finishing order by WPR, mapped back to WPR within the race (base mean + slope x score)
Scored on: winners inside the line at matched runner counts (2, 2.5, 3, 4.7 runners per race), top pick win %,
WPR error (MAE, runners with prior form). Racing Model (p_rm) and SP for reference.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, production, wpr_model as wm  # noqa: E402
from model import offset_model as om  # noqa: E402

OUT = ROOT / "reports/proj_rebuild_test.md"
OOS = ROOT / "data/interim/proj_rebuild_oos.parquet"
VARS = ["base", "rel", "front", "rel_front", "q60", "q70", "sd03", "sd05", "rank"]
COUNTS = [2.0, 2.5, 3.0, 4.7]


def fit(params, X, y, w=None, rounds=600):
    return lgb.train(params, lgb.Dataset(X, y, weight=w), rounds)


def fold(con, y):
    e = om.add_context(om.build(con, f"{y}-01-01"))
    cols = [c for c in production.COLS + production.MU if c in e or c in ("r_mu", "r_sigma")]
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    rm = production.fit_mu(tr)
    tr, te = wm.add_mu_abs(rm, tr), wm.add_mu_abs(rm, te)
    feats = [c for c in dict.fromkeys(cols + wm.CTX) if c in tr]
    beta = production._fit_raw(tr, [c for c in cols if c in tr])
    te["p_rm"] = om._softmax(production.utility(te, beta), te["race"].to_numpy())
    lab = tr["y_wpr"].notna()
    L = tr[lab].copy()
    X, Xt = L[feats].astype(float), te[feats].astype(float)
    yv = L["y_wpr"].to_numpy()
    rid = L["race_id"].to_numpy()
    rel = yv - L.groupby("race_id")["y_wpr"].transform("mean").to_numpy()
    gap = L.groupby("race_id")["y_wpr"].transform("max").to_numpy() - yv
    wf = np.where(gap <= 5, 4.0, np.where(gap <= 10, 2.0, 1.0))
    P = wm.PARAMS
    g = te["race_id"].to_numpy()
    def relevel(pred, base):    # keep the race level of base, the within-race order of pred
        s = pd.Series(pred, index=te.index)
        b = pd.Series(base, index=te.index)
        return (s - s.groupby(g).transform("mean") + b.groupby(g).transform("mean")).to_numpy()
    out = {}
    base = fit(P, X, yv).predict(Xt)
    out["base"] = base
    out["rel"] = relevel(fit(P, X, rel).predict(Xt), base)
    out["front"] = fit(P, X, yv, wf).predict(Xt)
    out["rel_front"] = relevel(fit(P, X, rel, wf).predict(Xt), base)
    for a in (60, 70):
        out[f"q{a}"] = fit(dict(P, objective="quantile", alpha=a / 100), X, yv).predict(Xt)
    # spread model as in wpr_model (holdout residuals)
    cut = L["race_date"].quantile(0.75)
    inner, hold = (L["race_date"] <= cut).to_numpy(), (L["race_date"] > cut).to_numpy()
    m1 = fit(P, X[inner], yv[inner])
    res = np.abs(yv[hold] - m1.predict(X[hold]))
    sd = np.clip(fit(dict(P, objective="l1"), X[hold], res, rounds=300).predict(Xt) * np.sqrt(np.pi / 2) * wm.SD_SCALE, 2, 25)
    out["sd03"], out["sd05"] = base + 0.3 * sd, base + 0.5 * sd
    # LambdaRank: relevance from WPR order within the race (top 5 graded), then mapped to WPR in training
    order = L.sort_values(["race_id", "y_wpr"], ascending=[True, False])
    rk = order.groupby("race_id").cumcount().to_numpy()
    relv = np.clip(5 - rk, 0, 5)
    grp = order.groupby("race_id", sort=False).size().to_numpy()
    rp = dict(P, objective="lambdarank", lambdarank_truncation_level=10, label_gain=list(range(6)))
    rmod = lgb.train(rp, lgb.Dataset(order[feats].astype(float), relv, group=grp), 400)
    s_tr = rmod.predict(X)
    s_dev = s_tr - pd.Series(s_tr).groupby(rid).transform("mean").to_numpy()
    slope = np.polyfit(s_dev, rel, 1)[0]
    s_te = rmod.predict(Xt)
    out["rank"] = relevel(slope * s_te, base)
    keep = te[["run_id", "race_id", "race_date", "state", "won", "sp", "y_wpr", "h_none", "p_rm"]].copy()
    for k, v in out.items():
        keep[k] = v
    keep["sd"] = sd
    print(y, "done", len(keep), "rank slope", round(slope, 2), flush=True)
    return keep.assign(fold=y)


def winners_at(d, col, target, higher=True):
    """Line (points from the top) giving `target` runners per race, and winners inside it (% of races)."""
    g = d.groupby("race_id")[col]
    gap = (g.transform("max") - d[col]) if higher else (d[col] - g.transform("min"))
    R = d["race_id"].nunique()
    ls = np.arange(0, 30.01, 0.05)
    cnt = np.array([(gap <= n).sum() / R for n in ls])
    n = ls[int(np.argmin(np.abs(cnt - target)))]
    return n, 100 * d.loc[gap <= n, "won"].sum() / R


def report(d):
    d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
    d["rt"] = 8.205 * np.log(d["p_rm"])
    d["lsp"] = -8.205 * np.log(d["sp"])
    hw = d[(d["h_none"] == 0) & d["y_wpr"].notna()]
    rows = []
    for v in VARS + ["rt", "lsp"]:
        r = {"variant": {"rt": "Rating (Racing Model)", "lsp": "SP (reference)"}.get(v, v)}
        top = d.loc[d.groupby("race_id")[v].idxmax()]
        r["top pick %"] = round(100 * top["won"].mean(), 2)
        for t in COUNTS:
            n, w = winners_at(d, v, t)
            r[f"{t} runners: line / winners %"] = f"{n:.1f} / {w:.1f}"
        r["MAE"] = round((hw[v] - hw["y_wpr"]).abs().mean(), 2) if v in VARS else ""
        rows.append(r)
    t = pd.DataFrame(rows)
    yr = []
    for y, e in d.groupby("fold"):
        r = {"fold": y, "races": e["race_id"].nunique()}
        for v in VARS + ["rt"]:
            r[v] = round(winners_at(e, v, 2.5)[1], 1)
        yr.append(r)
    L = ["# Proj rebuild: more winners inside n of the top, still a WPR (walk-forward 2023 to Sep 2026, VIC/SA/QLD)", "",
         f"- {d['race_id'].nunique():,} races. Lines are set per variant so each holds the same number of runners per race;",
         "  winners % = races whose winner is inside the line. MAE = WPR error, runners with prior form.", "",
         t.to_markdown(index=False), "", "## Winners inside the 2.5-runner line, by year (%)", "",
         pd.DataFrame(yr).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    if "--report" in sys.argv:
        return report(pd.read_parquet(OOS))
    con = duckdb.connect(str(figure.DB), read_only=True)
    d = pd.concat([fold(con, y) for y in wm.FOLDS], ignore_index=True)
    d.to_parquet(OOS)
    report(d)


if __name__ == "__main__":
    main()
