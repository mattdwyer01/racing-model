"""SP vs model vs model + SP blend on the same test races, blend weights fitted on training data only.

    python model/blend_eval.py                    # baseline only -> reports/blend_eval.md
    python model/blend_eval.py --variants gl      # baseline + variant(s), paired comparison vs baseline

Per fold (test year Y, 2023 to 2026 YTD; VIC/SA/QLD races, as validate_figure.py):
  model (no market): conditional logit, and LightGBM (per-race softmax, no SP offset), on figure + ability +
      jockey/trainer + race-day projection. No SP or market rank among the inputs.
  weights: the model is fitted on the first 75% of training dates and predicts the last 25%; on that window
      we fit  blend = softmax(a * log p_model + b * log p_SP)  and  SP calibrated = softmax(c * log p_SP).
      The model is then refitted on all training data; a, b, c are applied unchanged to the test year.
  SP raw = normalised 1 / SP.
Every variant uses the same fold builds, so comparisons with the baseline are paired race by race.
Per-race losses for all variants: reports/blend_per_race.csv.gz.

Variants (added inputs on top of the baseline):
  gl   GPS ground loss history: the horse's decayed mean extra ground and width from the rail (QLD GPS runs),
       with a missing flag
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
NOMKT = [c for c in om.GBM_FEATS if c not in ("log_p_sp", "mkt_rank")]
LOGIT_X = om.BASE + om.JT + om.PROJ
EXTRA = {"baseline": [], "gl": ["h_gl", "h_gl_miss", "h_rail"]}
BOOT = 2000
KEY = ["race_id", "race_date", "state", "fold"]


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def run_fold(e, y, variants):
    tr = _race(e[e.race_date < f"{y}-01-01"].copy())
    te = _race(e[e.race_date.dt.year == y].copy())
    assert tr.race_date.max() < te.race_date.min(), "train must end before the test period"
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())
    out = {"SP raw": race_ll(te["p_sp"].to_numpy(), te)}
    c = clogit.fit(bl[["log_p_sp"]].to_numpy(float), bl["race"].to_numpy(), bl["won"].to_numpy())[0]
    out["SP calibrated"] = race_ll(om._softmax(c * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
    weights = {"SP calibration c": c, "blend window": f"{bl.race_date.min():%d %b %Y} to {bl.race_date.max():%d %b %Y}"}
    for v in variants:
        fits = {"logit": lambda d, x=EXTRA[v]: om.logit_fit(d, LOGIT_X + x),
                "gbm": lambda d, x=EXTRA[v]: om.gbm_fit(d, feats=NOMKT + x, market=False)[0]}
        for name, fit in fits.items():
            p_bl = np.clip(fit(inner)(bl), 1e-12, 1)
            X = np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)]
            a, b = clogit.fit(X, bl["race"].to_numpy(), bl["won"].to_numpy())
            p_te = np.clip(fit(tr)(te), 1e-12, 1)
            out[f"{v}: model {name}"] = race_ll(p_te, te)
            out[f"{v}: blend {name}"] = race_ll(
                om._softmax(a * np.log(p_te) + b * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
            weights[f"{v} {name} a"], weights[f"{v} {name} b"] = a, b
    winners = te[te.won == 1][["race_id", "race_date", "state"]].reset_index(drop=True)
    return pd.concat([winners, pd.DataFrame(out)], axis=1).assign(fold=y), weights


def boot_ci(x, rng):
    idx = rng.integers(0, len(x), (BOOT, len(x)))
    m = x[idx].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


def diff_table(d, pairs, rng, subsets):
    rows = []
    for lab, a, b in pairs:
        for sname, mask in subsets:
            x = (d.loc[mask, a] - d.loc[mask, b]).to_numpy()
            lo, hi = boot_ci(x, rng)
            rows.append({"comparison": lab, "races": sname, "n": len(x), "mean": x.mean(), "95% lo": lo,
                         "95% hi": hi, "share of races better": (x < 0).mean()})
    return pd.DataFrame(rows)


def half_table(d, pairs, rng):
    d = d.assign(half=d["race_date"].dt.year.astype(str) + np.where(d["race_date"].dt.month <= 6, " H1", " H2"))
    rows = []
    for h, g in d.groupby("half"):
        row = {"period": h, "races": len(g)}
        for lab, a, b in pairs:
            x = (g[a] - g[b]).to_numpy()
            lo, hi = boot_ci(x, rng)
            row[lab] = x.mean()
            row[lab + " 95%"] = f"{lo:+.4f} to {hi:+.4f}"
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="*", default=[], choices=[k for k in EXTRA if k != "baseline"])
    variants = ["baseline"] + ap.parse_args().variants
    con = duckdb.connect(str(figure.DB), read_only=True)
    per_race, wts = [], {}
    for y in FOLDS:
        r, w = run_fold(om.add_context(om.build(con, f"{y}-01-01")), y, variants)
        per_race.append(r)
        wts[y] = w
        print(y, {k: round(float(r[k].mean()), 4) for k in r.columns if k not in KEY}, flush=True)
    d = pd.concat(per_race, ignore_index=True)
    d.to_csv(ROOT / "reports/blend_per_race.csv.gz", index=False, float_format="%.6f")
    cols = [c for c in d.columns if c not in KEY]
    rng = np.random.default_rng(0)

    by_fold = d.groupby("fold")[cols].mean()
    by_fold.insert(0, "races", d.groupby("fold").size())
    by_fold.loc["pooled"] = [len(d)] + [d[c].mean() for c in cols]
    allr = pd.Series(True, index=d.index)
    subsets = [("all", allr), ("QLD", d["state"] == "QLD"), ("VIC/SA", d["state"] != "QLD")]
    vs_sp = [(f"{v} blend {n} - SP {s}", f"{v}: blend {n}", f"SP {s}")
             for v in variants for n in ["logit", "gbm"] for s in ["raw", "calibrated"]]
    L = ["# SP vs model vs blend (same test races)", "",
         "- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner",
         "- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM",
         "- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using"
         " out-of-sample model predictions from a model fitted on the first 75%; never on test data",
         f"- Variants: {', '.join(variants)} (see module docstring); all share the same fold builds",
         "- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples", "",
         "## Log loss by fold", "", by_fold.T.to_markdown(floatfmt=".4f"), "",
         "## Differences vs SP, pooled", "", diff_table(d, vs_sp, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
         "## By 6-month period: blend minus SP calibrated", "",
         half_table(d, [(f"{v} {n}", f"{v}: blend {n}", "SP calibrated") for v in variants for n in ["logit", "gbm"]],
                    rng).to_markdown(index=False, floatfmt=".4f")]
    if len(variants) > 1:
        vs_base = [(f"{v} blend {n} - baseline blend {n}", f"{v}: blend {n}", f"baseline: blend {n}")
                   for v in variants[1:] for n in ["logit", "gbm"]] + \
                  [(f"{v} model {n} - baseline model {n}", f"{v}: model {n}", f"baseline: model {n}")
                   for v in variants[1:] for n in ["logit", "gbm"]]
        L += ["", "## Variants vs baseline (paired by race)", "",
              diff_table(d, vs_base, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              "## Variants vs baseline by 6-month period (blend)", "",
              half_table(d, [p for p in vs_base if "blend" in p[0]], rng).to_markdown(index=False, floatfmt=".4f")]
    wt = pd.DataFrame(wts).T
    L += ["", "## Weights (fitted on training data only)", "", wt.to_markdown(floatfmt=".3f")]
    out = ROOT / ("reports/blend_eval.md" if len(variants) == 1 else f"reports/blend_eval_{'_'.join(variants[1:])}.md")
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
