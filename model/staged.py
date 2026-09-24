"""Staged model: ability -> today's conditions -> race shape -> win probability.

    python model/staged.py      # walk-forward -> reports/staged.md, reports/staged_per_race.csv.gz
    python model/staged.py --prod-s3   # + production (with rating mu) + S3, and + S3's parts
                                       # -> reports/staged_prod_s3.md, reports/staged_prod_s3_per_race.csv.gz

Each stage is one number per horse in WPR points (relative to the field), built by its own sub-models:
  S1 ability     everything known from the horse's history: decayed WPR / figure, best and last figures, trend,
                 class, runs, form shape, past-run comments, past ground loss and width, debut trials, age / sex
  S2 conditions  today vs the horse: distance change and fit, going fit, surface, prep (first up, days, trials),
                 weight today, jockey / trainer (A/E, strike rates, change / upgrade)
                 S1 and S2 come from one ridge regression of today's WPR on both groups (within-race demeaned,
                 every runner, training rows only), so ability is estimated net of conditions
  S3 race shape  how the race is projected to be run and what it does to each horse:
                 - lengths behind the leader at the 800m (v4 two-stage model with rival-aware inputs, target
                   lengths / 15) and P(lengths bucket: lead, <=1.5L, 1.5-3L, 3-5L, 5-8L, 8L+)
                 - width from the rail (GPS: QLD around the turn, VIC/SA race average) -> P(fence, 1, 2, 3+ wide)
                 - race pace: early, mid and late shape (TopRate), each projected -> P(slow, even, fast)
                 - track bias maps in WPR (shrunk: global, track, track x distance, going, track x rail):
                   position x early pace, position x mid pace, position x late pace, width x early pace
                 - ground cost: WPR per extra metre by track (shrunk to the global slope) x projected extra metres
                 S3 = expected map values + ground cost, demeaned in the race
  Final          conditional logit on S1, S2, S3 and a debut flag: a handful of weights, one per stage (each
                 near the same value when the stages are calibrated in WPR points), then blended with SP
Walk-forward like blend_eval.py: test year Y; sub-models fitted on data before Y; blend weights on the last 25%
of training from out-of-sample predictions. Ablations: S1 only, S1 + S2. Reference: the production logit.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import ability, clogit, figure, position_map, production, projection, projection_v4  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.projection import GL_X, PACE_X, _fit, _r2  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
G = production.GROUPS
S1_X = list(dict.fromkeys([c for c in G["ability"] if c not in production.MU] + G["form shape"] + G["comments"] + G["ground loss (past runs)"] +
                          ["trial_pos_debut", "trial_marg_debut", "age2", "age3", "age7", "female"]))
S2_X = list(dict.fromkeys(G["distance / going"] + [c for c in G["prep"] if c not in S1_X] + ["wt_rel_today"] +
                          G["jockey / trainer"]))
RIDGE = 1.0
CTX = ["cx_g", "cx_t", "cx_td", "cx_go", "cx_tr"]
N_POS, N_WID, N_PACE = 6, 4, 3
GL_K = 2000.0          # shrinkage of the track ground-cost slope to the global slope (sum of squared metres)
BOOT = 2000
PROD_S3 = "--prod-s3" in sys.argv
S3_PARTS = ["ev_pos_b_early_b", "ev_pos_b_mid_b", "ev_pos_b_late_b", "ev_wid_b_early_b", "ev_ground"]


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def _dm(df, cols):
    X = df[cols].astype(float).fillna(0.0)
    return X - X.groupby(df["race_id"].to_numpy()).transform("mean")


# ---------------------------------------------------------------- S1 + S2: ridge regression on today's WPR

class Stage12:
    def fit(self, tr):
        t = tr[tr["y_wpr"].notna()]
        X = _dm(t, S1_X + S2_X).to_numpy(float)
        y = (t["y_wpr"] - t.groupby("race_id")["y_wpr"].transform("mean")).to_numpy(float)
        sd = X.std(0)
        sd[sd == 0] = 1
        Xs = X / sd
        self.beta = pd.Series(np.linalg.solve(Xs.T @ Xs + RIDGE * np.eye(Xs.shape[1]), Xs.T @ y) / sd,
                              index=S1_X + S2_X)
        pred = X @ self.beta.to_numpy()
        self.r2 = 1 - ((y - pred) ** 2).sum() / (y ** 2).sum()
        return self

    def stages(self, df):
        X = _dm(df, S1_X + S2_X)
        return X[S1_X] @ self.beta[S1_X], X[S2_X] @ self.beta[S2_X]


# ---------------------------------------------------------------- S3: race shape

def _probs_normal(mu, sd, cuts):
    c = [norm.cdf((k - mu) / sd) for k in cuts]
    return np.c_[c[0], c[1] - c[0], 1 - c[1]]


def _clf(X, y, n):
    return lgb.train(dict(position_map.CLF, num_class=n), lgb.Dataset(np.round(X.to_numpy(float), 6), y.astype(int)),
                     position_map.ROUNDS)


class Stage3:
    """Fitted on the full projected frame x (all runs, 2019 to train_end)."""

    def fit_predict(self, con, x, train_end):
        te = pd.Timestamp(train_end)
        tr = (x["race_date"] < te) & (x["race_date"] >= "2019-01-01")
        acc = {}
        # lengths behind the leader (v4 two-stage, rival aware), buckets
        x["y_lbs"] = x["lb"] / 15
        x["proj_lbs"] = projection_v4.settle(x, te, target="y_lbs")
        acc["lengths R2"] = _r2(x.loc[~tr & x["lb"].notna(), "lb"], 15 * x.loc[~tr & x["lb"].notna(), "proj_lbs"])
        x["pos_b"] = position_map._pos_bucket(x["pos800"].to_numpy(float), x["marg800"].to_numpy(float))
        m = tr & x["pos_b"].notna()
        cols_p = projection_v4.X1 + ["proj_lbs"]
        P_pos = _clf(x.loc[m, cols_p], x.loc[m, "pos_b"], N_POS).predict(np.round(x[cols_p].to_numpy(float), 6))
        # width from the rail, buckets
        x["width_m"] = x["run_id"].map(position_map._width(con, x))
        x["wid_b"] = pd.cut(x["width_m"], [-1, 2, 3.5, 5, 99], labels=False)
        cols_w = GL_X + ["proj_lbs"]
        mw = tr & x["wid_b"].notna()
        P_wid = _clf(x.loc[mw, cols_w], x.loc[mw, "wid_b"], N_WID).predict(np.round(x[cols_w].to_numpy(float), 6))
        width_tracks = set(x.loc[mw, "track"])
        # race pace: early / mid / late shape
        r = projection._pace_frame(x)
        r = r.join(x.groupby("race_id")[["y_mid", "y_late"]].first())
        rtr = (r["race_date"] < te) & (r["race_date"] >= "2019-01-01")
        P_pace, self.pace_cuts = {}, {}
        for name, col in [("early", "y_shape"), ("mid", "y_mid"), ("late", "y_late")]:
            ok = rtr & r[col].notna()
            mdl = _fit(r.loc[ok, PACE_X], r.loc[ok, col])
            proj = pd.Series(mdl.predict(r[PACE_X].to_numpy(float)), index=r.index)
            sd = float((r.loc[ok, col] - proj[ok]).std())
            cuts = [-2.0, 2.0] if name == "early" else list(np.percentile(r.loc[ok, col], [100 / 3, 200 / 3]))
            self.pace_cuts[name] = cuts
            P_pace[name] = _probs_normal(x["race_id"].map(proj).fillna(0).to_numpy(float), sd, cuts)
            x[f"{name}_b"] = x["race_id"].map(pd.Series(np.digitize(r[col], cuts), index=r.index).where(r[col].notna()))
            teok = ~rtr & r[col].notna()
            acc[f"pace {name} R2"] = _r2(r.loc[teok, col], proj[teok])
        # track bias maps (WPR points), fitted in sequence on what the previous maps leave
        x = pd.concat([x, position_map._context(x)], axis=1)
        res = (x["wpr"] - x["h_wpr"]).where((x["h_none"] == 0) & x["wpr"].notna())
        x["r"] = res - res.groupby(x["race_id"]).transform("mean")
        x["w"] = 0.5 ** ((te - x["race_date"]).dt.days.clip(lower=0) / position_map.HALF_LIFE_DAYS)
        base = tr & x["r"].notna()
        self.maps = []
        spec = [("pos_b", "early_b", CTX), ("pos_b", "mid_b", CTX), ("pos_b", "late_b", CTX),
                ("wid_b", "early_b", ["cx_g", "cx_t", "cx_td"])]
        E = np.zeros(len(x))
        for a, b, levels in spec:
            fm = base & x[a].notna() & x[b].notna()
            f = x[fm].copy()
            tabs = position_map._fit_levels(f, [a, b], levels)
            own = np.zeros(len(f))
            for lev, eff in tabs:
                own += f[[lev, a, b]].merge(eff, on=[lev, a, b], how="left")["v"].fillna(0).to_numpy()
            x.loc[fm, "r"] = x.loc[fm, "r"] - own
            self.maps.append((a, b, tabs))
            na, nb = (N_POS if a == "pos_b" else N_WID), N_PACE
            V = position_map._lookup(tabs, x, [a, b], [(i, j) for i in range(na) for j in range(nb)])
            Pa = P_pos if a == "pos_b" else P_wid
            Pb = P_pace[b.split("_")[0]]
            ev = (V * (Pa[:, :, None] * Pb[:, None, :]).reshape(len(x), -1)).sum(1)
            if a == "wid_b":
                ev = np.where(x["track"].isin(width_tracks), ev, 0.0)
            x[f"ev_{a}_{b}"] = ev
            E += ev
        # ground cost per extra metre by track, on what the maps leave (within race)
        g = x[base & x["y_gl"].notna()]
        gl = g["y_gl"] - g.groupby("race_id")["y_gl"].transform("mean")
        rr = g["r"] - g.groupby("race_id")["r"].transform("mean")
        b_all = float((gl * rr).sum() / (gl * gl).sum())
        by = pd.DataFrame({"t": g["track"], "xy": gl * rr, "xx": gl * gl}).groupby("t").sum()
        self.gl_cost = (by["xy"] + GL_K * b_all) / (by["xx"] + GL_K)
        self.gl_global = b_all
        cost = x["track"].map(self.gl_cost).fillna(b_all).to_numpy(float)
        x["ev_ground"] = cost * x["proj_gl"].fillna(0).to_numpy(float)
        E += x["ev_ground"].to_numpy()
        x["S3"] = E - pd.Series(E, index=x.index).groupby(x["race_id"]).transform("mean")
        self.acc = acc
        return x[["run_id", "S3", "proj_lbs", "ev_pos_b_early_b", "ev_pos_b_mid_b", "ev_pos_b_late_b",
                  "ev_wid_b_early_b", "ev_ground"]]


# ---------------------------------------------------------------- walk-forward

def _frame(con):
    d = ability.load(con)
    h = figure.history(d)
    fr = projection_v4.add_features(con, projection.frame(con, h))
    more = con.sql("""select r.run_id, r.res_pos800 pos800, r.res_marg800 marg800, ra.res_shape_mid y_mid,
                        ra.res_shape_late y_late from runs r join races ra using (race_id)""").df()
    fr = fr.merge(more, on="run_id", how="left")
    for c in ["y_mid", "y_late"]:                  # a few 2023 races carry absurd mid shapes (sd 9.8 vs ~2.5)
        fr[c] = fr[c].where(fr[c].abs() <= 12)
    return {"d": d, "h": h, "fr": fr}


def run_fold(con, shared, y):
    te_end = f"{y}-01-01"
    e = om.add_context(om.eval_set(om.build_features(con, te_end, shared=shared, light="no_posmap" if PROD_S3 else True)))
    px = om.LAST_PX.pop("full")
    s3 = Stage3()
    st3 = s3.fit_predict(con, px, te_end)
    del px
    e = e.merge(st3, on="run_id", how="left")
    e[["S3"] + S3_PARTS] = e[["S3"] + S3_PARTS].fillna(0.0)
    e = e.sort_values(["race_date", "race_id", "run_id"], kind="mergesort").reset_index(drop=True)
    tr = _race(e[e.race_date < te_end].copy())
    te = _race(e[e.race_date.dt.year == y].copy())
    assert tr.race_date.max() < te.race_date.min()
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())

    VARS = {"staged": ["S1", "S2", "S3", "h_none"], "S1 + S2": ["S1", "S2", "h_none"], "S1": ["S1", "h_none"]}

    def score(fit_rows, rows):
        s12 = Stage12().fit(fit_rows)
        out = {}
        for df in (fit_rows, rows):
            a, b = s12.stages(df)
            df["S1"], df["S2"] = a.to_numpy(), b.to_numpy()
        for name, cols in VARS.items():
            beta = production._fit_raw(fit_rows, cols)
            out[name] = (om._softmax(production.utility(rows, beta), rows["race"].to_numpy()), beta)
        bp = production._fit_raw(fit_rows, production.COLS)
        out["prod"] = (om._softmax(production.utility(rows, bp), rows["race"].to_numpy()), None)
        if PROD_S3:       # adopted production (with rating mu), + S3, + S3's parts with their own weights
            rm = production.fit_mu(fit_rows)
            fr2, rows2 = production.add_mu(rm, fit_rows), production.add_mu(rm, rows)
            for df in (fr2, rows2):
                for ccol in S3_PARTS:
                    df[ccol] = df[ccol] - df.groupby("race_id")[ccol].transform("mean")
            base = production.COLS + production.MU
            for name, cols in [("prod mu", base), ("prod mu + S3", base + ["S3"]), ("prod mu + S3 parts", base + S3_PARTS)]:
                b_ = production._fit_raw(fr2, cols)
                out[name] = (om._softmax(production.utility(rows2, b_), rows2["race"].to_numpy()),
                             b_[[c for c in cols if c == "S3" or c in S3_PARTS]])
        return out, s12

    pre, _ = score(inner, bl)
    race, won = bl["race"].to_numpy(), bl["won"].to_numpy()
    lsp = bl["log_p_sp"].to_numpy(float)
    c = clogit.fit(lsp[:, None], race, won)[0]
    w = {k: clogit.fit(np.c_[np.log(np.clip(p, 1e-12, 1)), lsp], race, won) for k, (p, _) in pre.items()}
    post, s12 = score(tr, te)
    race = te["race"].to_numpy()
    lsp = te["log_p_sp"].to_numpy(float)
    ll = {"SP calibrated": race_ll(om._softmax(c * lsp, race), te)}
    for k, (p, _) in post.items():
        lp = np.log(np.clip(p, 1e-12, 1))
        ll[f"model {k}"] = race_ll(p, te)
        ll[f"blend {k}"] = race_ll(om._softmax(w[k][0] * lp + w[k][1] * lsp, race), te)
    info = {"S1+S2 WPR R2 (train)": s12.r2, **{k: v for k, v in s3.acc.items()},
            "ground cost global (WPR / m)": s3.gl_global,
            "stage weights (S1, S2, S3, debut)": tuple(np.round(post["staged"][1].to_numpy(), 4)),
            "blend a/b staged": tuple(np.round(w["staged"], 3)), "blend a/b prod": tuple(np.round(w["prod"], 3))}
    if PROD_S3:
        info["S3 weight in prod mu + S3 (per WPR)"] = float(post["prod mu + S3"][1]["S3"])
        info["S3 part weights"] = tuple(np.round(post["prod mu + S3 parts"][1].to_numpy(), 4))
    winners = te[te.won == 1][["race_id", "race_date", "state"]].reset_index(drop=True)
    return pd.concat([winners, pd.DataFrame(ll)], axis=1).assign(fold=y), info, s12.beta


def boot(x, rng):
    m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
    return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    shared = _frame(con)
    print("frame", len(shared["fr"]), flush=True)
    per, infos, betas = [], {}, {}
    for y in FOLDS:
        r, info, beta = run_fold(con, shared, y)
        per.append(r)
        infos[y], betas[y] = info, beta
        print(y, {k: round(float(v), 4) for k, v in r.drop(columns=["race_id", "race_date", "state", "fold"]).mean().items()},
              flush=True)
    d = pd.concat(per, ignore_index=True)
    # production + model-alone improvers (prod2 without figure v2), paired by race from the prod2 run
    p2 = ROOT / "reports/blend_per_race_prod2.csv.gz"
    if p2.exists():
        q = pd.read_csv(p2)[["race_id", "prod2-fig2: model logit", "prod2-fig2: blend logit"]]
        d = d.merge(q.rename(columns={"prod2-fig2: model logit": "model prod2 (no fig2)",
                                      "prod2-fig2: blend logit": "blend prod2 (no fig2)"}), on="race_id", how="left")
    tag = "_prod_s3" if PROD_S3 else ""
    d.to_csv(ROOT / f"reports/staged{tag}_per_race.csv.gz", index=False, float_format="%.6f")
    rng = np.random.default_rng(0)
    cols = [c for c in d.columns if c not in ("race_id", "race_date", "state", "fold")]
    t = d.groupby("fold")[cols].mean()
    t.loc["pooled"] = d[cols].mean()
    pairs = [("model staged", "model prod"), ("blend staged", "blend prod"), ("blend staged", "SP calibrated"),
             ("model S1 + S2", "model S1"), ("model staged", "model S1 + S2"), ("blend staged", "blend S1 + S2")]
    if PROD_S3:
        pairs = [("model prod mu + S3", "model prod mu"), ("blend prod mu + S3", "blend prod mu"),
                 ("model prod mu + S3 parts", "model prod mu"), ("blend prod mu + S3 parts", "blend prod mu"),
                 ("blend prod mu + S3", "SP calibrated")] + pairs
    if "blend prod2 (no fig2)" in d:
        pairs += [("model staged", "model prod2 (no fig2)"), ("blend staged", "blend prod2 (no fig2)")]
    rows = []
    for a, b in pairs:
        z = d[[a, b, "state"]].dropna()
        x = (z[a] - z[b]).to_numpy()
        qm = (z["state"] == "QLD").to_numpy()
        rows.append({"first": a, "minus": b, "races": len(x), "all": boot(x, rng), "QLD": boot(x[qm], rng),
                     "VIC/SA": boot(x[~qm], rng)})
    B = pd.DataFrame(betas)
    B.index.name = "input"
    B.insert(0, "stage", ["S1 ability" if c in S1_X else "S2 conditions" for c in B.index])
    L = ["# Staged model: ability -> conditions -> race shape -> win probability", "",
         "- S1 ability and S2 conditions: one ridge regression of today's WPR (within race) on history and today's"
         " conditions; S3 race shape: projected lengths behind the leader, width, early / mid / late pace, valued by"
         " track bias maps (track, distance, going, rail) plus a track-specific cost per extra metre",
         "- Final: conditional logit on S1, S2, S3 and a debut flag; walk-forward 2023 to 2026, VIC/SA/QLD", "",
         "## Log loss by fold", "", t.T.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "## Stage fits and accuracy by fold", "", pd.DataFrame(infos).to_markdown(floatfmt=".4f"), "",
         "## S1 / S2 weights: WPR points per unit of each input (fit on all training rows)", "",
         B.sort_values(["stage", "input"]).to_markdown(floatfmt=".3f")]
    (ROOT / f"reports/staged{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
