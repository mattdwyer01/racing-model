"""Racing Queensland Triple S GPS data: download meeting ZIPs and parse the XML inside.

Each RQ meeting ZIP holds one XML per race with, per horse and per 200m section:
actual distance run, rank, cumulative and section time, average and top speed (m/s),
stride frequency and length, and average distance to the rail. Plus total distance
travelled and the difference to the winner.

    # 1. download every meeting ZIP listed on the RQ sectionals page (skips ones already saved)
    python ingest/rq_sectionals.py download
    #    or, from a page you saved in the browser:
    python ingest/rq_sectionals.py download --listing path/to/saved_page.html

    # 2. parse every saved ZIP into data/interim/rq_gps_{runs,sections}.parquet
    python ingest/rq_sectionals.py parse
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP_DIR = ROOT / "data/raw/rq_zip"
OUT_DIR = ROOT / "data/interim"
BASE = "https://www.racingqueensland.com.au"
LISTING = BASE + "/industry/thoroughbred/thoroughbred-sectionals"
LINK_RE = re.compile(r"RacingFile\.ashx\?path=(/Sectional/(\d{8})_([^\"'<>&]+?)\.zip)", re.I)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"}


# ---------------------------------------------------------------- download

def list_zips(html: str) -> list[tuple[str, str]]:
    """-> [(path, filename)] for every meeting ZIP linked on the page."""
    seen = {}
    for path, d, name in LINK_RE.findall(html):
        seen[path] = f"{d}_{name}.zip"
    return sorted(seen.items(), key=lambda x: x[1])


def download(listing_file: str | None = None, delay: float = 1.0, since: str | None = None) -> None:
    import requests
    s = requests.Session()
    s.headers.update(UA)
    html = Path(listing_file).read_text(encoding="utf-8", errors="ignore") if listing_file \
        else s.get(LISTING, timeout=60).text
    zips = list_zips(html)
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    if since:
        zips = [(p, f) for p, f in zips if f[:8] >= since.replace("-", "")]
    todo = [(p, f) for p, f in zips if not (ZIP_DIR / f).exists()]
    print(f"{len(zips)} meeting ZIPs listed, {len(todo)} to download")
    for i, (path, fname) in enumerate(todo, 1):
        try:
            r = s.get(f"{BASE}/RacingFile.ashx", params={"path": path}, timeout=60)
            r.raise_for_status()
            if not r.content.startswith(b"PK"):
                print(f"  {fname}: not a zip ({r.headers.get('content-type')}), skipped")
                continue
            (ZIP_DIR / fname).write_bytes(r.content)
        except Exception as e:
            print(f"  {fname}: {type(e).__name__}: {e}")
        if i % 50 == 0:
            print(f"  {i}/{len(todo)}")
        time.sleep(delay)


# ---------------------------------------------------------------- parse

def _secs(t: str | None) -> float | None:
    if not t:
        return None
    h, m, s = t.split(":")
    v = int(h) * 3600 + int(m) * 60 + float(s)
    return v or None


def _f(x: str | None) -> float | None:
    try:
        v = float(x)
        return v
    except (TypeError, ValueError):
        return None


def parse_race_xml(data: bytes, source: str) -> tuple[list[dict], list[dict]]:
    r = ET.fromstring(data)
    race = dict(
        source=source,
        race_date=r.get("EventDate", "")[:10],
        meeting_code=r.get("MeetingCode"),
        race_code=r.get("RaceCode"),
        course=r.findtext("CourseName"),
        race_name=r.findtext("RaceName"),
        track_config=r.findtext("TrackName"),
        going=r.findtext("TrackCondition"),
        rail_text=r.findtext("RailPosition"),
        race_time_s=_secs(ft.get("Time") if (ft := r.find("FinishTime")) is not None else None),
    )
    m = re.search(r"_R(\d+)\.xml$", source)
    race["race_no"] = int(m.group(1)) if m else None
    runs, secs = [], []
    for h in r.iter("HorseSummary"):
        state = h.findtext("ResultState")
        run = dict(race,
                   horse=h.get("Name"), horse_code=h.get("HorseCode"),
                   tab_no=_int(h.get("Bib")), draw_number_unreliable=_int(h.get("DrawNumber")),  # repeats tab no; use TopRate barrier
                   finish=_int(h.get("FinalRank")), result_state=state,
                   dist_travelled_m=_f(h.get("DistanceTravelled")),
                   dist_vs_winner_m=_f((h.get("DistanceTraveledDifference") or "").replace("+", "")),
                   official_margin=_f(h.get("OfficialMarginDecimal")),
                   time_s=_secs((h.find("FinishTime").get("Time")) if h.find("FinishTime") is not None else None),
                   top_speed_ms=_f((h.findtext("TopSpeed") or "").split(" ")[0]))
        runs.append(run)
        sections = h.find("Sections")
        if sections is None:
            continue
        for s in sections:
            it, st = s.find("IntermediateTime"), s.find("SectionTime")
            secs.append(dict(
                race_code=race["race_code"], race_date=race["race_date"], course=race["course"],
                race_no=race["race_no"], tab_no=run["tab_no"], horse=run["horse"],
                cum_dist_m=_int(s.get("CumulatedDistance")),
                real_dist_m=_f(s.findtext("RealDistance")),
                rank=_int(s.findtext("Rank")),
                elapsed_s=_secs(it.get("Time") if it is not None else None),
                split_s=_secs(st.get("Time") if st is not None else None),
                avg_speed_ms=_f(s.findtext("AvgSpeed")), top_speed_ms=_f(s.findtext("TopSpeed")),
                stride_hz=_f(s.findtext("AverageStrideFrequency")),
                stride_m=_f(s.findtext("AverageStrideLength")),
                rail_m=_f(s.findtext("AverageDistanceToRail")),
            ))
    return runs, secs


def _int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return None


def parse_all() -> tuple[pd.DataFrame, pd.DataFrame]:
    runs, secs = [], []
    for z in sorted(ZIP_DIR.glob("*.zip")):
        try:
            zf = zipfile.ZipFile(z)
        except Exception as e:
            print(f"  {z.name}: {type(e).__name__}: {e}")
            continue
        with zf:
            for n in zf.namelist():
                if not n.lower().endswith(".xml"):
                    continue
                try:  # one bad race XML must not drop the rest of the meeting
                    a, b = parse_race_xml(zf.read(n), n)
                except Exception as e:
                    print(f"  {z.name}/{n}: {type(e).__name__}: {e}")
                    continue
                for r in a:
                    r["zip_file"] = z.name
                runs += a
                secs += b
    runs, secs = pd.DataFrame(runs), pd.DataFrame(secs)
    # scratched / non-tracked horses carry all-zero sections: blank them
    if not secs.empty:
        dead = (secs["split_s"].isna()) | (secs["avg_speed_ms"].fillna(0) == 0)
        secs.loc[dead, ["real_dist_m", "avg_speed_ms", "top_speed_ms", "stride_hz", "stride_m", "rail_m"]] = None
    return runs, secs


def main():
    global ZIP_DIR, OUT_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["download", "parse"])
    ap.add_argument("--since", help="only download meetings on or after this date (YYYY-MM-DD)")
    ap.add_argument("--zip-dir", type=Path)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--listing", help="saved RQ sectionals page (HTML) instead of fetching it")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between downloads")
    a = ap.parse_args()
    ZIP_DIR = a.zip_dir or ZIP_DIR
    OUT_DIR = a.out_dir or OUT_DIR
    if a.cmd == "download":
        download(a.listing, a.delay, a.since)
    else:
        runs, secs = parse_all()
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        for d in (runs, secs):
            for c in ["tab_no", "cum_dist_m", "race_no", "rank", "finish"]:
                if c in d:
                    d[c] = pd.to_numeric(d[c], errors="coerce")
        runs.to_parquet(OUT_DIR / "rq_gps_runs.parquet", index=False)
        secs.to_parquet(OUT_DIR / "rq_gps_sections.parquet", index=False)
        print(f"{runs.race_code.nunique() if len(runs) else 0} races, {len(runs)} runs, {len(secs)} sections")


if __name__ == "__main__":
    sys.exit(main())
