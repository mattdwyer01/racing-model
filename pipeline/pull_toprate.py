"""Daily pull from the public TopRate repo (github.com/mattdwyer01/toprate): results, runners, TAB prices.

    python pipeline/pull_toprate.py            # download, archive prices, upload changed files to the store
    python pipeline/pull_toprate.py --no-store # download only (local runs)

Downloads (raw.githubusercontent.com, no credentials: the repo is public):
  race_results_<year>.csv.gz  current year (and last year in January)  -> data/raw/toprate/
  toprate_runners.csv         dashboard runners file: upcoming fields, race times, fixed prices -> data/raw/live/
  toprate_runners_archive.csv.gz  its races older than 60 days (split off 1 Oct 2026) -> data/raw/live/
  toprate_price_history.csv   rolling window of TAB fixed-price snapshots (run_id, snapshot_time, price)
Archives the price snapshots: merged into data/interim/tab_price_snapshots.csv.gz (deduplicated), so bet-time
price history keeps growing after the rolling window drops old rows. Changed files are uploaded to the store.
Dated WPRs: data/interim/wpr_dated.csv.gz keeps every (run_id, wpr, wprStatus) the first day it is seen and again
whenever TopRate revises it (`seen` = pull date, AEST), from the current and last year's results files. wpr_asof()
gives the value a run had on a given date (TopRate revises WPRs after race day: wpr_revision_test.md).
"""
import datetime as dt
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import store  # noqa: E402

BASE = "https://raw.githubusercontent.com/mattdwyer01/toprate/main/"
SNAPSHOTS = ROOT / "data/interim/tab_price_snapshots.csv.gz"
WPR_DATED = ROOT / "data/interim/wpr_dated.csv.gz"
AEST = dt.timezone(dt.timedelta(hours=10))


def _download(name, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(BASE + name, stream=True, timeout=300) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    changed = not dest.exists() or dest.read_bytes() != tmp.read_bytes()
    tmp.replace(dest)
    print(f"{name}: {dest.stat().st_size:,} bytes{' (changed)' if changed else ''}", flush=True)
    return changed


def archive_prices(history_csv):
    new = pd.read_csv(history_csv)
    if SNAPSHOTS.exists():
        new = pd.concat([pd.read_csv(SNAPSHOTS), new], ignore_index=True)
    new = new.drop_duplicates(["run_id", "snapshot_time"]).sort_values(["race_id", "run_id", "snapshot_time"])
    SNAPSHOTS.parent.mkdir(parents=True, exist_ok=True)
    new.to_csv(SNAPSHOTS, index=False, compression="gzip")
    print(f"price snapshots archived: {len(new):,} rows, {new['race_id'].nunique():,} races", flush=True)


def archive_wpr(results_files, today):
    """Append (run_id, wpr, wprStatus, seen) for runs that are new or whose WPR / status changed since last seen."""
    cur = pd.concat([pd.read_csv(f, usecols=["run_id", "date", "wpr", "wprStatus"], dtype={"run_id": str})
                     for f in results_files if f.exists()], ignore_index=True)
    cur = cur[cur["wpr"].notna()].drop_duplicates("run_id", keep="last")
    cur["wpr"] = cur["wpr"].round(2)
    old = pd.read_csv(WPR_DATED, dtype={"run_id": str}) if WPR_DATED.exists() else \
        pd.DataFrame(columns=["run_id", "date", "wpr", "wprStatus", "seen"])
    last = old.sort_values("seen", kind="stable").drop_duplicates("run_id", keep="last").set_index("run_id")
    m = cur.join(last[["wpr", "wprStatus"]], on="run_id", rsuffix="_old")
    new = m[m["wpr_old"].isna() | (m["wpr"] != m["wpr_old"]) | (m["wprStatus"].fillna("") != m["wprStatus_old"].fillna(""))]
    new = new[["run_id", "date", "wpr", "wprStatus"]].assign(seen=str(today))
    out = pd.concat([old, new], ignore_index=True)
    WPR_DATED.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(WPR_DATED, index=False, compression="gzip")
    print(f"dated WPRs: {len(new):,} new or revised rows ({len(out):,} total, {out['run_id'].nunique():,} runs)", flush=True)
    return len(new) > 0


def wpr_asof(asof):
    """WPR (and status) of every archived run as it stood at the end of `asof` (YYYY-MM-DD)."""
    d = pd.read_csv(WPR_DATED, dtype={"run_id": str})
    d = d[d["seen"] <= str(asof)].sort_values("seen", kind="stable")
    return d.drop_duplicates("run_id", keep="last").set_index("run_id")[["wpr", "wprStatus", "seen"]]


def main():
    use_store = "--no-store" not in sys.argv
    if use_store:
        store.get(SNAPSHOTS.name, SNAPSHOTS)          # keep the archive growing across runs / machines
        store.get(WPR_DATED.name, WPR_DATED)
    today = dt.datetime.now(AEST).date()
    years = [today.year] + ([today.year - 1] if today.month == 1 else [])
    prev = ROOT / "data/raw/toprate" / f"race_results_{today.year - 1}.csv.gz"
    if today.month != 1:                            # last year's file: TopRate re-rates older runs too
        try:
            _download(prev.name, prev)
        except requests.HTTPError as e:
            print(f"{prev.name}: {e.response.status_code}", flush=True)
    files = {f"race_results_{y}.csv.gz": ROOT / "data/raw/toprate" / f"race_results_{y}.csv.gz" for y in years}
    files["toprate_runners.csv"] = ROOT / "data/raw/live/toprate_runners.csv"
    # races older than 60 days (TopRate runners_io.py split, 1 Oct 2026)
    files["toprate_runners_archive.csv.gz"] = ROOT / "data/raw/live/toprate_runners_archive.csv.gz"
    changed = []
    for name, dest in files.items():
        try:
            if _download(name, dest):
                changed.append(name)
        except requests.HTTPError as e:            # the archive only exists once TopRate has split the file
            if name != "toprate_runners_archive.csv.gz":
                raise
            print(f"{name}: not there yet ({e.response.status_code})", flush=True)
    hist = ROOT / "data/raw/live/toprate_price_history.csv"
    _download("toprate_price_history.csv", hist)
    archive_prices(hist)
    wpr_changed = archive_wpr([prev] + list(v for k, v in files.items() if k.startswith("race_results_")), today)
    if use_store:
        if wpr_changed:
            store.put(WPR_DATED, WPR_DATED.name)
        for name in changed:
            store.put(files[name], name)
        store.put(SNAPSHOTS, SNAPSHOTS.name)


if __name__ == "__main__":
    main()
