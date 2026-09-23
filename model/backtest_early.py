"""Backtest at prices taken T minutes before the jump, from the git price history.

    python model/backtest_early.py [--prices data/interim/tab_price_history_from_git.csv.gz]
    -> reports/early_backtest.md

Prices: tools/extract_prices_from_git.py output (one row per runner per price change, stamped with
the commit time of toprate_runners.csv; snapshots every ~20 to 40 minutes on race days).
Price at T = last recorded price at or before start_utc - T (race_times.start_utc).
Field = runners not scratched at the final read; early prices are normalised over that field.

Models are trained on races before the first captured price with SP as the market (as offset_model.py)
and applied with the price at T as the market input. Bets are placed at the price at T.
CLV (closing line value) = mean log(price at T / final captured price) over bets: > 0 means the
model's bets were at better odds than the close, which is far less noisy than ROI.
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402
from model.backtest_fixed import boot_roi  # noqa: E402
from model.offset_model import add_context, build, fit_all  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402

TS = [0, 10, 30, 60, 120, 240]   # minutes before the jump (0 = last read before the start)
EDGES = [0.05, 0.10, 0.20]
PRICES = ROOT / "data/interim/tab_price_history_from_git.csv.gz"


def price_at(hist, starts, minutes):
    """Last price at or before start - minutes, per run_id."""
    h = hist.merge(starts, on="race_id")
    h = h[h["commit_utc"] <= h["start_utc"] - pd.Timedelta(minutes=minutes)]
    last = h.sort_values("commit_utc").groupby("run_id").tail(1)
    last = last[(last["scratched"] == 0) & (last["fixed_win_price"] > 1)]
    return last.set_index("run_id")[["fixed_win_price", "commit_utc", "start_utc"]]


def main(prices):
    con = duckdb.connect(str(figure.DB), read_only=True)
    hist = pd.read_csv(prices)
    hist["commit_utc"] = pd.to_datetime(hist["commit_utc"], utc=True)
    hist["scratched"] = hist["scratched"].fillna(0).astype(int)
    starts = con.sql("select race_id, start_utc from race_times where start_utc is not null").df()
    starts["start_utc"] = pd.to_datetime(starts["start_utc"], utc=True)
    final = con.sql("""select run_id, fixed_win_price fx from fixed_prices_final
                       where coalesce(scratched, 0) = 0 and fixed_win_price > 1""").df()
    start = hist["commit_utc"].min().tz_convert(None).normalize()

    e = build(con, start)
    tr = add_context(e[e.race_date < start])
    tr = tr.assign(race=pd.factorize(tr["race_id"])[0])
    fns, _, rounds = fit_all(tr)
    models = {"market": None, "logit: + ability + jt": fns["logit: SP + ability + jt"], "gbm offset": fns["gbm offset"]}
    base_te = e[e.race_date >= start].merge(final, on="run_id")
    base_te = base_te[base_te.groupby("race_id")["run_id"].transform("size")
                      == base_te.groupby("race_id")["fx"].transform("count")]

    ll_rows, bet_rows, cov_rows = [], [], []
    rng = np.random.default_rng(0)
    for T in TS:
        pt = price_at(hist, starts, T)
        te = base_te.join(pt["fixed_win_price"].rename("pT"), on="run_id")
        ok = te.groupby("race_id")["pT"].transform(lambda s: s.notna().all())
        te = te[ok].copy()
        inv = 1 / te["pT"]
        te["p_T"] = inv / inv.groupby(te["race_id"]).transform("sum")
        te["log_p_sp"] = np.log(te["p_T"])
        inv = 1 / te["fx"]
        te["p_fx"] = inv / inv.groupby(te["race_id"]).transform("sum")
        te = add_context(te).sort_values(["race_date", "race_id"]).reset_index(drop=True)
        te["race"] = pd.factorize(te["race_id"])[0]
        lag = (pt.loc[te["run_id"], "start_utc"].to_numpy() - pt.loc[te["run_id"], "commit_utc"].to_numpy())
        cov_rows.append({"T (min)": T, "races": te.race_id.nunique(), "runners": len(te),
                         "median actual minutes before jump": np.median(lag.astype("timedelta64[s]").astype(float)) / 60})
        ll_fx = race_ll(te["p_fx"].to_numpy(), te)
        ll_rows.append({"T (min)": T, "model": "final price (raw)", "log loss": ll_fx.mean(), "vs final": 0.0, "se": 0.0})
        ll = race_ll(te["p_T"].to_numpy(), te)
        ll_rows.append({"T (min)": T, "model": "price at T (raw)", "log loss": ll.mean(),
                        "vs final": (ll - ll_fx).mean(), "se": (ll - ll_fx).std() / np.sqrt(len(ll))})
        for name, f in models.items():
            if f is None:
                continue
            te["p"] = f(te)
            ll = race_ll(te["p"].to_numpy(), te)
            ll_rows.append({"T (min)": T, "model": name, "log loss": ll.mean(),
                            "vs final": (ll - ll_fx).mean(), "se": (ll - ll_fx).std() / np.sqrt(len(ll))})
            for th in EDGES:
                b = te[te["p"] * te["pT"] - 1 >= th].copy()
                b["stake"] = 1.0
                b["pl"] = np.where(b["won"] == 1, b["pT"] - 1, -1.0)
                clv = np.log(b["pT"] / b["fx"])
                lo, hi = boot_roi(b, rng) if len(b) else (np.nan, np.nan)
                bet_rows.append({"T (min)": T, "model": name, "edge >=": th, "bets": len(b),
                                 "avg price": b["pT"].mean(), "roi": b["pl"].mean() if len(b) else np.nan,
                                 "roi 95% lo": lo, "roi 95% hi": hi,
                                 "clv (mean log)": clv.mean(), "clv se": clv.std() / np.sqrt(max(len(b), 1)),
                                 "share shortened": (b["fx"] < b["pT"]).mean()})
        print(f"T={T}: {te.race_id.nunique()} races", flush=True)

    # market-wide CLV baseline: every runner at T vs final
    L = ["# Early-price backtest", "",
         f"- Prices: git history of toprate_runners.csv ({hist.run_id.nunique():,} runners, "
         f"{hist.commit_utc.min():%d %b} to {hist.commit_utc.max():%d %b %Y}); snapshots every ~20 to 40 min on race days",
         f"- Models trained on races before {start:%d %b %Y} with SP as the market (GBM rounds {rounds});"
         " at test time the price at T is the market input and the bet price",
         "- Eval: VIC/SA/QLD races where every final-field runner has a price at T and a final price",
         "- CLV = mean log(price at T / final price) over bets; > 0 = beat the close", "",
         "## Coverage", "", pd.DataFrame(cov_rows).to_markdown(index=False, floatfmt=".1f"), "",
         "## Log loss (vs final price; negative = better than the final market)", "",
         pd.DataFrame(ll_rows).to_markdown(index=False, floatfmt=".4f"), "",
         "## Betting at the price at T (flat 1 unit)", "",
         pd.DataFrame(bet_rows).to_markdown(index=False, floatfmt=".3f")]
    out = ROOT / "reports/early_backtest.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--prices", default=str(PRICES))
    main(ap.parse_args().prices)
