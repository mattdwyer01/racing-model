"""Per-run performance figure and the pre-race ability built from it.

Per-run components (post-race, from `runs`/`races`; only ever used for LATER races):
    wpr      TopRate WPR (already weight adjusted by TopRate, not pace adjusted)
    s_early  early sectional rating, lengths vs benchmark (+ = faster)
    s_l600   last 600m sectional rating
    wt_rel   weight carried minus race mean (kg); sectionals are not weight adjusted
    settle   position at 800m as a share of the field (0 = leader, 1 = last)
    shape    race early shape (+ = fast early; TopRate raceShapeEarly)
    pace     shape * (1 - settle): on-pace runner in a fast-early race
    gl       GPS extra ground vs the field mean (m, + = covered more); 0 when no GPS
    rail     GPS average distance from the rail vs the field mean (m); 0 when no GPS

The figure is linear in the components: fig = wpr + sum_j c_j * x_j. Because the
pre-race ability is a decayed mean of past figures, the c_j are fitted directly by a
conditional logit on the decayed means of each component (see validate_figure.py).

Missing sectionals are imputed from WPR and distance (fit on 2019-2021, before any test
data); missing settle/shape are set to neutral values and flagged.
"""
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/db/racing.duckdb"

COMPONENTS = ["wpr", "s_early", "s_l600", "wt_rel", "settle", "shape", "pace", "gl", "rail"]
K = 10                  # prior starts used
HALF_LIFE_RUNS = 3.0    # decay by starts back
HALF_LIFE_DAYS = 365.0  # and by age of the run

SQL = """
select r.run_id, r.race_id, r.horse_id, r.race_date, ra.distance dist, ra.field_size,
  ra.state, coalesce(ra.in_scope, false) in_scope, ra.full_coverage,
  r.sp, r.res_won::int won, r.res_finish finish, r.weight_kg,
  r.weight_kg - avg(r.weight_kg) over (partition by r.race_id) wt_rel_today,
  r.days_since_start, r.prep_run, r.career_starts_in_data,
  -- post-race components (become history)
  r.res_wpr wpr, r.res_s_early s_early, r.res_s_l600 s_l600,
  r.weight_kg - avg(r.weight_kg) over (partition by r.race_id) wt_rel,
  (r.res_pos800 - 1) / greatest(ra.field_size - 1, 1) settle,
  ra.res_shape_early shape{gps_cols}
from runs r join races ra using (race_id){gps_join}
where not r.is_trial_or_jumpout
"""
GPS_COLS = """,
  g.res_gps_extra_m gl,
  g.res_gps_rail_m - avg(g.res_gps_rail_m) over (partition by g.race_id) rail"""
GPS_JOIN = "\nleft join gps_runs g using (run_id)"


def components(con=None):
    con = con or duckdb.connect(str(DB), read_only=True)
    has_gps = con.sql("select count(*) from information_schema.tables where table_name = 'gps_runs'").fetchone()[0]
    sql = SQL.format(gps_cols=GPS_COLS if has_gps else ", null::double gl, null::double rail",
                     gps_join=GPS_JOIN if has_gps else "")
    d = con.sql(sql).df()
    d["race_date"] = pd.to_datetime(d["race_date"])
    # keep runs with no result yet (upcoming races): they are scored, but carry no weight in any history
    d["has_res"] = d["wpr"].notna().astype(float)

    # impute missing sectionals from wpr + distance, fitted on 2019-2021 only
    fit_rows = d["race_date"].dt.year.between(2019, 2021)
    for c in ["s_early", "s_l600"]:
        d[c + "_miss"] = d[c].isna().astype(float)
        m = fit_rows & d[c].notna()
        X = np.c_[np.ones(m.sum()), d.loc[m, "wpr"], d.loc[m, "dist"] / 1000]
        b = np.linalg.lstsq(X, d.loc[m, c], rcond=None)[0]
        Xa = np.c_[np.ones(len(d)), d["wpr"], d["dist"] / 1000]
        d[c] = d[c].fillna(pd.Series(Xa @ b, index=d.index))
    d["settle_miss"] = d["settle"].isna().astype(float)
    d["settle"] = d["settle"].clip(0, 1).fillna(0.5)
    d["shape"] = d["shape"].fillna(0.0)
    d["pace"] = d["shape"] * (1 - d["settle"])
    d["gl_miss"] = d["gl"].isna().astype(float)
    d[["gl", "rail"]] = d[["gl", "rail"]].fillna(0.0)
    return d


def history(d, half_life_runs=HALF_LIFE_RUNS, half_life_days=HALF_LIFE_DAYS, k=K):
    """Decayed mean of each component over the horse's prior starts (pre-race safe).

    Only prior starts with a result count; the current row's own result is never used.
    """
    d = d.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    g = d.groupby("horse_id", sort=False)
    cols = COMPONENTS + ["s_early_miss", "settle_miss", "gl_miss"]
    if "has_res" not in d:
        d["has_res"] = d["wpr"].notna().astype(float)
    num = {c: np.zeros(len(d)) for c in cols}
    den = np.zeros(len(d))
    last_wpr = g["wpr"].shift(1)
    for j in range(1, k + 1):
        dt = (d["race_date"] - g["race_date"].shift(j)).dt.days.to_numpy()
        ok = ~np.isnan(dt) & (g["has_res"].shift(j).fillna(0).to_numpy() == 1)
        w = np.where(ok, 0.5 ** ((j - 1) / half_life_runs) * 0.5 ** (np.nan_to_num(dt) / half_life_days), 0.0)
        den += w
        for c in cols:
            num[c] += w * np.nan_to_num(g[c].shift(j).to_numpy())
    out = d[["run_id", "race_id", "horse_id", "race_date", "dist", "field_size", "state", "in_scope",
             "full_coverage", "sp", "won", "finish", "weight_kg", "wt_rel_today", "days_since_start",
             "prep_run", "career_starts_in_data"]].copy()
    has = den > 0
    for c in cols:
        out["h_" + c] = np.where(has, num[c] / np.where(has, den, 1), 0.0)
    out["h_n"] = g.cumcount().to_numpy()
    out["h_weight"] = den
    out["h_none"] = (~has).astype(float)
    out["h_last_wpr"] = last_wpr.fillna(0).to_numpy()
    return out


def figure(d, coef):
    """Per-run figure from components and fitted weights {component: c_j} (wpr weight = 1)."""
    f = d["wpr"].copy()
    for c, v in coef.items():
        if c != "wpr":
            f = f + v * d[c]
    return f
