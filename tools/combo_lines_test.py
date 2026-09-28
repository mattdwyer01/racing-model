"""Where should the race page's "X from top rated" lines sit for the new Combo (2/3 WPR projection + 1/3 TopRate
rating, TopRate lib/raceModel.ts), and what are they on TopRate's rating scale?

    python -W ignore tools/combo_lines_test.py         # -> reports/combo_lines_test.md
    python -W ignore tools/combo_lines_test.py live    # -> reports/combo_lines_live.md

live: 22 Aug to 23 Sep 2026 only (the window with TopRate's pre-race speed_map terms and our out-of-sample parts,
tools/combo_redesign_test.py), comparing on the same races Combo as tested above ("TopRate proj") with Combo as the
dashboard builds it ("live": TopRate's speed_map + track_barrier taken out, our race-day adj + past ground loss put in,
TopRate rating 1/3; TopRate lib/racingModel.ts withModelAdjustments).

PRE-RACE TopRate values (tools/toprate_rating_snapshots.py; final stored values move with the market), VIC/SA/QLD
26 Apr to 23 Sep 2026, races where every runner has a pre-race projection. Gap = top Combo in the race minus the
runner's. By gap band: runners, share of all winners, win rate, A/E at SP (normalised 1 / SP) and price-matched
(vs all runners at the same SP), flat ROI at SP. Also the cumulative share of winners inside each gap.
TopRate rating scale: Combo mapped with the dashboard's own rescale constants (TRR = 96.26 + (Combo - 72.57) /
10.48 x 2.71), so a gap of g WPR is g x 0.259 TopRate rating points.
"""
import sys
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import figure  # noqa: E402
import compare_toprate_combo as ctc  # noqa: E402

K = ctc.TRR_S / ctc.WPR_S
BANDS = [0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 99]
SP_BINS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]


def tables(d):
    d = d.copy()
    d["gap"] = d.groupby("race_id")["combo"].transform("max") - d["combo"]
    inv = 1 / d["sp"]
    d["p_sp"] = inv / inv.groupby(d["race_id"]).transform("sum")
    d["p_ctl"] = d.groupby(pd.cut(d["sp"], SP_BINS), observed=True)["won"].transform("mean")
    d["band"] = pd.cut(d["gap"], BANDS, right=False)
    nw = d["won"].sum()
    t = d.groupby("band", observed=True).apply(lambda g: pd.Series({
        "runners": len(g), "per race": len(g) / d["race_id"].nunique(), "share of winners": g["won"].sum() / nw,
        "won %": 100 * g["won"].mean(), "A/E SP": g["won"].sum() / g["p_sp"].sum(),
        "A/E price-matched": g["won"].sum() / g["p_ctl"].sum(), "ROI %": 100 * ((g["won"] * g["sp"]).mean() - 1)}),
        include_groups=False)
    t.index = [f"{int(b.left)}-{int(b.right)} ({b.left * K:.1f}-{b.right * K:.1f} TR)" if b.right < 99 else
               f"{int(b.left)}+ ({b.left * K:.1f}+ TR)" for b in t.index]
    cum = pd.DataFrame({"gap within (WPR)": [2, 3, 4, 5, 6, 8, 10, 15],
                        "TopRate rating pts": [round(g * K, 1) for g in [2, 3, 4, 5, 6, 8, 10, 15]]})
    cum["runners per race inside"] = [(d["gap"] <= g).sum() / d["race_id"].nunique() for g in cum["gap within (WPR)"]]
    cum["share of winners inside"] = [d.loc[d["gap"] <= g, "won"].sum() / nw for g in cum["gap within (WPR)"]]
    cum["A/E pm inside"] = [d.loc[d["gap"] <= g, "won"].sum() / d.loc[d["gap"] <= g, "p_ctl"].sum() for g in cum["gap within (WPR)"]]
    cum["A/E pm outside"] = [d.loc[d["gap"] > g, "won"].sum() / d.loc[d["gap"] > g, "p_ctl"].sum() for g in cum["gap within (WPR)"]]
    cum["ROI % outside"] = [100 * ((d.loc[d["gap"] > g, "won"] * d.loc[d["gap"] > g, "sp"]).mean() - 1) for g in cum["gap within (WPR)"]]
    return t, cum, d["gap"]


def _contrib(s, key):
    try:
        v = json.loads(s).get(key) if isinstance(s, str) else None
        return float(v) if v is not None else 0.0
    except (ValueError, TypeError, AttributeError):
        return 0.0


def live_mode():
    import combo_redesign_test as crt
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql(f"""select l.run_id::varchar run_id, l.race_id, l.state, l.finish_position fp, l.starting_price_sp sp
                       from live_runners l where l.resulted = 1 and l.state in ('VIC','SA','QLD')
                         and coalesce(l.scratched,0) = 0 and l.date between date '{crt.START}' and date '{crt.END}'""").df()
    pre = pd.read_csv(ROOT / "data/interim/toprate_prerace_aug.csv.gz", dtype={"run_id": str})
    adj = crt.gps_scores(con)
    d = live.merge(pre.drop(columns=["race_id"], errors="ignore"), on="run_id", how="inner").merge(adj, on="run_id", how="inner")
    d = d[(d["sp"] > 1) & d["proj_pre"].notna()]
    full = live.groupby("race_id").size()
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()))
    ok = ok[(ok.n >= 4) & (ok.w == 1) & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].copy()
    d["won"] = (d["fp"] == 1).astype(int)
    trr = ctc.WPR_M + (d["trr_pre"] - ctc.TRR_M) / ctc.TRR_S * ctc.WPR_S
    comb = lambda proj: np.where(trr.notna(), (2 * proj + trr) / 3, proj)  # noqa: E731
    tp = d["contrib_pre"].map(lambda s: _contrib(s, "speed_map")) + d["contrib_pre"].map(lambda s: _contrib(s, "track_barrier"))
    ours = d["race-day adj"].fillna(0) + d["ground loss (past runs)"].fillna(0)
    ours = ours - ours.groupby(d["race_id"]).transform("mean")
    out, gaps = [], {}
    for name, proj in [("TopRate proj (as tested)", d["proj_pre"]), ("live (our adjustments)", d["proj_pre"] - tp + ours)]:
        t, cum, gaps[name] = tables(d.assign(combo=comb(proj)))
        out += [f"## {name}", "", "### By gap from the top Combo", "", t.to_markdown(floatfmt=".2f"), "",
                "### Inside / outside a line", "", cum.to_markdown(index=False, floatfmt=".2f"), ""]
    a, b = gaps.values()
    sw = {g: int(((a <= g) != (b <= g)).sum()) for g in (4, 10)}
    L = ["# Combo gap lines: as tested vs live Combo (pre-race TopRate values)", "",
         f"- {d['race_id'].nunique():,} VIC/SA/QLD races 22 Aug to 23 Sep 2026, {len(d):,} runners.",
         f"- Our adjustment sd {ours.std():.2f} WPR vs TopRate speed_map + barrier (demeaned) "
         f"{(tp - tp.groupby(d['race_id']).transform('mean')).std():.2f}; gap correlation {np.corrcoef(a, b)[0, 1]:.3f}.",
         f"- Runners changing side: 4 line {sw[4]} ({sw[4] / len(d):.1%}), 10 line {sw[10]} ({sw[10] / len(d):.1%}).", ""] + out
    (ROOT / "reports/combo_lines_live.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    live = con.sql("""select l.run_id::varchar run_id, l.race_id, l.state, l.finish_position fp, l.starting_price_sp sp
                      from live_runners l where l.resulted = 1 and l.state in ('VIC','SA','QLD')
                        and coalesce(l.scratched,0) = 0 and l.date between date '2026-04-26' and date '2026-09-23'""").df()
    pre = pd.read_csv(ROOT / "data/interim/toprate_rating_prerace.csv.gz", dtype={"run_id": str})
    d = live.merge(pre.drop(columns=["race_id"]), on="run_id", how="inner")
    d = d[d["sp"] > 1]
    full = live.groupby("race_id").size()
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()),
                                  p=("proj_pre", lambda s: s.notna().all()))
    ok = ok[(ok.n >= 4) & (ok.w == 1) & ok.p & (ok.n == full.reindex(ok.index))]
    d = d[d["race_id"].isin(ok.index)].copy()
    d["won"] = (d["fp"] == 1).astype(int)
    trr = ctc.WPR_M + (d["trr_pre"] - ctc.TRR_M) / ctc.TRR_S * ctc.WPR_S
    d["combo"] = np.where(trr.notna(), (2 * d["proj_pre"] + trr) / 3, d["proj_pre"])
    t, cum, _ = tables(d)
    L = ["# Combo gap lines (pre-race TopRate values)", "",
         f"- {d['race_id'].nunique():,} VIC/SA/QLD races 26 Apr to 23 Sep 2026, {len(d):,} runners; Combo = 2/3 WPR projection + "
         "1/3 TopRate rating (pre-race). TR = the same gap on TopRate's rating scale (x 0.259).", "",
         "## By gap from the top Combo", "", t.to_markdown(floatfmt=".2f"), "",
         "## Inside / outside a line", "", cum.to_markdown(index=False, floatfmt=".2f"), ""]
    (ROOT / "reports/combo_lines_test.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    live_mode() if sys.argv[1:] == ["live"] else main()
