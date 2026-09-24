"""Disagreement test: where a factor moves the model's price a lot, is the market wrong?

    python model/disagreement.py      # -> reports/disagreement.md
    python model/disagreement.py --prod2   # base = prod2 (production + v4 settle + GPS pace + figure v2 +
                                           # rating mu) -> reports/disagreement_prod2.md

Factors (vs the production logit, model/production.py COLS):
  jockey/trainer   production without the jockey/trainer inputs vs production
  past ground loss production without h_gl / h_gl_miss / h_rail vs production
  figure v2        production vs production with every figure-dependent input from figure v2
  position map     production vs production + expected position / width value
Per fold (test year Y, trained before Y), each model gets its own out-of-sample SP blend (weights from the last 25%
of training, as blend_eval.py). Per test runner: d = log(blend with factor) - log(blend without factor).
Groups: the runners the factor pushes UP most (top 5% / 10% of d) and DOWN most (bottom 5% / 10%).
Per group: wins vs SP-implied wins (A/E SP) and vs calibrated SP (A/E cal), flat 1-unit ROI at SP, and a control ROI
(all runners with SP in the same price bands, reweighted to the group's price mix). 95% ranges: race bootstrap.
A/E > 1 in the UP group (or < 1 in the DOWN group) = the market under- (over-) rates what the factor sees.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure, jt, position_map, production  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.blend_eval import feats_for  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
BOOT = 2000
PRICE_BANDS = [1, 2, 3.5, 6, 11, 21, 51, 10000]
C = production.COLS


def _swap_fig2(cols):
    return feats_for("fig2", [c for c in cols])


FACTORS = {
    "jockey/trainer": ([c for c in C if c not in jt.COLS], C),
    "past ground loss": ([c for c in C if c not in production.GL], C),
    "figure v2": (C, _swap_fig2(C)),
    "position map": (C, C + position_map.FEATS),
}
PROD2 = "--prod2" in sys.argv
if PROD2:
    from model import blend_eval as be
    C2 = list(dict.fromkeys(be.feats_for("prod2", be.LOGIT_X) + be.MU))

    def _no(cols, drop):
        return [c for c in cols if c not in drop]
    FACTORS = {
        "jockey/trainer": (_no(C2, jt.COLS), C2),
        "past ground loss": (_no(C2, production.GL), C2),
        "figure v2": (list(dict.fromkeys(be.feats_for("prod2-fig2", be.LOGIT_X) + be.MU)), C2),
        "rating mu": (_no(C2, be.MU), C2),
        "v4 settle": (list(dict.fromkeys(be.feats_for("prod2-v4", be.LOGIT_X) + be.MU)), C2),
        "GPS pace": (_no(C2, om.GPS_PACE), C2),
        "position map": (C2, C2 + position_map.FEATS),
    }


def _add_mu(fit_rows, *frames):
    """Rating model (rating.py) fitted on fit_rows; r_mu (vs field) and r_sigma added to each frame."""
    from model import rating
    m = rating.RatingModel().fit(rating.add_fig_sd(fit_rows))
    out = []
    for f in frames:
        f2 = rating.add_fig_sd(f)
        mu = pd.Series(m.mu(f2), index=f.index)
        out.append(f.assign(r_mu=mu - mu.groupby(f["race_id"].to_numpy()).transform("mean"), r_sigma=m.sigma(f2)))
    return out


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def blend_probs(inner, bl, tr, te, cols):
    b_in = production._fit_raw(inner, cols)
    p_bl = np.clip(om._softmax(production.utility(bl, b_in), bl["race"].to_numpy()), 1e-12, 1)
    a, b = clogit.fit(np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)], bl["race"].to_numpy(), bl["won"].to_numpy())
    beta = production._fit_raw(tr, cols)
    p = np.clip(om._softmax(production.utility(te, beta), te["race"].to_numpy()), 1e-12, 1)
    return om._softmax(a * np.log(p) + b * te["log_p_sp"].to_numpy(float), te["race"].to_numpy())


CKPT = ROOT / ("data/interim/disagreement_prod2" if "--prod2" in sys.argv else "data/interim/disagreement")


def run():
    """Per fold; each fold's runner table is saved to data/interim/disagreement/ and reused on a rerun."""
    import gc
    con = duckdb.connect(str(figure.DB), read_only=True)
    CKPT.mkdir(parents=True, exist_ok=True)
    rows = []
    for y in FOLDS:
        ck = CKPT / f"fold_{y}.parquet"
        if ck.exists():
            rows.append(pd.read_parquet(ck))
            print(y, "loaded", flush=True)
            continue
        om.EXTRA_PROJ = PROD2
        e = om.add_context(om.build(con, f"{y}-01-01"))
        tr = _race(e[e.race_date < f"{y}-01-01"].copy())
        te = _race(e[e.race_date.dt.year == y].copy())
        assert tr.race_date.max() < te.race_date.min()
        cut = tr["race_date"].quantile(0.75)
        inner, bl = _race(tr[tr.race_date <= cut].copy()), _race(tr[tr.race_date > cut].copy())
        if PROD2:          # rating mu: fitted on the first 75% for the blend window, on all training rows for Y
            inner, bl = _add_mu(inner, inner, bl)
            tr, te = _add_mu(tr, tr, te)
        c = clogit.fit(bl[["log_p_sp"]].to_numpy(float), bl["race"].to_numpy(), bl["won"].to_numpy())[0]
        out = te[["race_id", "run_id", "state", "sp", "p_sp", "won"]].copy()
        out["p_cal"] = om._softmax(c * te["log_p_sp"].to_numpy(float), te["race"].to_numpy())
        cache = {}
        for name, (without, with_) in FACTORS.items():
            for cols in (without, with_):
                key = tuple(cols)
                if key not in cache:
                    cache[key] = blend_probs(inner, bl, tr, te, list(cols))
            out[f"d {name}"] = np.log(cache[tuple(with_)]) - np.log(cache[tuple(without)])
            out[f"p {name}"] = cache[tuple(with_)]
        out = out.assign(fold=y)
        out.to_parquet(ck)
        rows.append(out)
        del e, tr, te, inner, bl, cache
        gc.collect()
        print(y, "done", flush=True)
    return pd.concat(rows, ignore_index=True)


def group_stats(g, ctrl_roi, rng):
    races = g["race_id"].to_numpy()
    uniq, inv = np.unique(races, return_inverse=True)
    w = pd.DataFrame({"inv": inv, "won": g["won"], "p_sp": g["p_sp"], "p_cal": g["p_cal"],
                      "ret": g["won"] * g["sp"] - 1, "ctrl": g["ctrl_roi"]}).groupby("inv").sum()
    idx = rng.integers(0, len(w), (BOOT, len(w)))
    W = w.to_numpy()[idx].sum(1)                                   # (BOOT, cols)
    cols = list(w.columns)
    ae_sp = W[:, cols.index("won")] / W[:, cols.index("p_sp")]
    ae_cal = W[:, cols.index("won")] / W[:, cols.index("p_cal")]
    n = len(g)
    roi = W[:, cols.index("ret")] / n
    excess = roi - W[:, cols.index("ctrl")] / n
    tot = w.sum()
    return {"runners": n, "avg SP": g["sp"].mean(), "wins": int(tot["won"]),
            "A/E SP": tot["won"] / tot["p_sp"], "A/E SP 95%": f"{np.percentile(ae_sp, 2.5):.2f} to {np.percentile(ae_sp, 97.5):.2f}",
            "A/E cal": tot["won"] / tot["p_cal"], "A/E cal 95%": f"{np.percentile(ae_cal, 2.5):.2f} to {np.percentile(ae_cal, 97.5):.2f}",
            "ROI at SP": tot["ret"] / n, "control ROI": tot["ctrl"] / n,
            "ROI - control 95%": f"{np.percentile(excess, 2.5):+.3f} to {np.percentile(excess, 97.5):+.3f}"}


def main():
    d = run()
    suffix = "_prod2" if PROD2 else ""
    d.to_csv(ROOT / f"reports/disagreement_per_runner{suffix}.csv.gz", index=False, float_format="%.6f")
    rng = np.random.default_rng(0)
    d["band"] = pd.cut(d["sp"], PRICE_BANDS)
    band_roi = (d["won"] * d["sp"] - 1).groupby(d["band"], observed=False).mean()
    d["ctrl_roi"] = d["band"].map(band_roi).astype(float)
    rows = []
    for name in FACTORS:
        x = d[f"d {name}"]
        for side, q in [("UP top 5%", 0.95), ("UP top 10%", 0.90), ("DOWN bottom 10%", 0.10), ("DOWN bottom 5%", 0.05)]:
            thr = x.quantile(q)
            m = x >= thr if side.startswith("UP") else x <= thr
            for st, sm in [("all", pd.Series(True, index=d.index)), ("QLD", d["state"] == "QLD"),
                           ("VIC/SA", d["state"] != "QLD")]:
                g = d[m & sm]
                if len(g) < 200:
                    continue
                rows.append({"factor": name, "group": side, "races": st,
                             "shift (median d)": float(np.median(x[m & sm])), **group_stats(g, None, rng)})
    t = pd.DataFrame(rows)
    L = ["# Disagreement test" + (" (base model: prod2)" if PROD2 else ""), "",
         "- Per factor: runners whose out-of-sample blended probability moves most when the factor is added (d = log p_with"
         " - log p_without), 2023 to 2026 test years, VIC/SA/QLD",
         "- A/E SP = wins / SP-implied wins; A/E cal = wins / calibrated-SP wins (removes the favourite-longshot bias)",
         "- ROI at SP: flat 1 unit on every runner in the group; control ROI: all runners at the same SP price bands"
         " (reweighted to the group's price mix). Positive ROI minus control = the factor finds value the market misses",
         "- 95% ranges: race bootstrap (2,000)", "",
         t.to_markdown(index=False, floatfmt=".3f")]
    out = ROOT / f"reports/disagreement{suffix}.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
