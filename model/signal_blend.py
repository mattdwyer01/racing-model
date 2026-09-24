"""Signal blend: give the market-beating signals their own weights in the blend.

    python model/signal_blend.py      # needs reports/disagreement_per_runner_prod2.csv.gz -> reports/signal_blend.md

The disagreement test (base prod2) found two signals the market misprices: the position map and past ground
loss. Inside the model they move prices only ~2%, so they get diluted. Here they enter the blend directly:
  base      log q = a log p_prod2blend                                  (p_prod2blend: out-of-sample blend of prod2
                                                                         with SP; refit a keeps it comparable)
  + signals log q = a log p_prod2blend + w_pm d_pm + w_gl d_gl          (per race softmax)
  d_pm = log p(prod2 + position map) - log p(prod2)       (the position map's shift, out of sample)
  d_gl = log p(prod2) - log p(prod2 without past ground loss)
  by state: separate w for QLD and VIC/SA
Walk-forward over the test years: weights for year Y fitted on the earlier years' out-of-sample rows; evaluated
2024 to 2026. Paired race bootstrap vs the base, by state; flat-stake overlay ROI at SP for a quick look.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit  # noqa: E402
from model import offset_model as om  # noqa: E402

EVAL_YEARS = [2024, 2025, 2026]
BOOT = 2000
BOOK_OK = (1.05, 2.5)


def load():
    d = pd.read_csv(ROOT / "reports/disagreement_per_runner_prod2.csv.gz")
    d = d.sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["lp"] = np.log(d["p past ground loss"].clip(1e-12))                  # prod2 blend (with = prod2)
    d["d_pm"] = d["d position map"]
    d["d_gl"] = d["d past ground loss"]
    d["qld"] = (d["state"] == "QLD").astype(float)
    for c in ["d_pm", "d_gl"]:
        d[c + "_q"] = d[c] * d["qld"]
        d[c + "_v"] = d[c] * (1 - d["qld"])
    return d


VARIANTS = {"base": ["lp"], "+ position map": ["lp", "d_pm"], "+ ground loss": ["lp", "d_gl"],
            "+ both": ["lp", "d_pm", "d_gl"], "+ both by state": ["lp", "d_pm_q", "d_pm_v", "d_gl_q", "d_gl_v"]}


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def main():
    d = load()
    per, W = [], {}
    for y in EVAL_YEARS:
        fit, te = _race(d[d["fold"] < y].copy()), _race(d[d["fold"] == y].copy())
        out = te[["race_id", "run_id", "state", "sp", "won", "fold"]].copy()
        for name, cols in VARIANTS.items():
            b = clogit.fit(fit[cols].to_numpy(float), fit["race"].to_numpy(), fit["won"].to_numpy())
            W[(name, y)] = dict(zip(cols, np.round(b, 3)))
            out[name] = om._softmax(te[cols].to_numpy(float) @ b, te["race"].to_numpy())
        per.append(out)
    r = pd.concat(per, ignore_index=True)
    ll = r[r["won"] == 1].set_index("race_id")[list(VARIANTS)].apply(lambda p: -np.log(p.clip(1e-12)))
    state = r[r["won"] == 1].set_index("race_id")["state"]
    rng = np.random.default_rng(0)

    def boot(x):
        x = x.to_numpy()
        m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"
    rows = []
    for v in list(VARIANTS)[1:]:
        x = ll[v] - ll["base"]
        q = state.reindex(x.index).eq("QLD")
        rows.append({"variant": v, "minus": "base", "all": boot(x), "QLD": boot(x[q]), "VIC/SA": boot(x[~q])})
    # quick overlay look at SP (races with a plausible book)
    book = (1 / r["sp"].where(r["sp"] > 1)).groupby(r["race_id"]).transform("sum")
    rb = r[book.between(*BOOK_OK)]
    bet = []
    for v in VARIANTS:
        for t in [0.0, 0.05, 0.1]:
            b = rb[(rb[v] * rb["sp"] - 1 > t) & (rb["sp"] <= 21)]
            ret = b["won"] * b["sp"] - 1
            g = pd.DataFrame({"r": ret, "race": b["race_id"]}).groupby("race")["r"].agg(["sum", "size"])
            idx = rng.integers(0, len(g), (BOOT, len(g))) if len(g) else None
            ci = (f"{np.percentile(g['sum'].to_numpy()[idx].sum(1) / g['size'].to_numpy()[idx].sum(1), 2.5):+.3f} to "
                  f"{np.percentile(g['sum'].to_numpy()[idx].sum(1) / g['size'].to_numpy()[idx].sum(1), 97.5):+.3f}") if len(g) else ""
            bet.append({"variant": v, "edge >": t, "bets": len(b), "ROI at SP": ret.mean() if len(b) else np.nan,
                        "95%": ci})
    L = ["# Signal blend: position map and past ground loss as their own blend weights", "",
         "- Base: the out-of-sample prod2 blend (prod2 + SP). Signals: the position map's and past ground loss's"
         " shifts to the prod2 blend (from the prod2 disagreement test)",
         "- Weights for year Y fitted on the earlier test years only; evaluated 2024 to 2026, VIC/SA/QLD", "",
         "## Mean race log loss", "", ll.groupby(r[r["won"] == 1].set_index("race_id")["fold"]).mean().T.assign(
             pooled=ll.mean()).to_markdown(floatfmt=".4f"), "",
         "## Paired differences vs the base (negative = better; 95% race bootstrap)", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "## Fitted weights by test year", "", pd.Series(W).unstack().to_markdown(), "",
         "## Overlay at SP, flat stakes, SP <= 21 (quick look)", "", pd.DataFrame(bet).to_markdown(index=False, floatfmt=".3f")]
    (ROOT / "reports/signal_blend.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
