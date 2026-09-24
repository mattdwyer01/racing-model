"""
Rebuild a fixed-price history from the git history of toprate_runners.csv.

Your TopRate workflows commit toprate_runners.csv every few minutes, and each
commit holds that moment's fixed_win_price for every pending runner. Walking
those commits recovers a price series back to when the price refresh began.

USAGE (run on your PC, not the Vultr box):
    # 1. Partial clone: commits and trees only, no file contents yet
    git clone --filter=blob:none --no-checkout https://github.com/mattdwyer01/TopRate.git toprate-history
    cd toprate-history

    # 2. Fetch just this one file's versions (git 2.49+; check with `git --version`)
    git sparse-checkout set --no-cone /toprate_runners.csv
    git backfill --sparse
    #    Older git: skip this step. The script still works but fetches each
    #    version one at a time, which is much slower (leave it overnight).

    # 3. Extract
    python path/to/extract_prices_from_git.py --repo . --out tab_price_history_from_git.csv.gz

OUTPUT (one row per runner per price CHANGE, not per commit):
    commit_utc, run_id, race_id, fixed_win_price, scratched
"""
import argparse
import io
import subprocess
import sys

import pandas as pd

FILE = "toprate_runners.csv"
COLS = ["run_id", "race_id", "fixed_win_price", "scratched", "resulted"]


def _read(data: bytes) -> pd.DataFrame:
    """Read only the needed columns; pyarrow is ~10x faster than pandas on these 100MB files."""
    try:
        import pyarrow.csv as pc
        head = data[:data.index(b"\n")].decode().split(",")
        keep = [c.strip('"') for c in head if c.strip('"') in COLS]
        t = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
            include_columns=keep, column_types={c: "float64" for c in keep}))
        return t.to_pandas()
    except Exception:   # no pyarrow, or a version it can't parse: fall back to pandas
        return pd.read_csv(io.BytesIO(data), usecols=lambda c: c in COLS, low_memory=False)


def commits(repo):
    out = subprocess.run(["git", "-C", repo, "log", "--reverse", "--format=%H %cI", "--", FILE],
                         capture_output=True, text=True, check=True).stdout.split("\n")
    return [l.split(" ", 1) for l in out if l.strip()]


def blobs(repo, shas):
    """Stream file contents for many commits through one `git cat-file --batch` process."""
    p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha in shas:
        p.stdin.write(f"{sha}:{FILE}\n".encode()); p.stdin.flush()
        header = p.stdout.readline().decode().split()
        if len(header) < 3 or header[1] != "blob":
            yield sha, None
            continue
        size = int(header[2])
        data = p.stdout.read(size); p.stdout.read(1)  # trailing newline
        yield sha, data
    p.stdin.close(); p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default="tab_price_history_from_git.csv.gz")
    a = ap.parse_args()

    cs = commits(a.repo)
    when = dict(cs)
    print(f"{len(cs)} commits touch {FILE}", file=sys.stderr)

    last = {}   # run_id -> (price, scratched) last written
    rows = []
    for i, (sha, data) in enumerate(blobs(a.repo, [c[0] for c in cs]), 1):
        if data is None:
            continue
        try:
            df = _read(data)
        except Exception as e:
            print(f"  skip {sha[:8]}: {e}", file=sys.stderr)
            continue
        if "fixed_win_price" not in df or "run_id" not in df:
            continue
        if "resulted" in df:
            df = df[df["resulted"] != 1]          # only pre-result prices
        df = df.dropna(subset=["run_id"])
        scr = df["scratched"].fillna(0).astype(int) if "scratched" in df else 0
        for rid, rc, px, s in zip(df["run_id"].astype("int64"), df["race_id"], df["fixed_win_price"],
                                  scr if not isinstance(scr, int) else [0] * len(df)):
            px = None if pd.isna(px) else float(px)
            if last.get(rid) != (px, s):
                last[rid] = (px, s)
                rows.append((when[sha], rid, rc, px, s))
        if i % 200 == 0:
            print(f"  {i}/{len(cs)} commits, {len(rows):,} price changes", file=sys.stderr)

    out = pd.DataFrame(rows, columns=["commit_utc", "run_id", "race_id", "fixed_win_price", "scratched"])
    out["commit_utc"] = pd.to_datetime(out["commit_utc"], utc=True)
    out.to_csv(a.out, index=False)
    print(f"wrote {len(out):,} rows, {out.run_id.nunique():,} runners, "
          f"{out.commit_utc.min()} to {out.commit_utc.max()} -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
