"""Does TAB fixed-price movement before the jump predict the result, and does the model add to the bet-time price?

    python -W ignore tools/price_drift_test.py       # -> reports/price_drift_test.md

Prices: data/interim/tab_price_snapshots.csv.gz (TopRate's TAB fixed-price snapshots, archived by
pipeline/pull_toprate.py; 17 Sep 2026 on, roughly every 15 minutes while a race is open). Start times, SP and
finishing positions: the dashboard runners file (data/raw/live). Per runner:
  p_open  = first snapshot of the day (normalised within the race), p_bet = last snapshot >= 10 min before the
  start (the price you could take), drift = log(p_bet / p_open) (> 0 = firmed).
Tests (conditional logit, race bootstrap):
  1. market at bet time: log p_bet alone vs log p_bet + drift (log loss, 2-fold by date)
  2. A/E at the bet-time price by drift band, and flat ROI at the bet-time price
  3. model at bet time (24 Sep on, racing_model.json p in the pre-race dashboard snapshots): log p_bet vs
     log p_bet + log p_model
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit  # noqa: E402

PRICES = ROOT / "data/interim/tab_price_snapshots.csv.gz"
RUNNERS = ROOT / "data/raw/live/toprate_runners.csv"
SNAPS = ROOT / "data/interim/dash_snapshots"
OUT = ROOT / "reports/price_drift_test.md"
BOOT = 2000
rng = np.random.default_rng(4)


def load():
    p = pd.read_csv(PRICES, dtype={"run_id": str, "race_id": str})
    p["t"] = pd.to_datetime(p["snapshot_time"], utc=True, format="ISO8601")
    r = pd.read_csv(RUNNERS, dtype={"run_id": str, "race_id": str}, low_memory=False,
                    usecols=["run_id", "race_id", "date", "venue", "state", "start_time", "starting_price_sp",
                             "finish_position", "scratched"])
    r = r[r["race_id"].isin(p["race_id"].unique())].copy()
    r["start"] = pd.to_datetime(r["start_time"], utc=True, errors="coerce")
    p = p.merge(r[["run_id", "start"]], on="run_id")
    p = p[(p["t"] <= p["start"] - pd.Timedelta(minutes=10)) & (p["t"] >= p["start"] - pd.Timedelta(hours=14))]
    p = p[pd.to_numeric(p["fixed_win_price"], errors="coerce") > 1]
    p = p.sort_values("t")
    first = p.groupby("run_id").first()[["fixed_win_price", "t"]].rename(columns={"fixed_win_price": "px_open",
                                                                              "t": "t_open"})
    last = p.groupby("run_id").last()[["fixed_win_price", "t"]].rename(columns={"fixed_win_price": "px_bet",
                                                                             "t": "t_bet"})
    d = r.merge(first, left_on="run_id", right_index=True).merge(last, left_on="run_id", right_index=True)
    d = d[d["scratched"].fillna(0) == 0]
    d["fp"] = pd.to_numeric(d["finish_position"], errors="coerce")
    d["sp"] = pd.to_numeric(d["starting_price_sp"], errors="coerce")
    full = r[r["scratched"].fillna(0) == 0].groupby("race_id").size()
    g = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()),
                                 open_age=("t_open", "max"))
    ok = g.index[(g["n"] >= 4) & (g["w"] == 1) & (g["n"] == full.reindex(g.index))]
    d = d[d["race_id"].isin(ok)].copy()
    d["won"] = (d["fp"] == 1).astype(int)
    for c in ("px_open", "px_bet"):
        inv = 1 / d[c].astype(float)
        d["p_" + c[3:]] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["drift"] = np.log(d["p_bet"] / d["p_open"])
    d["mins_before"] = (d["start"] - d["t_bet"]).dt.total_seconds() / 60
    d["hours_open"] = (d["t_bet"] - d["t_open"]).dt.total_seconds() / 3600
    return d


def race_ll(d, cols):
    """2-fold by date: fit on one half, score the other; per-race log loss."""
    dates = np.sort(d["date"].unique())
    half = set(dates[: len(dates) // 2])
    out = []
    for fit_first in (True, False):
        tr = d[d["date"].isin(half) == fit_first].sort_values("race_id")
        te = d[d["date"].isin(half) != fit_first]
        b = clogit.fit(tr[cols].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
        z = te[cols].to_numpy(float) @ b
        e = pd.Series(np.exp(z - pd.Series(z).groupby(te["race_id"].to_numpy()).transform("max").to_numpy()),
                      index=te.index)
        p = e / e.groupby(te["race_id"]).transform("sum")
        ll = -np.log(p[te["won"] == 1].clip(1e-9))
        out.append(pd.Series(ll.to_numpy(), index=te.loc[te["won"] == 1, "race_id"].to_numpy()))
    return pd.concat(out), b


def paired(a, b):
    diff = (b - a.reindex(b.index)).dropna().to_numpy()
    idx = rng.integers(0, len(diff), (BOOT, len(diff)))
    m = diff[idx].mean(1)
    return f"{diff.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def main():
    d = load()
    d["lp"] = np.log(d["p_bet"])
    races = d["race_id"].nunique()
    L = ["# TAB fixed-price movement and the model at bet time", "",
         f"- {races} races, {d['date'].min()} to {d['date'].max()}, all states (TopRate's TAB snapshots). Bet price ="
         f" last snapshot >= 10 min before the start (median {d['mins_before'].median():.0f} min before); open = first"
         f" snapshot of the day (median {d['hours_open'].median():.1f} h earlier).", ""]
    base, _ = race_ll(d, ["lp"])
    drift, b = race_ll(d, ["lp", "drift"])
    L += ["## 1. Does the move add to the bet-time price? (race log loss, lower = better)", "",
          f"- bet-time price alone: {base.mean():.4f}; + drift: {drift.mean():.4f}; difference {paired(base, drift)};"
          f" drift coefficient {b[1]:+.2f} (> 0: firmers win more than their bet-time price says)", ""]
    d["band"] = pd.cut(d["drift"], [-9, -0.3, -0.1, -0.03, 0.03, 0.1, 0.3, 9],
                       labels=["drifted > 30%", "drifted 10-30%", "drifted 3-10%", "steady", "firmed 3-10%",
                               "firmed 10-30%", "firmed > 30%"])
    pm = d.groupby(pd.cut(d["px_bet"], [1, 2, 3, 4, 6, 10, 20, 1000]), observed=True)["won"].transform("mean")
    d["p_ctl"] = pm
    t = d.groupby("band", observed=True).apply(lambda g: pd.Series({
        "runners": len(g), "won %": 100 * g["won"].mean(), "median bet price": g["px_bet"].median(),
        "A/E vs bet price": g["won"].sum() / g["p_bet"].sum(), "A/E price-matched": g["won"].sum() / g["p_ctl"].sum(),
        "ROI at bet price %": 100 * ((g["won"] * g["px_bet"]).sum() / len(g) - 1),
        "ROI at SP %": 100 * ((g["won"] * g["sp"]).sum() / g["sp"].notna().sum() - 1)}))
    L += ["## 2. By move from the open to bet time", "", t.round(3).to_markdown(), ""]
    # 3. model at bet time
    snaps = [pd.read_parquet(f) for f in sorted(SNAPS.glob("*.parquet"))]
    s = pd.concat(snaps, ignore_index=True)
    s = s[s["rm_p"].notna()][["run_id", "rm_p"]]
    s["run_id"] = s["run_id"].astype(str)
    m = d.merge(s, on="run_id")
    m = m[m.groupby("race_id")["run_id"].transform("size") == m["race_id"].map(d.groupby("race_id").size())]
    if m["race_id"].nunique() >= 50:
        m["lm"] = np.log(m["rm_p"].clip(1e-4) / m.groupby("race_id")["rm_p"].transform("sum"))
        b0, _ = race_ll(m, ["lp"])
        b1, bb = race_ll(m, ["lp", "lm"])
        b2, bb2 = race_ll(m, ["lp", "lm", "drift"])
        L += ["## 3. Model (racing_model.json at the time) on top of the bet-time price", "",
              f"- {m['race_id'].nunique()} races. Price alone {b0.mean():.4f}; + model {b1.mean():.4f}"
              f" ({paired(b0, b1)}; weights price {bb[0]:.2f}, model {bb[1]:.2f}); + model + drift {b2.mean():.4f}"
              f" ({paired(b0, b2)})", ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
