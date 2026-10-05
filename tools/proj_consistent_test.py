"""Proj with every race-day adjustment applied the same way.

    python -W ignore tools/proj_consistent_test.py            # walk-forward 2023 to 2026 -> reports/proj_consistent_test.md
    python -W ignore tools/proj_consistent_test.py --report   # rebuild from data/interim/proj_consistent_oos.parquet
    python -W ignore tools/proj_consistent_test.py --set2     # + trip_undo / style_x / posv_td -> proj_consistent_test2.md

One recipe for every adjustment: a term in WPR points vs the race mean (the runner's projected settle or barrier share vs
the field x a slope learned from past races only), times a calibration weight b >= 0 fitted jointly (non-negative least
squares) on the later 25% of each training window against the form model's within-race residual, front-weighted.
Form model = front-weighted LightGBM on the run's WPR without the race-day projection, age / sex / weight and track
bias groups. Terms:
  speed map     proj_adj (settle / pace / ground-loss cost)
  leader value  lv_x
  wet settle    sx_wet
  track bias    tbx_settle_long, tbx_settle_recent (same rail, last 35 days), tbx_bar_long, tbx_bar_recent
  track x dist  tdx_perf (barrier at this track and distance)
  by condition  cbx_dist_* / cbx_going_* / cbx_rail_* (track bias split by distance band, going band, rail band)
  vs own history  pos_chg (settling further forward than usual), bar_chg (drawn better than usual)
Variants: 'current' (live: track bias inside the trees + speed map / leader value / wet settle), 'consistent' (all
terms but the condition splits), 'all' (+ condition splits), and 'all - <term>' (each term left out).
Scored: winners inside the line holding 3.03 / 4.62 runners a race, top pick %; race bootstrap vs 'form'.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.optimize import nnls

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, production, projection, wpr_model as wm  # noqa: E402
from model import offset_model as om  # noqa: E402

OUT = ROOT / "reports/proj_consistent_test.md"
OOS = ROOT / "data/interim/proj_consistent_oos.parquet"
RD = production.GROUPS["race-day projection"]
ASW = production.GROUPS["age / sex / weight"]
TB = production.GROUPS["track bias"]
CUR = ["proj_adj", "lv_x", "sx_wet"]
CONS = CUR + ["tbx_settle_long", "tbx_settle_recent", "tbx_bar_long", "tbx_bar_recent", "tdx_perf"]
ALL = CONS + projection.CTX_BIAS + projection.CHG
if "--set2" in sys.argv:          # trip-neutral form, own running style, position value by track x distance
    ALL = ALL + projection.SET2
    OUT = ROOT / "reports/proj_consistent_test2.md"
    OOS = ROOT / "data/interim/proj_consistent_oos2.parquet"
BOOT = 1000
TERMS = []


def gbm(tr, feats):
    lab = tr["y_wpr"].notna()
    return lgb.train(wm.PARAMS, lgb.Dataset(tr.loc[lab, feats].astype(float), tr.loc[lab, "y_wpr"],
                                            weight=wm.front_weights(tr[lab])), 600)


def demean(df, cols):
    x = df.reindex(columns=cols).astype(float).fillna(0.0)
    return x - x.groupby(df["race_id"].to_numpy()).transform("mean")


def holdout(tr, feats):
    cut = tr["race_date"].quantile(0.75)
    a, b = tr[tr["race_date"] <= cut], tr[(tr["race_date"] > cut) & tr["y_wpr"].notna()].copy()
    b["base"] = gbm(a, feats).predict(b[feats].astype(float))
    b["res"] = b["y_wpr"] - b["base"]
    b["r"] = b["res"] - b.groupby("race_id")["res"].transform("mean")
    return b


def fit_b(b, terms, nonneg=True):
    sw = np.sqrt(wm.front_weights(b))
    X = demean(b, terms).to_numpy() * sw[:, None]
    y = b["r"].to_numpy() * sw
    coef = nnls(X, y)[0] if nonneg else np.linalg.lstsq(X, y, rcond=None)[0]
    return dict(zip(terms, coef))


def fit_win(b, terms):
    """Weights fitted to WHO WON: conditional logit on the holdout with the form base and the terms; WPR weight of a
    term = its coefficient / the base's. Negative weights are dropped and the fit repeated (all weights >= 0)."""
    from model import clogit
    terms = list(terms)
    while True:
        X = np.c_[demean(b, ["base"]).to_numpy(), demean(b, terms).to_numpy()]
        beta = clogit.fit(X, pd.factorize(b["race_id"])[0], b["won"].to_numpy())
        w = beta[1:] / beta[0]
        if (w >= 0).all() or not terms:
            return dict(zip(terms, w))
        terms = [t for t, v in zip(terms, w) if v >= 0]


def apply(te, base, coef):
    return base + (demean(te, list(coef)) * pd.Series(coef)).sum(1).to_numpy()


def fold(con, y):
    e = om.add_context(om.build(con, f"{y}-01-01"))
    cols = [c for c in production.COLS + production.MU if c in e or c in ("r_mu", "r_sigma")]
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    rm = production.fit_mu(tr)
    tr, te = wm.add_mu_abs(rm, tr), wm.add_mu_abs(rm, te)
    live = [c for c in dict.fromkeys(cols + wm.CTX) if c in tr]
    f1 = [c for c in live if c not in RD + ASW]
    f2 = [c for c in f1 if c not in TB]
    keep = te[["run_id", "race_id", "race_date", "state", "won", "sp", "y_wpr", "h_none"]].copy()
    b1, b2 = holdout(tr, f1), holdout(tr, f2)
    base1, base2 = gbm(tr, f1).predict(te[f1].astype(float)), gbm(tr, f2).predict(te[f2].astype(float))
    keep["form"] = base2
    keep["current"] = apply(te, base1, fit_b(b1, CUR, nonneg=False))
    coefs = {"fold": y}
    for name, terms in (("consistent", CONS), ("all", ALL)):
        c = fit_b(b2, [t for t in terms if t in tr])
        keep[name] = apply(te, base2, c)
        coefs.update({f"{name}:{k}": v for k, v in c.items()})
    for t in ALL:
        keep[f"all - {t}"] = apply(te, base2, fit_b(b2, [u for u in ALL if u != t and u in tr]))
    bw = b2.sort_values(["race_id", "run_id"])
    bw = bw[bw.groupby("race_id")["won"].transform("sum") == 1]
    for name, terms in (("win: consistent", CONS), ("win: all", ALL)):
        c = fit_win(bw, [t for t in terms if t in tr])
        keep[name] = apply(te, base2, c)
        coefs.update({f"{name}:{k}": v for k, v in c.items()})
    # terms saved for fast refits (no GBM): holdout and test rows, base + every term vs the race mean
    tt = [t for t in ALL if t in tr]
    hz = pd.concat([bw[["race_id", "won"]], demean(bw, ["base"] + tt)], axis=1).assign(fold=y, part="holdout")
    tz = pd.concat([te[["race_id", "won"]], demean(te.assign(base=base2), ["base"] + tt)], axis=1).assign(
        fold=y, part="test", base_abs=base2)
    TERMS.append(pd.concat([hz, tz], ignore_index=True))
    print(y, {k: round(v, 3) for k, v in coefs.items() if k.startswith("all:")}, flush=True)
    return keep.assign(fold=y), coefs


def inside(d, col, target):
    gap = d.groupby("race_id")[col].transform("max") - d[col]
    R = d["race_id"].nunique()
    ls = np.arange(0, 20.01, 0.05)
    cnt = np.array([(gap <= n).sum() / R for n in ls])
    n = ls[int(np.argmin(np.abs(cnt - target)))]
    return (d["won"] * (gap <= n)).groupby(d["race_id"]).sum()


def report(d, coefs=None):
    d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
    main = ["form", "current", "consistent", "all"] + [c for c in ("win: consistent", "win: all") if c in d]
    loo = [c for c in d if c.startswith("all - ")]
    rng = np.random.default_rng(1)
    ref = {"form": (inside(d, "form", 3.03), inside(d, "form", 4.62)),
           "all": (inside(d, "all", 3.03), inside(d, "all", 4.62))}
    idx = rng.integers(0, len(ref["form"][0]), (BOOT, len(ref["form"][0])))

    def row(v, against):
        w3, w5 = inside(d, v, 3.03), inside(d, v, 4.62)
        r = {"variant": v, "inside 3 %": round(100 * w3.mean(), 2), "inside 5 %": round(100 * w5.mean(), 2)}
        for lab, w, b in (("3", w3, ref[against][0]), ("5", w5, ref[against][1])):
            df = (w - b.reindex(w.index)).to_numpy()
            q = np.quantile(df[idx].mean(1), [0.025, 0.975])
            r[f"vs {against}, inside {lab}"] = f"{100 * df.mean():+.2f} ({100 * q[0]:+.2f} to {100 * q[1]:+.2f})"
        r["top pick %"] = round(100 * d.loc[d.groupby("race_id")[v].idxmax(), "won"].mean(), 2)
        return r
    t1 = pd.DataFrame([row(v, "form") for v in main])
    t2 = pd.DataFrame([row(v, "all") for v in loo])
    yr = pd.DataFrame([{"fold": y, **{v: round(100 * inside(e, v, 3.03).mean(), 1) for v in main}}
                       for y, e in d.groupby("fold")]).set_index("fold")
    L = ["# Proj: every race-day adjustment applied the same way (walk-forward 2023 to Sep 2026, VIC/SA/QLD)", "",
         f"- {d['race_id'].nunique():,} races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5 lines).",
         "- Each adjustment = term in WPR vs the race mean x weight b >= 0 fitted jointly on the later 25% of training dates",
         "  against the form model's residual. 'form' = no race-day, age / sex / weight or track bias groups.", "",
         "## Versions vs form only (winners per 100 races, 95% race bootstrap)", "", t1.to_markdown(index=False), "",
         "## Each adjustment left out of 'all' (negative = the adjustment adds winners)", "", t2.to_markdown(index=False), "",
         "## Inside 3 by year (%)", "", yr.T.to_markdown(), ""]
    if coefs is not None:
        c = pd.DataFrame(coefs).set_index("fold").T.round(3)
        L += ["## Fitted weights b (1 = the term at face value)", "", c.to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    if "--report" in sys.argv:
        return report(pd.read_parquet(OOS))
    con = duckdb.connect(str(figure.DB), read_only=True)
    parts, coefs = zip(*[fold(con, y) for y in wm.FOLDS])
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(OOS)
    pd.concat(TERMS, ignore_index=True).to_parquet(str(OOS).replace(".parquet", "_terms.parquet"))
    report(d, list(coefs))


if __name__ == "__main__":
    main()
