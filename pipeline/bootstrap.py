"""Fresh-machine setup: pull raw inputs from the data store, then build the core db.

    python pipeline/bootstrap.py            # skip files already on disk
    python pipeline/bootstrap.py --force    # re-download everything

Pulls every race_results_YYYY.csv.gz into data/raw/toprate/ and toprate_runners.csv
into data/raw/live/, GPS parquets (rq_/rc_gps_*) and the git price history into data/interim/, then runs ingest/build_core.py.
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
GPS = re.compile(r"(rq|rc)_gps_(runs|sections)\.parquet|tab_price_history_from_git\.csv\.gz|ra_fields\.parquet")


def pull(force=False):
    names = store.assets()
    wanted = {n: ROOT / "data/raw/toprate" / n for n in names if TOPRATE.fullmatch(n)}
    if LIVE in names:
        wanted[LIVE] = ROOT / "data/raw/live" / LIVE
    for n in names:
        if GPS.fullmatch(n):
            wanted[n] = ROOT / "data/interim" / n
    if not any(TOPRATE.fullmatch(n) for n in wanted):
        sys.exit("no TopRate yearly files in the store")
    for n, dest in sorted(wanted.items()):
        if dest.exists() and dest.stat().st_size == names[n]["size"] and not force:
            print(f"have {n}")
            continue
        store.get(n, dest)
        print(f"got  {n} ({dest.stat().st_size:,} bytes)")
    _numeric_gps()


def _numeric_gps():
    """Older daily parses stored some RQ GPS numbers as strings; every reader expects numbers."""
    import pandas as pd
    for n in ("rq_gps_runs.parquet", "rq_gps_sections.parquet"):
        p = ROOT / "data/interim" / n
        if not p.exists():
            continue
        d = pd.read_parquet(p)
        cols = [c for c in ("tab_no", "cum_dist_m", "race_no", "rank", "finish")
                if c in d and not pd.api.types.is_numeric_dtype(d[c])]
        if cols:
            d[cols] = d[cols].apply(pd.to_numeric, errors="coerce")
            d.to_parquet(p, index=False)
            print(f"fixed {n}: {', '.join(cols)} to numbers")


if __name__ == "__main__":
    pull(force="--force" in sys.argv)
    con = build_core.build()
    for t in [r[0] for r in con.sql("show tables").fetchall()]:
        print(t, f"{con.sql(f'select count(*) from {t}').fetchone()[0]:,}")
