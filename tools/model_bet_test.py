"""Betting on the Racing Model's own probabilities (not the dashboard's Combo lines).

    python -W ignore tools/model_bet_test.py          # -> reports/model_bet_test.md

Scores: tools/clear_test.py's out-of-sample production model (all-state training, retrained at the start of each
year 2023 to 2026, scoring that year; 2026 to 23 Sep). `blend %` = softmax(a log p_model + b log p_SP) with a / b
fitted inside each training window, so it is out of sample too. Every state.

Win overlays: bet a runner when blend chance x price > 1 + m (m = margin), flat $1 and 1/4 Kelly. At SP (the blend
uses SP, so this is an upper bound: SP is not known at bet time) and, 22 Aug to 23 Sep 2026, at the dashboard's
stored fixed price >= 10 min before the start (tools/dashboard_snapshots.py) with the blend re-formed on that price
(a / b recovered per year from the scores). Also model-alone overlays (model chance x price). A/E price-matched =
wins / win rate of all runners at the same SP (removes the favourite-longshot bias). CIs: bootstrap over race days.

Exotics: discounted Plackett-Luce (exponents 1 / 0.76 / 0.62) on blend and on SP chances. Estimated dividend =
k / SP chance of the combination (k = real dividend x fair-SP chance from 2 Oct's TAB dividends: quinella 0.83,
exacta 0.82, trifecta 0.79). Bet the combinations (quinella / exacta from the blend's top 6, trifecta from its top 6)
whose blend chance x estimated dividend > 1 + m; $1 per combination. So the ROI is k x (blend / SP chance on the
winning combination) - 1: it tests whether the blend's order chances beat the market's, at the 2 Oct take.
"""
import itertools
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
OUT = ROOT / "reports/model_bet_test.md"
SCORES = ROOT / "data/interim/clear_test_scores_{y}.csv.gz"
SNAPS = ROOT / "data/interim/dash_snapshots"
DB = ROOT / "data/db/racing.duckdb"
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]
MARGINS = [0.0, 0.1, 0.2, 0.3, 0.5]
LAM = [1.0, 0.76, 0.62]
K = {"Quinella": 0.83, "Exacta": 0.82, "Trifecta": 0.79}
BOOT = 1000
rng = np.random.default_rng(7)


def load():
    sc = pd.concat([pd.read_csv(str(SCORES).format(y=y)) for y in (2023, 2024, 2025, 2026)], ignore_index=True)
    con = duckdb.connect(str(DB), read_only=True)
    info = con.sql("""select r.run_id, r.race_id, r.race_date, ra.state, ra.venue, ra.location_class, r.sp,
                             r.res_finish from runs r join races ra using (race_id)
                      where r.race_date >= date '2023-01-01'""").df()
    d = sc.merge(info, on=["run_id", "race_id"])
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("res_finish", lambda s: (s == 1).sum()),
                                  sp=("sp", lambda s: (s > 1).all()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & ok.sp])].copy()
    d["won"] = (d["res_finish"] == 1).astype(int)
    d["p_b"] = d["blend %"] / 100
    d["p_m"] = d["model %"] / 100
    for c in ("p_b", "p_m"):
        d[c] = d[c] / d.groupby("race_id")[c].transform("sum")
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d["date"] = pd.to_datetime(d["race_date"])
    d["year"] = d["date"].dt.year
    d["sat"] = np.where(d["date"].dt.dayofweek == 5, "Saturday", "other days")
    d["grp"] = np.where(d["state"] == "QLD", "QLD", np.where(d["state"].isin(["VIC", "SA"]), "VIC/SA",
                                                            np.where(d["state"] == "NSW", "NSW", "WA/other")))
    d["tier"] = d["location_class"].map({"M": "metro", "P": "provincial", "C": "country"}).fillna("other")
    return d


def blend_weights(d):
    """a, b per year from blend % = softmax(a log p_model + b log p_SP): OLS on race-demeaned logs."""
    out = {}
    for y, g in d.groupby("year"):
        lb, lm, ls = (np.log(g[c].clip(1e-6)) for c in ("p_b", "p_m", "p_sp"))
        dm = lambda s: s - s.groupby(g["race_id"]).transform("mean")  # noqa: E731
        X = np.c_[dm(lm), dm(ls)]
        a, b = np.linalg.lstsq(X, dm(lb), rcond=None)[0]
        out[y] = (a, b)
    return out


def boot_days(g, f):
    days = g["race_date"].unique()
    if len(days) < 10:
        return ""
    by = {k: v for k, v in g.groupby("race_date")}
    vals = []
    for _ in range(BOOT):
        s = rng.choice(days, len(days))
        vals.append(f(pd.concat([by[x] for x in s])))
    return f"{np.percentile(vals, 2.5):+.1f} to {np.percentile(vals, 97.5):+.1f}"


def win_summary(b, price):
    roi = lambda g: 100 * ((g["won"] * g[price]).sum() / len(g) - 1)  # noqa: E731
    kel = lambda g: 100 * (g["kf"] * (g["won"] * g[price] - 1)).sum() / g["kf"].sum()  # noqa: E731
    return {"bets": len(b), "per day": round(len(b) / max(b["race_date"].nunique(), 1), 1),
            "win %": round(100 * b["won"].mean(), 1), "avg price": round(b[price].median(), 1),
            "A/E pm": round(b["won"].sum() / b["p_ctl"].sum(), 3),
            "ROI flat %": round(roi(b), 1), "95%": boot_days(b, roi),
            "ROI 1/4 Kelly %": round(kel(b), 1)}


def win_bets(d, p, price, m):
    b = d[(d[p] * d[price] > 1 + m) & d[price].notna()].copy()
    o = b[price] - 1
    b["kf"] = (0.25 * (b[p] * o - (1 - b[p])) / o).clip(lower=0)
    return b


def order_p(p, order):
    left = np.ones(len(p), bool)
    pr = 1.0
    for k, i in enumerate(order):
        w = np.where(left, p, 0.0) ** LAM[k]
        pr *= w[i] / w.sum()
        left[i] = False
    return pr


def exotics(d, margins=(0.0, 0.2, 0.5, 1.0)):
    rows = []
    for rid, g in d.groupby("race_id", sort=False):
        g = g.sort_values("p_b", ascending=False)
        pb, ps = g["p_b"].to_numpy(), g["p_sp"].to_numpy()
        fin = g["res_finish"].to_numpy()
        win = [np.flatnonzero(fin == k) for k in (1, 2, 3)]
        if any(len(w) != 1 for w in win):
            continue
        w1, w2, w3 = (int(w[0]) for w in win)
        top = range(min(6, len(g)))
        meta = (g["race_date"].iloc[0], g["grp"].iloc[0], g["sat"].iloc[0], g["tier"].iloc[0], g["year"].iloc[0])
        for pool, k in (("Quinella", 2), ("Exacta", 2), ("Trifecta", 3)):
            for c in itertools.permutations(top, k):
                if pool == "Quinella":
                    if c[0] > c[1]:
                        continue
                    cb = order_p(pb, c) + order_p(pb, c[::-1])
                    cs = order_p(ps, c) + order_p(ps, c[::-1])
                    hit = {c[0], c[1]} == {w1, w2}
                else:
                    cb, cs = order_p(pb, c), order_p(ps, c)
                    hit = tuple(c) == (w1, w2, w3)[:k]
                edge = cb * K[pool] / cs - 1
                if edge > margins[0]:
                    rows.append((rid, pool, *meta, edge, cs, cb, hit, K[pool] / cs))
    return pd.DataFrame(rows, columns=["race_id", "pool", "race_date", "grp", "sat", "tier", "year", "edge",
                                       "p_sp_c", "p_b_c", "hit", "div"])


def ex_summary(e):
    roi = lambda g: 100 * ((g["hit"] * g["div"]).sum() / len(g) - 1)  # noqa: E731
    return {"combos": len(e), "races": e["race_id"].nunique(), "hits": int(e["hit"].sum()),
            "hits / SP-expected": round(e["hit"].sum() / e["p_sp_c"].sum(), 3),
            "est ROI %": round(roi(e), 1), "95%": boot_days(e, roi)}


def table(rows):
    return pd.DataFrame(rows).to_markdown(index=False)


def main():
    d = load()
    ab = blend_weights(d)
    L = ["# Betting on the Racing Model's probabilities", "",
         f"- {d['race_id'].nunique():,} races, {d['race_date'].min()} to {d['race_date'].max()}, every state, out of"
         " sample (yearly retrain). See the module docstring for the method.",
         "- Blend weights recovered per year (a on the model, b on SP): "
         + ", ".join(f"{y} a {a:.2f} b {b:.2f}" for y, (a, b) in ab.items()), ""]

    L += ["## Win overlays at SP (blend chance x SP > 1 + margin)", ""]
    L.append(table([{"margin": m, **win_summary(win_bets(d, "p_b", "sp", m), "sp")} for m in MARGINS]))
    L += ["", "Model alone (model chance x SP > 1 + margin):", ""]
    L.append(table([{"margin": m, **win_summary(win_bets(d, "p_m", "sp", m), "sp")} for m in MARGINS]))
    base = win_bets(d, "p_b", "sp", 0.2)
    for col, name in (("grp", "state"), ("sat", "day"), ("tier", "meeting tier"), ("year", "year")):
        L += ["", f"Blend, margin 0.2, by {name}:", ""]
        L.append(table([{name: k, **win_summary(g, "sp")} for k, g in base.groupby(col)]))
    sat = base[base["sat"] == "Saturday"]
    L += ["", "Blend, margin 0.2, Saturdays by meeting tier:", ""]
    L.append(table([{"tier": k, **win_summary(g, "sp")} for k, g in sat.groupby("tier")]))

    # fixed prices (dashboard snapshots, >= 10 min before the start)
    snaps = [pd.read_parquet(f) for f in sorted(SNAPS.glob("*.parquet"))]
    if snaps:
        s = pd.concat(snaps, ignore_index=True)[["run_id", "fixed_win_price"]]
        s["run_id"] = s["run_id"].astype(str).str.replace(r"\.0$", "", regex=True)
        f = d.assign(run_id=d["run_id"].astype(str)).merge(s, on="run_id", how="inner")
        f["fx"] = pd.to_numeric(f["fixed_win_price"], errors="coerce").where(lambda v: v > 1)
        f = f[f["fx"].notna().groupby(f["race_id"]).transform("all")].copy()
        if len(f):
            inv = 1 / f["fx"]
            f["p_fx"] = inv / inv.groupby(f["race_id"]).transform("sum")
            a, b = ab[2026]
            z = a * np.log(f["p_m"].clip(1e-6)) + b * np.log(f["p_fx"])
            f["p_bfx"] = np.exp(z - z.groupby(f["race_id"]).transform("max"))
            f["p_bfx"] /= f.groupby("race_id")["p_bfx"].transform("sum")
            L += ["", f"## Win overlays at the dashboard's fixed price ({f['race_id'].nunique()} races,"
                  f" {f['race_date'].min()} to {f['race_date'].max()}; blend re-formed on the fixed price)", ""]
            L.append(table([{"margin": m, **win_summary(win_bets(f, "p_bfx", "fx", m), "fx")} for m in MARGINS]))
            L += ["", "Same bets settled at SP instead (price taken vs SP):", ""]
            L.append(table([{"margin": m, **win_summary(win_bets(f, "p_bfx", "fx", m), "sp")} for m in MARGINS]))

    # exotics: 2025-2026 (enumeration is slow)
    ex = exotics(d[d["year"] >= 2025])
    L += ["", "## Exotic overlays (blend order chances vs SP order chances, estimated dividends), 2025-2026", ""]
    rows = []
    for pool, g in ex.groupby("pool"):
        for m in (0.0, 0.2, 0.5, 1.0):
            rows.append({"pool": pool, "margin": m, **ex_summary(g[g["edge"] > m])})
    L.append(table(rows))
    for col, name in (("grp", "state"), ("sat", "day"), ("tier", "meeting tier")):
        L += ["", f"Exotics, margin 0.2, by {name}:", ""]
        rows = []
        for (pool, k), g in ex[ex["edge"] > 0.2].groupby(["pool", col]):
            rows.append({"pool": pool, name: k, **ex_summary(g)})
        L.append(table(rows))
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
