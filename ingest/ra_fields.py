"""Carried weights (and barriers) from Racing Australia's free fields pages -> data/interim/ra_fields.parquet.

    python ingest/ra_fields.py              # fetch every listed meeting, merge into the store copy, upload
    python ingest/ra_fields.py --no-store   # local only

TopRate stopped carrying weights (results files from 12 Sep 2026; the runners file and toprate_data.json never
had them), so upcoming races lost the weight input and resulted ones have no weight history. Racing Australia
publishes every Australian meeting's fields with barrier, weight and apprentice claim after acceptances
(racingaustralia.horse/FreeFields). Its calendar lists only current and upcoming meetings, so this runs daily
(dashboard.yml) and keeps an archive: past days cannot be backfilled.
Weight: the carried weight after any apprentice claim, the same as TopRate's weightCarried. The Weight column
is the allotted weight; the jockey cell shows "(a3/55kg)" = claim 3kg, rider's lowest riding weight 55kg, so
carried = max(weight - claim, riding weight) (a light allotment the rider cannot make is carried overweight). ingest/build_core.py fills missing weights from this file by
date + horse name.
"""
from __future__ import annotations

import html
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
OUT = ROOT / "data/interim/ra_fields.parquet"
BASE = "https://www.racingaustralia.horse/FreeFields/"
STATES = ["VIC", "QLD", "SA", "NSW", "WA", "TAS"]
HEADERS = {"User-Agent": "Mozilla/5.0 (racing-model fields fetch)"}
# calendar links that identify a meeting with a published field (each is fetched as its Form page)
PAGES = ("Form", "Acceptances", "Results")


def horse_key(name: str) -> str:
    """Name key shared with build_core: lower case, country suffix and non-letters dropped."""
    s = html.unescape(str(name)).lower()
    s = re.sub(r"\s*\([a-z]{2,3}\)\s*$", "", s)
    return re.sub(r"[^a-z]", "", s)


def _text(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def _kg(s: str) -> float | None:
    m = re.search(r"(\d+(?:\.\d+)?)\s*kg", s)
    return float(m.group(1)) if m else None


def parse_meeting(page: str, key: str) -> list[dict]:
    date_s, state, venue = (unquote(key).split(",") + ["", ""])[:3]
    date = datetime.strptime(date_s, "%Y%b%d").date()
    rows = []
    parts = re.split(r'<a name="Race(\d+)"', page)
    for i in range(1, len(parts) - 1, 2):
        race_no, chunk = int(parts[i]), parts[i + 1]
        t = re.search(r'class="race-strip-fields">(.*?)</table>', chunk, re.S)
        if not t:
            continue
        for tr in re.findall(r"<tr class='(?:Odd|Even)Row'[^>]*>(.*?)</tr>", t.group(1), re.S):
            cell = {c: v for c, v in re.findall(r"<td[^>]*class=[\"'](\w+)[\"'][^>]*>(.*?)</td>", tr, re.S)}
            if "horse" not in cell:
                continue
            no = re.search(r"\d+", _text(cell.get("no", "")))
            weight = _kg(_text(cell.get("weight", "")))
            claim = re.search(r"\(a(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)kg\)", cell.get("jockey", ""))
            c_kg = float(claim.group(1)) if claim else 0.0
            carried = None if weight is None else max(weight - c_kg, float(claim.group(2)) if claim else 0.0)
            barrier = re.search(r"\d+", _text(cell.get("barrier", "")))
            rows.append({
                "date": date, "state": state, "venue": venue, "race_no": race_no,
                "tab_no": int(no.group()) if no else None, "horse": _text(cell["horse"]),
                "horse_key": horse_key(_text(cell["horse"])),
                "barrier": int(barrier.group()) if barrier else None, "weight_kg": weight,
                "claim_kg": -c_kg, "carried_kg": carried,
                "scratched": "scratched" in tr.lower(),
            })
    return rows


def fetch(session: requests.Session) -> pd.DataFrame:
    keys = set()
    for st in STATES:
        cal = session.get(f"{BASE}Calendar.aspx?State={st}", headers=HEADERS, timeout=60).text
        for page, key in re.findall(r'href="/FreeFields/(\w+)\.aspx\?Key=([^"&]+)', cal):
            if page in PAGES and ",Trial" not in unquote(key) and ",Jumpout" not in unquote(key):
                keys.add((page, key))
    # one page per meeting: the Form page (final field with barriers and weights) for every listed meeting, even
    # when the calendar only links its Acceptances or Results page (Results uses a different layout)
    best = {unquote(key): ("Form", key) for _, key in keys}
    # The site answers some requests in a burst with an ~8 KB stub page (no fields table): retry those in later
    # passes after a pause. A meeting whose fields are not published yet stays empty and is tried next run.
    rows, todo = [], sorted(best.items())
    for pas in range(3):
        failed = []
        for k, (page, key) in todo:
            try:
                r = session.get(f"{BASE}{page}.aspx?Key={key}", headers=HEADERS, timeout=60)
                got = parse_meeting(r.text, key)
                size = len(r.text)
            except (requests.RequestException, ValueError) as e:
                got, size = [], 0
                print(f"{k}: failed ({e})", flush=True)
            if got:
                rows += got
                print(f"{k}: {page}, {len(got)} runners", flush=True)
            elif size < 50_000:
                failed.append((k, (page, key)))
            time.sleep(2 + 2 * pas)
        if not failed:
            break
        print(f"pass {pas + 1}: {len(failed)} meetings returned a stub page, retrying", flush=True)
        todo = failed
        time.sleep(60)
        session = requests.Session()
    else:
        print(f"still no fields for: {', '.join(k for k, _ in todo)}", flush=True)
    out = pd.DataFrame(rows)
    if len(out):
        out["fetched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return out


def main():
    use_store = "--no-store" not in sys.argv
    if use_store:
        import store
        store.get(OUT.name, OUT)
    old = pd.read_parquet(OUT) if OUT.exists() else pd.DataFrame()
    new = fetch(requests.Session())
    both = pd.concat([old, new], ignore_index=True)
    if len(both):
        both["date"] = pd.to_datetime(both["date"]).dt.date
        # latest fetch wins per runner (a Results page supersedes the fields page)
        both = both.sort_values("fetched_at").drop_duplicates(["date", "venue", "race_no", "horse_key"], keep="last")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        both.to_parquet(OUT, index=False)
    print(f"ra_fields: {len(new):,} runners fetched, {len(both):,} archived "
          f"({both['carried_kg'].notna().mean() if len(both) else 0:.0%} with a weight)", flush=True)
    if use_store and len(both):
        store.put(OUT, OUT.name)


if __name__ == "__main__":
    main()
