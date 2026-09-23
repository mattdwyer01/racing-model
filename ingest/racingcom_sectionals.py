"""racing.com sectional data (Triple S GPS for VIC, plus SA) via racing.com's own GraphQL API.

Per horse: distance run, distance vs winner, average distance from the rail (whole race),
barrier, early / mid / late / peak / average speed (m/s), and every 200m split with
position and speed. Per race: timing source (TripleS, Equitime, ...) and completeness.

Runs on your PC (the API is not reachable from cloud workspaces). Needs the site's public
web API key in an environment variable, kept out of the repo:

    set RACINGCOM_API_KEY=da2-...                      (Windows)
    python ingest/racingcom_sectionals.py fetch --from 2021-08-01 --states VIC,SA
    python ingest/racingcom_sectionals.py parse

`fetch` reads VIC/SA meeting dates and venues from data/db/racing.duckdb, looks up each
meeting's racing.com code, then saves every race's raw JSON to data/raw/racingcom/
(already-saved races are skipped, so it can be stopped and restarted any time).
`parse` turns the saved JSON into data/interim/rc_gps_{runs,sections}.parquet.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data/raw/racingcom"
OUT_DIR = ROOT / "data/interim"
DB = ROOT / "data/db/racing.duckdb"
ENDPOINT = "https://graphql.rmdprod.racing.com/"
HEADERS = {
    "Referer": "https://dxp-static.racing.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/140.0 Safari/537.36",
    "Content-Type": "application/json",
}

RACES_FOR_MEET = """query{ racesForMeet: getRacesForMeet(meetCode: "%s") {
  id raceNumber raceStatus distance time name trackCondition trackRating isTrial isJumpOut
  hasSectionals rdcClass meet { venue } } }"""

RACE_FORM = """query{ f: getRaceForm(meetCode: "%s", raceNumber:%d) {
  Horses: raceEntryTimes {
    FinalPosition: finishPosition FullName: horseName SaddleNumber: saddleNumber
    HorseUrl: horseUrl BarrierNumber: barrierNumber RaceTime: finishTime
    BeatenMargin: beatenMargin DistanceRun: distanceTravelled DistanceVarToWinner: distanceVarToWinner
    Early: avgSpeedEarly Mid: avgSpeedMid Late: avgSpeedLate
    OverallPeakSpeed: overallPeakSpeed PeakSpeedLocation: peakSpeedLocation
    OverallAvgSpeed: overallAvgSpeed DistanceFromRail: distanceFromRail
    SplitTimes: splitTimes { Distance: distance Position: position Time: time AvgSpeed: avgSpeed } }
  RaceTime: raceTime Source: timingSource IsComplete: isTimingComplete IsCompleteData: isCompleteData } }"""

# Venue slug + date -> racing.com meeting code(s), as the racing.com page itself asks.
MEET_CODE_QUERY = """query GetMeetCode_CD($venueName: String $date: String) {
  GetMeetingByVenue(venueName: $venueName date: $date) { id isJumpOut isTrial } }"""


# ---------------------------------------------------------------- fetch

class Client:
    def __init__(self, delay: float = 1.0):
        import requests
        key = os.environ.get("RACINGCOM_API_KEY")
        if not key:
            sys.exit("Set RACINGCOM_API_KEY first (the X-Api-Key value from the browser request).")
        self.s = requests.Session()
        self.s.headers.update({**HEADERS, "X-Api-Key": key})
        self.delay = delay

    def q(self, query: str, variables: dict | None = None) -> dict:
        params = {"query": query}
        if variables:
            params["variables"] = json.dumps(variables)
        for attempt in range(4):
            try:
                r = self.s.get(ENDPOINT, params=params, timeout=30)
                if r.status_code == 429:
                    time.sleep(30 * (attempt + 1)); continue
                r.raise_for_status()
                time.sleep(self.delay)
                return r.json()
            except Exception as e:
                if attempt == 3:
                    raise
                time.sleep(5 * (attempt + 1))


def slug(name: str) -> str:
    """'Sandown-Hillside' -> 'sandown-hillside', 'Morphettville Parks' -> 'morphettville-parks'."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def meet_code(c: Client, names: list[str], date: str) -> str | None:
    """racing.com meeting code for the race meeting (not trials/jump-outs) at a venue on a date.
    Tries each candidate name (TopRate track name first, then venue) as a URL slug."""
    for name in dict.fromkeys(n for n in names if n):
        d = c.q(MEET_CODE_QUERY, {"venueName": slug(name), "date": date})
        hits = ((d.get("data") or {}).get("GetMeetingByVenue")) or []
        races = [h for h in hits if not h.get("isTrial") and not h.get("isJumpOut")]
        if races:
            return str(races[0]["id"])
    return None


MEETINGS_CSV = ROOT / "ingest/meetings_vic_sa.csv"   # committed VIC/SA/QLD meeting list for backfills (from TopRate)
TRACKS_CSV = ROOT / "ingest/tracks.csv"


def meetings(date_from: str, date_to: str | None, states: list[str]) -> pd.DataFrame:
    """VIC/SA race meetings (date, track, venue) from the DB, else from the committed CSV."""
    if DB.exists():
        import duckdb
        con = duckdb.connect(str(DB), read_only=True)
        return con.execute("""
            select distinct race_date::varchar date, track, venue, state from races
            where not is_trial and not is_jumpout and state in (select unnest(?))
              and race_date >= ?::date and race_date <= coalesce(?::date, current_date)
            order by 1, 2""", [states, date_from, date_to]).df()
    m = pd.read_csv(MEETINGS_CSV, dtype=str)
    m = m[m.state.isin(states) & (m.date >= date_from)]
    return m[m.date <= date_to] if date_to else m


def recent_meetings(days: int, states: list[str]) -> pd.DataFrame:
    """Every VIC/SA track name for each of the last `days` days. The meet-code lookup
    simply finds nothing for tracks that didn't race, so this needs no TopRate data."""
    from datetime import date, timedelta
    t = pd.read_csv(TRACKS_CSV)
    t = t[t.state.isin(states)]
    dates = [(date.today() - timedelta(days=d)).isoformat() for d in range(days, -1, -1)]
    return pd.DataFrame([(d, r.track, r.venue, r.state) for d in dates for r in t.itertuples()],
                        columns=["date", "track", "venue", "state"])


def fetch(ms: pd.DataFrame, delay: float, quiet_missing: bool = False) -> None:
    c = Client(delay)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    codes_file = RAW_DIR / "_meet_codes.csv"
    codes = pd.read_csv(codes_file, dtype=str) if codes_file.exists() else \
        pd.DataFrame(columns=["date", "venue", "meet_code"])
    codes = codes.fillna("")
    known = {(r.date, r.venue): r.meet_code for r in codes.itertuples()}   # venue column holds track name
    print(f"{len(ms)} meeting slots to check")
    for i, m in enumerate(ms.itertuples(), 1):
        key = (m.date, m.track)
        if key not in known:
            try:
                known[key] = meet_code(c, [m.track, m.venue], m.date) or ""
            except Exception as e:
                print(f"  {m.date} {m.track}: meet code lookup failed: {e}"); continue
            if not known[key] and not quiet_missing:
                print(f"  {m.date} {m.track}: no racing.com meeting found")
            pd.DataFrame([(d, v, k) for (d, v), k in known.items()],
                         columns=["date", "venue", "meet_code"]).to_csv(codes_file, index=False)
        code = known[key]
        if not code:
            continue
        races_file = RAW_DIR / f"{code}_races.json.gz"
        if not races_file.exists():
            _save(races_file, c.q(RACES_FOR_MEET % code))
        races = (_load(races_file).get("data") or {}).get("racesForMeet") or []
        for rc in races:
            if not rc.get("hasSectionals"):
                continue
            n = int(rc["raceNumber"])
            f = RAW_DIR / f"{code}_{n:02d}.json.gz"
            if not f.exists():
                try:
                    _save(f, c.q(RACE_FORM % (code, n)))
                except Exception as e:
                    print(f"  {code} R{n}: {e}")
        if i % 25 == 0:
            print(f"  {i}/{len(ms)} meetings")


def _save(p: Path, obj) -> None:
    with gzip.open(p, "wt", encoding="utf-8") as f:
        json.dump(obj, f)


def _load(p: Path):
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- parse

def _secs(t) -> float | None:
    if t in (None, "", "0", "0.00"):
        return None
    t = str(t)
    if ":" in t:
        m, s = t.split(":")
        return int(m) * 60 + float(s)
    return float(t)


def _num(x) -> float | None:
    try:
        return float(str(x).replace("+", ""))
    except (TypeError, ValueError):
        return None


def parse_race(obj: dict, meet_code_: str, race_no: int, meta: dict | None = None):
    f = ((obj.get("data") or {}).get("f") or (obj.get("data") or {}).get("sectionaltimes_callback")) or {}
    meta = meta or {}
    race = dict(meet_code=meet_code_, race_no=race_no, venue=meta.get("venue"),
                start_utc=meta.get("time"), race_distance=meta.get("distance"),
                timing_source=f.get("Source"), timing_complete=f.get("IsComplete"),
                data_complete=f.get("IsCompleteData"), race_time_s=_secs(f.get("RaceTime")))
    runs, secs = [], []
    for h in f.get("Horses") or []:
        run = dict(race, horse=h.get("FullName"), tab_no=h.get("SaddleNumber"),
                   horse_url=h.get("HorseUrl"), barrier=_num(h.get("BarrierNumber")),
                   finish=h.get("FinalPosition"), time_s=_secs(h.get("RaceTime")),
                   beaten_margin_l=h.get("BeatenMargin"),
                   dist_travelled_m=_num(h.get("DistanceRun")) or None,
                   dist_vs_winner_m=_num(h.get("DistanceVarToWinner")),
                   rail_avg_m=h.get("DistanceFromRail"),
                   speed_early_ms=h.get("Early"), speed_mid_ms=h.get("Mid"), speed_late_ms=h.get("Late"),
                   speed_peak_ms=h.get("OverallPeakSpeed"), peak_at=h.get("PeakSpeedLocation"),
                   speed_avg_ms=h.get("OverallAvgSpeed"))
        if run["finish"] == 1 and run["dist_vs_winner_m"] is None:
            run["dist_vs_winner_m"] = 0.0
        runs.append(run)
        for sp in h.get("SplitTimes") or []:
            m = re.match(r"(\d+)m-(\d+m|FINISH)", sp.get("Distance") or "")
            secs.append(dict(meet_code=meet_code_, race_no=race_no, tab_no=run["tab_no"],
                             horse=run["horse"],
                             from_m=int(m.group(1)) if m else None,
                             to_m=(0 if m and m.group(2) == "FINISH" else int(m.group(2)[:-1])) if m else None,
                             pos=sp.get("Position"), split_s=_secs(sp.get("Time")),
                             avg_speed_ms=sp.get("AvgSpeed") or None))
    return runs, secs


def parse_all():
    runs, secs = [], []
    for p in sorted(RAW_DIR.glob("*_[0-9][0-9].json.gz")):
        code, n = p.name.split(".")[0].split("_")
        meta = {}
        rf = RAW_DIR / f"{code}_races.json.gz"
        if rf.exists():
            for rc in (_load(rf).get("data") or {}).get("racesForMeet") or []:
                if int(rc["raceNumber"]) == int(n):
                    meta = dict(rc, venue=(rc.get("meet") or {}).get("venue"))
        a, b = parse_race(_load(p), code, int(n), meta)
        runs += a; secs += b
    return pd.DataFrame(runs), pd.DataFrame(secs)


def main():
    global RAW_DIR, OUT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fetch", "parse"])
    ap.add_argument("--from", dest="date_from", default="2021-08-01")
    ap.add_argument("--to", dest="date_to")
    ap.add_argument("--recent-days", type=int, help="scan every VIC/SA track for the last N days")
    ap.add_argument("--states", default="VIC,SA")
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--raw-dir", type=Path)
    ap.add_argument("--out-dir", type=Path)
    a = ap.parse_args()
    RAW_DIR = a.raw_dir or RAW_DIR
    OUT_DIR = a.out_dir or OUT_DIR
    states = a.states.split(",")
    if a.cmd == "fetch":
        if a.recent_days is not None:
            fetch(recent_meetings(a.recent_days, states), a.delay, quiet_missing=True)
        else:
            fetch(meetings(a.date_from, a.date_to, states), a.delay)
    else:
        runs, secs = parse_all()
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        runs.to_parquet(OUT_DIR / "rc_gps_runs.parquet", index=False)
        secs.to_parquet(OUT_DIR / "rc_gps_sections.parquet", index=False)
        print(f"{len(runs)} runs, {len(secs)} sections")


if __name__ == "__main__":
    sys.exit(main())
