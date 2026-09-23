"""Ship the Vultr box's TAB price log into the data store, one file per month.

The TopRate poller (with tab_price_log.py) writes ~/racing-data/tab_prices/YYYY-MM-DD.csv[.gz].
This combines each month's days into tab_prices_YYYY-MM.csv.gz and uploads it,
replacing the previous upload, so the store always has every captured price.

    python pipeline/archive_tab_prices.py [--months 2]
"""
import argparse
import gzip
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import store  # noqa: E402

LOG_DIR = Path(os.environ.get("PRICE_LOG_DIR", Path.home() / "racing-data" / "tab_prices"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=2, help="how many recent months to (re)upload")
    a = ap.parse_args()
    files = sorted(LOG_DIR.glob("*.csv*"))
    if not files:
        sys.exit(f"no price logs in {LOG_DIR}")
    months = sorted({f.name[:7] for f in files})[-a.months:]
    out_dir = Path("work"); out_dir.mkdir(exist_ok=True)
    for m in months:
        out = out_dir / f"tab_prices_{m}.csv.gz"
        header_done = False
        with gzip.open(out, "wt", newline="") as dst:
            for f in sorted(LOG_DIR.glob(f"{m}-*.csv*")):
                opener = gzip.open if f.suffix == ".gz" else open
                with opener(f, "rt", newline="") as src:
                    first = src.readline()
                    if not header_done:
                        dst.write(first); header_done = True
                    shutil.copyfileobj(src, dst)
        store.put(out)


if __name__ == "__main__":
    main()
