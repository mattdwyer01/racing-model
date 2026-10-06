"""GPS data in the TopRate repo: data/gps/{name}_{year}.parquet (public, files in git; moved from the store 6 Oct 2026).

    python pipeline/gps_repo.py update TOPRATE_DIR NEW_DIR   # merge freshly parsed files (NEW_DIR, any depth) in
    python pipeline/gps_repo.py export TOPRATE_DIR OUT_DIR   # one parquet per name (data/interim layout)
    python pipeline/gps_repo.py fetch OUT_DIR                # download from GitHub (no checkout) and export

Split by year (rq: race_date, rc: start_utc; rc sections take the year of their meeting in rc_gps_runs) so the daily
commit only rewrites the current year's files. A year file is written only when its rows change. The first update with
no files in the repo seeds from the data store (pipeline/store.py), so nothing is lost in the move.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REPO = "mattdwyer01/toprate"
SUB = "data/gps"
KEYS = {
    "rq_gps_runs": ["race_code", "tab_no"],
    "rq_gps_sections": ["race_code", "tab_no", "cum_dist_m"],
    "rc_gps_runs": ["meet_code", "race_no", "tab_no"],
    "rc_gps_sections": ["meet_code", "race_no", "tab_no", "from_m"],
}
ORDER = ["rc_gps_runs", "rc_gps_sections", "rq_gps_runs", "rq_gps_sections"]   # rc runs first: sections need its years


def _files(d: Path, name: str) -> list[Path]:
    return sorted(d.glob(f"{name}_[0-9][0-9][0-9][0-9].parquet"))


def load(d: Path, name: str) -> pd.DataFrame:
    fs = _files(d, name)
    return pd.concat([pd.read_parquet(f) for f in fs], ignore_index=True) if fs else pd.DataFrame()


def _years(df: pd.DataFrame, name: str, meet_year: pd.Series | None) -> pd.Series:
    if name.startswith("rq_"):
        return pd.to_datetime(df["race_date"]).dt.year
    if name == "rc_gps_runs":
        return pd.to_numeric(df["start_utc"].astype(str).str[:4], errors="coerce")
    return df["meet_code"].astype(str).map(meet_year)


def save(df: pd.DataFrame, d: Path, name: str, meet_year: pd.Series | None = None) -> list[str]:
    """Write one file per year; only years whose rows changed. Returns the files written."""
    d.mkdir(parents=True, exist_ok=True)
    y = _years(df, name, meet_year)
    if y.isna().any():
        print(f"{name}: {int(y.isna().sum()):,} rows without a year dropped")
    out = []
    for yr, part in df[y.notna()].groupby(y[y.notna()].astype(int)):
        f = d / f"{name}_{yr}.parquet"
        part = part.reset_index(drop=True)
        if f.exists():
            old = pd.read_parquet(f)
            if len(old) == len(part) and old.astype(str).equals(part.astype(str)):
                continue
        part.to_parquet(f, index=False)
        out.append(f.name)
    return out


def merge(old: pd.DataFrame, new: list[pd.DataFrame], keys: list[str]) -> pd.DataFrame:
    frames = [f for f in [old, *new] if len(f)]
    df = pd.concat(frames, ignore_index=True)
    for c in ("tab_no", "cum_dist_m", "race_no", "rank", "finish", "from_m", "to_m", "pos"):
        if c in df and not pd.api.types.is_numeric_dtype(df[c]):   # older parses stored some numbers as strings
            df[c] = pd.to_numeric(df[c], errors="coerce")
    k = df[keys].astype("string")   # compare keys as strings (dtypes differ across files)
    df = df[~k.duplicated(keep="last")]
    sort = [c for c in ("race_date", "start_utc") if c in df] + keys
    return df.sort_values(sort, kind="stable").reset_index(drop=True)


def _meet_year(d: Path) -> pd.Series:
    r = load(d, "rc_gps_runs")
    if not len(r):
        return pd.Series(dtype=float)
    r = r.assign(y=pd.to_numeric(r["start_utc"].astype(str).str[:4], errors="coerce"))
    return r.groupby(r["meet_code"].astype(str))["y"].min()


def _seed(name: str) -> pd.DataFrame:
    from pipeline import store
    tmp = ROOT / "work/seed" / f"{name}.parquet"
    if not store.get(f"{name}.parquet", tmp):
        print(f"{name}: no store copy to seed from")
        return pd.DataFrame()
    print(f"{name}: seeded {tmp.stat().st_size:,} bytes from the store")
    return pd.read_parquet(tmp)


def update(top: Path, new_dir: Path) -> None:
    d = top / SUB
    summary = []
    for name in ORDER:
        new = [pd.read_parquet(p) for p in sorted(new_dir.rglob(f"{name}.parquet")) if p.stat().st_size]
        old = load(d, name)
        seeded = False
        if not len(old):
            old, seeded = _seed(name), True
        if not new and not seeded:
            print(f"{name}: no new rows")
            continue
        if not new and not len(old):
            continue
        df = merge(old, new, KEYS[name])
        wrote = save(df, d, name, _meet_year(d) if name == "rc_gps_sections" else None)
        print(f"{name}: {len(df):,} rows ({len(df) - len(old):+,}); wrote {', '.join(wrote) or 'nothing'}")
        summary.append((name, len(df), len(df) - len(old)))
    _summary(summary)


def _summary(rows):
    import os
    p = os.environ.get("GITHUB_STEP_SUMMARY")
    if p and rows:
        with open(p, "a") as f:
            f.write("| file | rows | new |\n|---|---|---|\n")
            for n, r, a in rows:
                f.write(f"| {n} | {r:,} | {a:+,} |\n")


def export(top: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    d = top / SUB
    for name in ORDER:
        df = load(d, name)
        if len(df):
            df.to_parquet(out / f"{name}.parquet", index=False)
            print(f"{name}: {len(df):,} rows -> {out / (name + '.parquet')}")


def fetch(out: Path) -> bool:
    """Download data/gps from GitHub (public repo, no token needed) and export. False if the folder is not there."""
    import os
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")   # optional: avoids the 60 an hour anonymous limit
    h = {"Authorization": f"Bearer {t}"} if t else {}
    r = requests.get(f"https://api.github.com/repos/{REPO}/contents/{SUB}", headers=h, timeout=60)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    tmp = ROOT / "work/gps_fetch"
    (tmp / SUB).mkdir(parents=True, exist_ok=True)
    for it in r.json():
        if it["name"].endswith(".parquet"):
            b = requests.get(it["download_url"], timeout=300)
            b.raise_for_status()
            pd.read_parquet(io.BytesIO(b.content))   # fail loudly on a truncated download
            (tmp / SUB / it["name"]).write_bytes(b.content)
    export(tmp, out)
    return True


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "update":
        update(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "export":
        export(Path(sys.argv[2]), Path(sys.argv[3]))
    elif cmd == "fetch":
        sys.exit(0 if fetch(Path(sys.argv[2])) else "no data/gps in the TopRate repo")
    else:
        sys.exit(__doc__)
