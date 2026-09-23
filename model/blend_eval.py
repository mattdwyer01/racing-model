"""SP vs model vs model + SP blend on the same test races, blend weights fitted on training data only.

    python model/blend_eval.py      # -> reports/blend_eval.md

Per fold (test year Y, 2023 to 2026 YTD; VIC/SA/QLD races, as validate_figure.py):
  model (no market): conditional logit, and LightGBM (per-race softmax, no SP offset), on figure + ability +
      jockey/trainer + race-day projection. No SP or market rank among the inputs.
  weights: the model is fitted on the first 75% of training dates and predicts the last 25%; on that window
      we fit  blend = softmax(a * log p_model + b * log p_SP)  and  SP calibrated = softmax(c * log p_SP).
      The model is then refitted on all training data; a, b, c are applied unchanged to the test year.
  SP raw = normalised 1 / SP.
Report: log loss by fold and pooled; blend minus SP (raw and calibrated) with a 95% range from 2,000 race
bootstrap resamples; the same by 6-month period.
"""
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
BOOT = 2000


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def _softmax_scores(score, race):
    return om._softmax(score, race)


def model_fns():
    return {"logit": lambda tr: om.logit_fit(tr, LOGIT_X),
            "gbm": lambda tr: om.gbm_fit(tr, feats=NOMKT, market=False)[0]}


def run_fold(e, y):
    tr = _race(e[e.race_date < f"{y}-01-01"].copy())
    te = _race(e[e.race_date.dt.year == y].copy())
    assert tr.race_date.max() < te.race_date.min()
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())
    out = {"SP raw": race_ll(te["p_sp"].to_numpy(), te)}
    c = clogit.fit(bl[["log_p_sp"]].to_numpy(float), bl["race"].to_numpy(), bl["won"].to_numpy())[0]
    out["SP calibrated"] = race_ll(_softmax_scores(c * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
    weights = {"SP calibrated": {"c": c}}
    for name, fit in model_fns().items():
        p_bl = np.clip(fit(inner)(bl), 1e-12, 1)
        X = np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)]
        a, b = clogit.fit(X, bl["race"].to_numpy(), bl["won"].to_numpy())
        p_te = np.clip(fit(tr)(te), 1e-12, 1)
        out[f"model: {name}"] = race_ll(p_te, te)
        blend = _softmax_scores(a * np.log(p_te) + b * te["log_p_sp"].to_numpy(), te["race"].to_numpy())
        out[f"blend: {name} + SP"] = race_ll(blend, te)
        weights[name] = {"a (model)": a, "b (SP)": b}
    winners = te[te.won == 1][["race_id", "race_date", "state"]].reset_index(drop=True)
    return pd.concat([winners, pd.DataFrame(out)], axis=1), weights, {"blend window": f"{bl.race_date.min():%d %b %Y} to {bl.race_date.max():%d %b %Y}"}


def boot_ci(x, rng):
    idx = rng.integers(0, len(x), (BOOT, len(x)))
    m = x[idx].mean(1)
    return np.percentile(m, 2.5), np.percentile(m, 97.5)


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    per_race, wts, info = [], {}, {}
    for y in FOLDS:
        e = om.add_context(om.build(con, f"{y}-01-01"))
        r, w, i = run_fold(e, y)
        per_race.append(r.assign(fold=y))
        wts[y], info[y] = w, i
        print(y, {k: round(float(r[k].mean()), 4) for k in r.columns if k not in ("race_id", "race_date", "state")},
              flush=True)
    d = pd.concat(per_race, ignore_index=True)
    models = [c for c in d.columns if c not in ("race_id", "race_date", "state", "fold")]
    rng = np.random.default_rng(0)

    by_fold = d.groupby("fold")[models].mean()
    by_fold.insert(0, "races", d.groupby("fold").size())
    by_fold.loc["pooled"] = [len(d)] + [d[m].mean() for m in models]

    rows = []
    for name in ["logit", "gbm"]:
        for base in ["SP raw", "SP calibrated"]:
            for lab, col in [(f"blend: {name} + SP", f"blend: {name} + SP"), (f"model: {name}", f"model: {name}")]:
                x = (d[col] - d[base]).to_numpy()
                lo, hi = boot_ci(x, rng)
                rows.append({"comparison": f"{lab} minus {base}", "mean": x.mean(), "95% lo": lo, "95% hi": hi,
                             "share of races better": (x < 0).mean()})
    ci = pd.DataFrame(rows)

    d["half"] = d["race_date"].dt.year.astype(str) + np.where(d["race_date"].dt.month <= 6, " H1", " H2")
    half_rows = []
    for h, g in d.groupby("half"):
        row = {"period": h, "races": len(g), "SP raw": g["SP raw"].mean(), "SP calibrated": g["SP calibrated"].mean()}
        for name in ["logit", "gbm"]:
            for base, tag in [("SP raw", "raw"), ("SP calibrated", "cal")]:
                x = (g[f"blend: {name} + SP"] - g[base]).to_numpy()
                lo, hi = boot_ci(x, rng)
                row[f"{name} blend - SP {tag}"] = x.mean()
                row[f"{name} vs {tag} 95%"] = f"{lo:+.4f} to {hi:+.4f}"
        half_rows.append(row)
    halves = pd.DataFrame(half_rows)

    wrows = [{"fold": y, "blend window": info[y]["blend window"], "SP calibration c": wts[y]["SP calibrated"]["c"],
              "logit a": wts[y]["logit"]["a (model)"], "logit b": wts[y]["logit"]["b (SP)"],
              "gbm a": wts[y]["gbm"]["a (model)"], "gbm b": wts[y]["gbm"]["b (SP)"]} for y in FOLDS]
    L = ["# SP vs model vs blend (same test races)", "",
         "- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner",
         "- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM",
         "- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using"
         " out-of-sample model predictions from a model fitted on the first 75%; never on test data",
         "- Negative differences = blend (or model) better than SP. 95% ranges: 2,000 race bootstrap resamples", "",
         "## Log loss by fold", "", by_fold.T.to_markdown(floatfmt=".4f"), "",
         "## Differences vs SP, pooled over all test races", "", ci.to_markdown(index=False, floatfmt=".4f"), "",
         "## By 6-month period (blend minus SP, with 95% range)", "", halves.to_markdown(index=False, floatfmt=".4f"), "",
         "## Blend weights (fitted on training data only)", "", pd.DataFrame(wrows).to_markdown(index=False, floatfmt=".3f")]
    out = ROOT / "reports/blend_eval.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
