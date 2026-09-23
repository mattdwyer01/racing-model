"""Settle projection v4: sharper speed maps.

    python model/projection_v4.py      # walk-forward vs v3 -> reports/projection_v4.md

Adds to the v3 settle inputs (projection.SETTLE_X), all from PAST runs or today's field:
  lengths back   the horse's lengths behind the leader at the 800m (0 = led, capped at 15): decayed mean, last,
                 best of last 3, distance-matched; field rank. Position share compresses big fields; lengths do not
  GPS early pos  position share about 400m after the start from GPS (QLD: RQ; VIC/SA: racing.com Triple S,
                 which covers the whole race): decayed mean, last, count; field rank. The 800m position mixes early
                 speed with how the race unfolds; the 400m-in position is the horse's early speed itself
  field relative settle history and early speed vs the field mean and vs the fastest rival
Two stages:
  stage 1  LightGBM on v3 + the inputs above
  stage 2  adds rival-aware inputs from every runner's stage-1 projection: projected rank, rivals projected
           just ahead, gap to the nearest rival ahead / behind, how many project to lead, own early speed vs the
           fastest other projected leader, rivals drawn inside projected ahead. Training rows use out-of-fold
           stage-1 projections (3 folds by race), so stage 2 learns from honest rival projections
Metrics per fold (fit 2019 to Y-1, test Y, VIC/SA/QLD): R2, in-race rank correlation, projected leader led at the
800m, position-bucket log loss (the position map's 6 buckets, multiclass on the settle inputs), and the win
logit (figure + projection) with v3 vs v4 settle feeding the pace / ground-loss / cost models.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, projection  # noqa: E402
from model.projection import K, SETTLE_X, _fit, _lags, _rank  # noqa: E402

LB = ["lb_mean", "lb_last", "lb_min3", "lb_dist", "lb_rank"]
EP = ["ep_mean", "ep_last", "ep_n", "ep_rank"]
REL = ["st_rel", "es_rel", "es_gap_best"]
NEW = LB + EP + REL
RIVAL = ["s1", "s1_rank", "s1_rel", "n_close_ahead", "gap_ahead", "gap_behind", "front_n", "es_gap_front",
         "inside_ahead"]
X1 = SETTLE_X + NEW
GPS_X = ["early_hist", "early_n"] + EP             # GPS-derived settle inputs (ablation: stage 1 without them)
X1_NOGPS = [c for c in X1 if c not in GPS_X]
X2 = X1 + RIVAL
FOLDS = [2023, 2024, 2025, 2026]
N_OOF = 3

LB_SQL = """
select r.run_id, case when r.res_pos800 = 1 then 0 else least(greatest(r.res_marg800, 0), 15) end lb
from runs r where r.res_pos800 is not null and not r.is_trial_or_jumpout
"""


def early_pos(con):
    """GPS position share about 400m after the start, per run_id (past-run measurement; used via history only)."""
    rq = con.sql("select run_id, res_gps_early400 ep from gps_runs where source = 'rq' and res_gps_early400 is not null").df()
    from model.extra_history import RC_SECTIONS
    if not RC_SECTIONS.exists():
        return rq.set_index("run_id")["ep"]
    s = pd.read_parquet(RC_SECTIONS, columns=["meet_code", "race_no", "tab_no", "from_m", "to_m", "pos"])
    s["race_code"] = s["meet_code"].astype(str) + "_" + s["race_no"].astype(str)
    key = con.sql("select run_id, src_race race_code, tab_no from gps_runs where source = 'rc' and res_gps_dist_m is not null").df()
    s = s.merge(key, on=["race_code", "tab_no"])          # Triple S rows (whole race covered)
    s["start"] = s.groupby("race_code")["from_m"].transform("max")
    at = s[(s["to_m"] == s["start"] - 400) & (s["pos"] > 0)].copy()
    n = at.groupby("race_code")["pos"].transform("count")
    at["ep"] = ((at["pos"] - 1) / (n - 1).clip(lower=1)).clip(0, 1)
    return pd.concat([rq.set_index("run_id")["ep"], at.set_index("run_id")["ep"]])


def _decayed(v):
    ok = ~np.isnan(v)
    w = np.where(ok, 0.5 ** (np.arange(K) / 3.0), 0)
    has = w.sum(1) > 0
    vv = np.nan_to_num(v)
    mean = np.where(has, (w * vv).sum(1) / np.maximum(w.sum(1), 1e-9), np.nan)
    last = np.where(has, vv[np.arange(len(v)), np.argmax(ok, 1)], np.nan)
    return ok, w, vv, has, mean, last


def add_features(con, x):
    """x = projection.frame(con) (sorted by horse, date, run). Adds NEW columns."""
    x = x.merge(con.sql(LB_SQL).df(), on="run_id", how="left")
    x["ep"] = x["run_id"].map(early_pos(con))
    x = x.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    den = (x["field_n"] - 1).clip(lower=1)

    ok, w, vv, has, mean, last = _decayed(_lags(x, "lb"))
    x["lb_mean"], x["lb_last"] = mean, last
    with np.errstate(all="ignore"):
        x["lb_min3"] = np.nanmin(np.where(ok & (np.cumsum(ok, 1) <= 3), vv, np.nan), 1)
    dl = _lags(x, "dist")
    near = ok & (np.abs(np.log(np.nan_to_num(dl, nan=1.0) / x["dist"].to_numpy()[:, None])) < 0.15)
    wn = np.where(near, w, 0)
    x["lb_dist"] = np.where(has, ((wn * vv).sum(1) + 2 * np.nan_to_num(mean)) / (wn.sum(1) + 2), np.nan)
    lb_fill = x["lb_dist"].fillna(x["lb_dist"].groupby(x["race_id"]).transform("median")).fillna(6.0)
    x["lb_rank"] = (_rank(lb_fill, x["race_id"]) - 1) / den

    ok, _, _, _, mean, last = _decayed(_lags(x, "ep"))
    x["ep_mean"], x["ep_last"], x["ep_n"] = mean, last, ok.sum(1)
    ep_fill = x["ep_mean"].fillna(x["st_mean"]).fillna(0.5)
    x["ep_rank"] = (_rank(ep_fill, x["race_id"]) - 1) / den

    g = x.groupby("race_id")
    st = x["st_mean"].fillna(0.5)
    x["st_rel"] = st - st.groupby(x["race_id"]).transform("mean")
    x["es_rel"] = x["es_today"] - g["es_today"].transform("mean")
    # own early speed minus the fastest rival's (0 when alone)
    es = x["es_today"].round(6)
    top1 = es.groupby(x["race_id"]).transform("max")
    top2 = es.groupby(x["race_id"]).transform(lambda s: s.nlargest(2).iloc[-1] if len(s) > 1 else s.iloc[0])
    x["es_gap_best"] = es - np.where(es >= top1, top2, top1)
    return x


def _rival(x, s1):
    """Rival-aware inputs from stage-1 projections s1 (array aligned with x)."""
    d = pd.DataFrame({"race_id": x["race_id"].to_numpy(), "run_id": x["run_id"].to_numpy(),
                      "barrier": x["barrier"].fillna(99).to_numpy(), "es": x["es_today"].round(6).to_numpy(),
                      "s1": np.round(s1, 6)}, index=x.index)
    den = (x["field_n"] - 1).clip(lower=1)
    out = pd.DataFrame(index=x.index)
    out["s1"] = d["s1"]
    out["s1_rank"] = (_rank(d["s1"], d["race_id"]) - 1) / den
    out["s1_rel"] = d["s1"] - d.groupby("race_id")["s1"].transform("mean")
    n_close, gap_a, gap_b, front_n, es_gf, ins = (np.zeros(len(d)) for _ in range(6))
    sv, ev, bv = d["s1"].to_numpy(), d["es"].to_numpy(), d["barrier"].to_numpy()
    for _, idx in d.groupby("race_id").indices.items():
        s, e, b = sv[idx], ev[idx], bv[idx]
        diff = s[:, None] - s[None, :]                     # own minus rival
        np.fill_diagonal(diff, np.nan)
        with np.errstate(all="ignore"):
            ahead = diff > 0
            n_close[idx] = ((diff > 0) & (diff <= 0.1)).sum(1)
            ga = np.where(ahead, diff, np.inf).min(1)
            gap_a[idx] = np.where(np.isinf(ga), -0.2, ga)       # -0.2 = no one projected ahead
            gb = np.where(diff < 0, -diff, np.inf).min(1)
            gap_b[idx] = np.where(np.isinf(gb), -0.2, gb)
            front = s < 0.2
            front_n[idx] = front.sum() - front
            other_front_es = np.where(front[None, :] & ~np.eye(len(s), dtype=bool), e[None, :], -np.inf).max(1)
            es_gf[idx] = np.where(np.isinf(other_front_es), 5.0, e - other_front_es)
            ins[idx] = (ahead & (b[None, :] < b[:, None])).sum(1)
    out["n_close_ahead"] = n_close / den
    out["gap_ahead"], out["gap_behind"] = gap_a, gap_b
    out["front_n"], out["es_gap_front"] = front_n, es_gf
    out["inside_ahead"] = ins / den
    return out


def settle(x, train_end, return_s1=False, target="y_settle"):
    """v4 projected settle for every row of x (fits on [2019, train_end) only). target: any 0..1 settle measure
    (default the 800m position share; staged.py uses lengths behind the leader / 15)."""
    train_end = pd.Timestamp(train_end)
    tr = (x["race_date"] < train_end) & (x["race_date"] >= "2019-01-01") & x[target].notna()
    s1 = _fit(x.loc[tr, X1], x.loc[tr, target]).predict(x[X1].to_numpy(float))
    oof = s1.copy()
    fold = (x["race_id"].to_numpy() % N_OOF)
    trv = tr.to_numpy()
    for k in range(N_OOF):
        fit_m, pred_m = trv & (fold != k), trv & (fold == k)
        oof[pred_m] = _fit(x.loc[fit_m, X1], x.loc[fit_m, target]).predict(x.loc[pred_m, X1].to_numpy(float))
    # training rows: rivals' out-of-fold projections; other rows: full stage-1 model
    s1_use = np.where(trv, oof, s1)
    riv = _rival(x, s1_use)
    x2 = pd.concat([x[X1], riv], axis=1)
    s2 = _fit(x2.loc[tr, X2], x.loc[tr, target]).predict(x2[X2].to_numpy(float)).clip(0, 1)
    return (s2, s1) if return_s1 else s2


# ---------------------------------------------------------------- evaluation

def _bucket_ll(x, tr, te, cols):
    """Multiclass log loss of the position map's 6 buckets (lead .. 8L+ back at the 800m)."""
    from model.position_map import CLF, POS, ROUNDS, _pos_bucket
    y = pd.Series(_pos_bucket(x["pos800"].to_numpy(float), x["marg800"].to_numpy(float)), index=x.index)
    mtr, mte = tr & y.notna(), te & y.notna()
    m = lgb.train(dict(CLF, num_class=len(POS)), lgb.Dataset(np.round(x.loc[mtr, cols].to_numpy(float), 6),
                                                             y[mtr].astype(int)), ROUNDS)
    p = m.predict(np.round(x.loc[mte, cols].to_numpy(float), 6))
    yy = y[mte].astype(int).to_numpy()
    return -np.log(np.clip(p[np.arange(len(yy)), yy], 1e-12, 1))


def main():
    from model.validate_figure import FIG, eval_set, fit_eval, race_ll
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = add_features(con, projection.frame(con))
    x0 = x0.merge(con.sql("select run_id, res_pos800 pos800, res_marg800 marg800 from runs").df(), on="run_id",
                  how="left")
    print("frame", len(x0), flush=True)
    WIN = FIG + ["barrier_pct", "proj_settle", "proj_pace", "proj_gl", "proj_adj"] + projection.BIAS
    acc, lls, per = [], [], {}
    for y in FOLDS:
        te_end = f"{y}-01-01"
        s2, s1 = settle(x0, te_end, return_s1=True)
        trm0 = (x0["race_date"] < te_end) & (x0["race_date"] >= "2019-01-01") & x0["y_settle"].notna()
        s1_ng = _fit(x0.loc[trm0, X1_NOGPS], x0.loc[trm0, "y_settle"]).predict(x0[X1_NOGPS].to_numpy(float))
        xv = x0.assign(v4=s2, v4_s1=s1, v4_s1_nogps=s1_ng)
        x3, _, _ = projection.project(x0, te_end)
        xv["v3"] = x3.set_index("run_id")["proj_settle"].reindex(xv["run_id"]).to_numpy()
        te_m = (xv.race_date.dt.year == y) & xv["in_scope"]
        te = xv[te_m]
        gh = te["ep_n"].fillna(0)
        for st, t in [("all", te), ("QLD", te[te.state == "QLD"]), ("VIC/SA", te[te.state != "QLD"]),
                      ("GPS history 2+ runs", te[gh >= 2]), ("no GPS history", te[gh == 0])]:
            for lab in ["v3", "v4_s1_nogps", "v4_s1", "v4"]:
                acc += [{"fold": y, "races": st, "model": lab, "metric": "R2", "v": projection._r2(t.y_settle, t[lab])},
                        {"fold": y, "races": st, "model": lab, "metric": "in-race rank corr",
                         "v": projection._spearman_in_race(t, "y_settle", lab)},
                        {"fold": y, "races": st, "model": lab, "metric": "projected leader led",
                         "v": projection._leader_hit(t, lab)}]
        for lab, t in [("first-up", te[te.first_up == 1]), ("debutants", te[te.h_none == 1])]:
            for m in ["v3", "v4"]:
                acc.append({"fold": y, "races": lab, "model": m, "metric": "R2", "v": projection._r2(t.y_settle, t[m])})
        # position-bucket log loss: v3 inputs vs v4 inputs (+ rival-aware)
        trm = (xv["race_date"] < te_end) & (xv["race_date"] >= "2019-01-01")
        riv = _rival(xv, xv["v4_s1"].to_numpy())
        xb = pd.concat([xv, riv.drop(columns=["s1"])], axis=1).assign(s1=xv["v4_s1"])
        for lab, cols in [("v3", SETTLE_X), ("v4", X2)]:
            b = _bucket_ll(xb, trm, te_m, cols)
            acc.append({"fold": y, "races": "all", "model": lab, "metric": "position bucket log loss", "v": b.mean()})
        # win logit: figure + projection, v3 vs v4 settle through pace / gl / cost
        x4, _, _ = projection.project(x0, te_end, settle_fn=lambda d, t: d["run_id"].map(
            xv.set_index("run_id")["v4"]).to_numpy())
        res = {"fold": y}
        for lab, xx in [("v3", x3), ("v4", x4)]:
            e = eval_set(xx)
            tr, tt = e[e.race_date < te_end], e[e.race_date.dt.year == y]
            ll = race_ll(fit_eval(tr, tt, WIN)[0], tt)
            res[lab] = ll.mean()
            per.setdefault(lab, []).append(ll)
            if lab == "v3":
                isq = (tt.loc[tt.won == 1, "state"] == "QLD").to_numpy()
                per.setdefault("isq", []).append(isq)
        lls.append(res)
        print(y, {k: round(v, 4) for k, v in res.items()}, flush=True)

    a = pd.DataFrame(acc).pivot_table(index=["metric", "races"], columns=["model", "fold"], values="v")
    d = np.concatenate(per["v4"]) - np.concatenate(per["v3"])
    isq = np.concatenate(per["isq"])
    rng = np.random.default_rng(0)

    def ci(z):
        b = [z[rng.integers(0, len(z), len(z))].mean() for _ in range(2000)]
        return f"{z.mean():+.4f} ({np.percentile(b, 2.5):+.4f} to {np.percentile(b, 97.5):+.4f})"
    L = ["# Settle projection v4 vs v3: walk-forward", "",
         "- Fit 2019 to Y-1, test year Y, VIC/SA/QLD runs. v4_s1 = stage 1 (v3 inputs + lengths back, GPS early"
         " position, field-relative); v4 = stage 2 (+ rival-aware inputs from out-of-fold stage-1 projections)",
         "- GPS ablation: v4_s1_nogps = stage 1 without the GPS inputs (" + ", ".join(GPS_X) + "); compare with v4_s1."
         " 'GPS history 2+ runs' = runners with at least 2 past runs that have a GPS early position",
         "- Position bucket log loss: multiclass over the position map's 6 buckets (lead .. 8L+ back at the 800m);"
         " lower is better", "",
         "## Accuracy", "", a.round(4).to_markdown(), "",
         "## Win logit (figure + projection; v4 settle also feeds pace, ground loss and cost)", "",
         pd.DataFrame(lls).set_index("fold").to_markdown(floatfmt=".4f"), "",
         f"- v4 minus v3, pooled race log loss (95% race bootstrap): all {ci(d)}; QLD {ci(d[isq])}; VIC/SA {ci(d[~isq])}"]
    out = ROOT / "reports/projection_v4.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
