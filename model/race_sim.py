"""Race-shape simulation: jointly draw settling positions and pace for the whole field, value each horse's run.

    python model/race_sim.py      # walk-forward -> reports/race_sim.md, reports/race_sim_per_runner.csv.gz

Per race, D draws of:
  settle   latent_i = projected settle share (v4, projection_v4.py) + sigma_i * z_i; ranking the latents gives every runner a position
           (only one horse can lead; two speed horses cannot both be first). sigma_i grows with thin or noisy
           settle history (fitted: |settle residual| on debut, runs with a position, first up, settle spread)
  pace     GPS pace (projection_gps.py: leaders' early speed vs the field's late speed), relative to the distance
           band mean. Projected by a model trained on GPS races (v3 pace inputs, v4 settle); per draw
           pace = projected + b * (early speed of the 3 drawn leaders - early speed of the 3 projected leaders)
           + noise (sd and b from held-out GPS races): a draw where two fast horses both go forward is hotter.
           Buckets: slow / even / fast = terciles of GPS pace on training GPS races. Past runs without GPS are
           bucketed by TopRate early shape mapped onto the GPS scale (linear fit on GPS races)
  value    V(position bin, pace bin | track, distance, going, rail): WPR points a run in that position and pace is
           worth vs the race average (position_map's shrunk hierarchy, on the 800m position share: leader, then
           fifths of the field)
Win probability, per draw exact under the logit's Gumbel noise:
  P(i wins | draw) = softmax(u_i + k * unit * V_i,draw),  p_sim = mean over draws
  u = production logit WITHOUT the settle / pace projection terms (they are what the simulation replaces);
  unit = its utility per WPR point; k = weight on the simulated position value (fitted by likelihood)
Walk-forward like blend_eval.py: per test year Y, fits on the first 75% of training predict the last 25% (the
blend window) where k and the SP blend weights are fitted; final fits on all training rows score year Y.
Compared, paired by race: production logit blend, simulation blend, and a three-way blend (production +
simulation + SP) that shows whether the simulation adds anything the production model does not have.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure, position_map, production  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
D = 400                       # draws per race
N_POS, N_PACE = 6, 3          # leader + fifths of the field; slow / even / fast
POSITIONAL = ["proj_settle", "proj_settle_rank", "proj_shape", "proj_pace", "proj_adj", "early_rank2",
              "wide_x_slow", "nb_diff_in", "nb_diff_out", "tdx_settle", "tdx_perf"]
BASE_COLS = [c for c in production.COLS if c not in POSITIONAL]
PX = ["run_id", "race_id", "race_date", "dist", "track", "going_num", "rail_m", "wpr", "h_wpr", "h_none",
      "y_settle", "y_shape", "proj_settle", "proj_shape", "es_today", "st_n", "st_sd", "first_up", "field_n",
      "synth", "track_code", "y_lead_early"]
DIST_BANDS = [0, 1100, 1300, 1600, 2000, 9999]
BOOT = 2000


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def _pos_bin(share):
    share = np.asarray(share, float)
    return np.where(share <= 0, 0, np.clip(np.ceil(share / 0.2), 1, 5)).astype(int)


# ---------------------------------------------------------------- fitted pieces (past rows only)

class SimParts:
    """Fitted on past rows only (race_date < end). px: runner frame with sim_settle; rr: race frame (PACE_X,
    y_shape, gps_pace, dist, race_date) indexed by race_id."""

    def fit(self, px, rr, end):
        from model.projection import PACE_X, _fit
        p = px[(px["race_date"] < end) & (px["race_date"] >= "2019-01-01")]
        R = rr[(rr["race_date"] < end) & (rr["race_date"] >= "2019-01-01")].copy()
        # GPS pace relative to the distance band; TopRate shape mapped onto that scale for races without GPS
        R["band"] = pd.cut(R["dist"], DIST_BANDS, labels=False)
        g = R[R["gps_pace"].notna()].copy()
        self.band_mean = g.groupby("band")["gps_pace"].mean()
        g["pace_rel"] = g["gps_pace"] - g["band"].map(self.band_mean)
        gm = g[g["y_shape"].notna()]
        self.map_ab = np.polyfit(gm["y_shape"].to_numpy(float), gm["pace_rel"].to_numpy(float), 1)
        mapped = pd.Series(np.polyval(self.map_ab, R["y_shape"].to_numpy(float)), index=R.index)
        R["pace_act"] = (R["gps_pace"] - R["band"].map(self.band_mean)).fillna(mapped)   # NaN if neither
        self.cuts = list(np.percentile(g["pace_rel"], [100 / 3, 200 / 3]))
        # GPS pace model: noise sd and lead response from held-out (latest 20%) GPS races, then refit on all
        g = g.sort_values("race_date")
        n_fit = int(len(g) * 0.8)
        m = _fit(g.iloc[:n_fit][PACE_X], g.iloc[:n_fit]["pace_rel"])
        ho = g.iloc[n_fit:].copy()
        ho["proj"] = m.predict(ho[PACE_X].to_numpy(float))
        s = p[p["y_settle"].notna() & p["sim_settle"].notna()]
        esf = self._esf(s, "y_settle").to_frame("act").join(self._esf(s, "sim_settle").rename("proj"))
        ho = ho.join(esf.rename(columns={"proj": "esf_proj", "act": "esf_act"})).dropna(subset=["esf_act", "esf_proj"])
        dx = (ho["esf_act"] - ho["esf_proj"]).to_numpy()
        dy = (ho["pace_rel"] - ho["proj"]).to_numpy()
        self.b = float(dx @ dy / (dx @ dx))
        self.pace_sd = float(np.std(dy - self.b * dx))
        self.pace_holdout_corr = float(np.corrcoef(ho["pace_rel"], ho["proj"])[0, 1])
        self.pace_model = _fit(g[PACE_X], g["pace_rel"])
        self._pace_x = PACE_X
        # value map on every past run with a position and a pace
        x = p[p["y_settle"].notna() & p["wpr"].notna() & (p["h_none"] == 0)].copy()
        x["pace_act"] = x["race_id"].map(R["pace_act"])
        x = x[x["pace_act"].notna()]
        res = x["wpr"] - x["h_wpr"]
        x["r"] = res - res.groupby(x["race_id"]).transform("mean")
        x["w"] = 0.5 ** ((pd.Timestamp(end) - x["race_date"]).dt.days.clip(lower=0) / position_map.HALF_LIFE_DAYS)
        x["pos_b"] = _pos_bin(x["y_settle"])
        x["pace_b"] = np.digitize(x["pace_act"], self.cuts)
        x = pd.concat([x, position_map._context(x)], axis=1)
        self.tabs = position_map._fit_levels(x, ["pos_b", "pace_b"], ["cx_g", "cx_t", "cx_td", "cx_go", "cx_tr"])
        # settle noise
        self.gamma = np.linalg.lstsq(self._z(s), np.abs(s["y_settle"] - s["sim_settle"]).to_numpy(float), rcond=None)[0]
        return self

    def pace_proj(self, rr):
        """Projected GPS pace (relative to the distance band) per race_id."""
        return pd.Series(self.pace_model.predict(rr[self._pace_x].to_numpy(float)), index=rr.index)

    @staticmethod
    def _z(df):
        return np.c_[np.ones(len(df)), df["h_none"], np.log1p(df["st_n"].fillna(0)), df["first_up"].fillna(0),
                     df["st_sd"].fillna(0.25)]

    @staticmethod
    def _esf(df, col):
        t = df.assign(_k=df[col].round(6)).sort_values(["race_id", "_k", "run_id"], kind="mergesort")
        return t.groupby("race_id").head(3).groupby("race_id")["es_today"].mean()

    def sigma(self, df):
        return np.maximum(self._z(df) @ self.gamma * np.sqrt(np.pi / 2), 0.03)

    def values(self, df):
        """V for every row x (position bin, pace bin): (n, N_POS * N_PACE), WPR points."""
        ctx = position_map._context(df)
        cells = [(a, b) for a in range(N_POS) for b in range(N_PACE)]
        return position_map._lookup(self.tabs, ctx, ["pos_b", "pace_b"], cells)


def draws(df, parts, seed=0):
    """Simulated position value per runner and draw, (n_rows, D) float32, P(lead) per runner and
    P(slow / even / fast pace) per runner's race (n_rows, N_PACE).
    df sorted by race; needs sim_settle, sim_pace0 (projected GPS pace), es_today, sigma inputs and context."""
    rng = np.random.default_rng(seed)
    V = parts.values(df).astype(np.float32)
    sig = parts.sigma(df)
    ps = df["sim_settle"].fillna(0.5).to_numpy(float)
    es = df["es_today"].fillna(df["es_today"].median()).to_numpy(float)
    shape0 = df["sim_pace0"].fillna(0).to_numpy(float)
    out = np.zeros((len(df), D), np.float32)
    lead = np.zeros(len(df))
    pace_p = np.zeros((len(df), N_PACE))
    race = df["race_id"].to_numpy()
    starts = np.r_[0, np.flatnonzero(race[1:] != race[:-1]) + 1, len(df)]
    sizes = np.diff(starts)
    for n in np.unique(sizes):
        idx0 = starts[:-1][sizes == n]
        for c0 in range(0, len(idx0), 400):
            ii = idx0[c0:c0 + 400, None] + np.arange(n)[None, :]            # (R, n) row indices
            R = len(ii)
            lat = ps[ii][:, None, :] + sig[ii][:, None, :] * rng.standard_normal((R, D, n))
            rank = lat.argsort(-1).argsort(-1)                               # 0 = leader
            share = rank / max(n - 1, 1)
            pb = _pos_bin(share)
            k3 = min(3, n)
            front = np.argpartition(lat, k3 - 1, axis=-1)[..., :k3]
            esf = np.take_along_axis(np.broadcast_to(es[ii][:, None, :], lat.shape), front, -1).mean(-1)
            p0 = np.argsort(ps[ii].round(6), -1, kind="stable")[:, :k3]
            esf0 = np.take_along_axis(es[ii], p0, -1).mean(-1)
            shape = shape0[ii[:, 0]][:, None] + parts.b * (esf - esf0[:, None]) + \
                parts.pace_sd * rng.standard_normal((R, D))
            pace = np.digitize(shape, parts.cuts)                            # (R, D)
            cell = pb * N_PACE + pace[:, :, None]                            # (R, D, n)
            v = np.take_along_axis(np.broadcast_to(V[ii][:, None, :, :], (R, D, n, V.shape[1])),
                                   cell[..., None], -1)[..., 0]
            out[ii.ravel()] = v.transpose(0, 2, 1).reshape(R * n, D)
            lead[ii.ravel()] = (rank == 0).mean(1).ravel()
            pp = np.stack([(pace == b).mean(1) for b in range(N_PACE)], 1)          # (R, N_PACE)
            pace_p[ii.ravel()] = np.repeat(pp, n, axis=0)
    return out, lead, pace_p


def sim_probs(u, Vd, k, unit, race):
    """p_i = mean over draws of softmax(u + k * unit * V_draw) within race."""
    s = u[:, None] + k * unit * Vd.astype(float)
    starts = om._starts(race)
    cnt = np.diff(np.r_[starts, len(s)])
    s = s - np.repeat(np.maximum.reduceat(s, starts, axis=0), cnt, axis=0)
    ex = np.exp(s)
    return (ex / np.repeat(np.add.reduceat(ex, starts, axis=0), cnt, axis=0)).mean(1)


def _nll(p, df):
    return -np.log(np.clip(p[df["won"].to_numpy() == 1], 1e-12, 1)).mean()


# ---------------------------------------------------------------- walk-forward

def run_fold(con, y):
    te_end = f"{y}-01-01"
    from model import projection, projection_gps
    om.PX_KEEP[:] = PX
    om.SETTLE_V4 = True
    e = om.add_context(om.build(con, te_end))
    px = om.LAST_PX.pop("px")
    px["sim_settle"] = px["proj_settle_v4"].fillna(px["proj_settle"])
    rr = projection._pace_frame(px.assign(proj_settle=px["sim_settle"]))
    rr = rr.join(projection_gps.gps_pace(con).rename("gps_pace"))
    extra = [c for c in PX + ["sim_settle"] if c not in e.columns]
    e = e.merge(px[["run_id"] + extra], on="run_id", how="left")
    e = e.sort_values(["race_date", "race_id", "run_id"], kind="mergesort").reset_index(drop=True)
    tr = _race(e[e.race_date < te_end].copy())
    te = _race(e[e.race_date.dt.year == y].copy())
    assert tr.race_date.max() < te.race_date.min()
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())

    def fit_all(fit_rows, score, parts):
        b_prod = production._fit_raw(fit_rows, production.COLS)
        b_base = production._fit_raw(fit_rows, BASE_COLS)
        unit = b_base[production.WPR_LEVEL].sum()
        race = score["race"].to_numpy()
        p_prod = om._softmax(production.utility(score, b_prod), race)
        u = production.utility(score, b_base)
        p_base = om._softmax(u, race)
        score = score.assign(sim_pace0=score["race_id"].map(parts.pace_proj(rr)).to_numpy())
        Vd, lead, _ = draws(score, parts)
        return p_prod, p_base, u, unit, Vd, lead

    parts_bl = SimParts().fit(px, rr, cut)
    p_prod, p_base, u, unit, Vd, _ = fit_all(inner, bl, parts_bl)
    race = bl["race"].to_numpy()
    k = minimize_scalar(lambda k: _nll(sim_probs(u, Vd, k, unit, race), bl), bounds=(0, 3), method="bounded",
                        options={"xatol": 0.01}).x
    p_sim = sim_probs(u, Vd, k, unit, race)
    lp = {"prod": np.log(np.clip(p_prod, 1e-12, 1)), "sim": np.log(np.clip(p_sim, 1e-12, 1)),
          "base": np.log(np.clip(p_base, 1e-12, 1)), "sp": bl["log_p_sp"].to_numpy(float)}
    won = bl["won"].to_numpy()
    c = clogit.fit(lp["sp"][:, None], race, won)[0]
    w = {m: clogit.fit(np.c_[lp[m], lp["sp"]], race, won) for m in ["prod", "sim", "base"]}
    w3 = clogit.fit(np.c_[lp["prod"], lp["sim"], lp["sp"]], race, won)
    del Vd

    parts = SimParts().fit(px, rr, te_end)
    p_prod, p_base, u, unit, Vd, lead = fit_all(tr, te, parts)
    race = te["race"].to_numpy()
    p_sim = sim_probs(u, Vd, k, unit, race)
    del Vd
    L = {"prod": np.log(np.clip(p_prod, 1e-12, 1)), "sim": np.log(np.clip(p_sim, 1e-12, 1)),
         "base": np.log(np.clip(p_base, 1e-12, 1)), "sp": te["log_p_sp"].to_numpy(float)}
    P = {"SP calibrated": om._softmax(c * L["sp"], race)}
    for m in ["prod", "sim", "base"]:
        P[f"model {m}"] = np.exp(L[m])
        P[f"blend {m}"] = om._softmax(w[m][0] * L[m] + w[m][1] * L["sp"], race)
    P["blend prod + sim"] = om._softmax(w3[0] * L["prod"] + w3[1] * L["sim"] + w3[2] * L["sp"], race)
    runners = te[["race_id", "run_id", "race_date", "state", "sp", "p_sp", "won", "barrier_pct"]].copy()
    for name, p in P.items():
        runners[name] = p
    runners["sim p_lead"] = lead
    runners["actual led"] = (te["y_settle"] == 0).astype(float).where(te["y_settle"].notna())
    runners["fold"] = y
    ll = {name: race_ll(p, te) for name, p in P.items()}
    info = {"k": k, "unit": unit, "pace b": parts.b, "pace sd": parts.pace_sd,
            "pace cuts": tuple(np.round(parts.cuts, 2)), "GPS pace holdout corr": parts.pace_holdout_corr,
            "blend prod a/b": tuple(np.round(w["prod"], 3)), "blend sim a/b": tuple(np.round(w["sim"], 3)),
            "3-way prod/sim/sp": tuple(np.round(w3, 3))}
    winners = te[te.won == 1][["race_id", "state"]].reset_index(drop=True)
    return pd.concat([winners, pd.DataFrame(ll)], axis=1).assign(fold=y), runners, info


def boot(x, rng):
    m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
    return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    per, runners, infos = [], [], {}
    for y in FOLDS:
        r, ru, info = run_fold(con, y)
        per.append(r)
        runners.append(ru)
        infos[y] = info
        print(y, {k: round(float(v), 4) for k, v in r.drop(columns=["race_id", "state", "fold"]).mean().items()},
              info, flush=True)
    d = pd.concat(per, ignore_index=True)
    ru = pd.concat(runners, ignore_index=True)
    ru.to_csv(ROOT / "reports/race_sim_per_runner.csv.gz", index=False, float_format="%.6f")
    rng = np.random.default_rng(0)
    cols = [c for c in d.columns if c not in ("race_id", "state", "fold")]
    t = d.groupby("fold")[cols].mean()
    t.loc["pooled"] = d[cols].mean()
    pairs = [("blend sim", "blend prod"), ("blend prod + sim", "blend prod"), ("blend prod", "SP calibrated"),
             ("blend sim", "SP calibrated"), ("blend prod + sim", "SP calibrated"), ("model sim", "model base"),
             ("model sim", "model prod")]
    rows = []
    for a, b in pairs:
        x = (d[a] - d[b]).to_numpy()
        q = (d["state"] == "QLD").to_numpy()
        rows.append({"first": a, "minus": b, "all": boot(x, rng), "QLD": boot(x[q], rng), "VIC/SA": boot(x[~q], rng)})
    # calibration of the simulated leader
    c = ru.dropna(subset=["actual led"])
    c = c.assign(bin=pd.cut(c["sim p_lead"], [0, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0], include_lowest=True))
    cal = c.groupby("bin", observed=True).agg(runners=("run_id", "size"), sim=("sim p_lead", "mean"),
                                              actual=("actual led", "mean"))
    L = ["# Race-shape simulation", "",
         "- Settle: v4 projection; pace: GPS pace model (terciles of distance-relative GPS pace)",
         f"- {D} joint draws per race of settling positions and pace; position value V(position, pace | track,"
         " distance, going, rail) in WPR points; win probability exact per draw under the logit's Gumbel noise",
         "- Base logit = production inputs minus the settle / pace projection terms (replaced by the simulation);"
         " k = weight on simulated position value, fitted on the blend window",
         "- Walk-forward 2023 to 2026, VIC/SA/QLD; blend weights and k never see the test year", "",
         "## Log loss by fold", "", t.T.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "## Simulated leader calibration (test years)", "", cal.to_markdown(floatfmt=".3f"), "",
         "## Fitted values by fold", "", pd.DataFrame(infos).to_markdown()]
    (ROOT / "reports/race_sim.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
