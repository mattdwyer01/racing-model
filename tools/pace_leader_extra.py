"""Walk-forward race-day projection v3 for NSW / WA (same as tools/pace_leader_test.build, other states).

    RACING_EXTRA_STATES=NSW,WA python -W ignore tools/pace_leader_extra.py   # -> data/interim/pace_leader_oos_nswwa.parquet

Projection fitted on 2019 to Y-1 with NSW / WA in scope (as production trains), runners of NSW / WA races in Y kept.
Used by tools/value_model.py to test the value model outside VIC / SA / QLD.
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure, projection  # noqa: E402
from pace_leader_test import KEEP  # noqa: E402

OUT = ROOT / "data/interim/pace_leader_oos_nswwa.parquet"


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = projection.frame(con)
    print("frame", len(x0), flush=True)
    parts = []
    for y in [2023, 2024, 2025, 2026]:
        x, _, ex = projection.project(x0, f"{y}-01-01")
        te = x[(x.race_date.dt.year == y) & x["state"].isin(["NSW", "WA"])]
        parts.append(te[KEEP].assign(fold=y))
        print(y, len(te), flush=True)
        del x
    pd.concat(parts, ignore_index=True).to_parquet(OUT)


if __name__ == "__main__":
    main()
