"""Which TopRate Combo, rebuilt on PRE-RACE TopRate values, with the Racing Model's race-day adjustment?

    python -W ignore tools/combo_redesign_test.py      # -> reports/combo_redesign_test.md

Combo (TopRate lib/raceModel.ts compositeScore) = 0.50 x WPR projection + 0.25 x TopRate rating + 0.25 x form factor
(the last two rescaled onto the WPR scale). All TopRate inputs are taken as they stood before each race
(tools/toprate_rating_snapshots.py --start 2026-08-22 --out data/interim/toprate_prerace_aug.csv.gz), never the final stored values, which move with
the market up to and after the jump. Racing Model race-day adjustment ("race-day adj": projected settle / width /
pace cost + track bias, WPR points) is out of sample (monthly retrain, tools/combo_swap_test.py cache).
Window: 22 Aug 2026 (TopRate's speed_map term starts) to 23 Sep 2026, VIC/SA/QLD.
Variants:
  A  Combo as shipped (pre-race values)
  B  A with TopRate's speed_map + track_barrier terms replaced by our race-day adjustment (demeaned in race)
  C  B without the TopRate rating (WPR projection 2/3, form factor 1/3)
  D  B without the form factor (WPR projection 2/3, TopRate rating 1/3)
  E  our adjusted projection alone (no rating, no form factor)
  F  fitted weights on [projection without speed_map / barrier, our adjustment, TopRate rating, form factor]
  G  B + our past ground-loss credit (GPS: extra ground / width in past runs, WPR points vs field)
  H  G + our position value (expected worth of projected position and width, WPR points vs race)
  I  fitted weights on F's inputs + past ground loss + position value
GPS parts and our adjustment come from one out-of-sample scoring pass (race_card.score retrained 22 Aug and 1 Sep),
cached in data/interim/combo_gps_scores.csv.gz.
Scores turned into chances with one-parameter conditional logits, fitted on one half of the dates and tested on the
other (swapped); also each with log SP. Race bootstrap 95% ranges on paired differences vs A.
"""
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure  # noqa: E402
import compare_toprate_combo as ctc  # noqa: E402

START, END = "2026-08-22", "2026-09-23"
BOOT = 2000
GPS_CACHE = ROOT / "data/interim/combo_gps_scores.csv.gz"
KEEP = ["run_id", "model %", "race-day adj", "ground loss (past runs)", "pos value"]


def gps_scores(con):
    """Out-of-sample Racing Model parts for the window: retrained on races before 22 Aug and before 1 Sep."""
    if GPS_CACHE.exists():
        return pd.read_csv(GPS_CACHE, dtype={"run_id": str})
    import race_card
    parts = []
    for te, lo, hi in [("2026-08-22", "2026-08-22", "2026-08-31"), ("2026-09-01", "2026-09-01", END)]:
        days = [str(x.date()) for x in pd.date_range(lo, hi)]
        c, _ = race_card.score(con, te, days)
        parts.append(c[[k for k in KEEP if k in c]])
        print(te, len(c), flush=True)
    out = pd.concat(parts, ignore_index=True)
    out["run_id"] = out["run_id"].astype(str)
    out.to_csv(GPS_CACHE, index=False, compression="gzip")
    return out


def _contrib(s, key):
    try:
        v = json.loads(s).get(key) if isinstance(s, str) else None
        return float(v) if v is not None else 0.0
    except (ValueError, TypeError, AttributeError):
        return 0.0


def comb(proj, trr, pfm, w=(ctc.W_WPR, ctc.W_TRR, ctc.W_PFM)):
    t = ctc.WPR_M + (trr - ctc.TRR_M) / ctc.TRR_S * ctc.WPR_S
    f = ctc.WPR_M + (pfm - ctc.PFM_M) / ctc.PFM_S * ctc.WPR_S
    s = w[0] * proj + (w[1] * t).fillna(0) + (w[2] * f).fillna(0)
    tot = w[0] + w[1] * t.notna() + w[2] * f.notna()
    return s / tot


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql(f"""select l.run_id::varchar run_id, l.race_id, l.date race_date, l.state, l.finish_position fp,
                              l.starting_price_sp sp
                       from live_runners l
                       where l.resulted = 1 and l.state in ('VIC','SA','QLD') and coalesce(l.scratched,0) = 0
                         and l.date between date '{START}' and date '{END}'""").df()
    pre = pd.read_csv(ROOT / "data/interim/toprate_prerace_aug.csv.gz", dtype={"run_id": str})
    adj = gps_scores(con)
    d = live.merge(pre, on="run_id", how="inner").merge(adj, on="run_id", how="inner")
    d = d[(d["sp"] > 1) & d["proj_pre"].notna()]
    full = live.groupby("race_id").size()
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()))
    ok = ok[(ok.n >= 4) & (ok.w == 1) & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["won"] = (d["fp"] == 1).astype(int)
    g = d.groupby("race_id")
    inv = 1 / d["sp"]
    d["lp_sp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    sm = d["contrib_pre"].map(lambda s: _contrib(s, "speed_map"))
    tb = d["contrib_pre"].map(lambda s: _contrib(s, "track_barrier"))
    ours = d["race-day adj"].fillna(0) - g["race-day adj"].transform("mean").fillna(0)
    d["proj_base"] = d["proj_pre"] - sm - tb
    d["proj_ours"] = d["proj_base"] + ours
    d["ours"] = ours
    d["A"] = comb(d["proj_pre"], d["trr_pre"], d["pfm_pre"])
    d["B"] = comb(d["proj_ours"], d["trr_pre"], d["pfm_pre"])
    d["C"] = comb(d["proj_ours"], d["trr_pre"] * np.nan, d["pfm_pre"])
    d["D"] = comb(d["proj_ours"], d["trr_pre"], d["pfm_pre"] * np.nan)
    d["E"] = d["proj_ours"]
    for c, k in [("ground loss (past runs)", "glp"), ("pos value", "pv")]:
        v = d[c].fillna(0) if c in d else pd.Series(0.0, index=d.index)
        d[k] = v - v.groupby(d["race_id"]).transform("mean")
    d["G"] = comb(d["proj_ours"] + d["glp"], d["trr_pre"], d["pfm_pre"])
    d["H"] = comb(d["proj_ours"] + d["glp"] + d["pv"], d["trr_pre"], d["pfm_pre"])
    for c in ["trr_pre", "pfm_pre"]:
        d[c + "_f"] = d[c].fillna(g[c].transform("mean")).fillna(0)
        d[c + "_m"] = d[c].isna().astype(float)
    names = {"A": "A Combo as shipped (pre-race)", "B": "B Combo, our race-day adj",
             "C": "C B without TopRate rating", "D": "D B without form factor", "E": "E our adjusted projection alone",
             "G": "G B + past ground loss (GPS)", "H": "H G + position value"}
    V = {names[k]: [k] for k in names}
    V["F fitted weights"] = ["proj_base", "ours", "trr_pre_f", "trr_pre_m", "pfm_pre_f", "pfm_pre_m"]
    V["I fitted weights + GPS"] = V["F fitted weights"] + ["glp", "pv"]
    V["SP (calibrated)"] = ["lp_sp"]
    for k in list(names.values()) + ["F fitted weights", "I fitted weights + GPS"]:
        V[k + " + SP"] = V[k] + ["lp_sp"]
    P = {k: ctc.fit_prob(d, v) for k, v in V.items()}
    w = d["won"] == 1
    L = pd.DataFrame({k: -np.log(p[w].clip(1e-12)).to_numpy() for k, p in P.items()})
    rng = np.random.default_rng(0)

    def ci(x):
        x = np.asarray(x)
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    rows = []
    for k, p in P.items():
        top = d[p.groupby(d["race_id"]).rank(ascending=False, method="first") == 1]
        rows.append({"model": k, "log loss": L[k].mean(), "top pick won": f"{top['won'].mean():.1%}",
                     "ROI top pick at SP": f"{(top['won'] * top['sp']).mean() - 1:+.1%}"})
    base = names["A"]
    ks = list(names.values())[1:] + ["F fitted weights", "I fitted weights + GPS"]
    prs = [{"first": k, "minus": base, "diff": ci(L[k] - L[base])} for k in ks]
    prs += [{"first": k + " + SP", "minus": base + " + SP", "diff": ci(L[k + " + SP"] - L[base + " + SP"])} for k in ks]
    prs += [{"first": names["G"], "minus": names["B"], "diff": ci(L[names["G"]] - L[names["B"]])},
            {"first": names["H"], "minus": names["G"], "diff": ci(L[names["H"]] - L[names["G"]])}]
    prs += [{"first": base + " + SP", "minus": "SP (calibrated)", "diff": ci(L[base + " + SP"] - L["SP (calibrated)"])}]
    fb = ctc.clogit.fit(d[V["I fitted weights + GPS"]].to_numpy(float), pd.factorize(d["race_id"])[0], d["won"].to_numpy())
    Lines = ["# Combo redesign on pre-race TopRate values", "",
             f"- {int(w.sum()):,} VIC/SA/QLD races {START} to {END}; TopRate inputs as they stood before each race; our race-day "
             "adjustment out of sample. Within-race sd: TopRate speed map "
             f"{(sm - sm.groupby(d['race_id']).transform('mean')).std():.2f}, ours {ours.std():.2f} WPR.",
             "", "## Log loss and top pick", "", pd.DataFrame(rows).to_markdown(index=False, floatfmt=".4f"), "",
             "## Paired differences vs A (negative = better; 95% race bootstrap)", "",
             pd.DataFrame(prs).to_markdown(index=False), "",
             "Fitted weights (I, all races; per unit): " + ", ".join(f"{c} {b:+.3f}" for c, b in zip(V["I fitted weights + GPS"], fb)),
             ""]
    (ROOT / "reports/combo_redesign_test.md").write_text("\n".join(Lines) + "\n")
    print("\n".join(Lines))


if __name__ == "__main__":
    main()
