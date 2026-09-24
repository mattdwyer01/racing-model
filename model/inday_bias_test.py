"""Does same-day track bias add anything on top of the production model?

    python -W ignore model/inday_bias_test.py        # -> reports/inday_bias_test.md

The production model's track bias uses PAST meetings only. An in-day update would add what today's earlier
races at the same meeting say about the bias. Tested on VIC/SA/QLD races 26 Apr to 11 Sep 2026 (TopRate
results with settle positions; race numbers from the runners file), on top of the production model's
out-of-sample probabilities (monthly retrain, cached by tools/compare_toprate_combo.py).

Per meeting, within-race slopes (demeaned by race, pooled over races, shrunk like projection.track_bias) of a
performance residual on a runner's position share and barrier share:
  (a) upper bound, all OTHER races that day (earlier and later), actual 800m position, WPR - prior average WPR
  (b) in-day, only races run EARLIER that day, using what is known during the day: finish margin (lengths
      behind the winner, capped at 10) as performance, the runner's pre-race average settle position as its
      position (actual in-running positions arrive only with the next results file), barrier
Features for a runner = slope x its position / barrier share vs the field. Offset logits: log p_model + terms,
fitted on one half of the dates and tested on the other (swapped); also with log SP. Race bootstrap CIs.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure  # noqa: E402
from compare_toprate_combo import OUT as SCORES, fit_prob  # noqa: E402

START, END = "2026-04-26", "2026-09-11"
LAM = 2.0          # shrinkage (in units of summed squared shares) for the per-meeting slopes
BOOT = 2000

SQL = f"""
with h as (
  select run_id, horse_id, race_date,
         avg(res_wpr) over (partition by horse_id order by race_date
                            rows between 4 preceding and 1 preceding) prior_wpr
  from runs where not is_trial_or_jumpout
)
select u.run_id, u.race_id, u.race_date, ra.track, ra.state, ra.field_size, rt.race_no, rt.start_utc,
       u.barrier, u.res_pos800, u.res_wpr, u.res_finish, u.res_margin_l, u.sp, h.prior_wpr,
       l.avg_settled_pos
from runs u join races ra using (race_id)
left join race_times rt using (race_id)
left join h using (run_id)
left join (select run_id, max(try_cast(avg_settled_pos as double)) avg_settled_pos from live_runners group by 1) l
  using (run_id)
where u.race_date between date '{START}' and date '{END}' and ra.state in ('VIC','SA','QLD')
  and not u.is_trial_or_jumpout
"""


def share(v, n):
    return (v - 1) / (n - 1).clip(lower=1)


def slopes(d, y, x, mask):
    """Per-race demeaned y, x (valid rows only) -> per-row products for pooling."""
    yy = d[y].where(mask)
    xx = d[x].where(mask & d[y].notna())
    yy = yy - yy.groupby(d["race_id"]).transform("mean")
    xx = xx - xx.groupby(d["race_id"]).transform("mean")
    return (yy * xx).fillna(0), (xx ** 2).fillna(0)


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    d = con.sql(SQL).df()
    sc = pd.read_csv(SCORES)[["run_id", "model %"]]
    d = d.merge(sc, on="run_id", how="inner")
    d = d[d["sp"] > 1]
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("res_finish", lambda s: (s == 1).sum()),
                                  m=("model %", lambda s: s.notna().all()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & ok.m])].copy()
    d = d.sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["won"] = (d["res_finish"] == 1).astype(int)
    fs = d.groupby("race_id")["run_id"].transform("size")
    d["pos_sh"] = share(d["res_pos800"], fs)
    d["bar_sh"] = share(d.groupby("race_id")["barrier"].rank(method="first"), fs)   # inside 0 .. outside 1
    d["exp_sh"] = d["avg_settled_pos"] / d["avg_settled_pos"].groupby(d["race_id"]).transform("max")
    d["res_a"] = d["res_wpr"] - d["prior_wpr"]
    d["res_b"] = -d["res_margin_l"].clip(upper=10)
    d.loc[d["res_finish"] == 1, "res_b"] = 0.0
    d["meet"] = d["track"] + "|" + d["race_date"].astype(str)
    def bias(y, x_fit, x_apply, earlier):
        """slope of residual y on position share x_fit from the meeting's other races (all, or earlier only),
        applied to the runner's x_apply vs the field."""
        xy, xx = slopes(d, y, x_fit, d[y].notna() & d[x_fit].notna())
        r = d.assign(xy=xy, xx=xx).groupby(["meet", "race_id"]).agg(
            xy=("xy", "sum"), xx=("xx", "sum"), race_no=("race_no", "first")).reset_index()
        if earlier:
            r = r.sort_values(["meet", "race_no"])
            gm = r.groupby("meet")
            r["oxy"], r["oxx"] = gm["xy"].cumsum() - r["xy"], gm["xx"].cumsum() - r["xx"]
            ok_no = r["race_no"].notna()
        else:
            gm = r.groupby("meet")
            r["oxy"], r["oxx"] = gm["xy"].transform("sum") - r["xy"], gm["xx"].transform("sum") - r["xx"]
            ok_no = pd.Series(True, index=r.index)
        r["slope"] = (r["oxy"] / (r["oxx"] + LAM)).where(ok_no, 0.0)
        sl = d["race_id"].map(r.set_index("race_id")["slope"]).fillna(0.0)
        return (sl * (d[x_apply] - d[x_apply].groupby(d["race_id"]).transform("mean"))).fillna(0.0)

    # a: upper bound (all other races, actual positions, WPR); b: live (earlier races, finish margin, expected
    # positions); c: earlier races, actual positions, WPR; d: all other races, finish margin, expected positions;
    # e: earlier races, actual positions, finish margin
    spec = {"a": ("res_a", "pos_sh", False), "b": ("res_b", "exp_sh", True), "c": ("res_a", "pos_sh", True),
            "d": ("res_b", "exp_sh", False), "e": ("res_b", "pos_sh", True)}
    feats = {}
    for k, (y, xf, early) in spec.items():
        feats[f"{k}_pos"] = bias(y, xf, "exp_sh", early)
        feats[f"{k}_bar"] = bias(y, "bar_sh", "bar_sh", early)
    for k, v in feats.items():
        d[k] = v.fillna(0.0)
    inv = 1 / d["sp"]
    d["lp_sp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    d["lp_model"] = np.log((d["model %"] / d.groupby("race_id")["model %"].transform("sum")).clip(1e-9))
    NAMES = {"a": "same-day bias, all other races, actual positions + WPR (upper bound)",
             "b": "in-day bias, earlier races, finish margin + expected positions (live now)",
             "c": "in-day bias, earlier races, actual positions + WPR",
             "d": "same-day bias, all other races, finish margin + expected positions",
             "e": "in-day bias, earlier races, actual positions + finish margin"}
    V = {"model": ["lp_model"], "model + SP": ["lp_model", "lp_sp"]}
    for k, nm in NAMES.items():
        V[f"model + {nm}"] = ["lp_model", f"{k}_pos", f"{k}_bar"]
        V[f"model + SP + {nm}"] = ["lp_model", "lp_sp", f"{k}_pos", f"{k}_bar"]
    w = d["won"] == 1
    L = pd.DataFrame({k: -np.log(fit_prob(d, v)[w].clip(1e-12)).to_numpy() for k, v in V.items()})
    rng = np.random.default_rng(0)

    def ci(x):
        x = x.to_numpy()
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    pairs = [(f"model + {nm}", "model") for nm in NAMES.values()] + \
            [(f"model + SP + {nm}", "model + SP") for nm in NAMES.values()]
    # late in the card: races with 4+ earlier races at the meeting (where an in-day update has the most to go on)
    rno = d.groupby("race_id")["race_no"].first()
    late = rno[rno >= 5].index
    Ls = L.loc[pd.Index(d.loc[w, "race_id"]).isin(late)]
    late_rows = [{"first": a, "minus": b, "diff": ci(Ls[a] - Ls[b])} for a, b in pairs
                 if "earlier races" in a]
    n_early = int((d.assign(b_bar=feats["b_bar"]).groupby("race_id")["b_bar"].apply(lambda s: (s != 0).any())).sum())
    Lines = ["# In-day track bias on top of the production model", "",
             f"- VIC/SA/QLD races {START} to {END}: {d['race_id'].nunique():,} races, {len(d):,} runners; "
             f"{n_early:,} races have an earlier race that day with a result (race order known).",
             "- (a) upper bound: all other races at the meeting, actual 800m positions and WPR residuals (not "
             "usable live: later races, and positions arrive the next day).",
             "- (b) in-day: earlier races only, finish margin, pre-race expected position, barrier (usable live).",
             "", "## Log loss", "", L.mean().to_frame("log loss").to_markdown(floatfmt=".4f"), "",
             "## Paired differences (negative = better; 95% race bootstrap)", "",
             pd.DataFrame([{"first": a, "minus": b, "diff": ci(L[a] - L[b])} for a, b in pairs]).to_markdown(index=False),
             "", f"## Race 5 onwards only ({len(Ls):,} races): in-day versions", "",
             pd.DataFrame(late_rows).to_markdown(index=False), "",
             "Reading: the same-day signal comes from LATER races (hindsight): using earlier races only adds nothing, "
             "even with perfect information (actual positions + WPR). A live in-day update cannot capture it.", ""]
    (ROOT / "reports/inday_bias_test.md").write_text("\n".join(Lines) + "\n")
    print("\n".join(Lines))


if __name__ == "__main__":
    main()
