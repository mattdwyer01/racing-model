"""Track pattern: where you need to settle (and draw) to win at a track under today's conditions.

    python -W ignore tools/track_pattern_test.py      # -> reports/track_pattern_test.md

1. Pattern per race = the winner's settle share (800m position, 0 = leader) and barrier share minus the field's means
   (negative = winners came from forward / inside). Races 2017 on, VIC/SA/QLD/NSW/WA with 800m positions.
2. Stability: race-weighted mean pattern per cell (track; x distance band; x going band; x rail band; combinations),
   computed separately on even and odd years; correlation between the halves (cells with 10+ races in each half).
   Reliability gives the shrinkage: est = sum / (n + lambda), lambda = n_cell x (1 - r) / r at the median cell.
3. Live-style test (walk-forward, 2024 to Sep 2026): term = cell pattern vs the all-track pattern, from PRIOR race days
   only, x the runner's
   expected settle share vs the field (mean of its last 5 settle shares, 0.5 if none) and barrier share vs the field.
   Added to the live Proj (proj_consistent_oos3 'win: consistent' = the 7-term recipe) with a weight fitted on the
   previous test year (conditional logit on who won); winners inside the 3 / 5 lines at matched runner counts and top
   pick %, race bootstrap.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure  # noqa: E402

OUT = ROOT / "reports/track_pattern_test.md"
OOS = ROOT / "data/interim/proj_consistent_oos3.parquet"
LIVE = "win: consistent"


def load():
    con = duckdb.connect(str(figure.DB), read_only=True)
    r = con.sql("""select cast(u.run_id as varchar) run_id, u.race_id, u.horse_id, u.race_date, u.barrier, u.res_pos800,
                          u.res_finish, r.track, r.distance, r.going_num, r.rail_m, r.state
                   from runs u join races r using (race_id)
                   where u.race_date >= date '2017-01-01' and not coalesce(u.is_trial_or_jumpout, false)
                     and r.state in ('VIC', 'SA', 'QLD', 'NSW', 'WA')""").df()
    r["race_date"] = pd.to_datetime(r["race_date"])
    g = r.groupby("race_id")
    n = g["run_id"].transform("count")
    r["s"] = (r["res_pos800"] - 1) / (n - 1).clip(lower=1)
    r["b"] = (g["barrier"].rank(method="average") - 1) / (n - 1).clip(lower=1)
    r["dist_b"] = pd.cut(r["distance"], [0, 1200, 1600, 9999], labels=["sprint", "mile", "stay"]).astype(str)
    r["going_b"] = pd.cut(r["going_num"].fillna(4), [-1, 4, 6, 99], labels=["good", "soft", "heavy"]).astype(str)
    r["rail_b"] = pd.cut(r["rail_m"].fillna(-1), [-2, -0.5, 0.5, 4.5, 99], labels=["na", "true", "out1_4", "out5"]).astype(str)
    return r


def race_patterns(r):
    ok = r["s"].notna()
    t = r[ok].copy()
    g = t.groupby("race_id")
    t["s_dm"], t["b_dm"] = t["s"] - g["s"].transform("mean"), t["b"] - g["b"].transform("mean")
    w = t[t["res_finish"] == 1].drop_duplicates("race_id")
    return w[["race_id", "race_date", "track", "dist_b", "going_b", "rail_b", "s_dm", "b_dm"]]


CELLS = {"track": ["track"], "track x distance": ["track", "dist_b"], "track x going": ["track", "going_b"],
         "track x rail": ["track", "rail_b"], "track x distance x going": ["track", "dist_b", "going_b"],
         "track x distance x going x rail": ["track", "dist_b", "going_b", "rail_b"]}


def stability(w):
    rows = []
    w = w.assign(half=w["race_date"].dt.year % 2)
    for name, keys in CELLS.items():
        for col, lab in (("s_dm", "settle"), ("b_dm", "barrier")):
            a = w.groupby(keys + ["half"])[col].agg(["mean", "count"]).unstack("half")
            a = a[(a[("count", 0)] >= 10) & (a[("count", 1)] >= 10)]
            if len(a) < 5:
                continue
            x, y = a[("mean", 0)], a[("mean", 1)]
            wt = np.sqrt(a[("count", 0)] * a[("count", 1)])
            mx, my = np.average(x, weights=wt), np.average(y, weights=wt)
            r_ = np.average((x - mx) * (y - my), weights=wt) / np.sqrt(
                np.average((x - mx) ** 2, weights=wt) * np.average((y - my) ** 2, weights=wt))
            nmed = float(np.median(a[("count", 0)] + a[("count", 1)]))
            lam = nmed * (1 - r_) / r_ if r_ > 0.02 else np.inf
            rows.append({"cells": name, "pattern": lab, "cells used": len(a), "median races": int(nmed),
                         "split-half r": round(r_, 3), "sd of cell means": round(float(np.concatenate([x, y]).std()), 3),
                         "lambda": round(lam, 1) if np.isfinite(lam) else None})
    return pd.DataFrame(rows)


def prior_cell(w, keys, col, lam):
    """Per race day: cell pattern from PRIOR race days, shrunk (sum / (n + lam)); keyed by cell + date."""
    d = w.groupby(keys + ["race_date"])[col].agg(["sum", "count"]).reset_index().sort_values(keys + ["race_date"])
    g = d.groupby(keys)
    d["cs"], d["cn"] = g["sum"].cumsum() - d["sum"], g["count"].cumsum() - d["count"]
    # deviation from the all-track pattern to date (winners come from forward almost everywhere: the speed map already
    # carries that), shrunk toward 0 with lam
    day = w.groupby("race_date")[col].agg(["sum", "count"]).sort_index()
    glob = (day["sum"].cumsum() - day["sum"]) / (day["count"].cumsum() - day["count"]).clip(lower=1)
    gl = d["race_date"].map(glob).fillna(0.0)
    d["est"] = (d["cs"] - d["cn"] * gl) / (d["cn"] + lam)
    return d[keys + ["race_date", "est"]]


def inside(d, col, target):
    gap = d.groupby("race_id")[col].transform("max") - d[col]
    R = d["race_id"].nunique()
    ls = np.arange(0, 25.01, 0.05)
    cnt = np.array([(gap <= n).sum() / R for n in ls])
    n = ls[int(np.argmin(np.abs(cnt - target)))]
    return (d["won"] * (gap <= n)).groupby(d["race_id"]).sum()


def main():
    r = load()
    w = race_patterns(r)
    st = stability(w)
    print(st.to_string(), flush=True)
    # runner expected settle: mean of its last 5 settle shares (prior runs only)
    r = r.sort_values(["horse_id", "race_date"])
    prev = r.groupby("horse_id")["s"].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    r["s_exp"] = prev.fillna(0.5)
    d = pd.read_parquet(OOS)
    d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
    d["run_id"] = d["run_id"].astype(str)
    d = d.merge(r[["run_id", "track", "dist_b", "going_b", "rail_b", "s_exp", "b"]], on="run_id", how="left")
    g = d.groupby("race_id")
    d["s_rel"] = (d["s_exp"] - g["s_exp"].transform("mean")).fillna(0)
    d["b_rel"] = (d["b"] - g["b"].transform("mean")).fillna(0)
    terms = []
    for name, keys in CELLS.items():
        for col, rel, lab in (("s_dm", "s_rel", "settle"), ("b_dm", "b_rel", "barrier")):
            row = st[(st["cells"] == name) & (st["pattern"] == lab)]
            lam = row["lambda"].iloc[0] if len(row) and pd.notna(row["lambda"].iloc[0]) else None
            if lam is None:
                continue
            pc = prior_cell(w, keys, col, lam)
            est = d[keys + ["race_date"]].merge(pc.sort_values("race_date"), on=keys + ["race_date"], how="left")["est"]
            # races on a day with no row of their own for the cell: take the latest prior estimate
            if est.isna().any():
                q = d[keys + ["race_date"]].reset_index().sort_values("race_date")
                q = pd.merge_asof(q, pc.sort_values("race_date"), on="race_date", by=keys).sort_values("index")
                est = est.fillna(pd.Series(q["est"].to_numpy(), index=est.index))
            t = f"{lab}: {name}"
            # positive = favoured: winners came from where this runner is expected to be (both negative or both positive)
            d[t] = (est.fillna(0).to_numpy() * d[rel].to_numpy()) * 100
            terms.append(t)
    d["fold"] = d["race_date"].dt.year
    d = d.sort_values(["race_id", "run_id"]).reset_index(drop=True)
    base = d[LIVE] - d.groupby("race_id")[LIVE].transform("mean")
    rng = np.random.default_rng(1)
    rows = []
    b3, b5 = inside(d[d.fold >= 2024], LIVE, 3.03), inside(d[d.fold >= 2024], LIVE, 4.62)
    idx = rng.integers(0, len(b3), (1000, len(b3)))
    ev = d[d.fold >= 2024].copy()
    for t in terms + ["settle + barrier: track x distance x going"]:
        cols = [t] if t in d else ["settle: track x distance x going", "barrier: track x distance x going"]
        if not all(c in d for c in cols):
            continue
        adj = pd.Series(0.0, index=d.index)
        ws = []
        for y in (2024, 2025, 2026):
            tr = d[d.fold == y - 1]
            X = np.c_[base[tr.index].to_numpy(), tr[cols].to_numpy()]
            beta = clogit.fit(X, pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
            wy = beta[1:] / beta[0]
            ws.append(wy)
            te = d.fold == y
            adj[te] = d.loc[te, cols].to_numpy() @ wy
        ev["v"] = (d[LIVE] + adj)[ev.index]
        w3, w5 = inside(ev, "v", 3.03), inside(ev, "v", 4.62)
        out = {"term": t, "weights (2024 / 25 / 26)": " / ".join(",".join(f"{v:.2f}" for v in x) for x in ws)}
        for lab, ww, bb in (("3", w3, b3), ("5", w5, b5)):
            df = (ww - bb.reindex(ww.index)).to_numpy()
            q = np.quantile(df[idx].mean(1), [0.025, 0.975])
            out[f"inside {lab} vs live"] = f"{100 * df.mean():+.2f} ({100 * q[0]:+.2f} to {100 * q[1]:+.2f})"
        out["top pick % (live)"] = f"{100 * ev.loc[ev.groupby('race_id')['v'].idxmax(), 'won'].mean():.2f} " \
                                   f"({100 * ev.loc[ev.groupby('race_id')[LIVE].idxmax(), 'won'].mean():.2f})"
        rows.append(out)
        print(out, flush=True)
    L = ["# Track pattern: where winners settle / draw at a track under today's conditions", "",
         f"- {w['race_id'].nunique():,} races 2017 on with 800m positions (VIC/SA/QLD/NSW/WA). Pattern per race = the winner's",
         "  settle (or barrier) share minus the field mean: negative = winners came from forward (inside).", "",
         "## Stability: even vs odd years (cells with 10+ races in each half)", "", st.to_markdown(index=False), "",
         "## On top of the live Proj (walk-forward 2024 to Sep 2026, weight fitted on the previous year)", "",
         f"- {ev['race_id'].nunique():,} races; lines set to hold 3.03 / 4.62 runners a race; winners per 100 races vs live.", "",
         pd.DataFrame(rows).to_markdown(index=False), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
