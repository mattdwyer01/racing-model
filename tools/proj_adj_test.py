"""Proj (front-weighted WPR model) input review: does every input group earn its place, and do new inputs help?

    python -W ignore tools/proj_adj_test.py            # walk-forward 2023 to 2026 -> reports/proj_adj_test.md
    python -W ignore tools/proj_adj_test.py --report   # rebuild the report from data/interim/proj_adj_oos.parquet

Per fold Y (fit on races before Y, score Y; VIC/SA/QLD): the live Proj recipe (model/wpr_model.py: LightGBM on the run's
WPR, production inputs + rating mu + race context, front weights). Variants:
  full          as live
  - <group>     leave one input group out (production.GROUPS, plus 'race context' = wpr_model.CTX minus mu_abs)
  + excuses     last-start stewards / video flags (wide, held up, laid / hung, vet, 'every chance', overraced),
                GPS extra ground, L600 rank, sire wet / staying index, jockey 365-day strike rate, apprentice
                (claimed in the last 120 days) - model/value_live.facts
  + class       class level, class change vs last start, carried weight change vs last start, handicap race,
                metro / provincial / country, field size
  + both
Scored on the test years: winners inside the line holding 3.03 / 4.62 runners a race (the dashboard's 3 / 5 lines),
top pick win %, WPR error (MAE, runners with prior form); race bootstrap of the winners-inside-3 difference vs full.
"""
import sys
from pathlib import Path

import duckdb
import lightgbm as lgb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, production, value_live, wpr_model as wm  # noqa: E402
from model import offset_model as om  # noqa: E402

OUT = ROOT / "reports/proj_adj_test.md"
OOS = ROOT / "data/interim/proj_adj_oos.parquet"
COUNTS = (3.03, 4.62)
BOOT = 1000
CTX_GROUP = [c for c in wm.CTX if c != "mu_abs"]


def extras(con):
    f = value_live.facts(con, "2021-06-01")
    x = f[["run_id"]].copy()
    for c in f:
        if c.startswith("last_") and c != "last_distance" and pd.api.types.is_numeric_dtype(f[c]):
            x["ex_" + c] = f[c].astype(float)
    for c in ("sire_wet_idx", "sire_stay_idx", "jockey_sr", "appr"):
        x["ex_" + c] = f[c].astype(float)
    x["run_id"] = x["run_id"].astype(str)
    r = con.sql("""select cast(u.run_id as varchar) run_id, u.horse_id, u.race_date, u.weight_kg, u.res_finish,
                          r.class_level, r.field_size, r.weight_type, r.location_class
                   from runs u join races r using (race_id)
                   where u.race_date >= date '2018-01-01' and not coalesce(u.is_trial_or_jumpout, false)""").df()
    r = r.sort_values(["horse_id", "race_date"])
    upcoming = r["res_finish"].isna() & (r["race_date"] >= pd.Timestamp.today().normalize())
    for c in ("class_level", "weight_kg"):
        prev = r[c].where(~upcoming).groupby(r["horse_id"]).transform(lambda s: s.shift(1).ffill())
        r["cl_d_" + c] = r[c] - prev
    r["cl_class"] = r["class_level"]
    r["cl_field"] = r["field_size"]
    r["cl_hcp"] = r["weight_type"].astype(str).str.lower().str.startswith("h").astype(float)
    r["cl_loc"] = r["location_class"].map({"M": 2.0, "P": 1.0, "C": 0.0})
    cl = r[["run_id", "cl_d_class_level", "cl_d_weight_kg", "cl_class", "cl_field", "cl_hcp", "cl_loc"]]
    return x.merge(cl, on="run_id", how="outer")


def fit_pred(tr, te, feats):
    lab = tr["y_wpr"].notna()
    w = wm.front_weights(tr[lab])
    m = lgb.train(wm.PARAMS, lgb.Dataset(tr.loc[lab, feats].astype(float), tr.loc[lab, "y_wpr"], weight=w), 600)
    return m.predict(te[feats].astype(float))


def fold(con, y, ex):
    e = om.add_context(om.build(con, f"{y}-01-01"))
    cols = [c for c in production.COLS + production.MU if c in e or c in ("r_mu", "r_sigma")]
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    rm = production.fit_mu(tr)
    tr, te = wm.add_mu_abs(rm, tr), wm.add_mu_abs(rm, te)
    tr["run_id"], te["run_id"] = tr["run_id"].astype(str), te["run_id"].astype(str)
    tr, te = tr.merge(ex, on="run_id", how="left"), te.merge(ex, on="run_id", how="left")
    full = [c for c in dict.fromkeys(cols + wm.CTX) if c in tr]
    exc = [c for c in ex if c.startswith("ex_")]
    cls = [c for c in ex if c.startswith("cl_")]
    variants = {"full": full}
    groups = dict(production.GROUPS, **{"race context": CTX_GROUP})
    for g, gc in groups.items():
        if any(c in full for c in gc):
            variants[f"- {g}"] = [c for c in full if c not in gc]
    variants["+ excuses"] = full + exc
    variants["+ class"] = full + cls
    variants["+ both"] = full + exc + cls
    keep = te[["run_id", "race_id", "race_date", "state", "won", "sp", "y_wpr", "h_none"]].copy()
    for k, f in variants.items():
        keep[k] = fit_pred(tr, te, f)
        print(y, k, flush=True)
    return keep.assign(fold=y)


def inside(d, col, target):
    gap = d.groupby("race_id")[col].transform("max") - d[col]
    R = d["race_id"].nunique()
    ls = np.arange(0, 20.01, 0.05)
    cnt = np.array([(gap <= n).sum() / R for n in ls])
    n = ls[int(np.argmin(np.abs(cnt - target)))]
    per_race = (d["won"] * (gap <= n)).groupby(d["race_id"]).sum()
    return n, per_race


def report(d):
    d = d[d.groupby("race_id")["won"].transform("sum") == 1].copy()
    vs = [c for c in d.columns if c == "full" or c.startswith("- ") or c.startswith("+ ")]
    hw = d[(d["h_none"] == 0) & d["y_wpr"].notna()]
    base3 = inside(d, "full", COUNTS[0])[1]
    rng = np.random.default_rng(1)
    idx = rng.integers(0, len(base3), (BOOT, len(base3)))
    rows = []
    for v in vs:
        r = {"variant": v}
        n3, w3 = inside(d, v, COUNTS[0])
        n5, w5 = inside(d, v, COUNTS[1])
        r["winners inside 3 %"] = round(100 * w3.mean(), 2)
        diff = (w3 - base3.reindex(w3.index)).to_numpy()
        bs = diff[idx].mean(1)
        r["vs full (pts)"] = f"{100 * diff.mean():+.2f} ({100 * np.quantile(bs, 0.025):+.2f} to {100 * np.quantile(bs, 0.975):+.2f})"
        r["winners inside 5 %"] = round(100 * w5.mean(), 2)
        top = d.loc[d.groupby("race_id")[v].idxmax()]
        r["top pick %"] = round(100 * top["won"].mean(), 2)
        r["MAE"] = round((hw[v] - hw["y_wpr"]).abs().mean(), 3)
        rows.append(r)
    t = pd.DataFrame(rows)
    yr = []
    for y, e in d.groupby("fold"):
        r = {"fold": y}
        for v in vs:
            r[v] = round(100 * inside(e, v, COUNTS[0])[1].mean(), 1)
        yr.append(r)
    L = ["# Proj input review (walk-forward 2023 to Sep 2026, VIC/SA/QLD, front-weighted WPR model)", "",
         f"- {d['race_id'].nunique():,} races. Lines set per variant to hold the dashboard's runner counts (3.03 / 4.62 a",
         "  race for the 3 / 5 lines). 'vs full' = winners inside 3 per 100 races vs the live recipe (95% race bootstrap):",
         "  negative for a '- group' row means the group HELPS. MAE = WPR error, runners with prior form.", "",
         t.to_markdown(index=False), "", "## Winners inside 3, by year (%)", "",
         pd.DataFrame(yr).set_index("fold").T.to_markdown(), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    if "--report" in sys.argv:
        return report(pd.read_parquet(OOS))
    con = duckdb.connect(str(figure.DB), read_only=True)
    ex = extras(con)
    d = pd.concat([fold(con, y, ex) for y in wm.FOLDS], ignore_index=True)
    d.to_parquet(OOS)
    report(d)


if __name__ == "__main__":
    main()
