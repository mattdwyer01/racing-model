"""Market-offset models: learn only what the market misses.

    python model/offset_model.py            # walk-forward on SP (2023-2026) -> reports/offset_validation.md
    python model/offset_model.py --fixed    # + fixed-price backtest (Apr 2026 on) -> reports/offset_fixed_backtest.md
    python model/offset_model.py --qld      # QLD test races: all-state vs QLD-only models -> reports/offset_qld.md

Models (all per race, softmax over runners):
    SP (calibrated)       beta * log p_sp
    logit: SP + figure + ability (+ jt, + projection)   conditional logit
    logit: + jt           adds jockey / trainer / horse market-relative form (model/jt.py)
    gbm offset            LightGBM with a custom per-race softmax objective; the score starts from
                          the calibrated SP (fitted on train) and trees learn only the correction.
                          Features: ability + jt + field-relative versions + market context.
Rounds for the GBM are picked on the last 20% of the training window (by date), then refitted on all of it.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import ability, clogit, extra_history, figure, jt, position_map, projection  # noqa: E402
from model.validate_figure import FIG, eval_set, race_ll  # noqa: E402

JT = jt.COLS
FIG2_COEF = {}                                     # figure v2 weights by training cut-off (set by build)
BASE = list(dict.fromkeys(FIG + ability.ALL))      # figure components' history + ability features
PROJ = projection.OUT
REL = ["dm", "best3", "fig_last", "h_class", "j_ae", "t_ae", "h_ae", "j_sr", "t_sr", "proj_pace"]
CONTEXT = ["log_p_sp", "mkt_rank", "field_n", "is_qld", "is_sa", "dist", "wet"]
GBM_FEATS = BASE + JT + PROJ + [f"{c}_rel" for c in REL] + [f"{c}_gap" for c in REL] + CONTEXT
GBM_NOPROJ = [c for c in GBM_FEATS if not (c in PROJ or c.startswith("proj_"))]
PARAMS = dict(num_leaves=15, learning_rate=0.03, min_data_in_leaf=1000, feature_fraction=0.7,
              bagging_fraction=0.8, bagging_freq=1, lambda_l2=10.0, verbose=-1, num_threads=4, seed=1,
              deterministic=True, force_row_wise=True)   # identical results run to run
# tuning grid, picked per fold on the inner validation window only (off by default: in the
# 2023-2026 walk-forward the grid points differed by <0.001 on inner validation and tuning did not help)
GRID = [dict(num_leaves=15, min_data_in_leaf=1000, learning_rate=0.03),
        dict(num_leaves=31, min_data_in_leaf=300, learning_rate=0.03),
        dict(num_leaves=63, min_data_in_leaf=300, learning_rate=0.02),
        dict(num_leaves=15, min_data_in_leaf=300, learning_rate=0.05, lambda_l2=30.0)]
MAX_ROUNDS, EARLY = 1500, 100
PX_KEEP = []      # projection-frame columns to keep from the last build (all runs), e.g. for race_sim.py
LAST_PX = {}


# ---------------------------------------------------------------- data

def build(con, train_end):
    return eval_set(build_features(con, train_end))


def build_features(con, train_end):
    """Every model input for every run (no eval filter). Fitted pieces use data before train_end only."""
    d = ability.load(con)
    h = figure.history(d)
    a = ability.features(d, ability.fit_coef(h, train_end))
    coef2 = ability.fit_coef_next(d, train_end)
    a2 = ability.features(d, coef2)[["run_id"] + ability.FIG_DEPENDENT]
    a = a.merge(a2.rename(columns={c: c + "_v2" for c in ability.FIG_DEPENDENT}), on="run_id")
    FIG2_COEF[str(train_end)[:10]] = coef2
    extra = [c for c in ability.ALL if c not in ability.BASE and c != "wt_rel_today"] + ["wet"] + [c + "_v2" for c in ability.FIG_DEPENDENT]
    px, _, _ = projection.project(projection.frame(con, h), train_end)
    if PX_KEEP:
        LAST_PX["px"] = px[PX_KEEP].copy()
    xh = extra_history.features(con, d, train_end)   # GPS sections + run comments history (variants only)
    pm = position_map.features(con, px, train_end)   # expected position / width value (variants only)
    e = h.merge(a[["run_id"] + extra], on="run_id") \
        .merge(a[["run_id", "wpr"]].rename(columns={"wpr": "y_wpr"}), on="run_id") \
        .merge(jt.features(con), on="run_id", how="left") \
        .merge(px[["run_id"] + PROJ], on="run_id", how="left") \
        .merge(xh, on="run_id", how="left") \
        .merge(pm, on="run_id", how="left")
    # y_wpr is today's result: a fitting target for the rating model only, never an input
    e[JT] = e[JT].fillna(0.0)
    # fixed row order, so adding columns or merges never changes what the GBM's row sampling sees
    return e.sort_values(["race_date", "race_id", "run_id"], kind="mergesort").reset_index(drop=True)


def add_context(e, mkt="log_p_sp"):
    e = e.copy()
    g = e.groupby("race_id")
    for c in REL + [c + "_v2" for c in REL if c + "_v2" in e]:
        e[c + "_rel"] = e[c] - g[c].transform("mean")
        e[c + "_gap"] = e[c] - g[c].transform("max")
    e["mkt_rank"] = e.groupby("race_id")[mkt].rank(ascending=False)
    e["field_n"] = g["run_id"].transform("size")
    e["is_qld"] = (e["state"] == "QLD").astype(float)
    e["is_sa"] = (e["state"] == "SA").astype(float)
    return e


# ---------------------------------------------------------------- models

def _starts(race):
    return np.r_[0, np.flatnonzero(np.diff(race)) + 1]


def _softmax(s, race):
    st = _starts(race)
    cnt = np.diff(np.r_[st, len(s)])
    s = s - np.repeat(np.maximum.reduceat(s, st), cnt)
    ex = np.exp(s)
    return ex / np.repeat(np.add.reduceat(ex, st), cnt)


def logit_fit(tr, cols):
    mu, sd = tr[cols].mean(), tr[cols].std().replace(0, 1)
    b = clogit.fit(((tr[cols] - mu) / sd).to_numpy(float), tr["race"].to_numpy(), tr["won"].to_numpy())
    return lambda df: clogit.probs(((df[cols] - mu) / sd).to_numpy(float), df["race"].to_numpy(), b)


def _score_fn(tr):
    """Calibrated market score: beta * log p (fitted on train)."""
    b = clogit.fit(tr[["log_p_sp"]].to_numpy(float), tr["race"].to_numpy(), tr["won"].to_numpy())[0]
    return lambda df: b * df["log_p_sp"].to_numpy(float)


def _gbm_train(tr, va, offset, rounds=None, extra=None, feats=None):
    def obj_for(df, off):
        race, y = df["race"].to_numpy(), df["won"].to_numpy(float)

        def fobj(preds, _):
            p = _softmax(preds + off, race)
            return p - y, np.maximum(p * (1 - p), 1e-6)
        return fobj

    def feval_for(df, off):
        race, y = df["race"].to_numpy(), df["won"].to_numpy()

        def feval(preds, _):
            p = _softmax(preds + off(df), race)
            return "race_ll", -np.log(np.clip(p[y == 1], 1e-12, 1)).mean(), False
        return feval

    feats = feats or GBM_FEATS
    dtr = lgb.Dataset(tr[feats].to_numpy(float), free_raw_data=False)
    params = dict(PARAMS, **(extra or {}), objective=obj_for(tr, offset(tr)))
    if rounds is None:
        dva = lgb.Dataset(va[feats].to_numpy(float), reference=dtr)
        m = lgb.train(params, dtr, MAX_ROUNDS, valid_sets=[dva], feval=feval_for(va, offset),
                      callbacks=[lgb.early_stopping(EARLY, verbose=False)])
        return m.best_iteration, m.best_score["valid_0"]["race_ll"]
    return lgb.train(params, dtr, rounds)


def gbm_fit(tr, tune=False, feats=None, market=True):
    """Pick rounds on the last 20% of train (by date), refit on all of train. Returns (predict fn, model, rounds)."""
    cut = tr["race_date"].quantile(0.8)
    inner, va = tr[tr.race_date <= cut], tr[tr.race_date > cut]
    inner = inner.assign(race=pd.factorize(inner["race_id"])[0])
    va = va.assign(race=pd.factorize(va["race_id"])[0])
    zero = lambda df: np.zeros(len(df))   # noqa: E731  (market=False: trees from scratch, no SP)
    off_in = _score_fn(inner) if market else zero
    feats = feats or GBM_FEATS
    trials = [(p, *_gbm_train(inner, va, off_in, extra=p, feats=feats)) for p in (GRID if tune else [{}])]
    best, rounds, score = min(trials, key=lambda t: t[2])
    rounds = max(rounds, 20)
    off = _score_fn(tr) if market else zero
    m = _gbm_train(tr, None, off, rounds, extra=best, feats=feats)
    m.chosen = (best, rounds, {str(p): round(float(sc), 5) for p, _, sc in trials})
    return (lambda df: _softmax(m.predict(df[feats].to_numpy(float)) + off(df), df["race"].to_numpy())), m, rounds


def fit_all(tr):
    fns = {"SP (calibrated)": logit_fit(tr, ["log_p_sp"]),
           "logit: SP + figure + ability": logit_fit(tr, ["log_p_sp"] + BASE),
           "logit: SP + figure + ability + jt": logit_fit(tr, ["log_p_sp"] + BASE + JT),
           "logit: SP + figure + ability + jt + projection": logit_fit(tr, ["log_p_sp"] + BASE + JT + PROJ)}
    fns["gbm offset, no projection"] = gbm_fit(tr, feats=GBM_NOPROJ)[0]
    g, m, rounds = gbm_fit(tr)
    fns["gbm offset"] = g
    return fns, m, rounds


# ---------------------------------------------------------------- runs

def walk_forward():
    con = duckdb.connect(str(figure.DB), read_only=True)
    rows, per, info = [], {}, {}
    for y in [2023, 2024, 2025, 2026]:
        e = add_context(build(con, f"{y}-01-01"))
        tr = e[e.race_date < f"{y}-01-01"].copy()
        te = e[e.race_date.dt.year == y].copy()
        assert tr.race_date.max() < te.race_date.min(), "train must end before the test period"
        tr["race"], te["race"] = pd.factorize(tr["race_id"])[0], pd.factorize(te["race_id"])[0]
        fns, m, rounds = fit_all(tr)
        res = {"fold": y, "races": te.race_id.nunique()}
        for k, f in fns.items():
            ll = race_ll(f(te), te)
            res[k] = ll.mean()
            per.setdefault(k, []).append(ll)
        info[y] = (rounds, pd.Series(m.feature_importance("gain"), index=GBM_FEATS), m.chosen)
        rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"}, "rounds", rounds, flush=True)

    tab = pd.DataFrame(rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    tab.loc["pooled"] = [tab["races"].sum()] + [pooled[k].mean() for k in per]
    base = pooled["SP (calibrated)"]
    diffs = [(k, (pooled[k] - base).mean(), (pooled[k] - base).std() / np.sqrt(len(base))) for k in per]
    imp = pd.concat({y: v[1] for y, v in info.items()}, axis=1)
    imp = (imp / imp.sum()).mean(1).sort_values(ascending=False).head(20)

    L = ["# Market-offset models: walk-forward on SP", "",
         "- Eval set and folds as validate_figure.py (VIC/SA/QLD, test 2023 to 2026 YTD, trained 2022 to Y-1)",
         "- gbm offset: LightGBM, per-race softmax objective, score = calibrated SP + trees; features include the race-day projection (model/projection.py); params tuned per fold on inner validation", "",
         "## Log loss by fold", "", tab.T.to_markdown(floatfmt=".4f"), "",
         "## vs SP (calibrated), pooled (negative = better)", "", "| model | diff | se |", "|---|---|---|"]
    L += [f"| {k} | {m:+.4f} | {s:.4f} |" for k, m, s in diffs]
    L += ["", "## GBM tuning (chosen on the inner validation window of each fold)", ""]
    L += [f"- {y}: chose {v[2][0]}, rounds {v[0]}; inner-val loss by grid point {v[2][2]}"
          for y, v in info.items()]
    L += ["",
          "## GBM feature importance (share of gain, mean over folds, top 20)", "",
          imp.rename("gain share").to_frame().to_markdown(floatfmt=".3f")]
    out = ROOT / "reports/offset_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def fixed_backtest():
    from model.backtest_fixed import bets
    con = duckdb.connect(str(figure.DB), read_only=True)
    start = pd.Timestamp(con.sql("select min(date) from live_runners").fetchone()[0])
    fx = con.sql("""select run_id, fixed_win_price fx from fixed_prices_final
                    where coalesce(scratched, 0) = 0 and fixed_win_price > 1""").df()
    e = build(con, start)
    tr = add_context(e[e.race_date < start])
    te = e[e.race_date >= start].merge(fx, on="run_id", how="left")
    te = te[te.groupby("race_id")["fx"].transform(lambda s: s.notna().all())].copy()
    inv = 1 / te["fx"]
    te["p_fx"] = inv / inv.groupby(te["race_id"]).transform("sum")
    te["log_p_sp"] = np.log(te["p_fx"])          # the market input at test time is the fixed price
    te = add_context(te).sort_values(["race_date", "race_id"]).reset_index(drop=True)
    tr = tr.assign(race=pd.factorize(tr["race_id"])[0])
    te["race"] = pd.factorize(te["race_id"])[0]
    fns, _, rounds = fit_all(tr)
    ll = {k: race_ll(f(te), te) for k, f in fns.items()}
    base = ll["SP (calibrated)"]
    ll_rows = [{"model": k.replace("SP", "fixed"), "log loss": v.mean(), "vs fixed (cal)": (v - base).mean(),
                "se": (v - base).std() / np.sqrt(len(v))} for k, v in ll.items()]
    rng = np.random.default_rng(0)
    rows = []
    for k in ["logit: SP + figure + ability + jt", "gbm offset"]:
        te["p"] = fns[k](te)
        for r in bets(te, "p", "fx", rng):
            rows.append(dict(r, model=k.replace("SP", "fixed")))
    L = ["# Market-offset models: fixed-price backtest", "",
         f"- Test: {te.race_id.nunique():,} VIC/SA/QLD races {te.race_date.min():%d %b} to {te.race_date.max():%d %b %Y};"
         f" trained on {tr.race_id.nunique():,} races before {start:%d %b %Y} (SP as the market), GBM rounds {rounds}",
         "- At test time the fixed price replaces SP as the market input", "",
         "## Log loss", "", pd.DataFrame(ll_rows).to_markdown(index=False, floatfmt=".4f"), "",
         "## Betting at the fixed price", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".3f")]
    out = ROOT / "reports/offset_fixed_backtest.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def qld():
    """QLD test races: models fitted on all states vs fitted on QLD only, all against SP."""
    con = duckdb.connect(str(figure.DB), read_only=True)
    rows, per = [], {}
    for y in [2023, 2024, 2025, 2026]:
        e = add_context(build(con, f"{y}-01-01"))
        tr = e[e.race_date < f"{y}-01-01"].copy()
        te = e[(e.race_date.dt.year == y) & (e.state == "QLD")].copy()
        trq = tr[tr.state == "QLD"].copy()
        assert tr.race_date.max() < te.race_date.min(), "train must end before the test period"
        for df in (tr, te, trq):
            df["race"] = pd.factorize(df["race_id"])[0]
        cols = ["log_p_sp"] + BASE + JT + PROJ
        fns = {"SP (calibrated, all-state fit)": logit_fit(tr, ["log_p_sp"]),
               "SP (calibrated, QLD fit)": logit_fit(trq, ["log_p_sp"]),
               "logit, all-state fit": logit_fit(tr, cols),
               "logit, QLD fit": logit_fit(trq, cols),
               "gbm offset, all-state fit": gbm_fit(tr)[0],
               "gbm offset, QLD fit": gbm_fit(trq)[0]}
        res = {"fold": y, "QLD races": te.race_id.nunique()}
        for k, f in fns.items():
            ll = race_ll(f(te), te)
            res[k] = ll.mean()
            per.setdefault(k, []).append(ll)
        rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"}, flush=True)
    tab = pd.DataFrame(rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    tab.loc["pooled"] = [tab["QLD races"].sum()] + [pooled[k].mean() for k in per]
    base = pooled["SP (calibrated, all-state fit)"]
    L = ["# QLD: all-state vs QLD-only models", "",
         "- Test: QLD races in year Y (2023 to 2026 YTD); fitted on 2022 to Y-1 (all states or QLD only)",
         "- Features: SP + figure + ability + jockey/trainer + race-day projection (incl. track bias, track x distance"
         " barrier, speed map)", "",
         "## Log loss", "", tab.T.to_markdown(floatfmt=".4f"), "",
         "## vs SP (calibrated, all-state fit), pooled", "", "| model | diff | se |", "|---|---|---|"]
    L += [f"| {k} | {(pooled[k] - base).mean():+.4f} | {(pooled[k] - base).std() / np.sqrt(len(base)):.4f} |"
          for k in per]
    out = ROOT / "reports/offset_qld.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--qld" in sys.argv:
        qld()
    else:
        walk_forward()
        if "--fixed" in sys.argv:
            fixed_backtest()
