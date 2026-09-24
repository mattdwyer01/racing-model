"""Extra horse-history inputs from data the baseline does not use: RQ GPS sections and TopRate run comments.

Per run (in-race, so only ever used as HISTORY for later starts):
  GPS (QLD, rq_gps_sections): speed in each 200m section relative to the field median in that section
    (GPS speed is along the horse's own path, so it already reflects extra ground)
      late400 / late200 / early400   mean relative speed over those sections
      top_rel / top_at               top speed vs the field's median top speed; where it came (share of race)
      trouble                        largest drop in relative speed between consecutive mid-race sections
      stride_rel / stride_late       stride length vs the field; late stride change vs the field's
      pos_gain                       places gained from 400m out to the finish
  Comments (all states, runs.res_stewards / res_video):
      stewards flags: slow start, checked / crowded / held up, wide, health (vetted, lame, bled, eased),
      over-racing; video flags: blocked / no clear run, wide / deep
      video tag (the [bracketed] verdict) scored as the mean next-start WPR residual of horses given that
      tag, fitted on training pairs only (per fold), shrunk toward 0

History features (pre-race): last start's value (gx_last_*, cm_last_*) and a decayed mean over prior starts
with a value (gx_dm_*, cm_dm_*), plus counts. Missing = 0 with the count / flag telling the model.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SECTIONS = ROOT / "data/interim/rq_gps_sections.parquet"
RC_SECTIONS = ROOT / "data/interim/rc_gps_sections.parquet"
RC_RUNS = ROOT / "data/interim/rc_gps_runs.parquet"
K = 6
GX = ["late400", "late200", "early400", "top_rel", "top_at", "trouble", "stride_rel", "stride_late", "pos_gain"]
STEW = {"slow": r"awkward|slow|began poorly|dwelt|missed the start|blundered",
        "checked": r"check|hamper|crowd|bump|interfer|steadied|held up|no clear|blocked|tighten|squeez|carried",
        "wide": r"wide",
        "health": r"vetted|lame|bled|cardiac|distress|eased|pulled up|abnormal|sore|lost a plate|injur",
        "over": r"over-rac|overrac|pulled hard|raced ungenerously|hung|laid in|laid out"}
VID = {"vblocked": r"held up|no clear|blocked|check|steadied|couldn.t get (a )?clear|shut in|trapped|no room",
       "vwide": r"wide|3 deep|4 deep|5 deep|three deep|four deep"}
CM = list(STEW) + list(VID) + ["tag"]
TAG_PRIOR_N = 50


# ---------------------------------------------------------------- per-run measurements

def gps_runs(con):
    """Per-run GPS measurements (res_gx_*), keyed by run_id: RQ (QLD) and racing.com (VIC/SA) sections."""
    parts = [p for p in (_rq_gps_runs(con), _rc_gps_runs(con)) if p is not None and len(p)]
    if not parts:
        return pd.DataFrame(columns=["run_id"] + ["res_gx_" + c for c in GX])
    return pd.concat(parts, ignore_index=True).drop_duplicates("run_id")


def _rc_gps_runs(con):
    """racing.com sections: 200m splits with position and speed (no stride / per-section rail).
    from_m / to_m are metres to go; the first section includes the standing start (relative speed still valid)."""
    if not RC_SECTIONS.exists():
        return None
    s = pd.read_parquet(RC_SECTIONS)
    s = s[s["avg_speed_ms"].notna() & (s["avg_speed_ms"] > 3) & s["to_m"].notna()].copy()
    s["race_code"] = s["meet_code"].astype(str) + "_" + s["race_no"].astype(str)
    key = con.sql("select run_id, src_race race_code, tab_no from gps_runs where source = 'rc'").df()
    s = s.merge(key, on=["race_code", "tab_no"])
    g = s.groupby(["race_code", "to_m"])
    s["rel"] = s["avg_speed_ms"] / g["avg_speed_ms"].transform("median") - 1
    s["start"] = s.groupby("run_id")["from_m"].transform("max")
    h = s.groupby("run_id")
    out = pd.DataFrame({
        "late400": s[s["to_m"] < 400].groupby("run_id")["rel"].mean(),
        "late200": s[s["to_m"] == 0].groupby("run_id")["rel"].mean(),
        "early400": s[s["from_m"] >= s["start"] - 200].groupby("run_id")["rel"].mean(),
    })
    r = pd.read_parquet(RC_RUNS, columns=["meet_code", "race_no", "tab_no", "speed_peak_ms", "peak_at", "race_distance"])
    r["race_code"] = r["meet_code"].astype(str) + "_" + r["race_no"].astype(str)
    r = r.merge(key, on=["race_code", "tab_no"])
    peak = r.set_index("run_id")["speed_peak_ms"].where(lambda v: v > 5)
    race_of = r.set_index("run_id")["race_code"]
    out["top_rel"] = peak / peak.groupby(race_of).transform("median") - 1
    togo = pd.to_numeric(r.set_index("run_id")["peak_at"].str.extract(r"(\d+)", expand=False), errors="coerce")
    dist = pd.to_numeric(r.set_index("run_id")["race_distance"].str.extract(r"(\d+)", expand=False), errors="coerce")
    out["top_at"] = (1 - togo / dist).clip(0, 1)
    s = s.sort_values(["run_id", "to_m"], ascending=[True, False])
    s["drop"] = s.groupby("run_id")["rel"].shift(1) - s["rel"]
    mid = (s["from_m"] < s["start"] - 200) & (s["to_m"] > 0)
    out["trouble"] = s[mid].groupby("run_id")["drop"].max()
    p400 = s[s["to_m"] == 400].groupby("run_id")["pos"].first()
    pfin = s[s["to_m"] == 0].groupby("run_id")["pos"].first()
    out["pos_gain"] = (p400 - pfin).where(p400 > 0)
    out["stride_rel"], out["stride_late"] = np.nan, np.nan
    for c in ["late400", "late200", "early400", "top_rel", "trouble"]:
        out[c] = out[c].clip(-0.3, 0.3)
    return out[GX].add_prefix("res_gx_").reset_index()


def read_rq_sections(columns=None) -> pd.DataFrame:
    """rq_gps_sections with numeric tab_no / cum_dist_m (some store copies have them as strings)."""
    s = pd.read_parquet(SECTIONS, columns=columns)
    for c in ("tab_no", "cum_dist_m"):
        if c in s:
            s[c] = pd.to_numeric(s[c], errors="coerce").astype("Int64")
    return s


def _rq_gps_runs(con):
    if not SECTIONS.exists():
        return None
    s = read_rq_sections()
    s = s[s["avg_speed_ms"].notna() & (s["avg_speed_ms"] > 5)].copy()
    s["race_code"] = s["race_code"].astype(str)
    key = con.sql("select run_id, src_race race_code, tab_no from gps_runs where source = 'rq'").df()
    key["race_code"] = key["race_code"].astype(str)
    s = s.merge(key, on=["race_code", "tab_no"])
    g = s.groupby(["race_code", "cum_dist_m"])
    s["rel"] = s["avg_speed_ms"] / g["avg_speed_ms"].transform("median") - 1
    s["stride_r"] = s["stride_m"] / g["stride_m"].transform("median") - 1
    s["last"] = s.groupby("run_id")["cum_dist_m"].transform("max")
    s["first"] = s.groupby("run_id")["cum_dist_m"].transform("min")
    last, first = s["last"], s["first"]
    h = s.groupby("run_id")
    out = pd.DataFrame({
        "late400": s[s["cum_dist_m"] > last - 400].groupby("run_id")["rel"].mean(),
        "late200": s[s["cum_dist_m"] == last].groupby("run_id")["rel"].mean(),
        "early400": s[s["cum_dist_m"] <= first + 200].groupby("run_id")["rel"].mean(),
        "stride_rel": h["stride_r"].mean(),
    })
    top = h["top_speed_ms"].max()
    race_of = h["race_code"].first()
    out["top_rel"] = top / top.groupby(race_of).transform("median") - 1
    idx = s.loc[h["avg_speed_ms"].idxmax()]
    out["top_at"] = (idx.set_index("run_id")["cum_dist_m"] / idx.set_index("run_id")["last"]).clip(0, 1)
    s = s.sort_values(["run_id", "cum_dist_m"])
    last, first = s["last"], s["first"]
    s["drop"] = s.groupby("run_id")["rel"].shift(1) - s["rel"]
    mid = (s["cum_dist_m"] > first + 200) & (s["cum_dist_m"] < last)
    out["trouble"] = s[mid].groupby("run_id")["drop"].max()
    mid_stride = s[(s["cum_dist_m"] > first + 200) & (s["cum_dist_m"] <= last - 400)].groupby("run_id")["stride_m"].mean()
    late_stride = s[s["cum_dist_m"] > last - 200].groupby("run_id")["stride_m"].mean()
    sl = late_stride / mid_stride - 1
    out["stride_late"] = sl - sl.groupby(race_of).transform("median")
    r400 = s[s["cum_dist_m"] > last - 400].groupby("run_id")["rank"].first()
    rfin = s[s["cum_dist_m"] == last].groupby("run_id")["rank"].first()
    out["pos_gain"] = (r400 - rfin).where(r400 > 0)
    for c in ["late400", "late200", "early400", "top_rel", "stride_rel", "stride_late"]:
        out[c] = out[c].clip(-0.3, 0.3)
    out["trouble"] = out["trouble"].clip(-0.3, 0.3)
    return out.add_prefix("res_gx_").reset_index()


def comment_runs(con):
    """Per-run comment flags and the raw video tag, keyed by run_id."""
    c = con.sql("""select run_id, lower(coalesce(res_stewards, '')) st, lower(coalesce(res_video, '')) vid
                   from runs where not is_trial_or_jumpout""").df()
    out = pd.DataFrame({"run_id": c["run_id"]})
    for k, pat in STEW.items():
        out["res_cm_" + k] = c["st"].str.contains(pat, regex=True).astype(float)
    body = c["vid"].str.replace(r"^\s*\[[^\]]*\]", "", regex=True)
    for k, pat in VID.items():
        out["res_cm_" + k] = body.str.contains(pat, regex=True).astype(float)
    out["tag"] = c["vid"].str.extract(r"^\s*\[([^\]]+)\]", expand=False).str.strip().str.replace(r"\s+", " ", regex=True)
    return out


# ---------------------------------------------------------------- tag scores and history

def tag_scores(d, tags, train_end):
    """Mean next-start WPR residual per video tag (pairs with the next start before train_end), shrunk."""
    t = d[["run_id", "horse_id", "race_date", "wpr"]].merge(tags[["run_id", "tag"]], on="run_id", how="left")
    t = t.sort_values(["horse_id", "race_date", "run_id"])
    g = t.groupby("horse_id")
    t["next_wpr"], t["next_date"] = g["wpr"].shift(-1), g["race_date"].shift(-1)
    m = t["wpr"].notna() & t["next_wpr"].notna() & (t["next_date"] < train_end) & t["tag"].notna()
    b = np.polyfit(t.loc[m, "wpr"], t.loc[m, "next_wpr"], 1)
    t["resid"] = t["next_wpr"] - np.polyval(b, t["wpr"])
    agg = t[m].groupby("tag")["resid"].agg(["sum", "size"])
    return (agg["sum"] / (agg["size"] + TAG_PRIOR_N)).clip(-5, 5)


def _history(x, cols, prefix):
    """Last start's value and decayed mean over prior starts with a value, per horse (rows sorted)."""
    g = x.groupby("horse_id", sort=False)
    out = {}
    lags = {c: np.stack([g[c].shift(j).to_numpy(float) for j in range(1, K + 1)], 1) for c in cols}
    for c in cols:
        v = lags[c]
        ok = ~np.isnan(v)
        w = np.where(ok, 0.5 ** (np.arange(K) / 2.0), 0)
        out[f"{prefix}_last_{c}"] = np.nan_to_num(v[:, 0])
        out[f"{prefix}_dm_{c}"] = (w * np.nan_to_num(v)).sum(1) / np.maximum(w.sum(1), 1e-9)
    out[f"{prefix}_n"] = (~np.isnan(lags[cols[0]])).sum(1)
    out[f"{prefix}_last_has"] = (~np.isnan(lags[cols[0]][:, 0])).astype(float)
    return pd.DataFrame(out, index=x.index)


def features(con, d, train_end):
    """History inputs for every run. d = figure.components-style frame (run_id, horse_id, race_date, wpr)."""
    x = d[["run_id", "horse_id", "race_date", "wpr"]].sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    gx = gps_runs(con)
    cm = comment_runs(con)
    sc = tag_scores(x, cm, train_end)
    cm["res_cm_tag"] = cm["tag"].map(sc).astype(float)
    x = x.merge(gx, on="run_id", how="left").merge(cm.drop(columns="tag"), on="run_id", how="left")
    x = x.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    hx = _history(x.rename(columns={"res_gx_" + c: c for c in GX}), GX, "gx")
    hc = _history(x.rename(columns={"res_cm_" + c: c for c in CM}), CM, "cm")
    return pd.concat([x[["run_id"]], hx, hc], axis=1)


GX_FEATS = [f"gx_{k}_{c}" for c in GX for k in ("last", "dm")] + ["gx_n", "gx_last_has"]
CM_FEATS = [f"cm_{k}_{c}" for c in CM for k in ("last", "dm")] + ["cm_last_has"]
