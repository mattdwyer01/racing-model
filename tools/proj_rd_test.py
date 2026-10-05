"""Proj without age / sex / weight, and the race-day projection as an explicit adjustment that must add winners.

    python -W ignore tools/proj_rd_test.py            # walk-forward 2023 to 2026 -> reports/proj_rd_test.md
    python -W ignore tools/proj_rd_test.py --report   # rebuild from data/interim/proj_rd_oos.parquet

Per fold Y (fit on races before Y, score Y; VIC/SA/QLD), front-weighted LightGBM on the run's WPR (model/wpr_model.py):
  live        current inputs (race-day projection and age / sex / weight inside the trees)
  no_asw      without age / sex / weight
  form        without age / sex / weight and without the race-day projection group
  form+rd     form + race-day adjustment: b1 x proj_adj + b2 x lv_x + b3 x sx_wet (each vs the race mean), b fitted on
              the later 25% of the training window against the residual of a form model fitted on the first 75%
              (front-weighted, within-race), then added to the full-window form model
  form+rd1    same with proj_adj only (the speed map cost in WPR, coefficient fitted)
  form+rdraw  form + proj_adj as it stands (coefficient 1, no fitting)
Scored: winners inside the line holding 3.03 / 4.62 runners a race, top pick %, MAE; race bootstrap vs 'form'
(a positive difference = the race-day adjustment adds winners).
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

OUT = ROOT / "reports/proj_rd_test.md"
OOS = ROOT / "data/interim/proj_rd_oos.parquet"
RD = production.GROUPS["race-day projection"]
ASW = production.GROUPS["age / sex / weight"]
RD_TERMS = ["proj_adj", "lv_x", "sx_wet"]
BOOT = 1000


def gbm(tr, feats):
    lab = tr["y_wpr"].notna()
    return lgb.train(wm.PARAMS, lgb.Dataset(tr.loc[lab, feats].astype(float), tr.loc[lab, "y_wpr"],
                                            weight=wm.front_weights(tr[lab])), 600)


def demean(df, cols):
    x = df[cols].astype(float).fillna(0.0)
    return x - x.groupby(df["race_id"].to_numpy()).transform("mean")


def fit_rd(tr, feats, terms):
    """Race-day coefficients on the later 25% of training dates vs the residual of a form model fitted on the rest."""
    cut = tr["race_date"].quantile(0.75)
    a, b = tr[tr["race_date"] <= cut], tr[(tr["race_date"] > cut) & tr["y_wpr"].notna()].copy()
    m = gbm(a, feats)
    b["res"] = b["y_wpr"] - m.predict(b[feats].astype(float))
    r = b["res"] - b.groupby("race_id")["res"].transform("mean")
    X = demean(b, terms).to_numpy()
    w = np.sqrt(wm.front_weights(b))
    coef = np.linalg.lstsq(X * w[:, None], r.to_numpy() * w, rcond=None)[0]
    return dict(zip(terms, coef))


def fold(con, y):
    e = om.add_context(om.build(con, f"{y}-01-01"))
    cols = [c for c in production.COLS + production.MU if c in e or c in ("r_mu", "r_sigma")]
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    rm = production.fit_mu(tr)
    tr, te = wm.add_mu_abs(rm, tr), wm.add_mu_abs(rm, te)
    live = [c for c in dict.fromkeys(cols + wm.CTX) if c in tr]
    no_asw = [c for c in live if c not in ASW]
    form = [c for c in no_asw if c not in RD]
    keep = te[["run_id", "race_id", "race_date", "state", "won", "sp", "y_wpr", "h_none"]].copy()
    keep["live"] = gbm(tr, live).predict(te[live].astype(float))
    keep["no_asw"] = gbm(tr, no_asw).predict(te[no_asw].astype(float))
    base = gbm(tr, form).predict(te[form].astype(float))
    keep["form"] = base
    terms = [t for t in RD_TERMS if t in tr]
    c3 = fit_rd(tr, form, terms)
    c1 = fit_rd(tr, form, ["proj_adj"])
    keep["form+rd"] = base + (demean(te, terms) * pd.Series(c3)).sum(1).to_numpy()
    keep["form+rd1"] = base + c1["proj_adj"] * demean(te, ["proj_adj"])["proj_adj"].to_numpy()
    keep["form+rdraw"] = base + demean(te, ["proj_adj"])["proj_adj"].to_numpy()
    print(y, "coef", {k: round(v, 3) for k, v in c3.items()}, "proj_adj only", round(c1["proj_adj"], 3), flush=True)
    return keep.assign(fold=y), {"fold": y, **{f"b_{k}": v for k, v in c3.items()}, "b1_proj_adj": c1["proj_adj"]}


def inside(d, col, target):
    gap = d.groupby("race_id")[col].transform("max") - d[col]
    R = d["race_id"].nunique()
    ls = np.arange(0, 20.01, 0.05)
    cnt = np.array([(gap <= n).sum() / R for n in ls])
    n = ls[int(np.argmin(np.abs(cnt - target)))]
    return (d["won"] * (gap <= n)).groupby(d["race_id"]).sum()


def report(d, coefs=None):
    d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
    vs = ["live", "no_asw", "form", "form+rd", "form+rd1", "form+rdraw"]
    hw = d[(d["h_none"] == 0) & d["y_wpr"].notna()]
    rng = np.random.default_rng(1)
    b3, b5 = inside(d, "form", 3.03), inside(d, "form", 4.62)
    idx = rng.integers(0, len(b3), (BOOT, len(b3)))
    rows = []
    for v in vs:
        w3, w5 = inside(d, v, 3.03), inside(d, v, 4.62)
        r = {"variant": v, "inside 3 %": round(100 * w3.mean(), 2), "inside 5 %": round(100 * w5.mean(), 2)}
        for lab, w, b in (("3", w3, b3), ("5", w5, b5)):
            df = (w - b.reindex(w.index)).to_numpy()
            q = np.quantile(df[idx].mean(1), [0.025, 0.975])
            r[f"vs form, inside {lab}"] = f"{100 * df.mean():+.2f} ({100 * q[0]:+.2f} to {100 * q[1]:+.2f})"
        top = d.loc[d.groupby("race_id")[v].idxmax()]
        r["top pick %"] = round(100 * top["won"].mean(), 2)
        r["MAE"] = round((hw[v] - hw["y_wpr"]).abs().mean(), 3)
        rows.append(r)
    yr = pd.DataFrame([{"fold": y, **{v: round(100 * inside(e, v, 3.03).mean(), 1) for v in vs}}
                       for y, e in d.groupby("fold")]).set_index("fold")
    L = ["# Proj: age / sex / weight out, race-day projection as an explicit adjustment (walk-forward 2023 to Sep 2026)", "",
         f"- {d['race_id'].nunique():,} VIC/SA/QLD races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5",
         "  lines). 'vs form' = winners per 100 races vs the form-only model (no race-day group, no age / sex / weight), 95% race",
         "  bootstrap: positive = the race-day part adds winners.", "",
         pd.DataFrame(rows).to_markdown(index=False), "", "## Inside 3 by year (%)", "", yr.T.to_markdown(), ""]
    if coefs is not None:
        L += ["## Fitted race-day coefficients (WPR per unit, vs race mean)", "", pd.DataFrame(coefs).round(3).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    if "--report" in sys.argv:
        return report(pd.read_parquet(OOS))
    con = duckdb.connect(str(figure.DB), read_only=True)
    parts, coefs = zip(*[fold(con, y) for y in wm.FOLDS])
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(OOS)
    report(d, list(coefs))


if __name__ == "__main__":
    main()
