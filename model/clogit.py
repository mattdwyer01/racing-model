"""Conditional (multinomial per race) logit.

Rows must be sorted so each race is contiguous. `race` is an int group id per row,
`won` is 1 for the single winner of each race.
"""
import numpy as np
from scipy.optimize import minimize


def _starts(race):
    return np.r_[0, np.flatnonzero(np.diff(race)) + 1]


def probs(X, race, beta):
    s = _starts(race)
    u = X @ beta
    u = u - np.repeat(np.maximum.reduceat(u, s), np.diff(np.r_[s, len(u)]))
    e = np.exp(u)
    return e / np.repeat(np.add.reduceat(e, s), np.diff(np.r_[s, len(u)]))


def fit(X, race, won, l2=1e-4):
    n_races = len(_starts(race))

    def f(beta):
        p = probs(X, race, beta)
        ll = np.log(p[won == 1]).sum()
        g = X.T @ (won - p)
        return -ll / n_races + l2 * beta @ beta, -g / n_races + 2 * l2 * beta

    r = minimize(f, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B")
    return r.x


def logloss(p, won, race):
    """Mean -log p(winner) per race."""
    return -np.log(np.clip(p[won == 1], 1e-12, 1)).mean()
