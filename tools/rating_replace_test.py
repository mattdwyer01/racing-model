"""Which single rating should replace Combo on the dashboard? (pre-race values, 22 Aug to 3 Oct 2026, all states)

    python -W ignore tools/rating_replace_test.py      # -> reports/rating_replace_test.md

Runners and pre-race values: tools/consensus_test.load (dashboard snapshots + 08:00 wpr_nett / form factor). Candidates,
all on the WPR scale (within-race gaps are what the dashboard uses):
  Combo now        0.30 adjusted projection + 0.15 Racing Model + 0.10 TopRate rating + 0.10 form factor + 0.35 WPR Nett
  Projection       TopRate adjusted projection (dashboard Proj)
  Proj v2          projection with the fitted base (tools/value of projection_improve: 0.26 dt180 + 0.42 ewm3 + 0.32 max5
                   - 1.83 ln(1 + runs) in place of ewm7) + WPR Nett, weights fitted (2-fold by date)
  RM rating        Racing Model chance on the WPR scale, 6.843 x ln p (clear_test OOS scores to 23 Sep, then served)
  RM + Nett        RM chance with the production wpr_nett layer (0.834 log p + 0.049 x Nett vs field), on the WPR scale
Per rating: top pick win %, top-2 / top-3, line giving the same runners as Combo's 4 / 8 lines and winners inside,
A/E vs SP inside the inner line, win rule (top pick clear by the inner line, SM >= +1, no FS) bets / win % / ROI, and a
fitted-scale log loss (2-fold by date). Race bootstrap on win % differences vs Combo.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import clogit  # noqa: E402

OUT = ROOT / "reports/rating_replace_test.md"
rng = np.random.default_rng(41)
S = Path("/tmp/claude-0/-home-user-racing-model/9a9ae262-cc87-5934-9222-4ece5edef6b6/scratchpad")


def load():
    d = pd.read_pickle(S / "smd.pkl") if (S / "smd.pkl").exists() else None
    if d is None:
        import consensus_test as ct
        d = ct.load(str(ROOT.parent / "toprate"), None)
    d = d.copy()
    d["run_id"] = d["run_id"].astype(str)
    d["rm_p"] = pd.to_numeric(d["rm_p"], errors="coerce")
    d["sm"] = pd.to_numeric(d["sm"], errors="coerce")
    d["fx"] = pd.to_numeric(d["fx"], errors="coerce")
    f = pd.read_parquet(ROOT / "data/interim/base_feats.parquet" if (ROOT / "data/interim/base_feats.parquet").exists()
                        else S / "base_feats.parquet", columns=["run_id", "ewm3", "ewm7", "max5", "dt180", "n_prior"])
    f["run_id"] = f["run_id"].astype(str)
    d = d.merge(f, on="run_id", how="left")
    g = d.groupby("race_id")
    ffr = 72.57 + (d["pfm"] - 38.35) / 30.88 * 10.48
    lp = np.log((d["rm_p"] / g["rm_p"].transform("sum")).clip(1e-4))
    pm = g["proj"].transform("mean")
    d["rm"] = pm + 6.843 * (lp - lp.groupby(d["race_id"]).transform("mean"))
    wn_r = (d["wpr_nett"] - g["wpr_nett"].transform("mean")).fillna(0)
    z = 0.834 * lp + 0.049 * wn_r + 0.128 * d["wpr_nett"].isna()
    d["rm_nett"] = pm + 6.843 / 0.834 * (z - z.groupby(d["race_id"]).transform("mean"))
    parts = {"proj": d["proj"], "rm": d["rm"], "trr": d["trr"], "ff": ffr, "wn": d["wpr_nett"]}
    w = {"proj": .30, "rm": .15, "trr": .10, "ff": .10, "wn": .35}
    num = sum(w[k] * parts[k].fillna(0) for k in w)
    den = sum(w[k] * parts[k].notna() for k in w)
    d["combo"] = num / den
    nb = 0.26 * d["dt180"] + 0.42 * d["ewm3"] + 0.32 * d["max5"] - 1.83 * np.log1p(d["n_prior"])
    nb = nb - nb.groupby(d["race_id"]).transform("mean") + d.groupby("race_id")["ewm7"].transform("mean")
    d["proj_newbase"] = d["proj"] + 0.8 * (nb - d["ewm7"]).fillna(0)
    d["spr"] = g["sp"].rank(method="first")
    return d


def fitted(d, cols):
    dates = np.sort(d["date"].unique())
    half = d["date"].isin(dates[: len(dates) // 2]).to_numpy()
    out = pd.Series(np.nan, index=d.index)
    bs = []
    for m in (half, ~half):
        tr = d[m].sort_values("race_id")
        X = tr[cols].fillna(0).to_numpy(float)
        b = clogit.fit(X, pd.factorize(tr["race_id"])[0], tr["won"].to_numpy())
        bs.append(b)
        te = d[~m]
        out[te.index] = te[cols].fillna(0).to_numpy(float) @ b
    return out, np.mean(bs, axis=0)


def summary(d, score, name, ref_lines=None):
    x = d.assign(s=score.astype(float))
    g = x.groupby("race_id")["s"]
    x["gap"] = g.transform("max") - x["s"]
    x["rk"] = g.rank(ascending=False, method="first")
    nr = x["race_id"].nunique()
    top = x[x["rk"] == 1]
    wr = x[x["won"] == 1].set_index("race_id")["rk"]
    Ls = np.linspace(0.3, 25, 248)
    runners = np.array([(x["gap"] <= L).sum() / nr for L in Ls])
    if ref_lines is None:
        ref_lines = ((x["gap"] <= 4).sum() / nr, (x["gap"] <= 8).sum() / nr)
    L1, L2 = Ls[np.argmin(abs(runners - ref_lines[0]))], Ls[np.argmin(abs(runners - ref_lines[1]))]
    ins = x[x["gap"] <= L1]
    x["clear"] = g.transform(lambda s: np.sort(s.values)[-1] - np.sort(s.values)[-2] if len(s) > 1 else 0)
    W = x[(x["rk"] == 1) & (x["clear"] >= L1) & (x["sm"] >= 1) & x["no_fs"]]
    # fitted-scale log loss (one coefficient, 2-fold by date)
    z, _ = fitted(x.assign(sr=x["s"] - g.transform("mean")), ["sr"])
    e = np.exp(z - z.groupby(x["race_id"]).transform("max"))
    p = e / e.groupby(x["race_id"]).transform("sum")
    ll = -np.log(p[x["won"] == 1].clip(1e-12)).mean()
    row = {"rating": name, "top pick win %": round(100 * top["won"].mean(), 1),
           "winner in top 2 %": round(100 * (wr <= 2).mean(), 1), "winner in top 3 %": round(100 * (wr <= 3).mean(), 1),
           "top = SP fav %": round(100 * (top["spr"] == 1).mean()), "log loss": round(ll, 4),
           "inner line (Combo 4)": round(L1, 1), "winners inside %": round(100 * ins["won"].sum() / nr, 1),
           "A/E vs SP inside": round(ins["won"].sum() / ins["p_sp"].sum(), 3),
           "outer line (Combo 8)": round(L2, 1), "winners inside outer %": round(100 * x.loc[x["gap"] <= L2, "won"].sum() / nr, 1),
           "win rule bets": len(W), "win rule win %": round(100 * W["won"].mean(), 1),
           "win rule ROI SP %": round(100 * ((W["won"] * W["sp"]).mean() - 1), 1)}
    return row, top.set_index("race_id")["won"], ref_lines


def main():
    d = load()
    d = d[d.groupby("race_id")["rm_p"].transform(lambda s: s.notna().all())].copy()
    g = d.groupby("race_id")
    for c in ("proj", "proj_newbase", "wpr_nett"):
        d[c + "_r"] = (d[c] - g[c].transform("mean")).fillna(0)
    v2, b2 = fitted(d, ["proj_newbase_r", "wpr_nett_r"])
    v2b, b2b = fitted(d, ["proj_r", "wpr_nett_r"])
    # put the fitted mixes back on the WPR scale (divide by the weight on the projection)
    d["proj_v2"] = d.groupby("race_id")["proj"].transform("mean") + v2 / b2[0]
    d["proj_nett"] = d.groupby("race_id")["proj"].transform("mean") + v2b / b2b[0]
    rows, tops = [], {}
    r0, t0, ref = summary(d, d["combo"], "Combo now")
    rows.append(r0)
    tops["Combo now"] = t0
    for col, name in (("proj", "Projection (dashboard Proj)"), ("proj_newbase", "Projection, new base"),
                      ("proj_nett", "Projection + WPR Nett (fitted)"), ("proj_v2", "Proj v2: new base + WPR Nett (fitted)"),
                      ("rm", "RM rating"), ("rm_nett", "RM + WPR Nett")):
        r, t, _ = summary(d, d[col], name, ref)
        rows.append(r)
        tops[name] = t
    for r in rows:
        df = (tops[r["rating"]].reindex(t0.index) - t0).to_numpy(float)
        m = 100 * df[rng.integers(0, len(df), (2000, len(df)))].mean(1)
        r["win % vs Combo"] = f"{100 * df.mean():+.1f} ({np.percentile(m, 2.5):+.1f} to {np.percentile(m, 97.5):+.1f})"
    t = pd.DataFrame(rows)
    L = ["# Replacing Combo with one rating (pre-race dashboard values, all states)", "",
         f"- {d['race_id'].nunique():,} races {d['date'].min():%d %b} to {d['date'].max():%d %b %Y}. Lines are set to hold the same"
         " number of runners as Combo's 4 / 8, so 'winners inside' compares like with like. Log loss: each rating with one"
         " fitted scale (2-fold by date).", "",
         t.T.to_markdown(), "",
         f"- Fitted weights (logit per WPR point): Proj v2 new-base projection {b2[0]:+.3f}, WPR Nett {b2[1]:+.3f}"
         f" (Nett share {b2[1] / (b2[0] + b2[1]):.2f}); projection + Nett {b2b[0]:+.3f} / {b2b[1]:+.3f}"
         f" (Nett share {b2b[1] / (b2b[0] + b2b[1]):.2f}).", ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
