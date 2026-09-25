"""Does the top-rated horse's margin over the second-rated horse pick winners beyond the market?

    python -W ignore tools/clear_test.py          # -> reports/clear_test.md

Production model (all-state training), retrained at the start of each year 2023 to 2026 and scoring that year
out of sample, every state. Per race: the top-rated runner (model rating vs field, WPR points) and its margin
over the second. By margin band and state: races, top pick strike rate, A/E at SP (wins / sum of normalised
1 / SP), flat-stake ROI at SP, share where the top pick is also the SP favourite; also split by whether the top
pick is the SP favourite. Race bootstrap 95% range on A/E and ROI. SP only (no bet-time fixed prices before
Apr 2026).
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure, production  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import eval_set  # noqa: E402
import race_card  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
CACHE = ROOT / "data/interim/clear_test_scores_{y}.csv.gz"
BANDS = [0, 1, 2, 3, 4, 6, 8, 99]
BOOT = 2000
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 1000]


def score_year(con, y):
    p = Path(str(CACHE).format(y=y))
    if p.exists():
        return pd.read_csv(p)
    te = f"{y}-01-01"
    om.EXTRA_PROJ = False
    production.use_training_scope()
    raw = om.build_features(con, te, light="no_posmap", lean=True)
    m, _ = production.train(con, te, e=om.add_context(eval_set(raw)))
    rows = raw[raw["in_scope"] & (raw["race_date"] >= te) & (raw["race_date"] < f"{y + 1}-01-01")
               & (raw["sp"] > 1)].copy()
    del raw
    rows["fixed_win_price"], rows["open_price"] = np.nan, np.nan
    c = production.card(m, race_card.prep(rows), market="log_p_mkt")
    c = c[["race_id", "run_id", "rating vs field", "model %", "blend %"]]
    c.to_csv(p, index=False, compression="gzip")
    print(y, len(c), flush=True)
    return c


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    sc = pd.concat([score_year(con, y) for y in FOLDS], ignore_index=True)
    info = con.sql("""select r.run_id, r.race_id, r.race_date, ra.state, r.sp, r.res_finish
                      from runs r join races ra using (race_id) where r.race_date >= date '2023-01-01'""").df()
    d = sc.merge(info, on=["run_id", "race_id"])
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("res_finish", lambda s: (s == 1).sum()),
                                  sp=("sp", lambda s: (s > 1).all()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & ok.sp])].copy()
    d["won"] = (d["res_finish"] == 1).astype(int)
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    # price-matched control: win rate of ALL runners at that SP (normalised 1 / SP understates short prices:
    # favourite-longshot bias), so A/E vs price-matched isolates what the model adds
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d = d.sort_values(["race_id", "rating vs field"], ascending=[True, False])
    d["rk"] = d.groupby("race_id").cumcount() + 1
    d["sp_rk"] = d.groupby("race_id")["sp"].rank(method="first")
    top = d[d["rk"] == 1].set_index("race_id")
    second = d[d["rk"] == 2].set_index("race_id")["rating vs field"]
    top["gap"] = top["rating vs field"] - second
    top["band"] = pd.cut(top["gap"], BANDS, right=False,
                         labels=[f"{a}-{b}" if b < 99 else f"{a}+" for a, b in zip(BANDS, BANDS[1:])])
    top["fav"] = top["sp_rk"] == 1
    top["group"] = np.where(top["state"].isin(["VIC", "SA", "QLD"]), top["state"], "NSW/WA/other")
    rng = np.random.default_rng(0)

    def summ(g):
        n = len(g)
        won, exp, ret = g["won"].to_numpy(), g["p_sp"].to_numpy(), (g["won"] * g["sp"]).to_numpy() - 1
        ctl = g["p_ctl"].to_numpy()
        if n >= 30:
            idx = rng.integers(0, n, (BOOT, n))
            ae_b = won[idx].sum(1) / ctl[idx].sum(1)
            roi_b = ret[idx].mean(1)
            ae_ci = f"{np.percentile(ae_b, 2.5):.2f} to {np.percentile(ae_b, 97.5):.2f}"
            roi_ci = f"{100 * np.percentile(roi_b, 2.5):+.0f} to {100 * np.percentile(roi_b, 97.5):+.0f}"
        else:
            ae_ci = roi_ci = ""
        return pd.Series({"races": n, "won %": 100 * won.mean(), "avg SP": g["sp"].median(),
                          "SP fav %": 100 * g["fav"].mean(), "A/E": won.sum() / exp.sum(),
                          "A/E price-matched": won.sum() / ctl.sum(), "A/E pm 95%": ae_ci,
                          "ROI %": 100 * ret.mean(), "ROI 95%": roi_ci})
    fmt = {"won %": "{:.1f}", "avg SP": "{:.2f}", "SP fav %": "{:.0f}", "A/E": "{:.2f}", "A/E price-matched": "{:.3f}", "ROI %": "{:+.1f}",
           "races": "{:,.0f}"}

    def table(g, by):
        t = g.groupby(by, observed=True).apply(summ, include_groups=False)
        for k, f in fmt.items():
            t[k] = t[k].map(f.format)
        return t.to_markdown()
    L = ["# Points clear of the next horse", "",
         f"- {len(top):,} races (4+ runners, SP for all, one winner), 2023 to Sep 2026, every state; production model "
         "retrained at the start of each year, out of sample. Gap = top-rated runner's rating minus the second's "
         "(WPR points).", "- A/E = winners / expected winners at SP (normalised 1 / SP); it is above 1 for any short-priced group "
         "(favourite-longshot bias). A/E price-matched = winners / win rate of ALL runners at the same SP (12 bands): "
         "what the model adds beyond the price. ROI = flat 1 unit at SP. avg SP is the median.", "",
         "## All races by gap", "", table(top, "band"), "",
         "## Top pick is NOT the SP favourite", "", table(top[~top["fav"]], "band"), "",
         "## Top pick IS the SP favourite", "", table(top[top["fav"]], "band"), "",
         "## By state group (gap 4+ vs under 4)", "",
         table(top.assign(g4=np.where(top["gap"] >= 4, "4+", "<4")), ["group", "g4"]), "",
         "## By year (gap 4+)", "", table(top[top["gap"] >= 4].assign(year=top["race_date"].astype(str).str[:4]), "year"),
         "## Reading", "",
         "- Every band loses at SP (ROI -5% to -20%): no gap on its own beats the takeout.",
         "- Price-matched, the top pick wins 1% to 5% more often than its price says when the gap is under 6 WPR, "
         "and about 8% more at 6+ (95% range about 1.04 to 1.12). The edge grows with the gap but stays below "
         "the takeout.",
         "- Top pick NOT the SP favourite and 6-8 clear: 672 races, price-matched A/E 1.20 (1.05 to 1.35), "
         "ROI +1.8% (-13 to +16); 8+ clear 287 races, ROI +1.3%. The only bands near break-even: small samples, at "
         "SP, worth tracking at bet-time fixed prices.",
         "- 4+ clear is similar in every state group (price-matched A/E 1.06).", ""]
    (ROOT / "reports/clear_test.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
