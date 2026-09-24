"""Production model: conditional logit on figure + ability + jockey/trainer + race-day projection + run comments,
plus past ground-loss credit and the rating model's expected WPR (r_mu, r_sigma; model alone -0.0033, blend level), blended with the market, and expressed in WPR points so every horse's rating can be read as
ability + bonuses / penalties.

    python model/production.py --train-end 2026-01-01      # train, save data/models/logit_<date>.pkl,
                                                            # write reports/logit_wpr_table.md

Training (all on races before train_end):
  logit weights  conditional logit on COLS (standardised inside the fit)
  blend weights  logit fitted on the first 75% of training dates predicts the last 25%; there we fit
                 blend = softmax(a * log p_model + b * log p_market) and calibrated market = softmax(c * log p_market)
WPR points: the logit's utility is sum_k beta_k x_k. One WPR point of ability = +1 on every ability-level input
(WPR_LEVEL: decayed WPR, decayed figure, last / best figures) at once, worth U = sum of their betas. So each
input's weight in WPR points is beta_k / U, and a horse's contribution vs the field is beta_k (x_k - field mean) / U.
"""
import argparse
import pickle
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, extra_history, figure, position_map, rating  # noqa: E402
from model import offset_model as om  # noqa: E402

GL = ["h_gl", "h_gl_miss", "h_rail"]     # past extra ground / width credit (QLD GPS); kept by decision, not for blend gain
COLS = list(dict.fromkeys(om.BASE + om.JT + om.PROJ + extra_history.CM_FEATS + GL))
MU = ["r_mu", "r_sigma"]   # rating model (rating.py): expected WPR vs the field and its uncertainty (adopted Sep 2026)
WPR_LEVEL = ["h_wpr", "dm", "fig_last", "best3", "best10", "mean3", "r_mu"]
GROUPS = {
    "ability": WPR_LEVEL + ["r_sigma", "h_class", "log_n", "h_none", "h_last_wpr"],
    "form shape": ["trend", "h_s_early", "h_s_l600", "h_s_early_miss", "h_settle", "h_shape", "h_pace",
                   "h_settle_miss", "h_wt_rel"],
    "distance / going": ["dist_ratio", "dist_abs", "dist_fit", "going_fit", "surface_fit"],
    "prep": ["fu", "su", "up3", "fu_apt", "su_apt", "log_days", "first_up", "trial_since", "trial_pos",
             "trial_marg", "trial_pos_debut", "trial_marg_debut"],
    "race-day projection": ["barrier_pct", "proj_settle", "proj_settle_rank", "proj_shape", "proj_pace", "proj_gl",
                            "proj_adj", "tdx_settle", "tdx_perf", "early_rank2", "wide_x_slow", "nb_diff_in",
                            "nb_diff_out"],
    "track bias": ["tbx_settle_long", "tbx_settle_recent", "tbx_bar_long", "tbx_bar_recent", "bias_adj"],
    "jockey / trainer": ["j_ae", "j_sr", "j90_ae", "t_ae", "t_sr", "c_ae", "tfu_ae", "h_ae", "j_change", "j_upgrade"],
    "comments": extra_history.CM_FEATS,
    "ground loss (past runs)": GL,
    "position value": position_map.FEATS,
    "age / sex / weight": ["age2", "age3", "age7", "female", "wt_rel_today"],
}
MODELS = ROOT / "data/models"
# Training scope: VIC/SA/QLD + these states (Sep 2026, blend_eval_nswwa_vs_ctl.md: model alone -0.0011, blend
# -0.0004 on VIC/SA/QLD races). Race cards still cover VIC/SA/QLD only (figure's core_scope).
TRAIN_EXTRA_STATES = ["NSW", "WA"]


def use_training_scope():
    """Put TRAIN_EXTRA_STATES in scope for this process (an explicit RACING_EXTRA_STATES, even empty, wins).
    Call before any feature build; research scripts that import this module keep the default scope."""
    import os
    if "RACING_EXTRA_STATES" not in os.environ:
        figure.EXTRA_STATES = list(TRAIN_EXTRA_STATES)
    return figure.EXTRA_STATES


def group_of(c):
    for g, cs in GROUPS.items():
        if c in cs:
            return g
    return "other"


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def _filled(df, cols):
    """Inputs with gaps (e.g. no weight for races taken from the dashboard runners file) = field average, else 0."""
    X = df[cols].astype(float)
    return X.fillna(X.groupby(df["race_id"].to_numpy()).transform("mean")).fillna(0.0)


def _fit_raw(tr, cols):
    """Conditional logit; returns raw-unit betas (utility = X @ beta, up to a per-race constant)."""
    X = _filled(tr, cols)
    mu, sd = X.mean(), X.std().replace(0, 1)
    b = clogit.fit(((X - mu) / sd).to_numpy(float), tr["race"].to_numpy(), tr["won"].to_numpy())
    return pd.Series(b / sd.to_numpy(), index=cols)


def add_mu(rm, df):
    """r_mu (rating model's expected WPR minus the field mean) and r_sigma for every row of df."""
    f2 = rating.add_fig_sd(df)
    mu = pd.Series(rm.mu(f2), index=df.index)
    return df.assign(r_mu=mu - mu.groupby(df["race_id"].to_numpy()).transform("mean"), r_sigma=rm.sigma(f2))


def fit_mu(rows):
    return rating.RatingModel().fit(rating.add_fig_sd(rows))


def utility(df, beta):
    return _filled(df, list(beta.index)).to_numpy(float) @ beta.to_numpy()


def train(con, train_end, e=None):
    e = e if e is not None else om.add_context(om.build(con, train_end))
    tr = _race(e[e.race_date < train_end].copy())
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())
    rm_in = fit_mu(inner)
    inner, bl = add_mu(rm_in, inner), add_mu(rm_in, bl)
    b_in = _fit_raw(inner, COLS + MU)
    p_bl = np.clip(om._softmax(utility(bl, b_in), bl["race"].to_numpy()), 1e-12, 1)
    a, b = clogit.fit(np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)], bl["race"].to_numpy(), bl["won"].to_numpy())
    c = clogit.fit(bl[["log_p_sp"]].to_numpy(float), bl["race"].to_numpy(), bl["won"].to_numpy())[0]
    rm = fit_mu(tr)
    tr = add_mu(rm, tr)
    beta = _fit_raw(tr, COLS + MU)
    unit = beta[WPR_LEVEL].sum()
    m = {"train_end": str(train_end)[:10], "beta": beta, "wpr_unit": unit, "a": a, "b": b, "c": c, "rating": rm,
         "blend_window": f"{bl.race_date.min():%d %b %Y} to {bl.race_date.max():%d %b %Y}"}
    return m, e


def wpr_table(m):
    t = pd.DataFrame({"beta": m["beta"], "WPR points per unit": m["beta"] / m["wpr_unit"]})
    t["group"] = [group_of(c) for c in t.index]
    return t.sort_values(["group", "WPR points per unit"])


def card(m, race_df, market="log_p_sp"):
    """Per-horse breakdown for one or more races: WPR-point contributions vs the field, by group, and prices."""
    df = _race(race_df.sort_values(["race_id", "barrier_pct"]).copy())
    if "rating" in m and "r_mu" in m["beta"].index:
        df = add_mu(m["rating"], df)
    X = df[m["beta"].index].astype(float)
    grp = df["race_id"].to_numpy()
    X = X.fillna(X.groupby(grp).transform("mean")).fillna(0.0)     # upcoming fields: missing weight etc. = field avg
    Xd = X - X.groupby(grp).transform("mean")
    contrib = Xd * m["beta"] / m["wpr_unit"]
    out = pd.DataFrame(index=df.index)
    for g in list(GROUPS) + ["other"]:
        cols = [c for c in contrib.columns if group_of(c) == g]
        if cols:
            out[g] = contrib[cols].sum(1)
    out["rating vs field"] = contrib.sum(1)
    race = df["race"].to_numpy()
    p_model = om._softmax(X.to_numpy() @ m["beta"].to_numpy(), race)
    out["model %"] = 100 * p_model
    out["model $"] = 1 / p_model
    if market in df:
        has = df[market].notna().groupby(grp).transform("all").to_numpy()     # blend races with a full market
        mk = df[market].fillna(0).to_numpy(float)
        p_mkt = np.where(has, om._softmax(m["c"] * mk, race), np.nan)
        p_blend = np.where(has, om._softmax(m["a"] * np.log(np.clip(p_model, 1e-12, 1)) + m["b"] * mk, race), np.nan)
        out["market $ (calibrated)"] = 1 / p_mkt
        out["blend %"] = 100 * p_blend
        out["blend $"] = 1 / p_blend
        out["SP"] = df["sp"]
        out["edge vs SP"] = p_blend * df["sp"] - 1
    return pd.concat([df[["race_id", "run_id", "horse_id"]], out], axis=1)


def save(m):
    MODELS.mkdir(parents=True, exist_ok=True)
    p = MODELS / f"logit_{m['train_end']}.pkl"
    with p.open("wb") as f:
        pickle.dump(m, f)
    return p


def load(train_end):
    with (MODELS / f"logit_{train_end}.pkl").open("rb") as f:
        return pickle.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-end", default="2026-01-01")
    ap.add_argument("--folds", nargs="*", default=["2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"],
                    help="training cut-offs for the stability table")
    a = ap.parse_args()
    use_training_scope()
    con = duckdb.connect(str(figure.DB), read_only=True)
    tabs = {}
    for te in a.folds:
        m, _ = train(con, te)
        tabs[te[:4]] = wpr_table(m)["WPR points per unit"]
        if te == a.train_end:
            main_m = m
        print(te, "done", flush=True)
    if a.train_end not in a.folds:
        main_m, _ = train(con, a.train_end)
    p = save(main_m)
    t = wpr_table(main_m).join(pd.DataFrame(tabs).add_prefix("fit to "), how="left")
    L = ["# Production logit in WPR points", "",
         f"- Model: conditional logit on {len(COLS)} inputs (figure, ability, jockey/trainer, race-day projection, run"
         " comments); saved to " + str(p.relative_to(ROOT)),
         f"- Training states: VIC, SA, QLD + {', '.join(figure.EXTRA_STATES) or 'none'}",
         f"- Trained on races before {main_m['train_end']}. One WPR point of ability = {main_m['wpr_unit']:.4f} utility",
         f"- Blend with the market: a = {main_m['a']:.3f} (model), b = {main_m['b']:.3f} (market); calibrated market"
         f" c = {main_m['c']:.3f}; fitted on {main_m['blend_window']}",
         "- 'WPR points per unit': the bonus / penalty for +1 on that input, holding the others; a horse's contribution"
         " is that times (its value minus the field average)",
         "- 'fit to YYYY' columns: the same weights fitted on races before that year (stability)", "",
         t.to_markdown(floatfmt=".3f")]
    out = ROOT / "reports/logit_wpr_table.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
