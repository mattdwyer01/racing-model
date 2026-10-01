"""Wet / heavy track form inputs (blend_eval variants wet, wet-sire).

All pre-race, from history only (no fitted pieces, so one build serves every fold):
  dev            a run's WPR minus the horse's decayed mean WPR before it (how far above / below its usual level)
  going band     dry (going 1-6), soft (7-8), heavy (9-10)
  h_heavy_dev    shrunk mean dev over the horse's past heavy runs (shrink 2 runs); h_soft_dev the same for 7-8
  heavy_x        today heavy x h_heavy_dev; soft_x today soft x h_soft_dev (the production going_fit lumps 7-10
                 together as "wet" and gets ~0 weight)
  untried_wet    today wet (7+), horse has form but no wet run; untried_heavy the same for heavy
  sire_wet_x     today wet x the sire's wet minus dry dev over progeny runs on EARLIER dates (shrunk, 30 runs a side);
                 sire_heavy_x the same for heavy vs dry
"""
import numpy as np
import pandas as pd

SQL = """
select r.run_id, r.race_id, r.horse_id, r.race_date, r.sire_id, r.res_wpr wpr, ra.going_num
from runs r join races ra using (race_id)
where not r.is_trial_or_jumpout
"""
K = 10
FEATS = ["heavy_x", "soft_x", "untried_wet", "untried_heavy", "sire_wet_x", "sire_heavy_x"]
NO_SIRE = ["heavy_x", "soft_x", "untried_wet", "untried_heavy"]


def _band(g):
    g = g.fillna(4)
    return np.select([g >= 9, g >= 7], [2, 1], 0)


def _sire(d, codes, lam=30.0):
    """Per run: sire's (mean dev in going bands `codes`) - (mean dev dry) over progeny runs on earlier dates, shrunk."""
    t = d.dropna(subset=["dev", "sire_id"])
    t = t[t["band"].isin([0, *codes])].assign(grp=lambda x: x["band"].isin(codes).astype(int))
    agg = t.groupby(["sire_id", "race_date", "grp"])["dev"].agg(["sum", "count"]).unstack("grp", fill_value=0)
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    for c in ["sum_1", "count_1", "sum_0", "count_0"]:
        if c not in agg:
            agg[c] = 0.0
    agg = agg.sort_index()
    cs = agg.groupby(level="sire_id").cumsum() - agg          # strictly earlier dates
    m_b = cs["sum_1"] / (cs["count_1"] + lam)
    m_0 = cs["sum_0"] / (cs["count_0"] + lam)
    s = (m_b - m_0).rename("v").reset_index()
    out = np.array(d[["sire_id", "race_date"]].merge(s, on=["sire_id", "race_date"], how="left")["v"], dtype=float)
    # a race date the sire has no runs on: last earlier value
    miss = np.isnan(out) & d["sire_id"].notna().to_numpy()
    if miss.any():
        s2 = s.sort_values("race_date")
        q = d.loc[miss, ["sire_id", "race_date"]].reset_index().sort_values("race_date")
        q = pd.merge_asof(q, s2, on="race_date", by="sire_id", allow_exact_matches=False)
        out[q["index"].to_numpy()] = q["v"].to_numpy()
    return np.nan_to_num(out)


def features(con):
    d = con.sql(SQL).df().sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    d["race_date"] = pd.to_datetime(d["race_date"])
    d["band"] = _band(d["going_num"])
    g = d.groupby("horse_id", sort=False)
    lag = np.stack([g["wpr"].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
    ok = ~np.isnan(lag)
    w = np.where(ok, 0.5 ** (np.arange(K) / 4.0), 0)
    has = w.sum(1) > 0
    d["prior"] = np.where(has, (w * np.nan_to_num(lag)).sum(1) / np.where(has, w.sum(1), 1), np.nan)
    d["dev"] = d["wpr"] - d["prior"]
    bl = np.stack([g["band"].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
    dl = np.stack([g["dev"].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
    okd = ~np.isnan(dl)

    def band_dev(code):
        m = okd & (bl == code)
        return (np.where(m, dl, 0)).sum(1) / (m.sum(1) + 2.0), m.sum(1)

    h_heavy, n_heavy = band_dev(2)
    h_soft, n_soft = band_dev(1)
    n_form = okd.sum(1)
    today_heavy = (d["band"] == 2).to_numpy()
    today_wet = (d["band"] >= 1).to_numpy()
    today_soft = (d["band"] == 1).to_numpy()
    out = pd.DataFrame({"run_id": d["run_id"]})
    out["heavy_x"] = np.where(today_heavy, h_heavy, 0.0)
    out["soft_x"] = np.where(today_soft, h_soft, 0.0)
    out["untried_wet"] = (today_wet & (n_form > 0) & (n_heavy + n_soft == 0)).astype(float)
    out["untried_heavy"] = (today_heavy & (n_form > 0) & (n_heavy == 0)).astype(float)
    out["sire_wet_x"] = np.where(today_wet, _sire(d, (1, 2)), 0.0)
    out["sire_heavy_x"] = np.where(today_heavy, _sire(d, (2,)), 0.0)
    return out
