"""What the dashboard showed before each race, from the TopRate repo's git history (22 Aug 2026 on).

    git -C ../toprate fetch --shallow-since=2026-08-21 --filter=blob:none origin main    # once
    python tools/dashboard_snapshots.py --repo ../toprate --end 2026-09-30   # -> data/interim/dash_snapshots/*.parquet

Per race day D, snapshots of toprate_runners.csv and racing_model.json at SNAP_AEST hours (the last commit before
each); each runner keeps the latest snapshot at least 10 minutes before its start (start_time in the runners file).
Per runner: TopRate rating, WPR projection and its adjustment breakdown (speed_map, track_barrier), fixed price
(the dashboard's stored TAB price at that time), and, from racing_model.json (24 Sep on), the Racing Model's
race-day adjustment (d) and past ground-loss credit. One parquet per day (reruns skip finished days).
"""
import argparse
import io
import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/interim/dash_snapshots"
SNAP_AEST = [8, 10, 11, 12, 13, 14, 15, 16, 17]
AEST = timezone(timedelta(hours=10))
COLS = ["run_id", "race_id", "date", "start_time", "toprate_rating", "wprp_proj", "wprp_contrib", "fixed_win_price",
        "scratched"]


def _sha(repo, t_utc, path):
    return subprocess.run(["git", "-C", repo, "log", "-1", "--format=%H", f"--before={t_utc.isoformat()}", "origin/main",
                           "--", path], capture_output=True, text=True).stdout.strip() or None


def _runners(repo, sha, day):
    import pyarrow.csv as pc
    data = subprocess.run(["git", "-C", repo, "show", f"{sha}:toprate_runners.csv"], capture_output=True,
                          check=True).stdout
    head = data[:data.index(b"\n")].decode().split(",")
    t = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=[c for c in COLS if c in head],
        column_types={"run_id": "string", "race_id": "string", "date": "string", "start_time": "string",
                      "wprp_contrib": "string"})).to_pandas()
    return t[t["date"] == day]


def _model(repo, sha):
    data = subprocess.run(["git", "-C", repo, "show", f"{sha}:racing_model.json"], capture_output=True, check=True).stdout
    rm = json.loads(data)
    return pd.DataFrame([{"run_id": k, "rm_d": v.get("d"), "rm_gl": (v.get("gb") or {}).get("ground loss (past runs)"),
                          "rm_p": v.get("p")} for k, v in rm["runners"].items()])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--start", default="2026-08-22")
    ap.add_argument("--end", default=str(date.today() - timedelta(days=1)))
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    d = date.fromisoformat(a.start)
    while d <= date.fromisoformat(a.end):
        f = OUT / f"{d}.parquet"
        if f.exists():
            d += timedelta(days=1)
            continue
        rows, seen = [], set()
        for h in SNAP_AEST:
            t = datetime(d.year, d.month, d.day, h, tzinfo=AEST).astimezone(timezone.utc)
            sha = _sha(a.repo, t, "toprate_runners.csv")
            if not sha or sha in seen:
                continue
            seen.add(sha)
            try:
                r = _runners(a.repo, sha, str(d))
            except Exception as e:                       # noqa: BLE001
                print(d, h, "runners", type(e).__name__, flush=True)
                continue
            msha = _sha(a.repo, t, "racing_model.json")
            if msha:
                try:
                    r = r.merge(_model(a.repo, msha), on="run_id", how="left")
                except Exception as e:                   # noqa: BLE001
                    print(d, h, "model", type(e).__name__, flush=True)
            rows.append(r.assign(snap_utc=t))
        if rows:
            s = pd.concat(rows, ignore_index=True)
            s["start_utc"] = pd.to_datetime(s["start_time"], utc=True, errors="coerce")
            ok = s["start_utc"].isna() & (s["snap_utc"] == s["snap_utc"].min()) | \
                (s["snap_utc"] <= s["start_utc"] - pd.Timedelta(minutes=10))
            s = s[ok].sort_values("snap_utc").drop_duplicates("run_id", keep="last")
            s.drop(columns=["start_time"]).to_parquet(f)
            print(d, len(seen), "snapshots,", len(s), "runners", flush=True)
        d += timedelta(days=1)


if __name__ == "__main__":
    main()
