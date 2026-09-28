"""Projected leader value: how much a forward position is worth in this race (tools/pace_forecast_test.py).

Target per race = realised leader value: within-race slope of (WPR - prior avg WPR) on projected settle share
(negative = forward runners ran better than their ability), weighted by the race's settle spread. Inputs: the v3
pace inputs (projection.PACE_X) + NEW (horse pace history, early speed contest, jockey / barrier of the fastest,
class, track x distance past shape and leader value). LightGBM, small trees.

project_lv(x, r, train_end) gives every race an out-of-sample value: races in year Z (2021 up to train_end) from a
fit on races before Z, races on / after train_end from a fit on everything before train_end. So a win model trained
on races before train_end sees the same kind of (out-of-sample) values it gets on race day.
Win-model input: lv_x = (projected settle share - race mean) x projected leader value.
"""
import lightgbm as lgb
import numpy as np
import pandas as pd

from model import projection
from model.projection import K, PACE_X, _lags

NEW = ["es_1", "es_2", "es_gap", "n_es_close", "lead_sum", "lead_max", "lead_2nd", "fwd_sum", "led_early_max",
       "led_early_2nd", "front3_shape_hist", "front3_lead", "front3_jfwd", "fast_bar", "fast_jfwd",
       "class_level", "maiden", "te_td_shape", "te_track_shape", "te_td_lv", "rail_m"]
X_LV = PACE_X + NEW
CLASS_SQL = "select race_id, class_level, (class_type ilike '%maiden%')::double maiden, res_shape_mid y_mid from races"
LV_PARAMS = dict(projection.PARAMS, num_leaves=15, min_data_in_leaf=1000, learning_rate=0.03, cat_smooth=50)
LV_ROUNDS = 300
FEATS = ["lv_x"]


def decayed(x, v, mask=None):
    """Decayed mean over the horse's last K runs of column v (optionally only runs where mask col is 1)."""
    a = _lags(x, v)
    ok = ~np.isnan(a)
    if mask is not None:
        ok &= _lags(x, mask) == 1
    w = np.where(ok, 0.5 ** (np.arange(K) / 3.0), 0)
    return np.where(ok.any(1), (w * np.nan_to_num(a)).sum(1) / np.maximum(w.sum(1), 1e-9), np.nan), ok.sum(1)


def horse_history(x):
    """Pace history per run (x sorted by horse, date as projection.frame leaves it)."""
    x["_led"] = (x["y_settle"] == 0).astype(float).where(x["y_settle"].notna())
    x["_fwd"] = (x["y_settle"] <= 0.2).astype(float).where(x["y_settle"].notna())
    x["hp_lead_rate"], n = decayed(x, "_led")
    x["hp_fwd_rate"], _ = decayed(x, "_fwd")
    x["hp_led_early"], _ = decayed(x, "y_lead_early", "_led")
    x["hp_shape_fwd"], _ = decayed(x, "y_shape", "_fwd")
    x["hp_n"] = n
    return x.drop(columns=["_led", "_fwd"])


def target_enc(r, key, col, lam):
    """Past mean of col per key, strictly earlier dates, shrunk to 0 with lam pseudo-races."""
    t = r[[*key, "race_date", col]].dropna(subset=[col])
    g = t.groupby([*key, "race_date"])[col].agg(["sum", "count"]).reset_index().sort_values("race_date")
    cs = g.groupby(key)[["sum", "count"]].cumsum() - g[["sum", "count"]].to_numpy()
    g["te"] = cs["sum"] / (cs["count"] + lam)
    return r[[*key, "race_date"]].merge(g[[*key, "race_date", "te"]], on=[*key, "race_date"], how="left")["te"].to_numpy()


def race_features(x, r):
    """NEW race-level inputs from runner rows x (with proj_settle, horse_history) onto race frame r (index race_id)."""
    x = x[["race_id", "proj_settle", "es_today", "hp_lead_rate", "hp_fwd_rate", "hp_led_early", "hp_shape_fwd",
           "jockey_fwd", "barrier_pct"]].copy()
    es = x.sort_values(["race_id", "es_today"], ascending=[True, False])
    top = es.groupby("race_id").head(2)
    rk = top.groupby("race_id").cumcount()
    f = pd.DataFrame(index=r.index)
    f["es_1"] = top[rk == 0].set_index("race_id")["es_today"]
    f["es_2"] = top[rk == 1].set_index("race_id")["es_today"]
    f["es_gap"] = f["es_1"] - f["es_2"]
    x["_close"] = (x["es_today"] >= x["race_id"].map(f["es_1"]) - 1.5).astype(float)
    f["n_es_close"] = x.groupby("race_id")["_close"].sum()
    fast = es.groupby("race_id").head(1).set_index("race_id")
    f["fast_bar"], f["fast_jfwd"] = fast["barrier_pct"], fast["jockey_fwd"]
    lr = x["hp_lead_rate"].fillna(0)
    f["lead_sum"] = lr.groupby(x["race_id"]).sum()
    s = x.assign(_lr=lr).sort_values(["race_id", "_lr"], ascending=[True, False])
    rk = s.groupby("race_id").cumcount()
    f["lead_max"] = s[rk == 0].set_index("race_id")["_lr"]
    f["lead_2nd"] = s[rk == 1].set_index("race_id")["_lr"]
    f["fwd_sum"] = x["hp_fwd_rate"].fillna(0).groupby(x["race_id"]).sum()
    s = x.dropna(subset=["hp_led_early"]).sort_values(["race_id", "hp_led_early"], ascending=[True, False])
    rk = s.groupby("race_id").cumcount()
    f["led_early_max"] = s[rk == 0].set_index("race_id")["hp_led_early"]
    f["led_early_2nd"] = s[rk == 1].set_index("race_id")["hp_led_early"]
    fr = x.sort_values(["race_id", "proj_settle"]).groupby("race_id").head(3).groupby("race_id")
    f["front3_shape_hist"] = fr["hp_shape_fwd"].mean()
    f["front3_lead"] = fr["hp_lead_rate"].mean()
    f["front3_jfwd"] = fr["jockey_fwd"].mean()
    for c in f.columns:
        r[c] = f[c]
    return r


def race_lv(x, col="proj_settle"):
    """Per race: within-race slope of perf (WPR - prior avg WPR) on col, and its weight (sum of squares of col)."""
    t = x[(x["h_none"] == 0) & x["wpr"].notna()][["race_id", col, "wpr", "h_wpr"]].copy()
    t["perf"] = t["wpr"] - t["h_wpr"]
    t = t[t.groupby("race_id")["perf"].transform("size") >= 4]
    xd = t[col] - t.groupby("race_id")[col].transform("mean")
    yd = t["perf"] - t.groupby("race_id")["perf"].transform("mean")
    return pd.DataFrame({"sxy": xd * yd, "sxx": xd * xd, "race_id": t["race_id"]}).groupby("race_id").sum()


def race_frame(con, x, r):
    """Add every leader-value input and the target (lv, lv_w) to the race frame r. x: projected runner frame."""
    if "hp_lead_rate" not in x:
        x = horse_history(x)
    r = r.join(con.sql(CLASS_SQL).df().set_index("race_id")[["class_level", "maiden"]])
    r = race_features(x, r)
    lv = race_lv(x)
    r["lv_w"] = lv["sxx"]
    r["lv"] = (lv["sxy"] / lv["sxx"]).where(r["lv_w"] > 0.05).clip(-40, 40)
    r["dist_b"] = pd.cut(r["dist"], [0, 1050, 1250, 1450, 1700, 2100, 9999], labels=False)
    rr = r.reset_index()
    r["te_td_shape"] = target_enc(rr, ["track_code", "dist_b"], "y_shape", 20)
    r["te_track_shape"] = target_enc(rr, ["track_code"], "y_shape", 20)
    r["te_td_lv"] = target_enc(rr, ["track_code", "dist_b"], "lv", 50)
    r["rail_m"] = x.groupby("race_id")["rail_m"].first()
    return r


def fit_lv(r, mask):
    m = mask & r["lv"].notna()
    cat = [i for i, c in enumerate(X_LV) if c == "track_code"]
    ds = lgb.Dataset(r.loc[m, X_LV].round(6).to_numpy(float), r.loc[m, "lv"].to_numpy(float),
                     weight=r.loc[m, "lv_w"].to_numpy(float), categorical_feature=cat)
    b = lgb.train(LV_PARAMS, ds, LV_ROUNDS)
    return lambda rr: b.predict(rr[X_LV].round(6).to_numpy(float))


def project_lv(con, x, r, train_end, first_year=2021):
    """Out-of-sample projected leader value per race (see module docstring). Returns a Series indexed by race_id."""
    train_end = pd.Timestamp(train_end)
    r = race_frame(con, x, r)
    out = pd.Series(np.nan, index=r.index)
    since = r["race_date"] >= "2019-01-01"
    # (fit before, rows): each calendar year before train_end from a fit on earlier years; the rest from train_end
    blocks = [(pd.Timestamp(f"{z}-01-01"), (r["race_date"].dt.year == z) & (r["race_date"] < train_end))
              for z in range(first_year, train_end.year + 1)]
    blocks.append((train_end, r["race_date"] >= train_end))
    for cut, sel in blocks:
        if sel.any():
            out[sel] = fit_lv(r, since & (r["race_date"] < cut))(r[sel])
    return out


def add(x, lv):
    """lv_x per runner: (projected settle share - race mean) x projected leader value."""
    sd = x["proj_settle"] - x.groupby("race_id")["proj_settle"].transform("mean")
    return sd * x["race_id"].map(lv)
