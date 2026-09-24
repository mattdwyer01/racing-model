"""TopRate Combo with the Racing Model's race-day adjustment in place of TopRate's speed map adjustment.

    python -W ignore tools/combo_swap_test.py        # -> reports/combo_swap_test.md

TopRate's WPR projection (wprp_proj) = base + adjustments; its `speed_map` adjustment is in wprp_contrib from
22 Aug 2026 only, so the window is 22 Aug to the last resulted day (VIC/SA/QLD).
Racing Model race-day adjustment ("race-day adj", WPR points: projected settle / width / pace cost + track
bias), out of sample from a model retrained at the start of each month (tools/race_card.score).
Variants (Combo weights 0.50 / 0.25 / 0.25 as in the dashboard, lib/raceModel.ts):
  Combo              as shipped
  Combo, no SM       speed_map removed from the projection
  Combo, our adj     speed_map replaced by our race-day adjustment (both demeaned within the race)
  Combo, our adj x2  same, also replacing TopRate's track_barrier term (our adjustment includes barrier bias)
  fitted             Combo no SM + k x our adjustment, k fitted (upper bound on what the swap can give)
Scored like tools/compare_toprate_combo.py: top pick strike, winner in top 3, log loss alone and with SP
(one-parameter logits fitted on one half of the dates, tested on the other, swapped), race bootstrap CIs.
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
import race_card  # noqa: E402
from compare_toprate_combo import combo, fit_prob  # noqa: E402

START = "2026-08-22"
BOOT = 2000
OUT = ROOT / "data/interim/combo_swap_scores.csv.gz"


def contrib(s, key):
    try:
        return json.loads(s).get(key) if isinstance(s, str) else None
    except ValueError:
        return None


def scores(con, end):
    if OUT.exists():
        return pd.read_csv(OUT)
    parts = []
    for s, e in [(START, "2026-09-01"), ("2026-09-01", str((pd.Timestamp(end) + pd.Timedelta(days=1)).date()))]:
        dates = [str(r[0]) for r in con.sql(f"select distinct race_date from races where race_date >= date '{s}' "
                                            f"and race_date < date '{e}' order by 1").fetchall()]
        train_end = "2026-08-01" if s == START else s
        c, _ = race_card.score(con, train_end, dates)
        parts.append(c[["run_id", "model %", "race-day adj"]])
        print(f"scored {s} to {e} (trained to {train_end}): {c['race_id'].nunique()} races", flush=True)
    out = pd.concat(parts, ignore_index=True)
    out.to_csv(OUT, index=False, compression="gzip")
    return out


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql(f"""select run_id, race_id, date race_date, state, finish_position fp, starting_price_sp sp,
                              wprp_proj, wprp_contrib, toprate_rating, pfm_score
                       from live_runners
                       where resulted = 1 and state in ('VIC','SA','QLD') and coalesce(scratched,0) = 0
                         and date >= date '{START}'""").df()
    end = str(live["race_date"].max())[:10]
    d = live.merge(scores(con, end), on="run_id", how="inner")
    d["sm"] = d["wprp_contrib"].map(lambda s: contrib(s, "speed_map"))
    d["tb"] = d["wprp_contrib"].map(lambda s: contrib(s, "track_barrier")).fillna(0)
    d = d[d["sp"] > 1]
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()),
                                  a=("race-day adj", lambda s: s.notna().all()), s=("sm", lambda s: s.notna().all()),
                                  p=("wprp_proj", lambda s: s.notna().all()))
    full = live.groupby("race_id").size()
    ok = ok[(ok.n >= 4) & (ok.w == 1) & ok.a & ok.s & ok.p & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d["won"] = (d["fp"] == 1).astype(int)
    g = d.groupby("race_id")
    dm = lambda c: d[c] - g[c].transform("mean")  # noqa: E731
    d["adj_z"], d["sm_z"], d["tb_z"] = dm("race-day adj"), dm("sm"), dm("tb")
    base = d["wprp_proj"] - d["sm"]
    d["c_asis"] = combo(d)
    d["c_nosm"] = combo(d.assign(wprp_proj=base))
    d["c_ours"] = combo(d.assign(wprp_proj=base + d["adj_z"]))
    d["c_ours2"] = combo(d.assign(wprp_proj=base - d["tb"] + d["adj_z"]))
    inv = 1 / d["sp"]
    d["lp_sp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    d["lp_model"] = np.log((d["model %"] / g["model %"].transform("sum")).clip(1e-9))

    probs = {"Combo (as shipped)": ["c_asis"], "Combo, no speed map": ["c_nosm"],
             "Combo, our race-day adj": ["c_ours"], "Combo, our adj (replaces SM + barrier)": ["c_ours2"],
             "Combo no SM + k x our adj (fitted)": ["c_nosm", "adj_z"], "Racing Model": ["lp_model"],
             "SP (calibrated)": ["lp_sp"]}
    P = {k: fit_prob(d, v) for k, v in probs.items()}
    for k in ["Combo (as shipped)", "Combo, our race-day adj", "Combo, our adj (replaces SM + barrier)",
              "Racing Model"]:
        P[f"{k} + SP"] = fit_prob(d, probs[k] + ["lp_sp"])
    w = d["won"] == 1
    ll = pd.DataFrame({k: -np.log(p[w].clip(1e-12)).to_numpy() for k, p in P.items()},
                      index=d.loc[w, "race_id"].to_numpy())
    rows = []
    for k, col in [("Combo (as shipped)", "c_asis"), ("Combo, no speed map", "c_nosm"),
                   ("Combo, our race-day adj", "c_ours"), ("Combo, our adj (replaces SM + barrier)", "c_ours2"),
                   ("Racing Model", "lp_model"), ("SP favourite", "lp_sp")]:
        r = g[col].rank(ascending=False, method="first")
        top = d[r == 1]
        rows.append({"pick": k, "top pick won": f"{top['won'].mean():.1%}",
                     "winner in top 3": f"{d[r <= 3].groupby('race_id')['won'].max().mean():.1%}",
                     "ROI at SP": f"{(top['won'] * top['sp']).sum() / len(top) - 1:+.1%}"})
    rng = np.random.default_rng(0)

    def ci(x):
        x = x.to_numpy()
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    pairs = [("Combo, our race-day adj", "Combo (as shipped)"),
             ("Combo, our adj (replaces SM + barrier)", "Combo (as shipped)"),
             ("Combo, no speed map", "Combo (as shipped)"),
             ("Combo no SM + k x our adj (fitted)", "Combo (as shipped)"),
             ("Combo, our race-day adj + SP", "Combo (as shipped) + SP"),
             ("Combo, our adj (replaces SM + barrier) + SP", "Combo (as shipped) + SP"),
             ("Combo, our race-day adj + SP", "SP (calibrated)"), ("Racing Model + SP", "SP (calibrated)")]
    corr = d[["sm_z", "adj_z"]].corr().iloc[0, 1]
    L = ["# TopRate Combo with the Racing Model's race-day adjustment", "",
         f"- VIC/SA/QLD races {START} to {end} (TopRate's speed_map term exists from 22 Aug 2026 only).",
         "- Our race-day adjustment out of sample (monthly retrain); both adjustments demeaned within the race.",
         f"- Races {d['race_id'].nunique()}, runners {len(d)}. Within-race sd: TopRate speed map "
         f"{d['sm_z'].std():.2f}, ours {d['adj_z'].std():.2f} WPR points; correlation {corr:.2f}.", "",
         "## Top pick", "", pd.DataFrame(rows).to_markdown(index=False), "",
         "## Log loss (lower is better)", "", ll.mean().to_frame("log loss").to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame([{"first": a, "minus": b, "diff": ci(ll[a] - ll[b])} for a, b in pairs]).to_markdown(index=False),
         ""]
    (ROOT / "reports/combo_swap_test.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
