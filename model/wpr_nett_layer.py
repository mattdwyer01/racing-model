"""TopRate wpr_nett as a top layer on the production model's win chances (live race cards / dashboard only).

wpr_nett (TopRate's own current rating) exists only in the dashboard runners file (26 Apr 2026 on), so it cannot be
a walk-forward input. Tested as an offset on production's out-of-sample log chance (`model/gear_wpr_test.py`,
`reports/gear_wpr_test_oct.md`, 6,422 races 26 Apr to 2 Oct 2026, 5 states, half-window swap): model alone -0.0074
(-0.0106 to -0.0043; every state), blend with SP +0.0001 (n.s.). Meets the adoption rule (CLAUDE.md).

    p = softmax(W_MODEL * log p_production + W_REL * (wpr_nett - race mean) + W_MISS * missing)

Weights = mean of the two half-window fits. Missing wpr_nett takes the race mean (and the missing flag). Refit with
model/gear_wpr_test.py when there is more data; switch off with RACING_WPR_NETT=0.
"""
import os

import numpy as np
import pandas as pd

W_MODEL, W_REL, W_MISS = 0.834, 0.049, 0.128
ENABLED = os.environ.get("RACING_WPR_NETT", "1") != "0"


def apply(race_id, p_model, wpr_nett):
    """Layered win chances (sum to 1 per race). Inputs aligned arrays / Series."""
    race = pd.Series(np.asarray(race_id))
    wn = pd.Series(pd.to_numeric(pd.Series(np.asarray(wpr_nett)), errors="coerce").to_numpy())
    miss = wn.isna().astype(float)
    wn = wn.fillna(wn.groupby(race).transform("mean")).fillna(0.0)
    rel = wn - wn.groupby(race).transform("mean")
    z = W_MODEL * np.log(np.clip(np.asarray(p_model, float), 1e-12, 1)) + W_REL * rel + W_MISS * miss
    z = z - z.groupby(race).transform("max")
    e = np.exp(z)
    return (e / e.groupby(race).transform("sum")).to_numpy()
