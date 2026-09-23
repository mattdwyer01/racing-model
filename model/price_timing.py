"""Price-timing test: does the model add to the market at T-60, T-30, T-10 and T-2 minutes? 2026 races.

    python model/price_timing.py            # uses the store copy -> reports/price_timing.md
    python model/price_timing.py --local    # use data/interim/ without checking the store

Needs tab_price_history_from_git.csv.gz (tools/extract_prices_from_git.py) in the store.
Model: trained on races before 2026 only (market-free logit and GBM, as blend_eval.py). Blend and calibration
weights are fitted on the last 25% of that training window with SP as the market (out-of-sample model
predictions), then applied unchanged with the price at T in place of SP:
    calibrated price at T = softmax(c * log p_T);  blend = softmax(a * log p_model + b * log p_T)
Test: 2026 VIC/SA/QLD races where every runner in the final field has a price at T (last snapshot at or
before start - T; snapshots are every ~20-40 minutes, so the actual age is reported).
Main figure: blend minus calibrated price at T, 95% range from 2,000 race bootstrap resamples.
Secondary: the same with c, a, b refitted on 2026 races before 1 July (price at T), tested from 1 July.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.backtest_early import price_at  # noqa: E402
from model.blend_eval import LOGIT_X, NOMKT, _race, boot_ci  # noqa: E402
from model.validate_figure import race_ll  # noqa: E402
from pipeline import store  # noqa: E402

TS = [60, 30, 10, 2]
TEST_FROM, REFIT_SPLIT = "2026-01-01", "2026-07-01"
PRICES = ROOT / "data/interim/tab_price_history_from_git.csv.gz"


def load_prices():
    if "--local" not in sys.argv:
        if not store.get(PRICES.name, PRICES):
            sys.exit(f"{PRICES.name} is not in the store yet (use --local to run on data/interim/)")
    elif not PRICES.exists():
        sys.exit(f"{PRICES} not found")
    h = pd.read_csv(PRICES)
    h["commit_utc"] = pd.to_datetime(h["commit_utc"], utc=True)
    h["scratched"] = h["scratched"].fillna(0).astype(int)
    return h


def main():
    hist = load_prices()
    con = duckdb.connect(str(figure.DB), read_only=True)
    starts = con.sql("select race_id, start_utc from race_times where start_utc is not null").df()
    starts["start_utc"] = pd.to_datetime(starts["start_utc"], utc=True)

    e = om.add_context(om.build(con, TEST_FROM))
    tr = _race(e[e.race_date < TEST_FROM].copy())
    te0 = e[e.race_date >= TEST_FROM].copy()
    assert tr.race_date.max() < te0.race_date.min()
    cut = tr["race_date"].quantile(0.75)
    inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())
    c = clogit.fit(bl[["log_p_sp"]].to_numpy(float), bl["race"].to_numpy(), bl["won"].to_numpy())[0]
    models = {}
    for name, fit in {"logit": lambda d: om.logit_fit(d, LOGIT_X),
                      "gbm": lambda d: om.gbm_fit(d, feats=NOMKT, market=False)[0]}.items():
        p_bl = np.clip(fit(inner)(bl), 1e-12, 1)
        a, b = clogit.fit(np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)], bl["race"].to_numpy(), bl["won"].to_numpy())
        models[name] = (fit(tr), a, b)

    rng = np.random.default_rng(0)
    rows, refit_rows, cover = [], [], []
    for T in TS:
        pt = price_at(hist, starts, T)
        te = te0.join(pt[["fixed_win_price", "commit_utc", "start_utc"]].rename(columns={"fixed_win_price": "pT"}), on="run_id")
        te = te[te.groupby("race_id")["pT"].transform(lambda s: s.notna().all())].copy()
        te = _race(te.sort_values(["race_date", "race_id"]).reset_index(drop=True))
        inv = 1 / te["pT"]
        te["log_p_T"] = np.log(inv / inv.groupby(te["race_id"]).transform("sum"))
        age = (te["start_utc"] - te["commit_utc"]).dt.total_seconds() / 60
        cover.append({"T (min)": T, "races": te.race_id.nunique(), "runners": len(te),
                      "median minutes before jump": age.median(), "90th pct": age.quantile(0.9)})
        race = te["race"].to_numpy()
        ll = {"price at T raw": race_ll(np.exp(te["log_p_T"]).to_numpy(), te),
              "price at T calibrated": race_ll(om._softmax(c * te["log_p_T"].to_numpy(), race), te),
              "SP raw (same races)": race_ll(te["p_sp"].to_numpy(), te)}
        preds = {}
        for name, (f, a, b) in models.items():
            p = np.clip(f(te), 1e-12, 1)
            preds[name] = p
            ll[f"model {name}"] = race_ll(p, te)
            ll[f"blend {name} + price at T"] = race_ll(om._softmax(a * np.log(p) + b * te["log_p_T"].to_numpy(), race), te)
        for k, v in ll.items():
            rows.append({"T (min)": T, "model": k, "log loss": v.mean()})
        for name in models:
            x = ll[f"blend {name} + price at T"] - ll["price at T calibrated"]
            lo, hi = boot_ci(x, rng)
            rows.append({"T (min)": T, "model": f"DIFF blend {name} - calibrated price at T", "log loss": x.mean(),
                         "95% lo": lo, "95% hi": hi, "races": len(x)})
        # secondary: weights refitted on early-2026 prices, tested from 1 July
        e1, e2 = _race(te[te.race_date < REFIT_SPLIT].copy()), _race(te[te.race_date >= REFIT_SPLIT].copy())
        if e1.race_id.nunique() > 200 and e2.race_id.nunique() > 200:
            cT = clogit.fit(e1[["log_p_T"]].to_numpy(float), e1["race"].to_numpy(), e1["won"].to_numpy())[0]
            base = race_ll(om._softmax(cT * e2["log_p_T"].to_numpy(), e2["race"].to_numpy()), e2)
            for name, (f, _, _) in models.items():
                p1, p2 = np.clip(f(e1), 1e-12, 1), np.clip(f(e2), 1e-12, 1)
                aT, bT = clogit.fit(np.c_[np.log(p1), e1["log_p_T"].to_numpy(float)], e1["race"].to_numpy(), e1["won"].to_numpy())
                bl2 = race_ll(om._softmax(aT * np.log(p2) + bT * e2["log_p_T"].to_numpy(), e2["race"].to_numpy()), e2)
                x = bl2 - base
                lo, hi = boot_ci(x, rng)
                refit_rows.append({"T (min)": T, "model": name, "fit races (before 1 Jul)": e1.race_id.nunique(),
                                   "test races (from 1 Jul)": len(x), "c_T": cT, "a_T": aT, "b_T": bT,
                                   "blend - calibrated price at T": x.mean(), "95% lo": lo, "95% hi": hi})
        print(f"T-{T}: {te.race_id.nunique()} races", flush=True)

    L = ["# Price timing: model + market at T minutes before the jump (2026 races)", "",
         "- Model trained on races before 2026 only; blend and calibration weights fitted on training data with SP"
         f" (c = {c:.3f}; " + "; ".join(f"{k}: a = {v[1]:.3f}, b = {v[2]:.3f}" for k, v in models.items()) + ")",
         "- Price at T = last git snapshot of toprate_runners.csv at or before start - T. Snapshots are sparse, so"
         " the actual age is shown; T-2 and T-10 often use the same snapshot",
         "- Caveat: snapshot prices are what the dashboard showed, not necessarily what TAB offered at that moment",
         "- Negative DIFF = blend better than the calibrated price at T. 95% ranges: race bootstrap", "",
         "## Coverage", "", pd.DataFrame(cover).to_markdown(index=False, floatfmt=".1f"), "",
         "## Log loss", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".4f"), "",
         "## Secondary: weights refitted on 2026 prices before 1 July, tested from 1 July", "",
         pd.DataFrame(refit_rows).to_markdown(index=False, floatfmt=".4f") if refit_rows else "not enough races"]
    out = ROOT / "reports/price_timing.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
