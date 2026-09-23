"""Walk-forward validation of the per-run figure by log loss against SP.

    python model/validate_figure.py            # print results, write reports/figure_validation.md
    python model/validate_figure.py --write    # also write model/figure_coef.json and table run_figure

Eval set: VIC/SA/QLD races (in_scope) from 2022, every runner with an SP, one winner.
Folds: test year Y in 2023..2026, trained on 2022..Y-1 (dates only).
Each variant is a conditional logit on pre-race decayed means of the run components.
"""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure  # noqa: E402

CONTEXT = ["h_none", "log_n", "log_days", "first_up"]
VARIANTS = {
    "wpr":           CONTEXT + ["h_wpr"],
    "+weight":       CONTEXT + ["h_wpr", "wt_rel_today", "h_wt_rel"],
    "+sectionals":   CONTEXT + ["h_wpr", "wt_rel_today", "h_wt_rel", "h_s_early", "h_s_l600", "h_s_early_miss"],
    "+pace (figure)": CONTEXT + ["h_wpr", "wt_rel_today", "h_wt_rel", "h_s_early", "h_s_l600", "h_s_early_miss",
                                 "h_settle", "h_shape", "h_pace", "h_settle_miss"],
}
FIG = VARIANTS["+pace (figure)"]
FOLDS = [2023, 2024, 2025, 2026]


def eval_set(h):
    e = h[h["in_scope"] & (h["race_date"] >= "2022-01-01")].copy()
    e["won"] = e["won"].fillna(0).astype(int)
    r = e.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), sp_ok=("sp", lambda s: (s > 1).all()))
    keep = r.index[(r.n >= 2) & (r.w == 1) & r.sp_ok]
    e = e[e["race_id"].isin(keep)].sort_values(["race_date", "race_id"]).reset_index(drop=True)
    e["race"] = pd.factorize(e["race_id"])[0]
    inv = 1 / e["sp"]
    e["p_sp"] = inv / inv.groupby(e["race_id"]).transform("sum")
    e["log_p_sp"] = np.log(e["p_sp"])
    e["log_n"] = np.log1p(e["h_n"])
    e["log_days"] = np.log1p(e["days_since_start"].fillna(0))
    e["first_up"] = (e["days_since_start"].fillna(999) >= 60).astype(float)
    return e


def fit_eval(tr, te, cols):
    mu, sd = tr[cols].mean(), tr[cols].std().replace(0, 1)
    Xtr = ((tr[cols] - mu) / sd).to_numpy(float)
    Xte = ((te[cols] - mu) / sd).to_numpy(float)
    b = clogit.fit(Xtr, tr["race"].to_numpy(), tr["won"].to_numpy())
    p = clogit.probs(Xte, te["race"].to_numpy(), b) if len(te) else None
    return p, pd.Series(b / sd.to_numpy(), index=cols)


def race_ll(p, te):
    return -np.log(np.clip(p[te["won"].to_numpy() == 1], 1e-12, 1))


def main(write=False):
    con = duckdb.connect(str(figure.DB), read_only=True)
    d = figure.components(con)
    h = figure.history(d)
    e = eval_set(h)
    print(f"eval races {e.race_id.nunique():,}, runners {len(e):,}")

    rows, per_race = [], {}
    for y in FOLDS:
        tr = e[(e.race_date >= "2022-01-01") & (e.race_date < f"{y}-01-01")]
        te = e[e.race_date.dt.year == y]
        res = {"fold": y, "races": te.race_id.nunique()}
        ll = {"SP (raw)": race_ll(te["p_sp"].to_numpy(), te)}
        ll["SP (calibrated)"] = race_ll(fit_eval(tr, te, ["log_p_sp"])[0], te)
        for name, cols in VARIANTS.items():
            ll[name] = race_ll(fit_eval(tr, te, cols)[0], te)
        ll["SP + figure"] = race_ll(fit_eval(tr, te, ["log_p_sp"] + FIG)[0], te)
        ll["SP + wpr"] = race_ll(fit_eval(tr, te, ["log_p_sp"] + VARIANTS["wpr"])[0], te)
        for k, v in ll.items():
            res[k] = v.mean()
            per_race.setdefault(k, []).append(v)
        rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"})

    tab = pd.DataFrame(rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per_race.items()}
    tab.loc["pooled"] = [sum(tab["races"])] + [pooled[k].mean() for k in tab.columns[1:]]

    def diff(a, b):
        x = pooled[a] - pooled[b]
        return x.mean(), x.std() / np.sqrt(len(x))
    comps = [("+weight", "wpr"), ("+sectionals", "+weight"), ("+pace (figure)", "+sectionals"),
             ("+pace (figure)", "wpr"), ("SP + wpr", "SP (calibrated)"), ("SP + figure", "SP + wpr"),
             ("SP + figure", "SP (calibrated)")]
    diffs = [(a, b, *diff(a, b)) for a, b in comps]

    # figure weights from all 2022+ data: c_j = beta_j / beta_wpr for the run components
    _, b_all = fit_eval(e, e.iloc[:0], FIG)
    comp_cols = ["h_s_early", "h_s_l600", "h_wt_rel", "h_settle", "h_shape", "h_pace"]
    coef = {"wpr": 1.0, **{c[2:]: float(b_all[c] / b_all["h_wpr"]) for c in comp_cols}}
    print("figure weights (per unit, WPR points):", {k: round(v, 3) for k, v in coef.items()})
    print("full logit:", b_all.round(4).to_dict())

    report(tab, diffs, coef, b_all, e)
    if write:
        (ROOT / "model/figure_coef.json").write_text(json.dumps(coef, indent=2) + "\n")
        d["fig"] = figure.figure(d, coef)
        w = duckdb.connect(str(figure.DB))
        out = d[["run_id", "race_id", "horse_id", "race_date", "wpr", "fig"] + figure.COMPONENTS[1:]]
        w.register("f", out)
        w.execute("create or replace table run_figure as select * from f")
        print("wrote run_figure", len(out))


def report(tab, diffs, coef, b_all, e):
    L = ["# Per-run figure: walk-forward validation", "",
         f"- Eval set: VIC/SA/QLD races 2022 on, SP for every runner, one winner "
         f"({e.race_id.nunique():,} races, {len(e):,} runners)",
         "- Folds: test year Y (2023 to 2026 YTD), trained on 2022 to Y-1",
         "- Metric: mean -log p(winner) per race (lower is better)", "",
         "## Log loss by fold", "", tab.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (pooled over test races, negative = first is better)", "",
         "| model | vs | diff | se |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {m:+.4f} | {s:.4f} |" for a, b, m, s in diffs]
    L += ["", "## Figure weights (fit on all 2022 on)", "",
          "fig = wpr + sum(c_j * x_j), per unit of each component:", "",
          "| component | c_j |", "|---|---|"]
    L += [f"| {k} | {v:+.3f} |" for k, v in coef.items()]
    L += ["", "Full logit coefficients (raw units):", "", "| feature | beta |", "|---|---|"]
    L += [f"| {k} | {v:+.4f} |" for k, v in b_all.items()]
    out = ROOT / "reports/figure_validation.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main(write="--write" in sys.argv)
