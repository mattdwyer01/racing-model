"""Leave-one-group-out for the production logit: which input groups earn their place?

    python -W ignore model/group_ablation.py        # -> reports/group_ablation.md, reports/group_ablation_per_race.csv.gz

Walk-forward folds 2023 to 2026 (VIC/SA/QLD, as the baseline). Per fold: production features (om.build, production
flags: leader value, wet form), rating model fitted on the training rows, conditional logit on production.COLS + MU
(full) and on the same minus one group (production.GROUPS). Blend weights a / b fitted the production way (logit on the
first 75% of training dates predicts the last 25%, races whose SPs sum below 100% left out). Per race: model-alone and
blend log loss; paired differences vs the full model with a race bootstrap. Positive = dropping the group hurts
(the group helps); about 0 or negative = noise.
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import clogit, figure, production  # noqa: E402
from model import offset_model as om  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
OUT = ROOT / "reports/group_ablation.md"
PER_RACE = ROOT / "reports/group_ablation_per_race.csv.gz"
BOOT = 2000


def race_ll(p, df):
    w = df["won"].to_numpy() == 1
    return -np.log(np.clip(p[w], 1e-12, 1))


def fold(e, y, variants):
    tr = production._race(e[e.race_date < f"{y}-01-01"].copy())
    te = production._race(e[e.race_date.dt.year == y].copy())
    cut = tr["race_date"].quantile(0.75)
    inner = production._race(tr[tr.race_date <= cut].copy())
    bl = production._race(tr[tr.race_date > cut].copy())
    bl = production._race(bl[(1 / bl["sp"]).groupby(bl["race_id"]).transform("sum") >= 1.0].copy())
    rm_in, rm = production.fit_mu(inner), production.fit_mu(tr)
    inner, bl = production.add_mu(rm_in, inner), production.add_mu(rm_in, bl)
    tr, te = production.add_mu(rm, tr), production.add_mu(rm, te)
    out = {"SP": race_ll(te["p_sp"].to_numpy(), te)}
    wts = {}
    for name, cols in variants.items():
        b_in = production._fit_raw(inner, cols)
        p_bl = np.clip(om._softmax(production.utility(bl, b_in), bl["race"].to_numpy()), 1e-12, 1)
        a, b = clogit.fit(np.c_[np.log(p_bl), bl["log_p_sp"].to_numpy(float)], bl["race"].to_numpy(),
                          bl["won"].to_numpy())
        beta = production._fit_raw(tr, cols)
        p_te = np.clip(om._softmax(production.utility(te, beta), te["race"].to_numpy()), 1e-12, 1)
        out[f"{name}: model"] = race_ll(p_te, te)
        out[f"{name}: blend"] = race_ll(om._softmax(a * np.log(p_te) + b * te["log_p_sp"].to_numpy(),
                                                    te["race"].to_numpy()), te)
        wts[name] = a
        print(y, name, round(out[f"{name}: model"].mean(), 4), round(out[f"{name}: blend"].mean(), 4), flush=True)
    winners = te[te.won == 1][["race_id", "race_date", "state"]].reset_index(drop=True)
    return pd.concat([winners, pd.DataFrame(out)], axis=1).assign(fold=y), wts


def main():
    full = production.COLS + production.MU
    variants = {"full": full}
    import os
    if os.environ.get("ABLATE_DROP"):        # joint test: ABLATE_DROP="comments,ground loss (past runs)"
        drop = [g.strip() for g in os.environ["ABLATE_DROP"].split(",")]
        gone = set().union(*[set(production.GROUPS[g]) for g in drop])
        variants["- " + " + ".join(drop)] = [c for c in full if c not in gone]
        return run(variants, ROOT / "reports/group_ablation_joint.md", ROOT / "reports/group_ablation_joint_per_race.csv.gz")
    for g, cs in production.GROUPS.items():
        kept = [c for c in full if c not in cs]
        if len(kept) < len(full):
            variants[f"- {g}"] = kept
    return run(variants, OUT, PER_RACE)


def run(variants, out_md, per_race_file):
    full = production.COLS + production.MU
    con = duckdb.connect(str(figure.DB), read_only=True)
    res, wts = [], {}
    for y in FOLDS:
        e = om.add_context(om.build(con, f"{y}-01-01"))
        missing = [c for c in full if c not in e]
        if missing:
            print("missing inputs (filled 0):", missing, flush=True)
            for c in missing:
                e[c] = 0.0
        r, w = fold(e, y, variants)
        res.append(r)
        wts[y] = w
        del e
    d = pd.concat(res, ignore_index=True)
    d.to_csv(per_race_file, index=False, float_format="%.6f")
    rng = np.random.default_rng(0)

    def ci(x):
        x = x.to_numpy()
        m = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"
    qld = d["state"] == "QLD"
    rows = []
    for v, cols in variants.items():
        if v == "full":
            continue
        g = v[2:]
        n_in = len(full) - len(cols)
        rows.append({"dropped group": g, "inputs": n_in,
                     "model alone": ci(d[f"{v}: model"] - d["full: model"]),
                     "blend": ci(d[f"{v}: blend"] - d["full: blend"]),
                     "blend QLD": ci((d[f"{v}: blend"] - d["full: blend"])[qld]),
                     "blend VIC/SA": ci((d[f"{v}: blend"] - d["full: blend"])[~qld])})
    L = ["# Leave-one-group-out, production logit (walk-forward 2023 to 2026, VIC/SA/QLD)", "",
         f"- {len(d):,} races. Full model: model alone {d['full: model'].mean():.4f}, blend {d['full: blend'].mean():.4f},"
         f" SP {d['SP'].mean():.4f}. Differences = without the group minus full (positive = the group helps).", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "Blend weight on the model (a) per fold:", "", pd.DataFrame(wts).T.round(3).to_markdown(), ""]
    out_md.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
