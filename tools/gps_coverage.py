"""RQ GPS coverage and match rate to TopRate.

    python pipeline/store.py get rq_gps_runs.parquet data/interim/rq_gps_runs.parquet
    python pipeline/store.py get rq_gps_sections.parquet data/interim/rq_gps_sections.parquet
    python tools/gps_coverage.py        # prints and writes reports/gps_coverage.md

Match key: date + venue + normalised horse name (TopRate has no race number).
RQ course names carry sponsor and surface suffixes; they are mapped to TopRate `venue`.
"""
import re
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
DB = ROOT / "data/db/racing.duckdb"

COURSE_TO_VENUE = {"Ladbrokes Cannon Park": "Cairns"}


def venue(course: str) -> str:
    c = COURSE_TO_VENUE.get(course, course)
    c = re.sub(r"^(Aquis Park|Picklebet Park)\s+", "", c)
    return re.sub(r"\s+Poly(\s+Track)?$", "", c)


def horse_key(s: pd.Series) -> pd.Series:
    s = s.str.upper().str.replace(r"\s*\([A-Z]{2,3}\)\s*$", "", regex=True)
    return s.str.replace(r"[^A-Z0-9]", "", regex=True)


def main():
    runs = pd.read_parquet(INTERIM / "rq_gps_runs.parquet")
    secs = pd.read_parquet(INTERIM / "rq_gps_sections.parquet")
    runs["race_date"] = pd.to_datetime(runs["race_date"])
    runs["year"] = runs["race_date"].dt.year
    ran = runs[runs["result_state"].isin(["Finished", "DidNotFinish", "Disqualified"])].copy()

    # ------------------------------------------------ rail-distance coverage
    s = secs.merge(ran[["race_code", "tab_no", "year"]], on=["race_code", "tab_no"])
    per_run = s.groupby(["race_code", "tab_no", "year"]).agg(
        n_sec=("cum_dist_m", "size"), n_rail=("rail_m", "count")).reset_index()
    ran = ran.merge(per_run, on=["race_code", "tab_no", "year"], how="left")
    ran[["n_sec", "n_rail"]] = ran[["n_sec", "n_rail"]].fillna(0)
    cov = ran.groupby("year").agg(
        meetings=("zip_file", "nunique"), races=("race_code", "nunique"), runs=("race_code", "size"),
        dist_travelled=("dist_travelled_m", lambda x: (x > 0).mean()),
        any_rail=("n_rail", lambda x: (x > 0).mean()),
        all_sections_rail=("n_rail", lambda x: (x == ran.loc[x.index, "n_sec"]).mean() if len(x) else 0),
        race_time=("race_time_s", lambda x: x.notna().mean()),
    )
    cov["rail_sections"] = s.groupby("year")["rail_m"].apply(lambda x: x.notna().mean())

    # ------------------------------------------------ match to TopRate
    con = duckdb.connect(str(DB), read_only=True)
    tr = con.sql("""select r.run_id, r.race_date, ra.venue, r.horse, r.is_trial_or_jumpout trial, ra.track
                    from runs r join races ra using (race_id)
                    where ra.state = 'QLD' and r.race_date >= date '2022-10-01'""").df()
    tr["race_date"] = pd.to_datetime(tr["race_date"])
    tr["hk"] = horse_key(tr["horse"])
    ran["venue"] = ran["course"].map(venue)
    ran["hk"] = horse_key(ran["horse"])
    key = ["race_date", "venue", "hk"]
    dup_tr = tr.duplicated(key, keep=False).sum()
    m = ran.merge(tr.drop_duplicates(key), on=key, how="left", indicator=True)
    m["matched"] = m["_merge"] == "both"
    rq_side = m.groupby("year").agg(rq_runs=("matched", "size"), matched=("matched", "mean"))
    rq_side["of_which_trials"] = m[m.matched].groupby("year")["trial"].mean()

    # TopRate side: races at venues/dates RQ covered
    gps_meet = ran[["race_date", "venue"]].drop_duplicates()
    trm = tr.merge(gps_meet, on=["race_date", "venue"])
    trm["year"] = trm["race_date"].dt.year
    trm = trm.merge(ran[key].drop_duplicates().assign(hit=True), on=key, how="left")
    tr_side = trm.groupby("year").agg(tr_runs_at_gps_meetings=("hit", "size"),
                                      matched=("hit", lambda x: x.notna().mean()))
    # share of all QLD TopRate race runs (not trials) covered by GPS, by venue
    tr_all = tr[~tr.trial].merge(ran[key].drop_duplicates().assign(hit=True), on=key, how="left")
    by_venue = tr_all.groupby("venue").agg(tr_runs=("hit", "size"), gps=("hit", lambda x: x.notna().mean()))
    by_venue = by_venue[by_venue.gps > 0].sort_values("tr_runs", ascending=False)
    tr_all["year"] = tr_all["race_date"].dt.year
    qld_share = tr_all.groupby("year")["hit"].apply(lambda x: x.notna().mean()).rename("share_of_all_QLD_race_runs")

    unmatched = m[~m.matched].groupby("venue").size().sort_values(ascending=False).head(10)

    L = ["# RQ GPS coverage and match to TopRate", "",
         f"- Files: rq_gps_runs {len(runs):,} rows ({len(ran):,} runners that ran), rq_gps_sections {len(secs):,} rows",
         f"- TopRate QLD runs from Oct 2022 with a duplicate date+venue+horse key: {dup_tr}", "",
         "## Coverage by year (runners that ran)", "", cov.to_markdown(floatfmt=".3f"), "",
         "## Match rate, RQ -> TopRate (date + venue + horse)", "", rq_side.to_markdown(floatfmt=".3f"), "",
         "## Match rate, TopRate -> RQ at meetings RQ covers", "", tr_side.to_markdown(floatfmt=".3f"), "",
         "## Share of all QLD TopRate race runs with GPS", "", qld_share.to_frame().to_markdown(floatfmt=".3f"), "",
         "## GPS share by TopRate venue", "", by_venue.to_markdown(floatfmt=".3f"), "",
         "## Unmatched RQ runners by venue (top 10)", "", unmatched.rename("n").to_frame().to_markdown()]
    out = ROOT / "reports/gps_coverage.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return m


if __name__ == "__main__":
    main()
