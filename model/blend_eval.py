"""SP vs model vs model + SP blend on the same test races, blend weights fitted on training data only.

    python model/blend_eval.py                    # baseline only -> reports/blend_eval.md
    python model/blend_eval.py --variants gl      # baseline + variant(s), paired comparison vs baseline
    python model/blend_eval.py --tag det          # report / per-race file suffix (keeps earlier runs' files)

Per fold (test year Y, 2023 to 2026 YTD; VIC/SA/QLD races, as validate_figure.py):
  model (no market): conditional logit, and LightGBM (per-race softmax, no SP offset), on figure + ability +
      jockey/trainer + race-day projection. No SP or market rank among the inputs.
  weights: the model is fitted on the first 75% of training dates and predicts the last 25%; on that window
      we fit  blend = softmax(a * log p_model + b * log p_SP)  and  SP calibrated = softmax(c * log p_SP).
      The model is then refitted on all training data; a, b, c are applied unchanged to the test year.
  SP raw = normalised 1 / SP.
Every variant uses the same fold builds, so comparisons with the baseline are paired race by race.
Per-race losses for all variants: reports/blend_per_race.csv.gz.
Also reported: blend and SP-calibration weights fitted per state (QLD vs VIC/SA) on the same window.

Variants (added inputs on top of the baseline):
  gl   GPS ground loss history: the horse's decayed mean extra ground and width from the rail (QLD GPS runs),
       with a missing flag
  fig2 figure v2 (ability.fit_coef_next: weights from a next-start WPR regression incl. preliminary WPR,
       missing sectionals, heavy defeats, heavy going, track class) replaces the win-logit figure in every
       figure-dependent ability input (form, trend, distance / going / surface fit, prep aptitude)
  gpsx GPS section history (QLD): relative speed early / late, top speed, trouble, stride, places gained
  comments  stewards' and video comment history: trouble / health flags and the scored video verdict tag
  prod      production inputs: baseline + comments + past ground-loss credit (h_gl, h_gl_miss, h_rail)
  posmap    prod + expected position value and width value (position_map.py)
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import ability, clogit, extra_history, figure, position_map, rating  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
NOMKT = [c for c in om.GBM_FEATS if c not in ("log_p_sp", "mkt_rank")]
LOGIT_X = om.BASE + om.JT + om.PROJ
EXTRA = {"baseline": [], "gl": ["h_gl", "h_gl_miss", "h_rail"], "fig2": [],
         "gpsx": extra_history.GX_FEATS, "comments": extra_history.CM_FEATS,
         "prod": extra_history.CM_FEATS + ["h_gl", "h_gl_miss", "h_rail"],
         "posmap": extra_history.CM_FEATS + ["h_gl", "h_gl_miss", "h_rail"] + position_map.FEATS,
         "prodmu": extra_history.CM_FEATS + ["h_gl", "h_gl_miss", "h_rail"]}
# production + model-alone improvers, all together and leave-one-out (logit only)
P2 = {"v4", "gps", "fig2", "mu"}
PARTS = {"prod2": P2, **{f"prod2-{k}": P2 - {k} for k in sorted(P2)}}
EXTRA.update({v: extra_history.CM_FEATS + ["h_gl", "h_gl_miss", "h_rail"] for v in PARTS})
MU = ["r_mu", "r_sigma"]   # prodmu: rating model (rating.py) expected WPR vs the field and its uncertainty, as logit inputs


def mu_logit_fit(d, cols):
    """Logit on cols + MU; the rating model is fitted on the same training rows d (never on the rows it scores)."""
    m = rating.RatingModel().fit(rating.add_fig_sd(d))

    def add(df):
        df2 = rating.add_fig_sd(df)
        mu = pd.Series(m.mu(df2), index=df.index)
        return df.assign(r_mu=mu - mu.groupby(df["race_id"].to_numpy()).transform("mean"), r_sigma=m.sigma(df2))
    f = om.logit_fit(add(d), cols + MU)
    return lambda df: f(add(df))


def feats_for(v, cols):
    """Inputs for variant v: baseline inputs + EXTRA[v]; fig2 swaps every figure-dependent input for its v2.
    prod2 variants: v4 = projection outputs from the v4 settle model; gps = + projected GPS pace; fig2 as above."""
    cols = cols + EXTRA[v]
    parts = PARTS.get(v, set())
    if "v4" in parts:
        cols = [c + "_v4" if c in om.PROJ else c for c in cols]
    if "gps" in parts:
        cols = cols + om.GPS_PACE
    if v == "fig2" or "fig2" in parts:
        dep = set(ability.FIG_DEPENDENT) | {f"{c}_{k}" for c in ability.FIG_DEPENDENT for k in ("rel", "gap")}
        cols = [c.replace(c.split("_rel")[0].split("_gap")[0], c.split("_rel")[0].split("_gap")[0] + "_v2", 1)
                if c in dep else c for c in cols]
    return cols
BOOT = 2000
RATING = False          # set by --rating
RATING_TABLES = {}
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
    # per-state weights (QLD vs VIC/SA), same blend window
    grp_bl, grp_te = np.where(bl["state"] == "QLD", "QLD", "VIC/SA"), np.where(te["state"] == "QLD", "QLD", "VIC/SA")
    c_s = {}
    for g_ in ["QLD", "VIC/SA"]:
        b_ = _race(bl[grp_bl == g_].copy())
        c_s[g_] = clogit.fit(b_[["log_p_sp"]].to_numpy(float), b_["race"].to_numpy(), b_["won"].to_numpy())[0]
        weights[f"SP calibration c, {g_}"] = c_s[g_]
    c_vec = np.vectorize(c_s.get)(grp_te)
    out["SP calibrated (per state)"] = race_ll(om._softmax(c_vec * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
    for v in variants:
        fits = {"logit": lambda d, v=v: om.logit_fit(d, feats_for(v, LOGIT_X)),
                "gbm": lambda d, v=v: om.gbm_fit(d, feats=feats_for(v, NOMKT), market=False)[0]}
        if v == "prodmu":
            fits = {"logit": lambda d: mu_logit_fit(d, feats_for("prodmu", LOGIT_X))}
        if v in PARTS:
            fits = {"logit": (lambda d, v=v: mu_logit_fit(d, feats_for(v, LOGIT_X))) if "mu" in PARTS[v]
                    else (lambda d, v=v: om.logit_fit(d, feats_for(v, LOGIT_X)))}
        if v == "baseline" and RATING:
            def fit_rating(d, y=y):
                f, m = rating.fit(d)
                RATING_TABLES[y] = (m.table(), m.gamma, m.scale)   # last call = fit on all training rows
                return f
            fits["rating"] = fit_rating
        for name, fit in fits.items():
            p_bl = np.clip(fit(inner)(bl), 1e-12, 1)
            X = np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)]
            a, b = clogit.fit(X, bl["race"].to_numpy(), bl["won"].to_numpy())
            p_te = np.clip(fit(tr)(te), 1e-12, 1)
            out[f"{v}: model {name}"] = race_ll(p_te, te)
            out[f"{v}: blend {name}"] = race_ll(
                om._softmax(a * np.log(p_te) + b * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
            weights[f"{v} {name} a"], weights[f"{v} {name} b"] = a, b
            ab = {}
            for g_ in ["QLD", "VIC/SA"]:
                m_ = grp_bl == g_
                b_ = _race(bl[m_].copy())
                ab[g_] = clogit.fit(np.c_[np.log(p_bl[m_]), b_["log_p_sp"].to_numpy(float)], b_["race"].to_numpy(),
                                    b_["won"].to_numpy())
                weights[f"{v} {name} a, {g_}"], weights[f"{v} {name} b, {g_}"] = ab[g_]
            a_vec = np.where(grp_te == "QLD", ab["QLD"][0], ab["VIC/SA"][0])
            b_vec = np.where(grp_te == "QLD", ab["QLD"][1], ab["VIC/SA"][1])
            out[f"{v}: blend {name} (per state)"] = race_ll(
                om._softmax(a_vec * np.log(p_te) + b_vec * te["log_p_sp"].to_numpy(), te["race"].to_numpy()), te)
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
    ap.add_argument("--tag", default=None, help="suffix for the report and per-race file (default: variants)")
    ap.add_argument("--rating", action="store_true", help="add the explicit rating model (rating.py) to the baseline")
    args = ap.parse_args()
    global RATING
    RATING = args.rating
    variants = ["baseline"] + args.variants
    om.EXTRA_PROJ = any(v in PARTS for v in variants)
    tag = args.tag or "_".join(variants[1:])
    suffix = f"_{tag}" if tag else ""
    con = duckdb.connect(str(figure.DB), read_only=True)
    per_race, wts = [], {}
    for y in FOLDS:
        r, w = run_fold(om.add_context(om.build(con, f"{y}-01-01")), y, variants)
        per_race.append(r)
        wts[y] = w
        print(y, {k: round(float(r[k].mean()), 4) for k in r.columns if k not in KEY}, flush=True)
    d = pd.concat(per_race, ignore_index=True)
    d.to_csv(ROOT / f"reports/blend_per_race{suffix}.csv.gz", index=False, float_format="%.6f")
    cols = [c for c in d.columns if c not in KEY]
    rng = np.random.default_rng(0)

    by_fold = d.groupby("fold")[cols].mean()
    by_fold.insert(0, "races", d.groupby("fold").size())
    by_fold.loc["pooled"] = [len(d)] + [d[c].mean() for c in cols]
    allr = pd.Series(True, index=d.index)
    subsets = [("all", allr), ("QLD", d["state"] == "QLD"), ("VIC/SA", d["state"] != "QLD")]
    names = {v: [n for n in ["logit", "gbm", "rating"] if f"{v}: blend {n}" in d] for v in variants}
    vs_sp = [(f"{v} blend {n} - SP {s}", f"{v}: blend {n}", f"SP {s}")
             for v in variants for n in names[v] for s in ["raw", "calibrated"]]
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
         half_table(d, [(f"{v} {n}", f"{v}: blend {n}", "SP calibrated") for v in variants for n in names[v]],
                    rng).to_markdown(index=False, floatfmt=".4f")]
    ps = [(f"{v} blend {n} (per state) - SP calibrated (per state)", f"{v}: blend {n} (per state)", "SP calibrated (per state)")
          for v in variants for n in names[v]] + \
         [(f"{v} blend {n} (per state) - {v} blend {n} (pooled weights)", f"{v}: blend {n} (per state)", f"{v}: blend {n}")
          for v in variants for n in names[v]] + \
         [("SP calibrated (per state) - SP calibrated (pooled)", "SP calibrated (per state)", "SP calibrated")]
    L += ["", "## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)", "",
          diff_table(d, ps, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
          "## Per-state blend minus per-state calibrated SP, by 6-month period", "",
          half_table(d, ps[:sum(len(names[v]) for v in variants)], rng).to_markdown(index=False, floatfmt=".4f")]
    if "posmap" in variants and "prod" in variants:
        pp = [(f"posmap blend {n} - prod blend {n}", f"posmap: blend {n}", f"prod: blend {n}") for n in ["logit", "gbm"]] + \
             [(f"posmap model {n} - prod model {n}", f"posmap: model {n}", f"prod: model {n}") for n in ["logit", "gbm"]]
        L += ["", "## Position map vs production inputs (paired by race)", "",
              diff_table(d, pp, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              half_table(d, pp[:2], rng).to_markdown(index=False, floatfmt=".4f")]
    if "prod2" in variants and "prod" in variants:
        p2 = [("prod2 model logit - prod model logit", "prod2: model logit", "prod: model logit"),
              ("prod2 blend logit - prod blend logit", "prod2: blend logit", "prod: blend logit")]
        for k in sorted(P2):
            if f"prod2-{k}" in variants:
                p2 += [(f"prod2 model logit - prod2 without {k}", "prod2: model logit", f"prod2-{k}: model logit"),
                       (f"prod2 blend logit - prod2 without {k}", "prod2: blend logit", f"prod2-{k}: blend logit")]
        L += ["", "## prod2 (production + v4 settle + GPS pace + figure v2 + rating mu) vs production, and what each"
              " part adds with the others present (paired by race)", "",
              diff_table(d, p2, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              half_table(d, p2[:2], rng).to_markdown(index=False, floatfmt=".4f")]
    if "prodmu" in variants and "prod" in variants:
        pm = [("prodmu blend logit - prod blend logit", "prodmu: blend logit", "prod: blend logit"),
              ("prodmu model logit - prod model logit", "prodmu: model logit", "prod: model logit")]
        L += ["", "## Rating mu as a logit input vs production inputs (paired by race)", "",
              diff_table(d, pm, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              half_table(d, pm[:1], rng).to_markdown(index=False, floatfmt=".4f")]
    if len(variants) > 1:
        vs_base = [(f"{v} blend {n} - baseline blend {n}", f"{v}: blend {n}", f"baseline: blend {n}")
                   for v in variants[1:] for n in names[v] if n != "rating"] + \
                  [(f"{v} model {n} - baseline model {n}", f"{v}: model {n}", f"baseline: model {n}")
                   for v in variants[1:] for n in names[v] if n != "rating"]
        L += ["", "## Variants vs baseline (paired by race)", "",
              diff_table(d, vs_base, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              "## Variants vs baseline by 6-month period (blend)", "",
              half_table(d, [p for p in vs_base if "blend" in p[0]], rng).to_markdown(index=False, floatfmt=".4f")]
    if RATING_TABLES:
        rv = [("rating blend - baseline logit blend", "baseline: blend rating", "baseline: blend logit"),
              ("rating blend - baseline gbm blend", "baseline: blend rating", "baseline: blend gbm"),
              ("rating model - baseline logit model", "baseline: model rating", "baseline: model logit")]
        tab = pd.DataFrame({y: t[0] for y, t in RATING_TABLES.items()})
        L += ["", "## Rating model vs the baseline models (paired by race)", "",
              diff_table(d, rv, rng, subsets).to_markdown(index=False, floatfmt=".4f"), "",
              "## Rating model: bonus / penalty per unit of each input (WPR points), fit on each fold's training rows", "",
              tab.to_markdown(floatfmt=".3f"), "",
              "Uncertainty (sigma) model, WPR points: " + "; ".join(
                  f"{y}: scale {t[2]:.2f}, intercept {t[1][0]:.2f}" for y, t in RATING_TABLES.items())]
    if "fig2" in variants:
        L += ["", "## Figure v2 weights by training cut-off (WPR points per unit)", "",
              pd.DataFrame(om.FIG2_COEF).to_markdown(floatfmt=".3f")]
    wt = pd.DataFrame(wts).T
    L += ["", "## Weights (fitted on training data only)", "", wt.to_markdown(floatfmt=".3f")]
    out = ROOT / f"reports/blend_eval{suffix}.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
