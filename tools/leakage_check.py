"""Leakage test: model inputs for races on day D must not change when every result from D on is removed.

    python tools/leakage_check.py [--day 2025-11-04] [--train-end 2025-01-01]

Copies the db, sets every res_* column (runs, races, gps_runs) to NULL for races on or after D (SP kept:
it is the intended market input), builds all model inputs from both dbs with fitted pieces trained before
--train-end, and compares every GBM / logit input for runs on D. Any use of a same-race or later result
shows up as a difference. Prints per-feature max abs diff; exit code 1 if any exceeds 1e-9.
"""
import argparse
import shutil
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402
from model import offset_model as om  # noqa: E402


def blank_results(path, day):
    con = duckdb.connect(str(path))
    for table, where in [("runs", f"race_date >= date '{day}'"),
                         ("races", f"race_date >= date '{day}'"),
                         ("gps_runs", f"run_id in (select run_id from runs where race_date >= date '{day}')")]:
        cols = [r[0] for r in con.sql(f"describe {table}").fetchall() if r[0].startswith("res_")]
        con.execute(f"update {table} set {', '.join(f'{c} = null' for c in cols)} where {where}")
        print(f"blanked {len(cols)} res_ columns in {table}")
    con.close()


def inputs(db, day, train_end):
    con = duckdb.connect(str(db), read_only=True)
    e = om.build_features(con, train_end)
    e = e[e["race_date"] == pd.Timestamp(day)].copy()
    inv = 1 / e["sp"].where(e["sp"] > 1)
    e["log_p_sp"] = np.log(inv / inv.groupby(e["race_id"]).transform("sum"))
    e["log_n"] = np.log1p(e["h_n"])
    e["log_days"] = np.log1p(e["days_since_start"].fillna(0))
    e["first_up"] = (e["days_since_start"].fillna(999) >= 60).astype(float)
    return om.add_context(e).set_index("run_id").sort_index()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", default="2025-11-04")
    ap.add_argument("--train-end", default="2025-01-01")
    a = ap.parse_args()
    tmp = ROOT / "data/leakage_check.duckdb"   # data/ is not in git
    shutil.copy(figure.DB, tmp)
    blank_results(tmp, a.day)
    full = inputs(figure.DB, a.day, a.train_end)
    blank = inputs(tmp, a.day, a.train_end)
    tmp.unlink()
    from model import extra_history as eh
    from model import rating
    feats = list(dict.fromkeys(om.GBM_FEATS + ["log_p_sp"] + eh.GX_FEATS + eh.CM_FEATS
                               + [c for c in rating.X_COLS + rating.SIGMA_COLS if c != "fig_sd"]))
    assert full.index.equals(blank.index), "different runs on the test day"
    diff = (full[feats].astype(float) - blank[feats].astype(float)).abs().max().sort_values(ascending=False)
    nan_mismatch = (full[feats].isna() != blank[feats].isna()).sum()
    print(f"day {a.day}: {len(full):,} runs, {full['race_id'].nunique()} races, {len(feats)} inputs compared")
    print("max abs diff, top 10:\n" + diff.head(10).to_string())
    bad = diff[diff > 1e-9].index.union(nan_mismatch[nan_mismatch > 0].index)
    print("LEAK in: " + ", ".join(bad) if len(bad) else "no leakage: every input identical with results removed")
    sys.exit(1 if len(bad) else 0)


if __name__ == "__main__":
    main()
