"""Racing Model vs TopRate's Combo (the dashboard's Cb column) on the races both cover.

    python -W ignore tools/compare_toprate_combo.py        # -> reports/compare_toprate_combo.md

Window: 26 Apr 2026 (start of the TopRate runners file) to the last resulted day, VIC/SA/QLD.
Racing Model: production model retrained at the start of each month (walk-forward; live it retrains daily,
so this slightly understates it), scores that month out of sample.
Combo (TopRate frontend lib/raceModel.ts compositeScore): 0.50 x WPR projection (wprp_proj) + 0.25 x TopRate
rating + 0.25 x form factor (pfm_score), the last two rescaled onto the WPR scale; missing parts drop out.
Also TopRate's WPR projection alone.
Metrics per race: top pick strike rate, winner in the top 3, top pick flat-stake ROI at SP, log loss.
Combo and Proj are scores, not probabilities: turned into win chances with a one-parameter conditional logit
(fitted on one half of the dates, tested on the other, swapped). Blends: each score plus log SP, same fitting.
Caveat: TopRate fields are the runners file's last values for each run (TopRate may refresh them after the
race), so TopRate's side, if anything, is flattered.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import clogit, figure  # noqa: E402
import race_card  # noqa: E402

START = "2026-04-26"
W_WPR, W_TRR, W_PFM = 0.50, 0.25, 0.25
WPR_M, WPR_S, TRR_M, TRR_S, PFM_M, PFM_S = 72.57, 10.48, 96.26, 2.71, 38.35, 30.88
BOOT = 2000
OUT = ROOT / "data/interim/compare_combo_scores.csv.gz"


def combo(d):
    s = W_WPR * d["wprp_proj"]
    w = pd.Series(W_WPR, index=d.index)
    trr = WPR_M + (d["toprate_rating"] - TRR_M) / TRR_S * WPR_S
    pfm = WPR_M + (d["pfm_score"] - PFM_M) / PFM_S * WPR_S
    s = s + (W_TRR * trr).fillna(0) + (W_PFM * pfm).fillna(0)
    w = w + W_TRR * trr.notna() + W_PFM * pfm.notna()
    return (s / w).where(d["wprp_proj"].notna())


def score_months(con, end):
    if OUT.exists():
        return pd.read_csv(OUT)
    months = pd.date_range(START, end, freq="MS").strftime("%Y-%m-%d").tolist()
    starts = [START] + [m for m in months if m > START]
    parts = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else str((pd.Timestamp(end) + pd.Timedelta(days=1)).date())
        dates = [str(r[0]) for r in con.sql(f"select distinct race_date from races where race_date >= date '{s}' "
                                            f"and race_date < date '{e}' order by 1").fetchall()]
        if not dates:
            continue
        c, _ = race_card.score(con, s, dates)
        parts.append(c[["run_id", "race_id", "model %"]])
        print(f"scored {s} to {e}: {c['race_id'].nunique()} races", flush=True)
    out = pd.concat(parts, ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, compression="gzip")
    return out


def fit_prob(d, cols):
    """Conditional logit on `cols`, fitted on one half of the dates and applied to the other (swapped)."""
    dates = np.sort(d["race_date"].unique())
    mid = dates[len(dates) // 2]
    p = pd.Series(np.nan, index=d.index)
    for fm, tm in [(d["race_date"] < mid, d["race_date"] >= mid), (d["race_date"] >= mid, d["race_date"] < mid)]:
        f, t = d[fm], d[tm]
        b = clogit.fit(f[cols].to_numpy(float), pd.factorize(f["race_id"])[0], f["won"].to_numpy())
        p[t.index] = clogit.probs(t[cols].to_numpy(float), pd.factorize(t["race_id"])[0], b)
    return p


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql("""select l.run_id, l.race_id, l.date race_date, l.state, l.finish_position fp,
                             l.starting_price_sp sp, l.wprp_proj, l.toprate_rating, l.pfm_score
                      from live_runners l
                      where l.resulted = 1 and l.state in ('VIC','SA','QLD') and coalesce(l.scratched,0) = 0
                        and l.date >= date '2026-04-26'""").df()
    end = str(live["race_date"].max())[:10]
    sc = score_months(con, end)
    d = live.merge(sc[["run_id", "model %"]], on="run_id", how="inner")
    d["combo"] = combo(d)
    d = d[d["sp"] > 1]
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()),
                                  m=("model %", lambda s: s.notna().all()), c=("combo", lambda s: s.notna().all()))
    full = live.groupby("race_id").size()
    ok = ok[(ok.n >= 4) & (ok.w == 1) & ok.m & ok.c & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["won"] = (d["fp"] == 1).astype(int)
    g = d.groupby("race_id")
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["p_model"] = d["model %"] / g["model %"].transform("sum")
    d["lp_model"], d["lp_sp"] = np.log(d["p_model"].clip(1e-9)), np.log(d["p_sp"])
    d["p_combo"] = fit_prob(d, ["combo"])
    d["p_proj"] = fit_prob(d, ["wprp_proj"])
    d["p_model_blend"] = fit_prob(d, ["lp_model", "lp_sp"])
    d["p_combo_blend"] = fit_prob(d, ["combo", "lp_sp"])
    d["p_sp_cal"] = fit_prob(d, ["lp_sp"])

    picks = {"Racing Model": "model %", "TopRate Combo": "combo", "TopRate Proj": "wprp_proj", "SP favourite": "p_sp"}
    rows, per = [], {}
    for name, col in picks.items():
        rank = g[col].rank(ascending=False, method="first")
        top = d[rank == 1]
        top3 = d[rank <= 3].groupby("race_id")["won"].max()
        per[name] = top.set_index("race_id")["won"]
        rows.append({"pick": name, "races": len(top), "top pick won": f"{top['won'].mean():.1%}",
                     "winner in top 3": f"{top3.mean():.1%}",
                     "ROI top pick at SP": f"{(top['won'] * top['sp']).sum() / len(top) - 1:+.1%}"})
    w = d[d["won"] == 1].set_index("race_id")
    ll = pd.DataFrame({k: -np.log(w[c].clip(1e-12)) for k, c in
                       [("Racing Model", "p_model"), ("TopRate Combo", "p_combo"), ("TopRate Proj", "p_proj"),
                        ("SP (calibrated)", "p_sp_cal"), ("Racing Model + SP", "p_model_blend"),
                        ("TopRate Combo + SP", "p_combo_blend")]})
    rng = np.random.default_rng(0)

    def ci(x):
        x = x.to_numpy()
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    diffs = [("Racing Model", "TopRate Combo"), ("Racing Model", "TopRate Proj"), ("TopRate Combo", "TopRate Proj"),
             ("Racing Model + SP", "TopRate Combo + SP"), ("Racing Model + SP", "SP (calibrated)"),
             ("TopRate Combo + SP", "SP (calibrated)")]
    strike = pd.DataFrame(per)
    by_state = []
    st = d.groupby("race_id")["state"].first()
    for s_name, idx in [("QLD", st[st == "QLD"].index), ("VIC/SA", st[st != "QLD"].index)]:
        by_state.append({"state": s_name, "races": len(idx),
                         **{f"{k} won": f"{strike.loc[idx, k].mean():.1%}" for k in picks},
                         "LL model - combo": f"{(ll.loc[idx, 'Racing Model'] - ll.loc[idx, 'TopRate Combo']).mean():+.4f}"})
    both = d[(g["model %"].rank(ascending=False, method="first") == 1)][["race_id", "run_id"]].merge(
        d[(g["combo"].rank(ascending=False, method="first") == 1)][["race_id", "run_id"]], on="race_id")
    same = (both["run_id_x"] == both["run_id_y"])
    L = ["# Racing Model vs TopRate Combo", "",
         f"- VIC/SA/QLD races {START} to {end} with every runner scored by both (full fields, one winner, SP known).",
         "- Racing Model retrained at the start of each month (out of sample); Combo = TopRate dashboard Cb column.",
         "- Combo / Proj turned into win chances by a one-parameter logit fitted on the other half of the dates.",
         "- Caveat: TopRate fields are the runners file's last values (may be refreshed after the race).", "",
         f"Races {len(ok)}, runners {len(d)}. Same top pick in {same.mean():.0%} of races.", "",
         "## Top pick", "", pd.DataFrame(rows).to_markdown(index=False), "",
         "## Log loss (lower is better)", "", ll.mean().to_frame("log loss").to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame([{"first": a, "minus": b, "diff": ci(ll[a] - ll[b])} for a, b in diffs]).to_markdown(index=False),
         "", "## By state", "", pd.DataFrame(by_state).to_markdown(index=False), ""]
    (ROOT / "reports/compare_toprate_combo.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
