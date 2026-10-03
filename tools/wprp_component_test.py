"""Which of TopRate's WPR projection adjustments carry information, and which are noise?

    python -W ignore tools/wprp_component_test.py --repo ../toprate     # -> reports/wprp_component_test.md

TopRate's projection = wprp_base + wprp_adj, adj = sum of components in wprp_contrib (speed_map, track_barrier,
own_first_up, own_second_up, own_long_spell, closing_merit, trainer_merit, jockey_merit, pop_distance, pop_going, ...).
Pre-race values: the 08:00 AEST runners file of each race day from TopRate's git history (cached in
data/interim/wprp_prerace). Results / SP: DB live_runners (TopRate final). All states, 27 Apr 2026 on.
Tests (conditional logit, 2-fold by date, race bootstrap on log loss):
  1. projection as TopRate builds it vs base alone (do the adjustments help at all?)
  2. leave-one-out: projection minus one component vs the full projection
  3. free weights: base + every component with its own fitted weight (1.0 = TopRate's weight is right)
  4. each with SP: does the component add anything the market misses?
"""
import argparse
import io
import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit  # noqa: E402

CACHE = ROOT / "data/interim/wprp_prerace"
OUT = ROOT / "reports/wprp_component_test.md"
AEST = timezone(timedelta(hours=10))
BOOT = 2000
rng = np.random.default_rng(21)


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
    cols = [c for c in ("run_id", "race_id", "date", "wprp_proj", "wprp_base", "wprp_adj", "wprp_contrib") if c in head]
    if "wprp_contrib" not in cols:
        return None
    tb = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=cols, column_types={"run_id": "string", "race_id": "string", "date": "string",
                                            "wprp_contrib": "string"})).to_pandas()
    tb = tb[tb["date"] == str(d)]
    tb.to_parquet(f)
    return tb


def load(repo, start, end):
    CACHE.mkdir(parents=True, exist_ok=True)
    rows, d = [], date.fromisoformat(start)
    while d <= date.fromisoformat(end):
        s = snap(repo, d)
        if s is not None and len(s):
            rows.append(s)
        d += timedelta(days=1)
    x = pd.concat(rows, ignore_index=True)
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    res = con.sql("""select cast(run_id as varchar) run_id, finish_position fp, starting_price_sp sp, scratched
                     from live_runners where resulted = 1""").df()
    x = x.merge(res, on="run_id")
    x = x[(x["scratched"].fillna(0) == 0)]
    comp = pd.DataFrame([json.loads(v) if isinstance(v, str) and v.startswith("{") else {} for v in x["wprp_contrib"]],
                        index=x.index).astype(float)
    keep = [c for c in comp.columns if comp[c].notna().mean() > 0.2 and comp[c].abs().sum() > 0]
    x = pd.concat([x, comp[keep].fillna(0.0)], axis=1)
    for c in ("wprp_proj", "wprp_base", "sp", "fp"):
        x[c] = pd.to_numeric(x[c], errors="coerce")
    g = x.groupby("race_id")
    ok = g.agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()), p=("wprp_proj", lambda s: s.notna().all()),
               b=("wprp_base", lambda s: s.notna().all()), sp=("sp", lambda s: (s > 1).all()),
               ovr=("sp", lambda s: (1 / s).sum()))
    x = x[x["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & ok.p & ok.b & ok.sp & (ok.ovr >= 1.0)])].copy()
    x["won"] = (x["fp"] == 1).astype(int)
    inv = 1 / x["sp"]
    x["lsp"] = np.log(inv / inv.groupby(x["race_id"]).transform("sum"))
    x["date"] = pd.to_datetime(x["date"])
    for c in ["wprp_proj", "wprp_base"] + keep:
        x[c + "_r"] = x[c] - x.groupby("race_id")[c].transform("mean")
    return x.sort_values(["race_id", "run_id"]).reset_index(drop=True), keep


def two_fold(x, cols):
    dates = np.sort(x["date"].unique())
    half = x["date"].isin(dates[: len(dates) // 2])
    ll, betas = pd.Series(dtype=float), []
    for fm in (half, ~half):
        tr = x[fm].sort_values("race_id")
        b = clogit.fit(tr[cols].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
        betas.append(b)
        te = x[~fm]
        z = pd.Series(te[cols].to_numpy(float) @ b, index=te.index)
        e = np.exp(z - z.groupby(te["race_id"]).transform("max"))
        p = e / e.groupby(te["race_id"]).transform("sum")
        w = te["won"] == 1
        ll = pd.concat([ll, pd.Series(-np.log(p[w].clip(1e-12)).to_numpy(), index=te.loc[w, "race_id"].to_numpy())])
    return ll, np.mean(betas, axis=0)


def ci(a, b):
    x = (a - b.reindex(a.index)).dropna().to_numpy()
    m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
    return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--start", default="2026-04-27")
    ap.add_argument("--end", default="2026-10-02")
    a = ap.parse_args()
    x, comps = load(a.repo, a.start, a.end)
    # TopRate's own adjusted projection; leave-one-out projections drop one component (vs the field)
    full, bfull = two_fold(x, ["wprp_proj_r"])
    base, _ = two_fold(x, ["wprp_base_r"])
    fullsp, _ = two_fold(x, ["wprp_proj_r", "lsp"])
    basesp, _ = two_fold(x, ["wprp_base_r", "lsp"])
    sp, _ = two_fold(x, ["lsp"])
    L = ["# TopRate WPR projection: which adjustments help? (pre-race 08:00 values)", "",
         f"- {x['race_id'].nunique():,} races, {x['date'].min():%d %b} to {x['date'].max():%d %b %Y}, all states. Log loss"
         " per race, 2-fold by date (fit on one half, score the other). Positive difference = the first is worse.", "",
         f"- Projection {full.mean():.4f}, base (no adjustments) {base.mean():.4f}: base minus projection"
         f" {ci(base, full)}. With SP: projection + SP {fullsp.mean():.4f}, base + SP {basesp.mean():.4f}"
         f" ({ci(basesp, fullsp)}), SP alone {sp.mean():.4f}.", "",
         "## Leave one component out (projection minus that component vs full projection)", ""]
    rows = []
    for c in comps:
        x["loo"] = x["wprp_proj_r"] - x[c + "_r"]
        lo, _ = two_fold(x, ["loo"])
        losp, _ = two_fold(x, ["loo", "lsp"])
        rows.append({"component": c, "share non-zero %": round(100 * (x[c] != 0).mean(), 1),
                     "sd vs field (WPR)": round(x[c + "_r"].std(), 2),
                     "drop it: alone": ci(lo, full), "drop it: with SP": ci(losp, fullsp)})
    L += [pd.DataFrame(rows).to_markdown(index=False), "",
          "- Positive = removing the component makes the projection worse (it helps); negative = it hurts (noise or"
          " wrong sign).", ""]
    cols = ["wprp_base_r"] + [c + "_r" for c in comps]
    free, b = two_fold(x, cols)
    freesp, bsp = two_fold(x, cols + ["lsp"])
    unit = b[0]
    L += ["## Free weights (base + every component fitted separately)", "",
          f"- Free weights alone {free.mean():.4f} vs projection {ci(free, full)}; with SP {freesp.mean():.4f} vs"
          f" projection + SP {ci(freesp, fullsp)}.", "",
          "| input | weight per WPR point | relative to base (1.0 = TopRate's weight) | with SP, relative |", "|---|---|---|---|"]
    for i, c in enumerate(cols):
        L.append(f"| {c[:-2]} | {b[i]:+.4f} | {b[i] / unit:+.2f} | {bsp[i] / bsp[0]:+.2f} |")
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
