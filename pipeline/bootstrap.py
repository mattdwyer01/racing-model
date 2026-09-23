"""Fresh-machine setup: pull raw inputs from the data store, then build the core db.

    python pipeline/bootstrap.py            # skip files already on disk
    python pipeline/bootstrap.py --force    # re-download everything

Pulls every race_results_YYYY.csv.gz into data/raw/toprate/ and toprate_runners.csv
into data/raw/live/, then runs ingest/build_core.py.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ingest import build_core  # noqa: E402
from pipeline import store  # noqa: E402

TOPRATE = re.compile(r"race_results_\d{4}\.csv\.gz")
LIVE = "toprate_runners.csv"


def pull(force=False):
    names = store.assets()
    wanted = {n: ROOT / "data/raw/toprate" / n for n in names if TOPRATE.fullmatch(n)}
    if LIVE in names:
        wanted[LIVE] = ROOT / "data/raw/live" / LIVE
    if not any(TOPRATE.fullmatch(n) for n in wanted):
        sys.exit("no TopRate yearly files in the store")
    for n, dest in sorted(wanted.items()):
        if dest.exists() and dest.stat().st_size == names[n]["size"] and not force:
            print(f"have {n}")
            continue
        store.get(n, dest)
        print(f"got  {n} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    pull(force="--force" in sys.argv)
    con = build_core.build()
    for t in [r[0] for r in con.sql("show tables").fetchall()]:
        print(t, f"{con.sql(f'select count(*) from {t}').fetchone()[0]:,}")
