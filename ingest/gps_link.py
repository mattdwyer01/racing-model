"""Link GPS runs (RQ, racing.com) to TopRate runs -> table `gps_runs`.

Called by build_core when data/interim/{rq,rc}_gps_runs.parquet exist. Match key:
race date + venue + normalised horse name (TopRate has no race number).

Every column except run_id/race_id/source is an in-race measurement (res_ prefix):
    res_gps_dist_m      distance travelled (m)
    res_gps_extra_m     distance travelled minus the mean of valid finishers in the race
                        (+ = covered more ground than the field)
    res_gps_rail_m      average distance from the rail over the race (m)
    res_gps_extra_l600_m  (RQ only) extra ground in the last 600m vs the field mean
A run is valid when it finished and distance travelled is within 0.98 to 1.06 of the
official distance (drops GPS glitches, about 0.1%). Distance travelled is masked (rail kept) where
it looks broken: see SUSPECT_DIST.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"

COURSE_TO_VENUE = {"Ladbrokes Cannon Park": "Cairns"}
RATIO_OK = (0.98, 1.06)
# RQ distance travelled stops tracking barrier and settle at these tracks from early 2026
# (corr with barrier 0.3-0.4 -> 0 or negative) while rail distance stays sane: mask extra ground there.
SUSPECT_DIST = {("Doomben", "2026-01-01"), ("Ipswich", "2026-01-01")}


def venue(course: str) -> str:
    c = COURSE_TO_VENUE.get(course, course) or ""
    c = re.sub(r"^(Aquis Park|Picklebet Park)\s+", "", c)
    return re.sub(r"\s+Poly(\s+Track)?$", "", c)


def horse_key(s: pd.Series) -> pd.Series:
    s = s.fillna("").str.upper().str.replace(r"\s*\([A-Z]{2,3}\)\s*$", "", regex=True)
    return s.str.replace(r"[^A-Z0-9]", "", regex=True)


def _rq():
    p = INTERIM / "rq_gps_runs.parquet"
    if not p.exists():
        return None
    r = pd.read_parquet(p)
    s = pd.read_parquet(INTERIM / "rq_gps_sections.parquet")
    r = r[r["result_state"] == "Finished"].copy()
    r["race_key"] = "rq" + r["race_code"].astype(str)
    agg = s.groupby(["race_code", "tab_no"]).agg(rail_m=("rail_m", "mean"), last_cum=("cum_dist_m", "max"))
    s = s.join(agg["last_cum"], on=["race_code", "tab_no"])
    l600 = s[s["cum_dist_m"] > s["last_cum"] - 600].groupby(["race_code", "tab_no"])["real_dist_m"].sum(min_count=1)
    r = r.join(agg["rail_m"], on=["race_code", "tab_no"]).join(l600.rename("l600_m"), on=["race_code", "tab_no"])
    return pd.DataFrame({"source": "rq", "race_key": r["race_key"], "race_date": pd.to_datetime(r["race_date"]),
                         "venue": r["course"].map(venue), "horse": r["horse"],
                         "dist_m": r["dist_travelled_m"], "rail_m": r["rail_m"], "l600_m": r["l600_m"]})


def _rc():
    p = INTERIM / "rc_gps_runs.parquet"
    if not p.exists():
        return None
    r = pd.read_parquet(p)
    fin = pd.to_numeric(r["finish"], errors="coerce")
    r = r[fin.between(1, 40)].copy()
    date = pd.to_datetime(r["start_utc"], utc=True).dt.tz_convert("Australia/Melbourne").dt.tz_localize(None).dt.normalize()
    return pd.DataFrame({"source": "rc", "race_key": "rc" + r["meet_code"].astype(str) + "_" + r["race_no"].astype(str),
                         "race_date": date, "venue": r["venue"].map(venue), "horse": r["horse"],
                         "dist_m": r["dist_travelled_m"], "rail_m": pd.to_numeric(r["rail_avg_m"], errors="coerce"),
                         "l600_m": float("nan")})


def build(con) -> int:
    parts = [x for x in (_rq(), _rc()) if x is not None]
    if not parts:
        return 0
    g = pd.concat(parts, ignore_index=True)
    g["hk"] = horse_key(g["horse"])
    tr = con.sql("""select r.run_id, r.race_id, r.race_date, ra.venue, r.horse, ra.distance
                    from runs r join races ra using (race_id)
                    where r.race_date >= date '2021-01-01' and ra.state in ('QLD','VIC','SA')""").df()
    tr["race_date"] = pd.to_datetime(tr["race_date"])
    tr["hk"] = horse_key(tr["horse"])
    key = ["race_date", "venue", "hk"]
    tr = tr[~tr.duplicated(key, keep=False)]
    m = g.merge(tr[key + ["run_id", "race_id", "distance"]], on=key)
    for v, since in SUSPECT_DIST:
        bad = (m["source"] == "rq") & (m["venue"] == v) & (m["race_date"] >= since)
        m.loc[bad, ["dist_m", "l600_m"]] = float("nan")
    ratio = (m["dist_m"] / m["distance"]).fillna(1.0)
    m = m[ratio.between(*RATIO_OK)].copy()
    grp = m.groupby("race_key")
    m["extra_m"] = m["dist_m"] - grp["dist_m"].transform("mean")
    m["extra_l600_m"] = m["l600_m"] - grp["l600_m"].transform("mean")
    m["n_gps"] = grp["dist_m"].transform("count")
    out = m.rename(columns={"dist_m": "res_gps_dist_m", "extra_m": "res_gps_extra_m", "rail_m": "res_gps_rail_m",
                            "extra_l600_m": "res_gps_extra_l600_m"})
    out = out[["run_id", "race_id", "source", "n_gps", "res_gps_dist_m", "res_gps_extra_m",
               "res_gps_rail_m", "res_gps_extra_l600_m"]].drop_duplicates("run_id")
    con.register("gps_df", out)
    con.execute("create or replace table gps_runs as select * from gps_df")
    con.unregister("gps_df")
    return len(out)
