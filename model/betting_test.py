"""Betting test: overlay rules on the out-of-sample blends, backtested at SP.

    python model/betting_test.py      # needs reports/race_sim_per_runner.csv.gz (model/race_sim.py) and
                                      # reports/disagreement_per_runner.csv.gz (model/disagreement.py)
                                      # -> reports/betting_test.md

Rule: bet a runner when edge = p * SP - 1 > threshold, p = an out-of-sample blended win probability
  (production blend, simulation blend, production + simulation blend), optionally SP <= cap.
Stakes: flat 1 unit, and quarter Kelly (0.25 * edge / (SP - 1) of a unit bank per bet, no compounding).
Control: the same rule with p = calibrated SP alone (market only). What the control earns comes from the
  favourite-longshot bias, not from the model; the model's contribution is ROI minus the control's.
Signal filters (from the disagreement test): position map pushed up (top 10% of d), past ground loss pushed up
  (top 10% of d), each alone and on top of an overlay rule.
95% ranges: race bootstrap of profit and turnover (2,000). By state and year for the main rules.

Caveats: SP is known only at the jump, and the blend uses SP itself, so this is not an executable strategy; it
measures whether the model finds prices that are too long at the market's final price. The executable version
needs the TAB fixed price at bet time (the Vultr poller log). SP here is TopRate's starting price.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ["blend prod", "blend sim", "blend prod + sim", "SP calibrated"]
THRESH = [0.0, 0.05, 0.1, 0.2, 0.3]
CAPS = [None, 21.0]
BOOT = 2000
BOOK_OK = (1.05, 2.5)    # SP book %: under 105% = missing runners / bad SPs (fake overlays); over 250% = broken data
DROPPED = {}


def load():
    r = pd.read_csv(ROOT / "reports/race_sim_per_runner.csv.gz", parse_dates=["race_date"])
    dz = ROOT / "reports/disagreement_per_runner.csv.gz"
    if dz.exists():
        d = pd.read_csv(dz, usecols=["run_id", "d position map", "d past ground loss"])
        r = r.merge(d, on="run_id", how="left")
        for c, lab in [("d position map", "posmap up"), ("d past ground loss", "gl up")]:
            r[lab] = r[c] >= r[c].quantile(0.9)
    r = r[r["sp"] > 1].copy()
    book = (1 / r["sp"]).groupby(r["race_id"]).transform("sum")
    bad = ~book.between(*BOOK_OK)
    DROPPED["races"] = int(r.loc[bad, "race_id"].nunique())
    return r[~bad].copy()


def stats(b, rng, all_races):
    """b: bet rows with stake, ret (profit). Race bootstrap of ROI."""
    if len(b) == 0:
        return {"bets": 0}
    g = b.groupby("race_id")[["stake", "ret"]].sum()
    idx = rng.integers(0, len(g), (BOOT, len(g)))
    W = g.to_numpy()[idx].sum(1)
    roi = W[:, 1] / W[:, 0]
    cum = b.sort_values("race_date")["ret"].cumsum()
    return {"bets": len(b), "races bet": len(g), "share of races": len(g) / all_races,
            "strike": b["won"].mean(), "avg SP": b["sp"].mean(), "turnover": b["stake"].sum(),
            "profit": b["ret"].sum(), "ROI": b["ret"].sum() / b["stake"].sum(),
            "ROI 95%": f"{np.percentile(roi, 2.5):+.3f} to {np.percentile(roi, 97.5):+.3f}",
            "max drawdown": float((cum.cummax() - cum).max())}


def bets(r, src, t, cap, kelly=False, extra=None):
    edge = r[src] * r["sp"] - 1
    m = edge > t
    if cap:
        m &= r["sp"] <= cap
    if extra is not None:
        m &= extra
    b = r[m].copy()
    e = edge[m]
    b["stake"] = 0.25 * e / (b["sp"] - 1) * 100 if kelly else 1.0
    b["ret"] = b["stake"] * (b["won"] * b["sp"] - 1)
    return b


def main():
    r = load()
    rng = np.random.default_rng(0)
    n_races = r["race_id"].nunique()
    rows = []
    for src in SOURCES:
        for cap in CAPS:
            for t in THRESH:
                for kelly in (False, True):
                    s = stats(bets(r, src, t, cap, kelly), rng, n_races)
                    rows.append({"p from": src, "SP cap": cap or "-", "edge >": t,
                                 "stakes": "1/4 Kelly" if kelly else "flat", **s})
    T = pd.DataFrame(rows)

    # model minus control, flat, paired on the same thresholds
    ctrl = T[(T["p from"] == "SP calibrated") & (T.stakes == "flat")].set_index(["SP cap", "edge >"])["ROI"]
    exc = T[(T["p from"] != "SP calibrated") & (T.stakes == "flat")].copy()
    exc["control ROI"] = [ctrl.get((c, t), np.nan) for c, t in zip(exc["SP cap"], exc["edge >"])]
    exc["ROI - control"] = exc["ROI"] - exc["control ROI"]

    # by state and year for the main rules
    main_rules = [("blend prod", 0.1, 21.0), ("blend prod + sim", 0.1, 21.0), ("blend sim", 0.1, 21.0),
                  ("SP calibrated", 0.1, 21.0)]
    split = []
    for src, t, cap in main_rules:
        b = bets(r, src, t, cap)
        for lab, m in [("QLD", b.state == "QLD"), ("VIC/SA", b.state != "QLD")] + \
                [(str(y), b.fold == y) for y in sorted(b.fold.unique())]:
            split.append({"rule": f"{src}, edge > {t}, SP <= {cap:g}", "subset": lab,
                          **stats(b[m], rng, n_races)})
    # signal filters
    sig = []
    if "posmap up" in r:
        for lab, m in [("position map up", r["posmap up"]), ("ground loss up", r["gl up"]),
                       ("ground loss up, VIC/SA", r["gl up"] & (r.state != "QLD")),
                       ("position map or ground loss up", r["posmap up"] | r["gl up"])]:
            for src, t in [(None, None), ("blend prod", 0.0), ("blend prod", 0.1), ("blend prod + sim", 0.1)]:
                if src is None:
                    b = r[m & (r.sp <= 21)].assign(stake=1.0)
                    b["ret"] = b["won"] * b["sp"] - 1
                    rule = "all such runners, SP <= 21"
                else:
                    b = bets(r, src, t, 21.0, extra=m)
                    rule = f"{src} edge > {t}, SP <= 21"
                sig.append({"signal": lab, "rule": rule, **stats(b, rng, n_races)})
    fmt = dict(index=False, floatfmt=".3f")
    L = ["# Betting test (backtest at SP, 2023 to 2026 test years, VIC/SA/QLD)", "",
         "- Bet when p x SP - 1 > edge threshold; p = out-of-sample blended probability. Flat = 1 unit per bet;"
         " 1/4 Kelly = 25 x edge / (SP - 1) units per bet (100-unit notional bank, no compounding)",
         "- Control: the same rule with p = calibrated SP only. ROI minus control = what the model adds",
         f"- Races dropped for an implausible SP book (outside {BOOK_OK[0]:.0%} to {BOOK_OK[1]:.0%}): "
         f"{DROPPED.get('races', 0)} (missing runners or bad SPs; they create fake overlays)",
         "- Not executable as is: SP is known only at the jump and the blend uses it. Needs the TAB fixed price at"
         " bet time to confirm", "",
         "## All rules", "", T.to_markdown(**fmt), "",
         "## Model rules vs the market-only control (flat stakes)", "",
         exc[["p from", "SP cap", "edge >", "bets", "ROI", "ROI 95%", "control ROI", "ROI - control"]].to_markdown(**fmt), "",
         "## Main rules by state and year (flat stakes)", "", pd.DataFrame(split).to_markdown(**fmt)]
    if sig:
        L += ["", "## Disagreement signals (flat stakes)", "", pd.DataFrame(sig).to_markdown(**fmt)]
    (ROOT / "reports/betting_test.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
