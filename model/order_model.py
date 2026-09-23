"""Finishing-order model for place and exotic betting: win probabilities -> P(exacta), P(trifecta), P(place).

    python model/order_model.py      # needs reports/race_sim_per_runner.csv.gz -> reports/order_model.md

Stagewise (Plackett-Luce) with discounting:
  P(i first)                 = p_i                                  (a win-probability source)
  P(j second | i first)      = p_j^l2 / sum over k != i of p_k^l2
  P(k third | i, j)          = p_k^l3 / sum over m not in {i, j} of p_m^l3
  Harville = l2 = l3 = 1. l < 1 flattens the minor placings (favourites run 2nd / 3rd less often than
  Harville says, long shots more often).
Walk-forward: l2, l3 fitted by likelihood on earlier test years' out-of-sample win probabilities (race_sim.py
  per-runner file), applied to year Y; evaluated on 2024 to 2026 (2023 has no earlier out-of-sample year).
Sources: calibrated SP (market only), production blend, simulation blend, production + simulation blend.
Metrics per race: exacta and trifecta log loss (-log P(actual order)); place log loss per runner (TAB rules:
  3 places with 8+ runners, 2 with 5 to 7, none under 5). Races with a dead heat in the first 3 are dropped.
Paired race bootstrap: discounted vs Harville, and model blend vs calibrated SP (both discounted).
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402

SOURCES = ["SP calibrated", "blend prod", "blend sim", "blend prod + sim"]
EVAL_YEARS = [2024, 2025, 2026]
BOOT = 2000


def load():
    r = pd.read_csv(ROOT / "reports/race_sim_per_runner.csv.gz", parse_dates=["race_date"])
    con = duckdb.connect(str(figure.DB), read_only=True)
    fin = con.sql("select run_id, res_finish finish from runs").df()
    r = r.merge(fin, on="run_id", how="left")
    top = r[r["finish"].between(1, 3)]
    ok = top.groupby("race_id")["finish"].agg(lambda s: sorted(s.tolist()) == list(range(1, len(s) + 1)) and len(s) >= 2)
    r = r[r["race_id"].isin(ok.index[ok])]
    r["n"] = r.groupby("race_id")["run_id"].transform("size")
    return r.sort_values(["race_id", "run_id"]).reset_index(drop=True)


def _cond_ll(r, src, lam, pos):
    """Mean log P(the runner finishing `pos` | the ones ahead), with discount lam, over races with that place."""
    p = r[src].clip(1e-9) ** lam
    ahead = r["finish"].between(1, pos - 1)
    denom = p.groupby(r["race_id"]).transform("sum") - (p * ahead).groupby(r["race_id"]).transform("sum")
    m = r["finish"] == pos
    return np.log(p[m] / denom[m])


def fit_lambda(r, src, pos):
    return minimize_scalar(lambda l: -_cond_ll(r, src, l, pos).mean(), bounds=(0.3, 1.5), method="bounded",
                           options={"xatol": 0.002}).x


def race_metrics(g, src, l2, l3):
    """Exacta / trifecta log loss for one race and place probabilities per runner."""
    p = g[src].to_numpy(float).clip(1e-9)
    p = p / p.sum()
    n = len(p)
    fin = g["finish"].to_numpy()
    A, B = p ** l2, p ** l3
    eye = np.eye(n, dtype=bool)
    Q2 = np.where(eye, 0.0, A[None, :] / (A.sum() - A)[:, None])           # Q2[w, s] = P(s 2nd | w 1st)
    first = np.flatnonzero(fin == 1)[0]
    second = np.flatnonzero(fin == 2)
    out = {}
    if len(second):
        s = second[0]
        out["exacta"] = -np.log(p[first] * Q2[first, s])
        third = np.flatnonzero(fin == 3)
        if len(third) and n >= 3:
            t = third[0]
            out["trifecta"] = -np.log(p[first] * Q2[first, s] * B[t] / (B.sum() - B[first] - B[s]))
    P1, P2 = p, p @ Q2
    if n >= 3:
        W = p[:, None] * Q2                                                   # P(w 1st, s 2nd)
        den = B.sum() - B[:, None] - B[None, :]                              # (w, s)
        with np.errstate(divide="ignore", invalid="ignore"):
            P3 = np.einsum("ws,wsi->i", W, np.where(
                (np.arange(n)[None, None, :] != np.arange(n)[:, None, None]) &
                (np.arange(n)[None, None, :] != np.arange(n)[None, :, None]),
                B[None, None, :] / den[:, :, None], 0.0))
    else:
        P3 = np.zeros(n)
    k = 3 if n >= 8 else (2 if n >= 5 else 0)
    if k:
        pp = np.clip(P1 + P2 + (P3 if k == 3 else 0), 1e-9, 1 - 1e-9)
        placed = (fin >= 1) & (fin <= k)
        out["place"] = -np.mean(np.where(placed, np.log(pp), np.log(1 - pp)))
    return out


def evaluate(r, src, l2, l3):
    rows = []
    for rid, g in r.groupby("race_id", sort=False):
        m = race_metrics(g, src, l2, l3)
        m["race_id"] = rid
        rows.append(m)
    return pd.DataFrame(rows).set_index("race_id")


def boot(x, rng):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
    return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def main():
    r = load()
    lam, res = {}, {}
    for y in EVAL_YEARS:
        fit, te = r[r["fold"] < y], r[r["fold"] == y]
        for src in SOURCES:
            l2, l3 = fit_lambda(fit, src, 2), fit_lambda(fit, src, 3)
            lam[(src, y)] = (round(l2, 3), round(l3, 3))
            for lab, a, b in [("Harville", 1.0, 1.0), ("discounted", l2, l3)]:
                res.setdefault((src, lab), []).append(evaluate(te, src, a, b))
        print(y, {k[0]: v for k, v in lam.items() if k[1] == y}, flush=True)
    R = {k: pd.concat(v) for k, v in res.items()}
    state = r.groupby("race_id")["state"].first()
    rng = np.random.default_rng(0)
    tab = pd.DataFrame({f"{s} / {m}": R[(s, m)].mean() for s, m in R}).T
    rows = []
    comps = [((s, "discounted"), (s, "Harville")) for s in SOURCES] + \
            [((s, "discounted"), ("SP calibrated", "discounted")) for s in SOURCES[1:]]
    for a, b in comps:
        for metric in ["exacta", "trifecta", "place"]:
            d = (R[a][metric] - R[b][metric]).dropna()
            q = state.reindex(d.index).eq("QLD").to_numpy()
            rows.append({"first": " / ".join(a), "minus": " / ".join(b), "metric": metric, "races": len(d),
                         "all": boot(d, rng), "QLD": boot(d[q], rng), "VIC/SA": boot(d[~q], rng)})
    L = ["# Finishing-order model (place and exotics)", "",
         "- Stagewise Plackett-Luce from out-of-sample win probabilities; 2nd and 3rd use p^l2, p^l3 (Harville: 1, 1)",
         "- l2, l3 fitted on earlier test years only; evaluated 2024 to 2026 VIC/SA/QLD; place = TAB rules",
         "- Log loss: exacta / trifecta per race (-log P(actual order)); place per runner (binary); lower is better", "",
         "## Mean log loss (2024 to 2026)", "", tab.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "## Fitted discounts (l2, l3) by test year", "",
         pd.Series(lam).unstack().to_markdown()]
    (ROOT / "reports/order_model.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
