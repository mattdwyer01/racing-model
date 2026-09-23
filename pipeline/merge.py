"""Merge newly scraped parquet into the stored copy, newest row wins on duplicate keys.

    python pipeline/merge.py OUT.parquet KEY1,KEY2 EXISTING.parquet NEW1.parquet [NEW2 ...]

Missing input files are skipped, so the first ever run (nothing stored yet) works.
"""
import sys
from pathlib import Path

import pandas as pd


def merge(out: str, keys: list[str], inputs: list[str]) -> pd.DataFrame:
    frames = [pd.read_parquet(p) for p in inputs if Path(p).exists() and Path(p).stat().st_size]
    frames = [f for f in frames if len(f)]
    if not frames:
        print(f"{out}: nothing to merge")
        return pd.DataFrame()
    df = pd.concat(frames, ignore_index=True)
    # keys may have been read with different dtypes across files; compare as strings
    for k in keys:
        df[k] = df[k].astype("string")
    df = df.drop_duplicates(subset=keys, keep="last").reset_index(drop=True)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"{out}: {len(df):,} rows")
    return df


if __name__ == "__main__":
    merge(sys.argv[1], sys.argv[2].split(","), sys.argv[3:])
