"""Are past-run WPRs revised after race day, and does using the revised (current) values leak?

    python -W ignore tools/wpr_revision_test.py --repo ../toprate     # -> reports/wpr_revision_test.md

The model's history uses each past run's CURRENT WPR from the results files (TopRate revises Preliminary to Final).
The dashboard runners file carries `wpr_last1` (the WPR of the horse's last start) as it stood that morning. Per
race day (26 Apr 2026 on), the 08:00 AEST git snapshot of toprate_runners.csv gives the pre-race value; the DB's
`prev_wpr` (from the current results files) gives today's value of the same run. Revision = current - pre-race.
Leak check: if revisions carry information about the horse's NEXT race (the one being predicted) beyond SP,
backtests that use current values are flattered. Measured as A/E at SP by revision band.
"""
import argparse
import io
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/interim/wpr_prerace"
OUT = ROOT / "reports/wpr_revision_test.md"
AEST = timezone(timedelta(hours=10))


def snap(repo, d):
    f = CACHE / f"{d}.parquet"
    if f.exists():
        return pd.read_parquet(f)
    t = datetime(d.year, d.month, d.day, 8, tzinfo=AEST).astimezone(timezone.utc)
    sha = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%H", f"--before={t.isoformat()}", "origin/main",
                          "--", "toprate_runners.csv"], capture_output=True, text=True).stdout.strip()
    if not sha:
        return None
    import pyarrow.csv as pc
    data = subprocess.run(["git", "-C", repo, "show", f"{sha}:toprate_runners.csv"], capture_output=True).stdout
    if not data:
        return None
    head = data[:data.index(b"\n")].decode().split(",")
    cols = [c for c in ("run_id", "date", "wpr_last1", "wpr_avg_last3", "runs_with_wpr") if c in head]
    tb = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=cols, column_types={"run_id": "string", "date": "string"})).to_pandas()
    tb = tb[tb["date"] == str(d)]
    tb.to_parquet(f)
    return tb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--start", default="2026-04-27")
    ap.add_argument("--end", default="2026-10-02")
    a = ap.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    d, rows = date.fromisoformat(a.start), []
    while d <= date.fromisoformat(a.end):
        s = snap(a.repo, d)
        if s is not None and len(s):
            rows.append(s)
        d += timedelta(days=1)
    pre = pd.concat(rows, ignore_index=True)
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    db = con.sql("""select cast(r.run_id as varchar) run_id, r.race_id, r.race_date, r.sp, r.res_finish, r.prev_wpr,
                           r.prev_race_id, ra.state from runs r join races ra using (race_id)
                    where r.race_date >= date '2026-04-26' and r.prev_wpr is not null""").df()
    x = db.merge(pre, on="run_id")
    x["pre"] = pd.to_numeric(x["wpr_last1"], errors="coerce")
    x = x[x["pre"].notna() & (x["sp"] > 1) & x["res_finish"].notna()].copy()
    x["rev"] = x["prev_wpr"] - x["pre"]
    x["won"] = (x["res_finish"] == 1).astype(int)
    inv = 1 / x["sp"]
    x["p_sp"] = inv / inv.groupby(x["race_id"]).transform("sum")   # within matched runners only (approximate)
    gap = (pd.to_datetime(x["race_date"]) - pd.to_datetime(
        con.sql("select race_id, race_date d from races").df().set_index("race_id")["d"]
        .reindex(x["prev_race_id"]).to_numpy())).dt.days
    x["days_since_prev"] = gap.to_numpy()
    L = ["# Past-run WPR revisions (pre-race value vs current)", "",
         f"- {len(x):,} runners with a last start, {x['race_date'].min()} to {x['race_date'].max()}. Pre-race value ="
         " `wpr_last1` in the 08:00 AEST runners file; current = DB `prev_wpr` (results files now).", "",
         f"- Exactly equal (|rev| < 0.05): {100 * (x['rev'].abs() < 0.05).mean():.1f}%; |rev| > 1: "
         f"{100 * (x['rev'].abs() > 1).mean():.1f}%; > 3: {100 * (x['rev'].abs() > 3).mean():.1f}%;"
         f" mean |rev| {x['rev'].abs().mean():.2f}; mean rev {x['rev'].mean():+.2f}; corr(pre, current)"
         f" {x[['pre', 'prev_wpr']].corr().iloc[0, 1]:.3f}", ""]
    x["gapband"] = pd.cut(x["days_since_prev"], [-1, 7, 14, 28, 9999], labels=["<=7 d", "8-14 d", "15-28 d", "29+ d"])
    t = x.groupby("gapband", observed=True).apply(lambda g: pd.Series({
        "runners": len(g), "% revised (>0.05)": 100 * (g["rev"].abs() > 0.05).mean(),
        "mean |rev|": g["rev"].abs().mean(), "% |rev| > 3": 100 * (g["rev"].abs() > 3).mean()}))
    L += ["## By days since the last start (recent runs are the ones still preliminary)", "",
          t.round(2).to_markdown(), ""]
    x["band"] = pd.cut(x["rev"], [-99, -3, -1, -0.05, 0.05, 1, 3, 99],
                       labels=["< -3", "-3 to -1", "-1 to 0", "0", "0 to 1", "1 to 3", "> 3"])
    t = x.groupby("band", observed=True).apply(lambda g: pd.Series({
        "runners": len(g), "won %": 100 * g["won"].mean(), "A/E at SP": g["won"].sum() / g["p_sp"].sum()}))
    L += ["## Next-race result by revision (leak check: A/E should be ~flat if revisions carry no future info)", "",
          t.round(3).to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
