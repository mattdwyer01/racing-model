"""Which ranking picks the most winners? Combo and alternatives on what the dashboard showed BEFORE each race.

    python -W ignore tools/combo_strike_test.py --repo ../toprate      # -> reports/combo_strike_test.md

Races: tools/dashboard_review.load() (pre-race snapshots from TopRate git history, 22 Aug 2026 on, all states;
Combo / adjusted projection / speed map exactly as the dashboard builds them). Extra inputs:
  rm_p      Racing Model win chance: clear_test out-of-sample scores (model trained before each year) to 23 Sep, then
            racing_model.json as served before the race (24 Sep on)
  wpr_nett  TopRate's own rating from the 08:00 AEST runners file (pre-race), cached in data/interim/wpr_nett_prerace
  fx        dashboard's stored fixed price at the snapshot (>= 10 min before the start)
Rankings: single inputs, Combo, and conditional-logit mixes fitted on one half of the dates and scored on the other
(swapped), with and without the fixed price. Per ranking: top pick win %, top-2 / top-3 containing the winner, A/E of
the top pick vs SP, flat ROI at SP, log loss where it is a probability model. Race bootstrap 95% on win % gaps vs Combo.
"""
import argparse
import io
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import dashboard_review as dr  # noqa: E402
from model import clogit  # noqa: E402

CACHE = ROOT / "data/interim/wpr_nett_prerace"
OUT = ROOT / "reports/combo_strike_test.md"
AEST = timezone(timedelta(hours=10))
BOOT = 2000
rng = np.random.default_rng(9)


def wpr_nett_day(repo, d):
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
    head = data[:data.index(b"\n")].decode().split(",")
    if "wpr_nett" not in head:
        return None
    tb = pc.read_csv(io.BytesIO(data), convert_options=pc.ConvertOptions(
        include_columns=["run_id", "date", "wpr_nett"], column_types={"run_id": "string", "date": "string"})).to_pandas()
    tb = tb[tb["date"] == str(d)][["run_id", "wpr_nett"]]
    tb.to_parquet(f)
    return tb


def load(repo, runners_dir=None):
    d = dr.load(runners_dir or repo)
    d["run_id"] = d["run_id"].astype(str)
    days = sorted(pd.to_datetime(d["date"]).dt.date.unique())
    CACHE.mkdir(parents=True, exist_ok=True)
    wn = pd.concat([x for x in (wpr_nett_day(repo, x) for x in days) if x is not None], ignore_index=True)
    d = d.merge(wn.drop_duplicates("run_id"), on="run_id", how="left")
    sc = pd.concat([pd.read_csv(ROOT / f"data/interim/clear_test_scores_{y}.csv.gz", dtype={"run_id": str})
                    for y in (2026,)], ignore_index=True)
    d = d.merge(sc[["run_id", "model %"]], on="run_id", how="left")
    d["rm_p"] = d["rm_p"].where(d["rm_p"].notna(), d["model %"] / 100)
    full = lambda c: d[c].notna().groupby(d["race_id"]).transform("all")  # noqa: E731
    d = d[full("rm_p") & full("combo")].copy()
    d["fx_ok"] = full("fx")
    d["trr"] = dr.WPR_M + (d["toprate_rating"] - dr.TRR_M) / dr.TRR_S * dr.WPR_S
    for c in ("combo", "proj", "trr", "wpr_nett"):
        g = d.groupby("race_id")[c]
        d[c + "_r"] = (d[c] - g.transform("mean")).fillna(0)
    d["lrm"] = np.log((d["rm_p"] / d.groupby("race_id")["rm_p"].transform("sum")).clip(1e-6))
    inv = 1 / d["fx"]
    d["lfx"] = np.log((inv / inv.groupby(d["race_id"]).transform("sum")).clip(1e-6))
    d["date"] = pd.to_datetime(d["date"])
    return d.sort_values(["race_id", "run_id"]).reset_index(drop=True)


def fitted(d, cols):
    """2-fold by date: conditional logit fitted on one half, scored on the other."""
    dates = np.sort(d["date"].unique())
    half = d["date"].isin(dates[: len(dates) // 2])
    out = pd.Series(np.nan, index=d.index)
    coefs = []
    for fit_mask in (half, ~half):
        tr = d[fit_mask].sort_values("race_id")
        b = clogit.fit(tr[cols].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
        coefs.append(b)
        te = d[~fit_mask]
        out[te.index] = te[cols].to_numpy(float) @ b
    return out, np.mean(coefs, axis=0)


def summary(d, score, name):
    x = d.assign(s=pd.to_numeric(score, errors="coerce").astype(float))
    x["rk"] = x.groupby("race_id")["s"].rank(ascending=False, method="first")
    top = x[x["rk"] == 1].set_index("race_id")
    win_rk = x[x["won"] == 1].set_index("race_id")["rk"]
    return {"ranking": name, "races": len(top), "top pick win %": 100 * top["won"].mean(),
            "winner in top 2 %": 100 * (win_rk <= 2).mean(), "winner in top 3 %": 100 * (win_rk <= 3).mean(),
            "top pick A/E vs SP": top["won"].sum() / top["p_sp"].sum(),
            "top pick ROI at SP %": 100 * ((top["won"] * top["sp"]).sum() / len(top) - 1),
            "top pick median SP": top["sp"].median()}, top["won"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    ap.add_argument("--runners-dir", default=None, help="folder with toprate_runners.csv (default: --repo)")
    a = ap.parse_args()
    d = load(a.repo, a.runners_dir)
    rows, tops, notes = [], {}, []

    def add(score, name):
        r, t = summary(d, score, name)
        rows.append(r)
        tops[name] = t

    add(d["combo"], "Combo (dashboard now)")
    add(d["proj"], "adjusted WPR projection only")
    add(d["trr"].fillna(d["proj"]), "TopRate rating only")
    add(d["wpr_nett"].fillna(d.groupby("race_id")["wpr_nett"].transform("mean")).fillna(0), "TopRate wpr_nett only")
    add(d["lrm"], "Racing Model chance only")
    for cols, name in ((["combo_r"], "Combo, refitted scale"),
                       (["proj_r", "trr_r"], "projection + TopRate rating (fitted weights)"),
                       (["combo_r", "lrm"], "Combo + Racing Model"),
                       (["proj_r", "trr_r", "lrm"], "projection + rating + Racing Model"),
                       (["proj_r", "trr_r", "lrm", "wpr_nett_r"], "projection + rating + Racing Model + wpr_nett")):
        s, b = fitted(d, cols)
        add(s, name)
        notes.append(f"- {name}: weights " + ", ".join(f"{c} {x:+.3f}" for c, x in zip(cols, b)))
    fx = d[d["fx_ok"]].copy()
    sp_rows = []
    if fx["race_id"].nunique() > 300:
        sub = d["race_id"].isin(fx["race_id"])
        for score, name in ((d["combo"], "Combo"), (d["lfx"], "fixed price favourite")):
            r, _ = summary(d[sub], score[sub], name)
            sp_rows.append(r)
        for cols, name in ((["combo_r", "lfx"], "Combo + fixed price"),
                           (["proj_r", "trr_r", "lrm", "lfx"], "projection + rating + Racing Model + fixed price")):
            s, b = fitted(fx, cols)
            r, _ = summary(fx, s, name)
            sp_rows.append(r)
            notes.append(f"- {name}: weights " + ", ".join(f"{c} {x:+.3f}" for c, x in zip(cols, b)))
        r, _ = summary(fx, fx["lfx"], "fixed price favourite (check)")
    base = tops["Combo (dashboard now)"]
    for r in rows:
        diff = (tops[r["ranking"]].reindex(base.index) - base).to_numpy(float)
        idx = rng.integers(0, len(diff), (BOOT, len(diff)))
        m = 100 * diff[idx].mean(1)
        r["win % vs Combo"] = f"{100 * diff.mean():+.1f} ({np.percentile(m, 2.5):+.1f} to {np.percentile(m, 97.5):+.1f})"
    sp_fav = d.loc[d.groupby("race_id")["sp"].idxmin()]
    L = ["# Picking more winners: Combo vs alternatives (pre-race dashboard values)", "",
         f"- {d['race_id'].nunique():,} races, {d['date'].min():%d %b} to {d['date'].max():%d %b %Y}, all states."
         f" SP favourite won {100 * sp_fav['won'].mean():.1f}% (ROI {100 * ((sp_fav['won'] * sp_fav['sp']).mean() - 1):+.1f}%)."
         " Fitted mixes: weights fitted on one half of the dates, scored on the other.", "",
         pd.DataFrame(rows).round(2).to_markdown(index=False), "", *notes, ""]
    if sp_rows:
        L += [f"## With the market ({fx['race_id'].nunique():,} races with a full fixed-price snapshot)", "",
              pd.DataFrame(sp_rows).round(2).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
