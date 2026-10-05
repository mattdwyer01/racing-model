"""WPR projection v2: predict the WPR each horse will RUN (not just who wins), with a per-horse spread.

    python -W ignore model/wpr_model.py        # walk-forward 2023 to 2026 -> reports/wpr_model.md, data/interim/wpr_model_oos.parquet

Per fold Y (fit on races before Y, score Y; VIC/SA/QLD as the baseline):
  inputs   the production logit's inputs (production.COLS: ability / form / race-day projection / jockey-trainer /
           comments / ground loss / leader value / wet form), the rating model's expected WPR (absolute and vs the
           field) and race context (distance, going, field size, state, field mean / max prior WPR and rating mu)
  mean     LightGBM regression on the run's WPR (y_wpr), runners with a WPR only, front-weighted (front_weights)
  spread   LightGBM on |residual| from a date holdout inside the training window (later 25%), x sqrt(pi / 2) = sd
  win %    Monte Carlo: WPR ~ Normal(mean, sd) per runner, P(highest), 4,000 draws per race
Compared on the test year with the production Racing Model (same fold, same rows): WPR error (MAE / RMSE) against the
prior-average baseline (h_wpr), top pick win %, log loss (simulated chances and with one fitted scale on the mean).
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure, production, rating  # noqa: E402
from model import offset_model as om  # noqa: E402

OUT = ROOT / "reports/wpr_model.md"
OOS = ROOT / "data/interim/wpr_model_oos.parquet"
FOLDS = [2023, 2024, 2025, 2026]
CTX = ["dist", "going_num", "field_n", "is_qld", "is_sa", "wet", "f_mean_hwpr", "f_max_hwpr", "f_mean_mu", "f_max_mu",
       "mu_abs"]
PARAMS = dict(objective="l2", learning_rate=0.05, num_leaves=63, min_data_in_leaf=200, feature_fraction=0.8,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, deterministic=True, force_row_wise=True,
              seed=7)
rng = np.random.default_rng(3)
SD_SCALE = 1.12   # walk-forward test: 60% of runs within +/- 1 raw sd; x1.12 brings that to ~68% (normal)


def front_weights(df):
    """Training weights on runners near the front (6 Oct 2026, tools/proj_rebuild_test.py): x4 within 5 of the race's
    best WPR, x2 within 10. Walk-forward: +0.6 winners per 100 races inside the 2.5-runner line, MAE 6.48 vs 6.59."""
    gap = df.groupby("race_id")["y_wpr"].transform("max") - df["y_wpr"]
    return np.where(gap <= 5, 4.0, np.where(gap <= 10, 2.0, 1.0))


def add_mu_abs(rm, df):
    f2 = rating.add_fig_sd(df)
    mu = pd.Series(rm.mu(f2), index=df.index)
    g = df["race_id"].to_numpy()
    df = df.assign(mu_abs=mu, r_mu=mu - mu.groupby(g).transform("mean"), r_sigma=rm.sigma(f2))
    df["f_mean_mu"] = mu.groupby(g).transform("mean")
    df["f_max_mu"] = mu.groupby(g).transform("max")
    hw = df["h_wpr"].where(df["h_none"] == 0)
    df["f_mean_hwpr"] = hw.groupby(g).transform("mean")
    df["f_max_hwpr"] = hw.groupby(g).transform("max")
    if "going_num" not in df:
        df["going_num"] = np.nan
    return df


def sim_win(mean, sd, race, draws=4000):
    p = np.zeros(len(mean))
    order = np.argsort(race, kind="stable")
    r = race[order]
    starts = np.r_[0, np.flatnonzero(np.diff(r)) + 1, len(r)]
    m, s = mean[order], sd[order]
    out = np.zeros(len(mean))
    for a, b in zip(starts[:-1], starts[1:]):
        z = m[a:b, None] + s[a:b, None] * rng.standard_normal((b - a, draws))
        w = np.bincount(z.argmax(0), minlength=b - a) / draws
        out[a:b] = (w * draws + 0.5) / (draws + 0.5 * (b - a))     # no exact zeros
    p[order] = out
    return p


def fold(con, y):
    e = om.add_context(om.build(con, f"{y}-01-01"))
    cols = [c for c in production.COLS + production.MU if c in e or c in ("r_mu", "r_sigma")]
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    rm = production.fit_mu(tr)
    tr, te = add_mu_abs(rm, tr), add_mu_abs(rm, te)
    feats = [c for c in dict.fromkeys(cols + CTX) if c in tr]
    # Racing Model (production logit), same fold
    beta = production._fit_raw(tr, [c for c in cols if c in tr])
    p_rm = om._softmax(production.utility(te, beta), te["race"].to_numpy())
    # WPR mean model
    lab = tr["y_wpr"].notna()
    cut = tr["race_date"].quantile(0.75)
    inner = lab & (tr["race_date"] <= cut)
    hold = lab & (tr["race_date"] > cut)
    w = pd.Series(front_weights(tr[lab]), index=tr.index[lab])
    m1 = lgb.train(PARAMS, lgb.Dataset(tr.loc[inner, feats].astype(float), tr.loc[inner, "y_wpr"], weight=w[inner[lab]]), 600)
    res = (tr.loc[hold, "y_wpr"] - m1.predict(tr.loc[hold, feats].astype(float))).abs()
    sp = dict(PARAMS, objective="l1")
    ms = lgb.train(sp, lgb.Dataset(tr.loc[hold, feats].astype(float), res), 300)
    m = lgb.train(PARAMS, lgb.Dataset(tr.loc[lab, feats].astype(float), tr.loc[lab, "y_wpr"], weight=w), 600)
    te["wpr_mean"] = m.predict(te[feats].astype(float))
    te["wpr_sd"] = np.clip(ms.predict(te[feats].astype(float)) * np.sqrt(np.pi / 2), 2.0, 25.0)
    te["p_sim"] = sim_win(te["wpr_mean"].to_numpy(), te["wpr_sd"].to_numpy(), te["race"].to_numpy())
    te["p_rm"] = p_rm
    imp = pd.Series(m.feature_importance("gain"), index=feats).sort_values(ascending=False)
    print(y, "done", len(te), flush=True)
    keep = ["run_id", "race_id", "race_date", "state", "won", "sp", "y_wpr", "h_wpr", "h_none", "mu_abs", "wpr_mean",
            "wpr_sd", "p_sim", "p_rm"]
    return te[[c for c in keep if c in te]].assign(fold=y), imp


# Proj recipe (6 Oct 2026, user: age / sex / weight out; the race-day projection must add winners): a front-weighted form
# model without the race-day projection and age / sex / weight groups, plus an explicit race-day adjustment
# b x (proj_adj, lv_x, sx_wet) vs the race mean, b fitted on the later 25% of the training window against the form
# model's within-race residual. tools/proj_rd_test.py (38,310 races walk-forward): +0.64 winners per 100 races inside the
# 3 line vs form alone (+0.45 to +0.82), +0.56 vs the old recipe; b proj_adj 0.48-0.63, lv_x 0.08-0.38, sx_wet -0.14-0.45.
RD_TERMS = ["proj_adj", "lv_x", "sx_wet"]
DROP = production.GROUPS["race-day projection"] + production.GROUPS["age / sex / weight"]


def _demean(df, cols):
    x = df.reindex(columns=cols).astype(float).fillna(0.0)
    return x - x.groupby(df["race_id"].to_numpy()).transform("mean")


def fit_live(e, rm, train_end, years=3):
    """Live fit for the dashboard: form model, race-day coefficients and spread model on the last `years` of training
    rows (e = the production training frame, om.add_context(eval_set(raw)); rm = production rating model)."""
    end = pd.Timestamp(train_end)
    tr = production._race(e[(e["race_date"] < end) & (e["race_date"] >= end - pd.DateOffset(years=years))].copy())
    tr = add_mu_abs(rm, tr)
    feats = [c for c in dict.fromkeys(production.COLS + production.MU + CTX) if c in tr and c not in DROP]
    lab = tr["y_wpr"].notna()
    cut = tr["race_date"].quantile(0.75)
    inner, hold = lab & (tr["race_date"] <= cut), lab & (tr["race_date"] > cut)
    w = pd.Series(front_weights(tr[lab]), index=tr.index[lab])
    m1 = lgb.train(PARAMS, lgb.Dataset(tr.loc[inner, feats].astype(float), tr.loc[inner, "y_wpr"], weight=w[inner[lab]]), 600)
    h = tr[hold].copy()
    h["res"] = h["y_wpr"] - m1.predict(h[feats].astype(float))
    ms = lgb.train(dict(PARAMS, objective="l1"), lgb.Dataset(h[feats].astype(float), h["res"].abs()), 300)
    terms = [t for t in RD_TERMS if t in tr]
    r = (h["res"] - h.groupby("race_id")["res"].transform("mean")).to_numpy()
    sw = np.sqrt(front_weights(h))
    coef = np.linalg.lstsq(_demean(h, terms).to_numpy() * sw[:, None], r * sw, rcond=None)[0]
    m = lgb.train(PARAMS, lgb.Dataset(tr.loc[lab, feats].astype(float), tr.loc[lab, "y_wpr"], weight=w), 600)
    print("wpr_model race-day coefficients", dict(zip(terms, np.round(coef, 3))), flush=True)
    return {"mean": m, "sd": ms, "feats": feats, "rd": dict(zip(terms, coef))}


def predict(wm, rows, rm):
    """Projected WPR (form + race-day adjustment), its spread (sd) and the race-day part, for card rows (production
    features, as race_card.prep builds them)."""
    x = add_mu_abs(rm, rows.copy())
    for c in wm["feats"]:
        if c not in x:
            x[c] = np.nan
    X = x[wm["feats"]].astype(float)
    sd = np.clip(wm["sd"].predict(X) * np.sqrt(np.pi / 2) * SD_SCALE, 2.0, 25.0)
    rd = wm.get("rd") or {}
    adj = (_demean(x, list(rd)) * pd.Series(rd)).sum(1).to_numpy() if rd else np.zeros(len(x))
    return pd.DataFrame({"run_id": x["run_id"].to_numpy(), "wpr_proj": wm["mean"].predict(X) + adj, "wpr_sd": sd,
                         "wpr_rd": adj})


def ll(p, d):
    return -np.log(np.clip(p[d["won"] == 1], 1e-12, 1))


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    parts, imps = [], []
    for y in FOLDS:
        t, imp = fold(con, y)
        parts.append(t)
        imps.append(imp.rename(y))
    d = pd.concat(parts, ignore_index=True)
    d.to_parquet(OOS)
    report(d, pd.concat(imps, axis=1))


def report(d, imps=None):
    d = d.sort_values(["race_id", "run_id"]).reset_index(drop=True)
    w = d[d["y_wpr"].notna()]
    hw = w[w["h_none"] == 0]
    err = lambda a, b: (np.abs(a - b).mean(), np.sqrt(((a - b) ** 2).mean()))  # noqa: E731
    # fitted-scale win chance from the WPR mean alone (2-fold by fold year parity)
    d["mr"] = d["wpr_mean"] - d.groupby("race_id")["wpr_mean"].transform("mean")
    d["race"] = pd.factorize(d["race_id"])[0]
    p_fit = pd.Series(np.nan, index=d.index)
    for k in (0, 1):
        trm = (d["fold"] % 2) != k
        b = clogit.fit(d.loc[trm, ["mr"]].to_numpy(float), pd.factorize(d.loc[trm, "race_id"])[0], d.loc[trm, "won"].to_numpy())
        tem = ~trm
        p_fit[tem] = clogit.probs(d.loc[tem, ["mr"]].to_numpy(float), pd.factorize(d.loc[tem, "race_id"])[0], b)
    d["p_fit"] = p_fit
    rows = []
    for name, col in (("Racing Model (win logit)", "p_rm"), ("WPR model, simulated", "p_sim"), ("WPR model, fitted scale", "p_fit")):
        top = d.loc[d.groupby("race_id")[col].idxmax()]
        rows.append({"model": name, "top pick win %": round(100 * top["won"].mean(), 2),
                     "log loss": round(ll(d[col].to_numpy(), d).mean(), 4)})
    yrs = d.groupby("fold").apply(lambda g: pd.Series({
        "races": g["race_id"].nunique(),
        "RM top %": 100 * g.loc[g.groupby("race_id")["p_rm"].idxmax(), "won"].mean(),
        "WPR top %": 100 * g.loc[g.groupby("race_id")["wpr_mean"].idxmax(), "won"].mean(),
        "RM ll": ll(g["p_rm"].to_numpy(), g).mean(), "WPR sim ll": ll(g["p_sim"].to_numpy(), g).mean()})).round(3)
    a1, b1 = err(hw["wpr_mean"], hw["y_wpr"])
    a2, b2 = err(hw["h_wpr"], hw["y_wpr"])
    a3, b3 = err(hw["mu_abs"], hw["y_wpr"])
    cov = ((w["y_wpr"] - w["wpr_mean"]).abs() <= w["wpr_sd"]).mean()
    L = ["# WPR projection v2: the WPR each horse runs (walk-forward 2023 to 2026, VIC/SA/QLD)", "",
         f"- {d['race_id'].nunique():,} races, {len(w):,} runs with a WPR ({len(hw):,} with prior form).", "",
         "## WPR forecast error (runners with prior form)", "",
         "| forecast | MAE | RMSE |", "|---|---|---|",
         f"| WPR model | {a1:.2f} | {b1:.2f} |", f"| rating model expected WPR (mu) | {a3:.2f} | {b3:.2f} |",
         f"| prior average WPR (h_wpr) | {a2:.2f} | {b2:.2f} |", "",
         f"- Spread: actual within +/- 1 predicted sd for {100 * cov:.0f}% of runs (68% if calibrated); median sd"
         f" {w['wpr_sd'].median():.1f} WPR.", "",
         "## Picking winners", "", pd.DataFrame(rows).to_markdown(index=False), "", yrs.to_markdown(), ""]
    if imps is not None:
        L += ["## Top inputs (gain, mean over folds)", "",
              (imps.mean(1).sort_values(ascending=False).head(15) / imps.mean(1).sum()).round(3).to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--report-only" in sys.argv:
        report(pd.read_parquet(OOS))
    else:
        main()
