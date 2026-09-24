"""Explicit rating model: expected WPR today = ability + race-day adjustments, with a per-horse uncertainty.

    mu_i    = sum_k beta_k * x_ik          (WPR points; x = ability and adjustment inputs, all pre-race)
    sigma_i = uncertainty of horse i's performance today (WPR points)
    P(i wins) = P(mu_i + sigma_i z_i > mu_j + sigma_j z_j for every rival j), z ~ N(0, 1) independent
              (Thurstone model; computed by Gauss-Hermite integration, no simulation noise)

Fitting (training rows only):
  beta   least squares of today's WPR on the inputs, both demeaned within the race (only relative
         performance matters for who wins), small ridge penalty. Each beta is a bonus / penalty in WPR points.
  sigma  |residual| regressed on uncertainty drivers (debut, runs, first up, days, form spread, health
         note last start, age), times sqrt(pi / 2), floored.
  scale  one global multiplier on sigma, fitted by maximum likelihood of the winners on the training rows.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.special import ndtr

ABILITY = ["dm_v2", "fig_last_v2", "best3_v2", "best10_v2", "trend_v2", "h_class", "log_n", "h_none",
           "trial_pos_debut", "trial_marg_debut", "age2", "age3", "age7", "female"]
ADJUST = ["proj_adj", "bias_adj", "tdx_perf", "proj_settle", "proj_pace", "proj_gl", "barrier_pct",
          "dist_ratio", "dist_abs", "dist_fit_v2", "going_fit_v2", "surface_fit_v2",
          "fu", "su", "up3", "fu_apt_v2", "su_apt_v2", "log_days", "trial_since", "trial_pos", "trial_marg",
          "wt_rel_today", "j_ae", "j_sr", "t_ae", "t_sr", "c_ae", "tfu_ae", "j_upgrade", "j_change", "h_ae"]
COMMENTS = ["cm_last_tag", "cm_dm_tag", "cm_last_checked", "cm_last_vblocked", "cm_last_slow", "cm_last_wide",
            "cm_last_vwide", "cm_last_health", "cm_last_over", "cm_dm_checked", "cm_dm_vblocked"]
X_COLS = ABILITY + ADJUST + COMMENTS
SIGMA_COLS = ["h_none", "log_n", "first_up", "log_days", "fig_sd", "cm_last_health", "age2", "age3", "age7"]
RIDGE = 1.0
SIGMA_FLOOR = 2.0
GH = np.polynomial.hermite_e.hermegauss(40)      # nodes / weights for E[f(z)], z ~ N(0,1) (weights sum sqrt(2 pi))


def win_probs(mu, sigma, race, chunk=1000):
    """Thurstone win probabilities per runner. race = contiguous int race index per row."""
    z, w = GH[0], GH[1] / np.sqrt(2 * np.pi)
    starts = np.r_[0, np.flatnonzero(np.diff(race)) + 1]
    sizes = np.diff(np.r_[starts, len(race)])
    out = np.empty(len(mu))
    n_max = sizes.max()
    for c0 in range(0, len(starts), chunk):
        st, sz = starts[c0:c0 + chunk], sizes[c0:c0 + chunk]
        R = len(st)
        M = np.full((R, n_max), -1e9)
        S = np.ones((R, n_max))
        idx = st[:, None] + np.arange(n_max)[None, :]
        valid = np.arange(n_max)[None, :] < sz[:, None]
        M[valid], S[valid] = mu[idx[valid]], sigma[idx[valid]]
        # x = mu_i + sigma_i z_k : shape (R, n_i, K)
        x = M[:, :, None] + S[:, :, None] * z[None, None, :]
        # log Phi((x - mu_j) / sigma_j) for every j: (R, n_i, n_j, K)
        lp = np.log(np.clip(ndtr((x[:, :, None, :] - M[:, None, :, None]) / S[:, None, :, None]), 1e-300, 1))
        lp = np.where(valid[:, None, :, None], lp, 0.0)
        tot = lp.sum(2)                                                    # (R, n_i, K) incl. j = i
        ar = np.arange(n_max)
        own = lp[:, ar, ar, :]                                             # (R, n_i, K): the j = i term
        p = (np.exp(tot - own) * w[None, None, :]).sum(2)
        p = p / np.where(valid, p, 0).sum(1, keepdims=True)
        out[idx[valid]] = p[valid]
    return out


def _filled(df, cols):
    """Inputs with gaps (e.g. no weight in the dashboard runners file) set to the field average, else 0."""
    X = df[cols].astype(float)
    return X.fillna(X.groupby(df["race_id"].to_numpy()).transform("mean")).fillna(0.0)


def _dm(df, cols):
    X = _filled(df, cols)
    return X - X.groupby(df["race_id"].to_numpy()).transform("mean")


class RatingModel:
    def fit(self, tr):
        tr = tr[tr["y_wpr"].notna()]
        X = _dm(tr, X_COLS).to_numpy(float)
        y = (tr["y_wpr"] - tr.groupby("race_id")["y_wpr"].transform("mean")).to_numpy(float)
        sd = X.std(0)
        sd[sd == 0] = 1
        Xs = X / sd
        self.beta = np.linalg.solve(Xs.T @ Xs + RIDGE * np.eye(Xs.shape[1]), Xs.T @ y) / sd
        res = np.abs(y - (X @ self.beta))
        Z = np.c_[np.ones(len(tr)), _filled(tr, SIGMA_COLS).to_numpy(float)]
        self.gamma = np.linalg.lstsq(Z, res, rcond=None)[0]
        self.scale = 1.0
        return self

    def mu(self, df):
        return _filled(df, X_COLS).to_numpy(float) @ self.beta

    def sigma(self, df):
        Z = np.c_[np.ones(len(df)), _filled(df, SIGMA_COLS).to_numpy(float)]
        return np.maximum(Z @ self.gamma * np.sqrt(np.pi / 2), SIGMA_FLOOR)

    def calibrate(self, df):
        """Fit the global sigma scale by maximum likelihood of the winners (df: training rows, race index)."""
        mu, sg, race, won = self.mu(df), self.sigma(df), df["race"].to_numpy(), df["won"].to_numpy()

        def nll(k):
            p = win_probs(mu, sg * k, race)
            return -np.log(np.clip(p[won == 1], 1e-12, 1)).mean()
        self.scale = minimize_scalar(nll, bounds=(0.3, 3.0), method="bounded", options={"xatol": 0.01}).x
        return self

    def predict(self, df):
        return win_probs(self.mu(df), self.sigma(df) * self.scale, df["race"].to_numpy())

    def table(self):
        """Bonus / penalty per unit of each input, WPR points."""
        return pd.Series(self.beta, index=X_COLS)


def add_fig_sd(e):
    """Spread of the horse's recent figures (v2): best of last 3 minus the decayed mean, a cheap proxy."""
    e = e.copy()
    e["fig_sd"] = (e["best3_v2"] - e["dm_v2"]).abs().where(e["h_none"] == 0, 0.0)
    return e


def fit(tr, calib_races=8000):
    """Fit on training rows; calibrate the sigma scale on the most recent calib_races training races."""
    tr = add_fig_sd(tr)
    m = RatingModel().fit(tr)
    recent = tr[tr["race_id"].isin(tr.drop_duplicates("race_id").tail(calib_races)["race_id"])]
    recent = recent.assign(race=pd.factorize(recent["race_id"])[0])
    m.calibrate(recent)
    return lambda df, m=m: m.predict(add_fig_sd(df)), m
