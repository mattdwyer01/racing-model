"""Backtest the ability model against captured TAB fixed prices (fixed_prices_final, Apr 2026 on).

    python model/backtest_fixed.py      # -> reports/fixed_backtest.md

Train: every in-scope race before the first captured price (figure weights and logits).
Test:  VIC/SA/QLD races from then on where every TopRate runner has a captured fixed price.
fixed_win_price is the dashboard's last read before the result (near the jump; about SP).
The market blend is fitted on SP history and applied with the fixed price in place of SP.

Bets: back runner when p_model * price - 1 >= edge threshold; returns at the fixed price.
Flat 1 unit stakes, and quarter-Kelly on a notional 100 unit bank (stakes not compounded).
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import ability, clogit, figure  # noqa: E402
from model.validate_figure import FIG, eval_set, fit_eval, race_ll  # noqa: E402

THRESHOLDS = [0.0, 0.05, 0.10, 0.20, 0.30]
KELLY = 0.25
BOOT = 2000


def boot_roi(g, rng):
    """95% CI of ROI by resampling races."""
    by = g.groupby("race_id").agg(st=("stake", "sum"), pl=("pl", "sum"))
    if len(by) < 5:
        return np.nan, np.nan
    idx = rng.integers(0, len(by), (BOOT, len(by)))
    st, pl = by["st"].to_numpy()[idx].sum(1), by["pl"].to_numpy()[idx].sum(1)
    r = pl / st
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


def bets(te, pcol, price, rng):
    rows = []
    edge = te[pcol] * te[price] - 1
    for th in THRESHOLDS:
        for kind in ["flat", "kelly"]:
            b = te[edge >= th].copy()
            if kind == "flat":
                b["stake"] = 1.0
            else:
                b["stake"] = 100 * KELLY * (edge[edge >= th] / (b[price] - 1)).clip(lower=0)
            b["pl"] = np.where(b["won"] == 1, b["stake"] * (b[price] - 1), -b["stake"])
            lo, hi = boot_roi(b, rng) if len(b) else (np.nan, np.nan)
            rows.append({"model": pcol, "edge >=": th, "staking": kind, "bets": len(b),
                         "strike": b["won"].mean() if len(b) else np.nan,
                         "avg price": b[price].mean() if len(b) else np.nan,
                         "staked": b["stake"].sum(), "profit": b["pl"].sum(),
                         "roi": b["pl"].sum() / b["stake"].sum() if len(b) else np.nan,
                         "roi 95% lo": lo, "roi 95% hi": hi})
    return rows


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    fx = con.sql("""select run_id, fixed_win_price fx from fixed_prices_final
                    where coalesce(scratched, 0) = 0 and fixed_win_price > 1""").df()
    start = pd.Timestamp(con.sql("select min(date) from live_runners").fetchone()[0])

    d = ability.load(con)
    h = figure.history(d)
    coef = ability.fit_coef(h, start)
    a = ability.features(d, coef)
    extra = [c for c in ability.ALL if c not in ability.BASE and c != "wt_rel_today"]
    e = eval_set(h.merge(a[["run_id"] + extra], on="run_id"))
    tr = e[e.race_date < start]
    te = e[e.race_date >= start].merge(fx, on="run_id", how="left")
    full = te.groupby("race_id")["fx"].transform(lambda s: s.notna().all())
    te = te[full].sort_values(["race_date", "race_id"]).reset_index(drop=True)
    te["race"] = pd.factorize(te["race_id"])[0]
    inv = 1 / te["fx"]
    te["p_fx"] = inv / inv.groupby(te["race_id"]).transform("sum")
    te["log_p_fx"] = np.log(te["p_fx"])
    print(f"train races {tr.race_id.nunique():,}; test races {te.race_id.nunique():,} "
          f"({te.race_date.min():%d %b} to {te.race_date.max():%d %b %Y})")

    def fit_apply(cols, market_col=None):
        """Fit on train (SP as market), predict test with market_col substituted for log_p_sp."""
        mu, sd = tr[cols].mean(), tr[cols].std().replace(0, 1)
        b = clogit.fit(((tr[cols] - mu) / sd).to_numpy(float), tr["race"].to_numpy(), tr["won"].to_numpy())
        X = te[cols].copy()
        if market_col:
            X["log_p_sp"] = te[market_col]
        return clogit.probs(((X - mu) / sd).to_numpy(float), te["race"].to_numpy(), b)

    te["p_ability"] = fit_apply(ability.ALL)
    te["p_blend_fig"] = fit_apply(["log_p_sp"] + FIG, "log_p_fx")
    te["p_blend"] = fit_apply(["log_p_sp"] + ability.ALL, "log_p_fx")
    te["p_mkt_cal"] = fit_apply(["log_p_sp"], "log_p_fx")

    ll = {k: race_ll(te[p].to_numpy(), te) for k, p in
          [("fixed (raw, normalised)", "p_fx"), ("SP (raw, normalised)", "p_sp"), ("fixed (calibrated)", "p_mkt_cal"),
           ("ability only", "p_ability"), ("fixed + figure", "p_blend_fig"), ("fixed + ability", "p_blend")]}
    base = ll["fixed (calibrated)"]
    ll_rows = [{"model": k, "log loss": v.mean(), "vs fixed (cal)": (v - base).mean(),
                "se": (v - base).std() / np.sqrt(len(v))} for k, v in ll.items()]

    rng = np.random.default_rng(0)
    bt = pd.DataFrame(bets(te, "p_blend", "fx", rng) + bets(te, "p_ability", "fx", rng)
                      + bets(te, "p_blend_fig", "fx", rng))
    # by state / price band for the main strategy
    main_ = te[(te["p_blend"] * te["fx"] - 1) >= 0.05].copy()
    main_["pl"] = np.where(main_["won"] == 1, main_["fx"] - 1, -1)
    main_["band"] = pd.cut(main_["fx"], [1, 3, 6, 11, 21, 1000], labels=["<3", "3-6", "6-11", "11-21", "21+"])
    by_state = main_.groupby("state").agg(bets=("pl", "size"), profit=("pl", "sum")).assign(roi=lambda x: x.profit / x.bets)
    by_band = main_.groupby("band", observed=True).agg(bets=("pl", "size"), strike=("won", "mean"), profit=("pl", "sum")) \
        .assign(roi=lambda x: x.profit / x.bets)
    # calibration of blend vs market on test
    te["bin"] = pd.qcut(te["p_blend"], 10, duplicates="drop")
    calib = te.groupby("bin", observed=True).agg(n=("won", "size"), p_blend=("p_blend", "mean"),
                                                  p_fixed=("p_fx", "mean"), won=("won", "mean"))

    L = ["# Fixed-price backtest", "",
         f"- Test: VIC/SA/QLD races {te.race_date.min():%d %b} to {te.race_date.max():%d %b %Y} with a captured fixed "
         f"price for every runner: {te.race_id.nunique():,} races, {len(te):,} runners",
         f"- Train: in-scope races 2022 to {start:%d %b %Y} ({tr.race_id.nunique():,} races); blend fitted with SP as the market",
         f"- Fixed price = last dashboard read before the result; median fixed/SP 1.00, so this is close to a jump price",
         "- Flat = 1 unit per bet; Kelly = quarter Kelly on a 100 unit notional bank, not compounded",
         "- ROI CI: race-level bootstrap", "",
         "## Log loss on test races", "", pd.DataFrame(ll_rows).to_markdown(index=False, floatfmt=".4f"), "",
         "## Betting at the fixed price", "", bt.to_markdown(index=False, floatfmt=".3f"), "",
         "## fixed + ability, edge >= 5%, flat: by state", "", by_state.to_markdown(floatfmt=".3f"), "",
         "## fixed + ability, edge >= 5%, flat: by price band", "", by_band.to_markdown(floatfmt=".3f"), "",
         "## Calibration on test (deciles of p_blend)", "", calib.to_markdown(floatfmt=".4f")]
    out = ROOT / "reports/fixed_backtest.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
