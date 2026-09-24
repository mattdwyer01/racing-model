"""Daily pull from the public TopRate repo (github.com/mattdwyer01/toprate): results, runners, TAB prices.

    python pipeline/pull_toprate.py            # download, archive prices, upload changed files to the store
    python pipeline/pull_toprate.py --no-store # download only (local runs)

Downloads (raw.githubusercontent.com, no credentials: the repo is public):
  race_results_<year>.csv.gz  current year (and last year in January)  -> data/raw/toprate/
  toprate_runners.csv         dashboard runners file: upcoming fields, race times, fixed prices -> data/raw/live/
  toprate_price_history.csv   rolling window of TAB fixed-price snapshots (run_id, snapshot_time, price)
Archives the price snapshots: merged into data/interim/tab_price_snapshots.csv.gz (deduplicated), so bet-time
price history keeps growing after the rolling window drops old rows. Changed files are uploaded to the store.
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
    new.to_csv(SNAPSHOTS, index=False, compression="gzip")
    print(f"price snapshots archived: {len(new):,} rows, {new['race_id'].nunique():,} races", flush=True)


def main():
    use_store = "--no-store" not in sys.argv
    if use_store:
        store.get(SNAPSHOTS.name, SNAPSHOTS)          # keep the archive growing across runs / machines
    today = dt.date.today()
    years = [today.year] + ([today.year - 1] if today.month == 1 else [])
    files = {f"race_results_{y}.csv.gz": ROOT / "data/raw/toprate" / f"race_results_{y}.csv.gz" for y in years}
    files["toprate_runners.csv"] = ROOT / "data/raw/live/toprate_runners.csv"
    changed = [name for name, dest in files.items() if _download(name, dest)]
    hist = ROOT / "data/raw/live/toprate_price_history.csv"
    _download("toprate_price_history.csv", hist)
    archive_prices(hist)
    if use_store:
        for name in changed:
            store.put(files[name], name)
        store.put(SNAPSHOTS, SNAPSHOTS.name)


if __name__ == "__main__":
    main()
