"""Does GPS ground loss improve the per-run figure? QLD races, walk-forward.

    python model/validate_gps.py      # prints and writes reports/gps_figure_validation.md

Eval set: QLD races (RQ GPS from Oct 2022). Folds: test year Y in 2024..2026, trained on
QLD 2023..Y-1. Same eval rules and conditional logit as validate_figure.py.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402
from model.validate_figure import FIG, eval_set, fit_eval, race_ll  # noqa: E402

GL = FIG + ["h_gl", "h_gl_miss"]
GL_RAIL = GL + ["h_rail"]
VARIANTS = {
    "figure": FIG,
    "figure + ground loss": GL,
    "figure + ground loss + rail": GL_RAIL,
    "SP (calibrated)": ["log_p_sp"],
    "SP + figure": ["log_p_sp"] + FIG,
    "SP + figure + ground loss + rail": ["log_p_sp"] + GL_RAIL,
}
FOLDS = [2024, 2025, 2026]
COMPS = [("figure + ground loss", "figure"), ("figure + ground loss + rail", "figure + ground loss"),
         ("SP + figure", "SP (calibrated)"), ("SP + figure + ground loss + rail", "SP + figure"),
         ("SP + figure + ground loss + rail", "SP (calibrated)")]


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    h = figure.history(figure.components(con))
    e = eval_set(h)
    e = e[(e["state"] == "QLD") & (e["race_date"] >= "2023-01-01")].reset_index(drop=True)
    e["race"] = pd.factorize(e["race_id"])[0]
    # field-level GPS history coverage, to split results by how much GPS form the field has
    e["field_gps"] = 1 - e.groupby("race_id")["h_gl_miss"].transform("mean")

    rows, per, cover = [], {}, []
    for y in FOLDS:
        tr = e[e.race_date < f"{y}-01-01"]
        te = e[e.race_date.dt.year == y]
        res = {"fold": y, "races": te.race_id.nunique()}
        for name, cols in VARIANTS.items():
            ll = race_ll(fit_eval(tr, te, cols)[0], te)
            res[name] = ll.mean()
            per.setdefault(name, []).append(ll)
        cover.append(te.loc[te.won == 1, "field_gps"].to_numpy())
        rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"})
    tab = pd.DataFrame(rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    tab.loc["pooled"] = [tab["races"].sum()] + [pooled[k].mean() for k in VARIANTS]
    fg = np.concatenate(cover)

    def diff(a, b, mask=None):
        x = pooled[a] - pooled[b]
        x = x if mask is None else x[mask]
        return x.mean(), x.std() / np.sqrt(len(x)), len(x)

    _, b_all = fit_eval(e, e.iloc[:0], GL_RAIL)
    c = {k: b_all[k] / b_all["h_wpr"] for k in ["h_gl", "h_rail", "h_settle", "h_pace", "h_s_l600"]}
    print("figure weights (WPR pts per unit):", {k: round(v, 3) for k, v in c.items()})

    L = ["# Ground loss in the figure: QLD walk-forward", "",
         f"- Eval set: QLD races 2023 on, SP for every runner, one winner ({e.race_id.nunique():,} races)",
         "- Folds: test year Y (2024 to 2026 YTD), trained on QLD 2023 to Y-1",
         "- Ground loss = GPS metres travelled vs field mean; rail = avg distance from rail vs field mean;"
         " decayed means over prior starts, 0 plus a missing flag where a past run has no GPS", "",
         "## Log loss by fold", "", tab.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better)", "",
         "| model | vs | test races | diff | se |", "|---|---|---|---|---|"]
    for a, b in COMPS:
        for lab, mask in [("all", None), ("field GPS history >= 60%", fg >= 0.6)]:
            m, s, n = diff(a, b, mask)
            L.append(f"| {a} | {b} ({lab}) | {n:,} | {m:+.4f} | {s:.4f} |")
    L += ["", "## Figure weights (fit on all QLD 2023 on, WPR points per unit)", "",
          "| component | c_j |", "|---|---|"] + [f"| {k[2:]} | {v:+.3f} |" for k, v in c.items()]
    out = ROOT / "reports/gps_figure_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
