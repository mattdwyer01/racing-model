"""Exotic betting rules on pre-race dashboard values, dividends estimated from SP and calibrated on real TAB dividends.

    python -W ignore tools/exotics_test.py --repo ../toprate     # -> reports/exotics_test.md

Data: tools/dashboard_review.load() (pre-race Combo gap / speed map tag / SP / finishing positions, 22 Aug on) and
TopRate's tab_dividends.csv (real TAB dividends per race, all pools; captured from 2 Oct 2026, TAB's API serves no past
dates). Calibration days = dates in tab_dividends.csv; test days = the rest.

Estimate: chance of the winning combination from normalised SP with a discounted Plackett-Luce order model (exponents
1 / 0.76 / 0.62 / 0.55 for 1st-4th, model/order_model.md fitted 0.75-0.78 and 0.59-0.64); multi-race pools multiply
the winners' chances. Per pool, log(real dividend) = a + b log(1 / chance) is fitted on the calibration days; the
estimate for a test-day hit is exp(a + b log(1 / chance)) (smearing-corrected for the mean). Pools: Win, Quinella,
Exacta, Trifecta, FirstFour, RunningDouble (each consecutive pair), DailyDouble (last-2 and last race), Treble (last 3),
Quaddie (last 4), EarlyQuaddie (the 4 races before the main quaddie; races 1-4 at meetings of 7 races or fewer) - leg layout as TAB's 2 Oct dividends show it.

Rules use the dashboard lines: A = within 4 Combo points of the top, B = A + 4 to 8 back unless speed map unfavoured,
T = Combo top pick; controls pick by SP only (S2 / S3 / ... = shortest 2 / 3 / ... in the market). Cost = number of
$1 combinations; ROI = estimated return / cost. CIs: bootstrap over meeting-days.
"""
import argparse
import itertools
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import dashboard_review as dr  # noqa: E402

OUT = ROOT / "reports/exotics_test.md"
LAM = [1.0, 0.76, 0.62, 0.55]
BOOT = 2000
rng = np.random.default_rng(11)
CAPS = {"Quaddie": 600, "EarlyQuaddie": 600}


def order_prob(p, order):
    """Discounted Plackett-Luce chance of runners `order` (indices into p) filling places 1..len(order)."""
    left = np.ones(len(p), bool)
    pr = 1.0
    for k, i in enumerate(order):
        w = np.where(left, p, 0.0) ** LAM[k]
        pr *= w[i] / w.sum()
        left[i] = False
    return pr


def n_combos(sets):
    """Number of combinations with distinct runners across positional sets (lists of run ids)."""
    if any(len(s) == 0 for s in sets):
        return 0
    return sum(1 for c in itertools.product(*sets) if len(set(c)) == len(c))


def prep(d):
    for c in ["sp", "gap", "won", "rank", "p_sp", "race", "finish_position"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["date"] = d["date"].astype(str).str[:10]
    d = d[d["sp"] > 1].copy()
    d["p"] = (1 / d["sp"]) / d.groupby("race_id")["sp"].transform(lambda s: (1 / s).sum())
    d["sp_rank"] = d.groupby("race_id")["sp"].rank(method="first")
    unf = d["sm_tag"] == "unfavoured"
    d["A"] = d["gap"] <= 4
    d["B"] = d["A"] | ((d["gap"] <= 8) & ~unf)
    d["T"] = d["rank"] == 1
    return d


def races(d):
    """Per race: dict with runner ids, p, finish order (first 4, no dead heats), selection lists."""
    out = {}
    for rid, g in d.groupby("race_id", sort=False):
        g = g.reset_index(drop=True)
        fp = g["finish_position"]
        top = []
        for k in range(1, 5):
            m = g.index[fp == k]
            if len(m) != 1:
                break
            top.append(int(m[0]))
        sel = {"A": list(g.index[g["A"]]), "B": list(g.index[g["B"]]), "T": list(g.index[g["T"]])}
        # matched SP controls: the same NUMBER of runners as A / B, shortest priced
        sp_order = list(g.sort_values("sp_rank").index)
        sel["SA"] = sp_order[:len(sel["A"])]
        sel["SB"] = sp_order[:len(sel["B"])]
        for n in range(1, 7):
            sel[f"S{n}"] = list(g.index[g.sp_rank <= n])
            sel[f"C{n}"] = list(g.index[g["rank"] <= n])
        out[rid] = dict(date=g["date"].iloc[0], venue=g["venue"].iloc[0], race=int(g["race"].iloc[0]),
                        grp=g["grp"].iloc[0], p=g["p"].to_numpy(float), top=top, sel=sel, n=len(g))
    return out


# rule = (pool, name, positional selection keys)
SINGLE = [
    ("Win", "Combo top", ["T"]), ("Win", "SP fav (control)", ["S1"]),
    ("Quinella", "box SP, same count as A (control)", ["SA", "SA"]),
    ("Exacta", "box SP, same count as A (control)", ["SA", "SA"]),
    ("Exacta", "SP fav / SP same count as B (control)", ["S1", "SB"]),
    ("Trifecta", "box SP, same count as A (control)", ["SA", "SA", "SA"]),
    ("Trifecta", "SA / SA / SB (control)", ["SA", "SA", "SB"]),
    ("Trifecta", "SP fav / SA / SB (control)", ["S1", "SA", "SB"]),
    ("FirstFour", "SA / SA / SB / SB (control)", ["SA", "SA", "SB", "SB"]),
    ("Quinella", "box A", ["A", "A"]), ("Quinella", "box Combo top 3", ["C3", "C3"]),
    ("Quinella", "box SP top 3 (control)", ["S3", "S3"]),
    ("Exacta", "box A", ["A", "A"]), ("Exacta", "T / B", ["T", "B"]), ("Exacta", "box Combo top 3", ["C3", "C3"]),
    ("Exacta", "box SP top 3 (control)", ["S3", "S3"]),
    ("Trifecta", "box A", ["A", "A", "A"]), ("Trifecta", "T / A / B", ["T", "A", "B"]),
    ("Trifecta", "A / A / B", ["A", "A", "B"]), ("Trifecta", "box Combo top 4", ["C4", "C4", "C4"]),
    ("Trifecta", "box SP top 4 (control)", ["S4", "S4", "S4"]),
    ("FirstFour", "A / A / B / B", ["A", "A", "B", "B"]), ("FirstFour", "T / A / B / B", ["T", "A", "B", "B"]),
    ("FirstFour", "box Combo top 5", ["C5", "C5", "C5", "C5"]),
    ("FirstFour", "box SP top 5 (control)", ["S5", "S5", "S5", "S5"]),
]
MULTI = [("A", "A x A ..."), ("B", "B x B ... (dashboard quaddie rule)"), ("T", "Combo top only"),
         ("SA", "SP, same count as A each leg (control)"), ("SB", "SP, same count as B each leg (control)"),
         ("S2", "SP top 2 each leg (control)"), ("S3", "SP top 3 each leg (control)")]
NLEG = {"RunningDouble": 2, "DailyDouble": 2, "Treble": 3, "Quaddie": 4, "EarlyQuaddie": 4}


def multi_legs(meet):
    """{pool: [list of race numbers per bet]} for one meeting (sorted race numbers)."""
    nos = sorted(meet)
    last = nos[-1]
    out = {"RunningDouble": [[a, b] for a, b in zip(nos, nos[1:]) if b == a + 1]}
    if len(nos) >= 3:
        out["DailyDouble"] = [[last - 2, last]]
        out["Treble"] = [[last - 2, last - 1, last]]
    if len(nos) >= 4:
        out["Quaddie"] = [list(range(last - 3, last + 1))]
    # early quaddie: the 4 races before the main quaddie; at 7 races or fewer, races 1-4 (overlapping the main)
    if len(nos) >= 8:
        out["EarlyQuaddie"] = [list(range(last - 7, last - 3))]
    elif len(nos) >= 5:
        out["EarlyQuaddie"] = [nos[:4]]
    return {k: [l for l in v if all(x in meet for x in l)] for k, v in out.items()}


def bets(R):
    """Every (pool, rule, day, venue, grp, cost, hit, chance of the winning combination) over all races / meetings."""
    rows = []
    for rid, r in R.items():
        for pool, name, keys in SINGLE:
            k = len(keys)
            if len(r["top"]) < k or r["n"] < k + 1:
                continue
            sets = [r["sel"][x] for x in keys]
            cost = n_combos(sets)
            if not cost:
                continue
            win = r["top"][:k]
            hit = all(w in s for w, s in zip(win, sets))
            if pool == "Quinella":
                ch = order_prob(r["p"], win) + order_prob(r["p"], win[::-1])
                cost //= 2
                hit = set(win) <= set(sets[0])
            else:
                ch = order_prob(r["p"], win)
            rows.append((pool, name, r["date"], r["venue"], r["race"], r["grp"], cost, hit, ch))
    meets = {}
    for rid, r in R.items():
        meets.setdefault((r["date"], r["venue"]), {})[r["race"]] = r
    for (day, venue), meet in meets.items():
        for pool, leg_lists in multi_legs(meet).items():
            for legs in leg_lists:
                rr = [meet[x] for x in legs]
                if any(len(r["top"]) < 1 for r in rr):
                    continue
                ch = float(np.prod([r["p"][r["top"][0]] for r in rr]))
                for key, name in MULTI:
                    cost = int(np.prod([len(r["sel"][key]) for r in rr]))
                    if not cost or cost > CAPS.get(pool, 10 ** 9):
                        continue
                    hit = all(r["top"][0] in r["sel"][key] for r in rr)
                    rows.append((pool, name, day, venue, legs[-1], rr[0]["grp"], cost, hit, ch))
    return pd.DataFrame(rows, columns=["pool", "rule", "date", "venue", "race", "grp", "cost", "hit", "chance"])


def real_dividends(repo, R):
    """Calibration rows: pool, date, venue, race (dividend race), real dividend, model chance of that combination."""
    sys.path.insert(0, str(Path(repo)))
    from tab_results_poller import provider_venue_for
    t = pd.read_csv(Path(repo) / "tab_dividends.csv")
    t = t[t["product"].isin(["Win", "Quinella", "Exacta", "Trifecta", "FirstFour", *NLEG])].dropna(subset=["amount"])
    by = {}
    for rid, r in R.items():
        by[(r["date"], r["venue"].upper(), r["race"])] = r
    rows = []
    for _, x in t.iterrows():
        v = provider_venue_for(x["venue"]).upper()
        n = int(x["race_no"])
        pool = x["product"]
        if pool in NLEG:
            k = NLEG[pool]
            legs = ([n - 2, n] if pool == "DailyDouble" else list(range(n - k + 1, n + 1)))
            rr = [by.get((x["date"], v, l)) for l in legs]
            if any(r is None or not r["top"] for r in rr):
                continue
            ch = float(np.prod([r["p"][r["top"][0]] for r in rr]))
        else:
            r = by.get((x["date"], v, n))
            k = {"Win": 1, "Quinella": 2, "Exacta": 2, "Trifecta": 3, "FirstFour": 4}[pool]
            if r is None or len(r["top"]) < k:
                continue
            win = r["top"][:k]
            ch = order_prob(r["p"], win) + (order_prob(r["p"], win[::-1]) if pool == "Quinella" else 0)
        rows.append((pool, x["date"], v, n, float(x["amount"]), ch))
    return pd.DataFrame(rows, columns=["pool", "date", "venue", "race", "div", "chance"])


def calibrate(cal):
    """Per pool: a, b of log(div) = a + b log(1/chance), smearing factor, n, plain ratio stats."""
    out = {}
    for pool, g in cal.groupby("pool"):
        x, y = np.log(1 / g["chance"]), np.log(g["div"])
        if len(g) >= 8 and x.std() > 0:
            b, a = np.polyfit(x, y, 1)
        else:
            b = 1.0
            a = float((y - x).mean())
        res = y - (a + b * x)
        out[pool] = dict(a=a, b=b, smear=float(np.exp(res).mean()), n=len(g),
                         ratio_med=float(np.median(g["div"] * g["chance"])),
                         ratio_geo=float(np.exp(np.log(g["div"] * g["chance"]).mean())))
    return out


def est_div(cal, pool, chance):
    c = cal[pool]
    return np.exp(c["a"] + c["b"] * np.log(1 / chance)) * c["smear"]


def summarise(b, value):
    rows = []
    for (pool, rule), g in b.groupby(["pool", "rule"], sort=False):
        ret = np.where(g["hit"], g[value], 0.0)
        cost = g["cost"].to_numpy(float)
        key = (g["date"] + g["venue"]).to_numpy()
        u = pd.unique(key)
        idx = {k: np.flatnonzero(key == k) for k in u}
        bs = []
        for _ in range(BOOT):
            pick = np.concatenate([idx[k] for k in rng.choice(u, len(u))])
            bs.append(ret[pick].sum() / cost[pick].sum() - 1)
        vs = (g["grp"] != "NSW/WA/other").to_numpy()
        flexi = ret / cost                       # return per bet at an equal (flexi) stake per bet
        bs2 = []
        for _ in range(BOOT):
            pick = np.concatenate([idx[k] for k in rng.choice(u, len(u))])
            bs2.append(flexi[pick].mean() - 1)
        rows.append({"pool": pool, "rule": rule, "bets": len(g), "hit %": 100 * g["hit"].mean(),
                     "avg combos": cost.mean(), "ROI $1/combo %": 100 * (ret.sum() / cost.sum() - 1),
                     "95%": f"{100 * np.percentile(bs, 2.5):+.0f} to {100 * np.percentile(bs, 97.5):+.0f}",
                     "ROI flexi %": 100 * (flexi.mean() - 1),
                     "95% flexi": f"{100 * np.percentile(bs2, 2.5):+.0f} to {100 * np.percentile(bs2, 97.5):+.0f}",
                     "VIC/SA/QLD %": 100 * (ret[vs].sum() / cost[vs].sum() - 1) if vs.any() else np.nan})
    return pd.DataFrame(rows)


PAIRS = [("Win", "Combo top", "SP fav (control)"),
         ("Quinella", "box A", "box SP, same count as A (control)"),
         ("Exacta", "box A", "box SP, same count as A (control)"),
         ("Exacta", "T / B", "SP fav / SP same count as B (control)"),
         ("Trifecta", "box A", "box SP, same count as A (control)"),
         ("Trifecta", "A / A / B", "SA / SA / SB (control)"),
         ("Trifecta", "T / A / B", "SP fav / SA / SB (control)"),
         ("FirstFour", "A / A / B / B", "SA / SA / SB / SB (control)")]
PAIRS += [(p, "A x A ...", "SP, same count as A each leg (control)") for p in NLEG]
PAIRS += [(p, "B x B ... (dashboard quaddie rule)", "SP, same count as B each leg (control)") for p in NLEG]


def paired(b, value):
    """Rule minus its matched SP control on the SAME bets (same races, same combination count), flexi staking:
    mean return per unit staked, difference with a meeting-day bootstrap CI."""
    rows = []
    for pool, rule, ctl in PAIRS:
        g = b[b["pool"] == pool]
        k = ["date", "venue", "race"]
        x = g[g["rule"] == rule].set_index(k)
        y = g[g["rule"] == ctl].set_index(k)
        j = x.join(y, lsuffix="_r", rsuffix="_c", how="inner")
        j = j[j["cost_r"] > 0]
        if j.empty:
            continue
        fr = np.where(j["hit_r"], j[value + "_r"], 0) / j["cost_r"]
        fc = np.where(j["hit_c"], j[value + "_c"], 0) / j["cost_c"]
        key = np.array([f"{a}|{b_}" for a, b_ in zip(j.index.get_level_values(0), j.index.get_level_values(1))])
        u = pd.unique(key)
        idx = {kk: np.flatnonzero(key == kk) for kk in u}
        diff = np.asarray(fr - fc, dtype=float)
        bs = [diff[np.concatenate([idx[kk] for kk in rng.choice(u, len(u))])].mean() for _ in range(BOOT)]
        rows.append({"pool": pool, "rule": rule, "bets": len(j), "rule hit %": 100 * j["hit_r"].mean(),
                     "control hit %": 100 * j["hit_c"].mean(), "rule ROI flexi %": 100 * (fr.mean() - 1),
                     "control ROI flexi %": 100 * (fc.mean() - 1), "rule - control (pts)": 100 * diff.mean(),
                     "95%": f"{100 * np.percentile(bs, 2.5):+.1f} to {100 * np.percentile(bs, 97.5):+.1f}"})
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(ROOT.parent / "toprate"))
    a = ap.parse_args()
    d = prep(dr.load(a.repo))
    R = races(d)
    cal_rows = real_dividends(a.repo, R)
    cal_days = sorted(cal_rows["date"].unique())
    cal = calibrate(cal_rows)
    b = bets(R)
    b = b[b["pool"].isin(cal)]
    b["est"] = [est_div(cal, p, c) for p, c in zip(b["pool"], b["chance"])]
    test = b[~b["date"].isin(cal_days)]
    L = ["# Exotic rules (dividends estimated from SP, calibrated on real TAB dividends)", "",
         f"- Test: {test['date'].min()} to {test['date'].max()}, {test[['date', 'venue']].drop_duplicates().shape[0]}"
         f" meetings, pre-race dashboard values (all states on the dashboard). Calibration: real TAB dividends on"
         f" {', '.join(cal_days)} ({len(cal_rows)} pool results). See the module docstring for the method.", "",
         "## Calibration (real dividend vs 1 / chance of the winning combination)", "",
         "| pool | n | median real x chance | geo mean | fitted b (1 = proportional) |", "|---|---|---|---|---|"]
    for pool, c in cal.items():
        L.append(f"| {pool} | {c['n']} | {c['ratio_med']:.2f} | {c['ratio_geo']:.2f} | {c['b']:.2f} |")
    L += ["", "- real x chance = what $1 returns relative to a fair price from SP (0.80 would be a 20% take with no"
          " bias). b < 1: long-odds combinations pay less than proportionally, short ones more.", "",
          "## Rules on the test days (estimated dividends)", "",
          "- ROI $1/combo: every combination $1 (big tickets weigh more). ROI flexi: the same stake per bet whatever the"
          " combinations (how a flexi punter bets). VIC/SA/QLD column is $1/combo.", "",
          summarise(test, "est").to_markdown(index=False, floatfmt=".1f"), ""]
    L += ["## Rule vs matched SP control (same bets, flexi; the calibration level cancels out)", "",
          "- Control = the same number of runners per position, picked by SP instead of Combo / speed map. A gap here"
          " is what the dashboard adds beyond the market; it does not depend on the calibration level (only on its"
          " slope b, about 1 for every pool).", "",
          paired(test, "est").to_markdown(index=False, floatfmt=".1f"), ""]
    calb = b[b["date"].isin(cal_days)].copy()
    realmap = {(r.pool, r.date, r.venue, r.race): r.div for r in cal_rows.itertuples()}
    calb["real"] = [realmap.get((p, dt, v.upper(), rc), np.nan)
                    for p, dt, v, rc in zip(calb["pool"], calb["date"], calb["venue"], calb["race"])]
    miss = calb["hit"] & calb["real"].isna()
    calb = calb[~miss]
    L += [f"## Calibration days with REAL dividends ({', '.join(cal_days)}; few bets, in-sample for the calibration)", "",
          f"- Hits without a matching TAB dividend dropped: {int(miss.sum())}.", "",
          summarise(calb, "real").drop(columns=["95%", "95% flexi"]).to_markdown(index=False, floatfmt=".1f"), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
