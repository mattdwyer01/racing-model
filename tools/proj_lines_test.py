"""Proj line choice (inner 2 / 2.3 / 3, outer 5 / 6) on data/interim/proj_rebuild_oos.parquet: winners inside, A/E,
exotic coverage (finish order proxied by WPR run), win rule by clear margin. python -W ignore tools/proj_lines_test.py"""
import pandas as pd, numpy as np
d = pd.read_parquet("data/interim/proj_rebuild_oos.parquet")
d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
d = d[d["sp"] > 1]
g = d.groupby("race_id")
d["q"] = (1 / d["sp"]) / g["sp"].transform(lambda s: (1 / s).sum())
d["gap"] = g["front"].transform("max") - d["front"]
d["fs"] = g["h_none"].transform("max") > 0
d["fin"] = g["y_wpr"].rank(ascending=False, method="first")   # finishing order proxy by WPR run
R = d.race_id.nunique()
def row(lab, m, e=d):
    Re = e.race_id.nunique(); x = e[m]
    return dict(set=lab, runners=round(len(x) / Re, 2), winners_pct=round(100 * x.won.sum() / Re, 1),
                AE=round(x.won.sum() / x.q.sum(), 3), ROI_SP=round(100 * ((x.won * x.sp).mean() - 1), 1))
out = []
for n in (2, 2.3, 3):
    out.append(row(f"inside {n}", d.gap <= n))
for n in (5, 6):
    out.append(row(f"inside {n}", d.gap <= n))
for a, b in ((2, 5), (2, 6), (3, 5), (3, 6)):
    out.append(row(f"between {a} and {b}", (d.gap > a) & (d.gap <= b)))
for n in (5, 6):
    out.append(row(f"outside {n}", d.gap > n))
print(f"{R:,} races 2023 to Sep 2026, walk-forward front-weighted Proj, SP\n")
print(pd.DataFrame(out).to_markdown(index=False))
# by period
print("\nWinners inside / A/E by period")
rows = []
for per, e in (("2023-24", d[d.fold <= 2024]), ("2025-26", d[d.fold >= 2025])):
    for n in (2, 3, 5, 6):
        r = row(f"{per} inside {n}", e.gap <= n, e); rows.append(r)
print(pd.DataFrame(rows).to_markdown(index=False))
# exotic hit rates (finish order by actual WPR run as proxy for 1-2-3 is wrong; use won + y_wpr rank among placed?)
# quinella box inner: top 2 by WPR run both inside; trifecta A/A/B: winner+2nd in inner, 3rd in outer
d["r"] = g["y_wpr"].rank(ascending=False, method="first")
ex = []
for a in (2, 2.3, 3):
    for b in (5, 6):
        t = d.assign(i=d.gap <= a, o=d.gap <= b)
        k = t.groupby("race_id").apply(lambda s: pd.Series({
            "nA": s.i.sum(), "nB": s.o.sum(),
            "quin": bool(s.loc[s.r <= 2, "i"].all()) and s.r.le(2).sum() == 2,
            "tri_AAB": bool(s.loc[s.r <= 2, "i"].all() and s.loc[s.r == 3, "o"].all()) and s.r.le(3).sum() == 3,
            "tri_box_B": bool(s.loc[s.r <= 3, "o"].all()) and s.r.le(3).sum() == 3}))
        ok = k[(k.nA >= 2)]
        combos = (ok.nA * (ok.nA - 1) * (ok.nB - 2).clip(lower=0)).mean()
        ex.append(dict(inner=a, outer=b, races_ok=f"{100*len(ok)/len(k):.0f}%", quin_hit=round(100 * ok.quin.mean(), 1),
                       quin_combos=round((ok.nA * (ok.nA - 1) / 2).mean(), 1), tri_AAB_hit=round(100 * ok.tri_AAB.mean(), 1),
                       tri_AAB_combos=round(combos, 1), tri_box_outer_hit=round(100 * k.tri_box_B.mean(), 1)))
print("\nExotic coverage (1-2-3 = top three WPRs run, races with a WPR for all placegetters; races with 2+ inside the inner line)")
print(pd.DataFrame(ex).to_markdown(index=False))
# win rule: top pick clear by >= n, no FS, SP >= 2
print("\nWin rule: Proj top pick n+ clear of 2nd, no first starter, SP $2+")
s = d.sort_values(["race_id", "front"], ascending=[True, False]); s["k"] = s.groupby("race_id").cumcount()
top = s[s.k == 0].set_index("race_id"); sec = s[s.k == 1].set_index("race_id"); top["clear"] = top.front - sec.front
w = []
for n in (2, 2.3, 3):
    b = top[(top.clear >= n) & ~top.fs & (top.sp >= 2)]
    for per, e in (("all", b), ("2023-24", b[b.fold <= 2024]), ("2025-26", b[b.fold >= 2025])):
        w.append(dict(clear=n, period=per, bets=len(e), win_pct=round(100 * e.won.mean(), 1), AE=round(e.won.sum() / e.q.sum(), 3),
                      ROI_SP=round(100 * ((e.won * e.sp).mean() - 1), 1)))
print(pd.DataFrame(w).to_markdown(index=False))
