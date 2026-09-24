"""Link GPS runs (RQ, racing.com) to TopRate runs -> table `gps_runs`.

Called by build_core when data/interim/{rq,rc}_gps_runs.parquet exist. Match key:
race date + venue + normalised horse name (TopRate has no race number).

src_race / tab_no: the source's race key and saddlecloth (to join the per-section files).
Every column except run_id/race_id/source/src_race/tab_no is an in-race measurement (res_ prefix):
    res_gps_dist_m      distance travelled (m)
    res_gps_extra_m     distance travelled minus the mean of valid finishers in the race
                        (+ = covered more ground than the field)
    res_gps_rail_m      average distance from the rail over the race (m)
    res_gps_extra_l600_m  (RQ only) extra ground in the last 600m vs the field mean
    res_gps_early200 / res_gps_early400  (RQ only) position at the first section at or past 200m / 400m
                        from the start, as a share of tracked runners (0 = leader)
A run is valid when it finished and distance travelled is within 0.98 to 1.06 of the
official distance (drops GPS glitches, about 0.1%). Distance travelled is masked (rail kept) where
it looks broken: see SUSPECT_DIST.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"

COURSE_TO_VENUE = {"Ladbrokes Cannon Park": "Cairns", "The Valley": "Moonee Valley", "Murray Bridge": "Murray Bridge GH",
                   "Hillside": "Sandown", "Lakeside": "Sandown", "Sandown Hillside": "Sandown",
                   "Sandown Lakeside": "Sandown", "Yarra Valley": "Yarra Glen", "Spendthrift Australia Park": "Werribee"}
RC_PREFIX = r"^(Sportsbet-|Sportsbet |bet365 Park |bet365 |Ladbrokes Park |Ladbrokes |Picklebet Park |TAB Park |Apiam |" \
            r"Thomas Farms RC |Southside |BetDeluxe )"
RC_SUFFIX = r"\s+(Synthetic|Heath|Parks)$"
RATIO_OK = (0.98, 1.06)
# RQ distance travelled stops tracking barrier and settle at these tracks from early 2026
# (corr with barrier 0.3-0.4 -> 0 or negative) while rail distance stays sane: mask extra ground there.
SUSPECT_DIST = {("Doomben", "2026-01-01"), ("Ipswich", "2026-01-01")}


def venue(course: str) -> str:
    c = COURSE_TO_VENUE.get(course, course) or ""
    c = re.sub(r"^(Aquis Park|Picklebet Park)\s+", "", c)
    c = re.sub(r"\s+Poly(\s+Track)?$", "", c)
    c = re.sub(RC_SUFFIX, "", re.sub(RC_PREFIX, "", c))        # racing.com sponsor names (VIC/SA)
    return COURSE_TO_VENUE.get(c, c)


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
    ranked = s[s["rank"] > 0]
    for mark in (200, 400):
        at = ranked[ranked["cum_dist_m"] >= mark]
        at = at[at["cum_dist_m"] == at.groupby("race_code")["cum_dist_m"].transform("min")]
        n = at.groupby("race_code")["rank"].transform("count")
        share = ((at["rank"] - 1) / (n - 1).clip(lower=1)).clip(0, 1)
        r = r.join(pd.Series(share.to_numpy(), index=pd.MultiIndex.from_frame(at[["race_code", "tab_no"]]),
                             name=f"early{mark}"), on=["race_code", "tab_no"])
    return pd.DataFrame({"source": "rq", "race_key": r["race_key"], "src_race": r["race_code"].astype(str),
                         "tab_no": r["tab_no"], "race_date": pd.to_datetime(r["race_date"]),
                         "venue": r["course"].map(venue), "horse": r["horse"],
                         "dist_m": r["dist_travelled_m"], "rail_m": r["rail_m"], "l600_m": r["l600_m"],
                         "early200": r["early200"], "early400": r["early400"]})


def _rc():
    p = INTERIM / "rc_gps_runs.parquet"
    if not p.exists():
        return None
    r = pd.read_parquet(p)
    fin = pd.to_numeric(r["finish"], errors="coerce")
    r = r[fin.between(1, 40)].copy()
    date = pd.to_datetime(r["start_utc"], utc=True).dt.tz_convert("Australia/Melbourne").dt.tz_localize(None).dt.normalize()
    return pd.DataFrame({"source": "rc", "race_key": "rc" + r["meet_code"].astype(str) + "_" + r["race_no"].astype(str),
                         "src_race": r["meet_code"].astype(str) + "_" + r["race_no"].astype(str),
                         "tab_no": pd.to_numeric(r["tab_no"], errors="coerce"),
                         "race_date": date, "venue": r["venue"].map(venue), "horse": r["horse"],
                         # only Triple S timing measures distance travelled / rail; 'dailysectionals' rows have 0
                         "dist_m": r["dist_travelled_m"].where(r["timing_source"] == "TripleS"),
                         "rail_m": pd.to_numeric(r["rail_avg_m"], errors="coerce").where(r["timing_source"] == "TripleS"),
                         "l600_m": float("nan"), "early200": float("nan"), "early400": float("nan")})


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
                            "extra_l600_m": "res_gps_extra_l600_m", "early200": "res_gps_early200",
                            "early400": "res_gps_early400"})
    out = out[["run_id", "race_id", "source", "src_race", "tab_no", "n_gps", "res_gps_dist_m", "res_gps_extra_m",
               "res_gps_rail_m", "res_gps_extra_l600_m", "res_gps_early200", "res_gps_early400"]].drop_duplicates("run_id")
    con.register("gps_df", out)
    con.execute("create or replace table gps_runs as select * from gps_df")
    con.unregister("gps_df")
    return len(out)
