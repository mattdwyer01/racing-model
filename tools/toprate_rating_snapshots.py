"""TopRate rating and form factor as they stood BEFORE each race, from the git history of toprate_runners.csv.

    python tools/toprate_rating_snapshots.py --repo ../toprate     # -> data/interim/toprate_rating_prerace.csv.gz

The runners file keeps overwriting toprate_rating through the day (it follows the market: on 24 Sep 2026 the
change from the morning file to the final one correlated 0.33 with -log SP and winners rose 0.27 points vs their
race), so the last stored value is not what was known before the jump. Per race day D (26 Apr 2026 on) this reads
the last commit before 08:00, 12:00 and 15:00 AEST, and each race takes the latest snapshot at least 10 minutes
before its start (race_times.start_utc; the 08:00 snapshot when the start is unknown).
Output: run_id, race_id, snap_utc, trr_pre, pfm_pre, proj_pre (TopRate WPR projection), contrib_pre (its
adjustment breakdown JSON, incl. speed_map / track_barrier).
"""
import argparse
import io
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402

FILE = "toprate_runners.csv"
OUT = ROOT / "data/interim/toprate_rating_prerace.csv.gz"
SNAP_AEST = [8, 12, 15]
START, END = date(2026, 4, 26), date(2026, 9, 23)


def _commit_before(repo, t_utc):
    out = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%H", f"--before={t_utc.isoformat()}",
                          "origin/main", "--", FILE], capture_output=True, text=True).stdout.strip()
    return out or None


def _read(repo, sha):
    data = subprocess.run(["git", "-C", repo, "show", f"{sha}:{FILE}"], capture_output=True, check=True).stdout
    import pyarrow.csv as pc
    head = data[:data.index(b"\n")].decode().split(",")
    want = [c for c in ["run_id", "race_id", "date", "toprate_rating", "pfm_score", "wprp_proj", "wprp_contrib"]
            if c in head]
    t = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=want, column_types={"run_id": "string", "race_id": "string", "date": "string",
                                            "wprp_contrib": "string"}))
    return t.to_pandas()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--start", default=None, help="first race day (default 2026-04-26)")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    con = duckdb.connect(str(figure.DB), read_only=True)
    starts = con.sql("select race_id::varchar race_id, start_utc from race_times").df()
    starts["start_utc"] = pd.to_datetime(starts["start_utc"], utc=True)
    rows = []
    d = date.fromisoformat(a.start) if a.start else START
    while d <= END:
        snaps = []
        for h in SNAP_AEST:
            t = datetime(d.year, d.month, d.day, h, tzinfo=timezone(timedelta(hours=10))).astimezone(timezone.utc)
            sha = _commit_before(a.repo, t)
            if sha and sha not in [s[1] for s in snaps]:
                snaps.append((t, sha))
        for t, sha in snaps:
            try:
                df = _read(a.repo, sha)
            except Exception as e:
                print(f"{d} {t:%H:%M}Z {sha[:8]}: {type(e).__name__}", flush=True)
                continue
            df = df[df["date"] == d.isoformat()]
            df = df.assign(snap_utc=t)
            rows.append(df)
        print(d, len(snaps), "snapshots", flush=True)
        d += timedelta(days=1)
    s = pd.concat(rows, ignore_index=True)
    s = s.merge(starts, on="race_id", how="left")
    ok = s["start_utc"].isna() & (s["snap_utc"].dt.hour == (SNAP_AEST[0] - 10) % 24) | \
        (s["snap_utc"] <= s["start_utc"] - pd.Timedelta(minutes=10))
    s = s[ok].sort_values("snap_utc").drop_duplicates("run_id", keep="last")
    s = s.rename(columns={"toprate_rating": "trr_pre", "pfm_score": "pfm_pre"})
    s = s.rename(columns={"wprp_proj": "proj_pre", "wprp_contrib": "contrib_pre"})
    keep = [c for c in ["run_id", "race_id", "snap_utc", "trr_pre", "pfm_pre", "proj_pre", "contrib_pre"] if c in s]
    s[keep].to_csv(a.out, index=False, compression="gzip")
    print(f"{len(s):,} runners -> {a.out}")


if __name__ == "__main__":
    main()
