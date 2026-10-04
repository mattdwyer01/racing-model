"""Value models: fitted on what the market gets WRONG, judged on edge and ROI in years they never saw.

    python -W ignore tools/value_model.py        # -> reports/value_model.md

Both models are conditional logits per race with log SP as an input (so the price is the starting point and the other
inputs only move a runner where the market is wrong). Walk-forward: fit on all years before Y, score Y (2024, 2025,
2026 to Sep). VIC/SA/QLD, runners from tools/filter_screen2 (walk-forward Racing Model scores, race-day adj, flags).
  SP only        log SP (calibration only; the bar to beat)
  RM value       log SP + Racing Model chance + flags + negatives + price interactions
  Proj value     log SP + projection-style inputs (prior WPR vs field, race-day adj, track bias) + flags + negatives +
                 price interactions; no Racing Model
  RM blend       log SP + Racing Model chance (today's production blend, for reference)
Race-level conditions (field 13+, wet, state) cannot move a runner within a race on their own, so they enter as
interactions with log SP (do longshots beat their price more in big fields, wet tracks, QLD ...).
Betting: back every runner whose value = model chance x SP is above a cut (and SP <= $21); flat 1 unit at SP.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from model import clogit  # noqa: E402

OUT = ROOT / "reports/value_model.md"
CACHE = ROOT / "data/interim/value_feats.parquet"
rng = np.random.default_rng(29)


def build():
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    import filter_screen as fsc
    d = pd.read_parquet(ROOT / "data/interim/filter_screen2_runs.parquet")
    f = fsc.facts()
    d = d.merge(f.drop(columns=["race_date", "won_all", "prep_run", "days_since_start"]), on="run_id", how="left")
    b = lambda c: d[c].astype("boolean").fillna(False).astype(float)  # noqa: E731
    q = lambda s, p: s >= s.quantile(p)  # noqa: E731
    F = {
        "f_barrier10": d["barrier"] >= 10, "f_dist_down": d["distance"] <= d["last_distance"] - 200,
        "f_dist_up": d["distance"] >= d["last_distance"] + 200, "f_back14": d["days_since_start"] <= 14,
        "f_4thup": d["prep_run"] >= 4, "f_age6": d["age"] >= 6, "f_weak_jockey": (d["jockey_sr"] < 0.07) & (d["jockey_n"] >= 50),
        "f_sm": q(d["sm"], 0.82), "f_bias": q(d["bias_adj"], 0.8),
        "f_wide": b("last_cs_raced wide / without cover"), "f_gps_ground": q(d["last_gps_rel"], 0.8),
        "f_heldup": b("last_cs_held up / checked / hampered"), "f_laid": b("last_cs_laid / hung / shifted"),
        "f_vet": b("last_cs_vet issue (lame, bled, heart)"), "f_l600_worst": d["last_l600_rel"] <= d["last_l600_rel"].quantile(0.2),
        "f_wet_poor_sire": (d["going_num"] >= 7) & (d["sire_wet_idx"] <= 0.8),
        "n_top_jockey": (d["jockey_sr"] >= 0.18) & (d["jockey_n"] >= 50), "n_apprentice": d["weight_claim_kg"] > 0,
        "n_every_chance": b("last_cs_video: every chance"), "n_stay_poor_sire": (d["dist"] >= 1600) & (d["sire_stay_idx"] <= 0.8),
    }
    for k, v in F.items():
        d[k] = pd.Series(v, index=d.index).fillna(False).astype(float)
    g = d.groupby("race_id")
    inv = 1 / d["sp"]
    d["lsp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    d["lrm"] = np.log((d["model %"] / g["model %"].transform("sum")).clip(1e-5))
    d["wpr_r"] = (d["h_wpr"] - g["h_wpr"].transform("mean")).fillna(0)
    d["adj_r"] = d["sm"].fillna(0)
    d["bias_r"] = (d["bias_adj"] - g["bias_adj"].transform("mean")).fillna(0)
    d["debut"] = d["h_none"].fillna(0).astype(float)
    for c, m in (("field13", d["n"] >= 13), ("wet", d["going_num"].fillna(4) >= 7), ("qld", d["state"] == "QLD"),
                 ("fs_race", d["fs_race"]), ("sprint", d["dist"] < 1200)):
        d["lsp_x_" + c] = d["lsp"] * m.astype(float)
    keep = ["run_id", "race_id", "race_date", "year", "state", "sp", "won", "p_ctl", "gap", "rk", "fs_race", "lsp", "lrm",
            "wpr_r", "adj_r", "bias_r", "debut"] + list(F) + [c for c in d if c.startswith("lsp_x_")]
    d = d[keep].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    d.to_parquet(CACHE)
    return d


FLAGS = ["f_barrier10", "f_dist_down", "f_dist_up", "f_back14", "f_4thup", "f_age6", "f_weak_jockey", "f_sm", "f_bias",
         "f_wide", "f_gps_ground", "f_heldup", "f_laid", "f_vet", "f_l600_worst", "f_wet_poor_sire",
         "n_top_jockey", "n_apprentice", "n_every_chance", "n_stay_poor_sire"]
INTER = ["lsp_x_field13", "lsp_x_wet", "lsp_x_qld", "lsp_x_fs_race", "lsp_x_sprint"]
MODELS = {"SP only": ["lsp"],
          "RM blend (production style)": ["lsp", "lrm"],
          "RM value": ["lsp", "lrm"] + FLAGS + INTER,
          "Proj value": ["lsp", "wpr_r", "adj_r", "bias_r", "debut"] + FLAGS + INTER}


def walk(d, cols, l2=1e-3):
    p = pd.Series(np.nan, index=d.index)
    betas = {}
    for y in (2024, 2025, 2026):
        tr, te = d[d["year"] < y], d[d["year"] == y]
        b = clogit.fit(tr[cols].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy(), l2=l2)
        p[te.index] = clogit.probs(te[cols].to_numpy(float), pd.factorize(te["race_id"])[0], b)
        betas[y] = b
    return p, betas


def ci_mean(x):
    m = x[rng.integers(0, len(x), (2000, len(x)))].mean(1)
    return f"{x.mean():+.4f} ({np.percentile(m, 2.5):+.4f} to {np.percentile(m, 97.5):+.4f})"


def roi_ci(b):
    r = (b["won"] * b["sp"]).to_numpy()
    if len(r) < 30:
        return ""
    m = r[rng.integers(0, len(r), (2000, len(r)))].mean(1)
    return f"{100 * (np.percentile(m, 2.5) - 1):+.0f} to {100 * (np.percentile(m, 97.5) - 1):+.0f}"


def main():
    d = build()
    te = d["year"] >= 2024
    P, B = {}, {}
    for name, cols in MODELS.items():
        P[name], B[name] = walk(d, cols)
        print(name, "done", flush=True)
    w = d["won"] == 1
    ll = {k: pd.Series(-np.log(P[k][w & te].clip(1e-12)).to_numpy(), index=d.loc[w & te, "race_id"]) for k in P}
    L = ["# Value models fitted on the market's errors (walk-forward, VIC/SA/QLD, test 2024 to Sep 2026, SP)", "",
         f"- {d.loc[te, 'race_id'].nunique():,} test races (fits on all earlier years; 2023 is training only).", "",
         "## Accuracy against SP (log loss per race; negative = better than calibrated SP)", "",
         "| model | log loss | vs SP only (95%) | QLD | VIC / SA |", "|---|---|---|---|---|"]
    qld = d.loc[w & te, "state"].to_numpy() == "QLD"
    for k in P:
        x = (ll[k] - ll["SP only"]).to_numpy()
        L.append(f"| {k} | {ll[k].mean():.4f} | {ci_mean(x) if k != 'SP only' else ''} | {x[qld].mean():+.4f} | {x[~qld].mean():+.4f} |")
    L += ["", "## Betting on value (model chance x SP above the cut, SP <= $21, flat at SP)", ""]
    rows = []
    for k in ("RM blend (production style)", "RM value", "Proj value"):
        v = P[k] * d["sp"]
        for cut in (1.0, 1.05, 1.1, 1.2, 1.3):
            for pool, pm in (("all", np.ones(len(d), bool)), ("within 4, no FS", ((d["gap"] <= 4) & ~d["fs_race"]).to_numpy())):
                m = te.to_numpy() & (v >= cut).to_numpy() & (d["sp"] <= 21).to_numpy() & pm
                b = d[m]
                if len(b) < 50:
                    continue
                yrs = {f"ROI {y} %": round(100 * ((t["won"] * t["sp"]).mean() - 1), 1) for y, t in b.groupby("year")}
                rows.append({"model": k, "value cut": cut, "pool": pool, "bets": len(b),
                             "per week": round(7 * len(b) / (d.loc[te, "race_date"].max() - d.loc[te, "race_date"].min()).days, 1),
                             "median SP": b["sp"].median(), "A/E pm": round(b["won"].sum() / b["p_ctl"].sum(), 3),
                             "ROI %": round(100 * ((b["won"] * b["sp"]).mean() - 1), 1), "95%": roi_ci(b), **yrs})
    L += [pd.DataFrame(rows).to_markdown(index=False), "", "## Fitted weights (2026 fit: all of 2023-2025)", ""]
    for k in ("RM value", "Proj value"):
        L += [f"**{k}**: " + ", ".join(f"{c} {x:+.3f}" for c, x in zip(MODELS[k], B[k][2026])), ""]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    pd.DataFrame({"run_id": d["run_id"], **{k: P[k] for k in P}}).to_parquet(ROOT / "data/interim/value_model_scores.parquet")




def fit_live():
    """Refit the Proj value model through model/value_live.py (the code path the dashboard uses), check it walk-forward,
    and write model/value_params.json (fit on every resulted race to date)."""
    import json
    import duckdb
    from model import value_live as vl
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    p = pd.read_parquet(ROOT / "data/interim/pace_leader_oos.parquet")
    p["run_id"] = p["run_id"].astype(str)
    p = p[(p["race_date"] < "2026-10-01") & p["won"].notna() & (p["sp"] > 1)].copy()
    p["won"] = p["won"].astype(int)
    ok = p.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ovr=("sp", lambda s: (1 / s).sum()))
    p = p[p["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & (ok.ovr >= 1.08) & (ok.ovr <= 1.6)])]
    f = vl.facts(con, "2023-01-01")
    x = p.drop(columns=["state", "going_num"]).merge(f, on="run_id", how="left")
    x["dist"] = x["dist"].fillna(x["distance"])
    inv = 1 / x["sp"]
    x["lsp"] = np.log(inv / inv.groupby(x["race_id"]).transform("sum"))
    adj = x["proj_adj"].fillna(0) + x["bias_adj"].fillna(0)
    adj_r = adj - adj.groupby(x["race_id"]).transform("mean")
    thr = {"sm": float(adj_r.quantile(0.82)), "bias": float(x["bias_adj"].quantile(0.8)),
           "gps": float(x["last_gps_rel"].quantile(0.8)), "l600": float(x["last_l600_rel"].quantile(0.2))}
    x = vl.design(x, thr).sort_values(["race_id", "run_id"]).reset_index(drop=True)
    x["year"] = pd.to_datetime(x["race_date"]).dt.year
    x["p_ctl"] = x.groupby(pd.cut(x["sp"], [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]), observed=True)["won"].transform("mean")
    pr, _ = walk(x, vl.COLS)
    sp_only, _ = walk(x, ["lsp"])
    te = x["year"] >= 2024
    w = (x["won"] == 1) & te
    dll = (-np.log(pr[w].clip(1e-12)) + np.log(sp_only[w].clip(1e-12))).to_numpy()
    v = pr * x["sp"]
    L = [f"## Live pipeline check (model/value_live.py, apprentice = claimed in the last 120 days)", "",
         f"- Walk-forward log loss vs SP only: {ci_mean(dll)}.", "",
         "| value cut | bets | A/E pm | ROI % | 95% | 2024 | 2025 | 2026 |", "|---|---|---|---|---|---|---|---|"]
    for cut in (1.0, 1.05):
        b = x[te & (v >= cut) & (x["sp"] <= 21)]
        yrs = [f"{100 * ((t['won'] * t['sp']).mean() - 1):+.1f}" for _, t in b.groupby("year")]
        L.append(f"| {cut} | {len(b)} | {b['won'].sum() / b['p_ctl'].sum():.3f} | {100 * ((b['won'] * b['sp']).mean() - 1):+.1f} |"
                 f" {roi_ci(b)} | " + " | ".join(yrs) + " |")
    beta = clogit.fit(x[vl.COLS].to_numpy(float), pd.factorize(x["race_id"])[0], x["won"].to_numpy(), l2=1e-3)
    params = {"fitted": str(pd.Timestamp.now())[:10], "train_from": "2023-01-01", "train_to": str(x["race_date"].max())[:10],
              "races": int(x["race_id"].nunique()), "thresholds": thr, "beta": dict(zip(vl.COLS, map(float, beta)))}
    vl.PARAMS.write_text(json.dumps(params, indent=1))
    L += ["", "Final fit (all races): " + ", ".join(f"{c} {b:+.3f}" for c, b in zip(vl.COLS, beta)), "",
          "Thresholds: " + ", ".join(f"{k} {v:.3f}" for k, v in thr.items()), ""]
    with OUT.open("a") as fh:
        fh.write("\n" + "\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    if "--fit-live" in sys.argv:
        fit_live()
    elif "--five-states" in sys.argv:
        five_states()
    else:
        main()


def five_states():
    """Value model walk-forward on VIC/SA/QLD + NSW/WA (tools/pace_leader_extra.py), through model/value_live.py.
    Fits: (a) VIC/SA/QLD only, scored everywhere; (b) all five states. ROI at value >= 1.0 (SP <= $51) by state."""
    import json
    import duckdb
    from model import value_live as vl
    con = duckdb.connect(str(ROOT / "data/db/racing.duckdb"), read_only=True)
    p = pd.concat([pd.read_parquet(ROOT / "data/interim/pace_leader_oos.parquet"),
                   pd.read_parquet(ROOT / "data/interim/pace_leader_oos_nswwa.parquet")], ignore_index=True)
    p["run_id"] = p["run_id"].astype(str)
    p = p[(p["race_date"] < "2026-10-01") & p["won"].notna() & (p["sp"] > 1)].drop_duplicates("run_id").copy()
    p["won"] = p["won"].astype(int)
    ok = p.groupby("race_id").agg(n=("run_id", "size"), w=("won", "sum"), ovr=("sp", lambda s: (1 / s).sum()))
    p = p[p["race_id"].isin(ok.index[(ok.n >= 4) & (ok.w == 1) & (ok.ovr >= 1.08) & (ok.ovr <= 1.6)])]
    f = vl.facts(con, "2023-01-01")
    x = p.drop(columns=["state", "going_num"]).merge(f, on="run_id", how="left")
    x["state"] = x["state"].fillna(p.set_index("run_id")["state"].reindex(x["run_id"]).to_numpy())
    x["dist"] = x["dist"].fillna(x["distance"])
    inv = 1 / x["sp"]
    x["lsp"] = np.log(inv / inv.groupby(x["race_id"]).transform("sum"))
    thr = json.loads(vl.PARAMS.read_text())["thresholds"]
    x = vl.design(x, thr).sort_values(["race_id", "run_id"]).reset_index(drop=True)
    x["year"] = pd.to_datetime(x["race_date"]).dt.year
    x["p_ctl"] = x.groupby(pd.cut(x["sp"], [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 15, 25, 50, 1000]), observed=True)["won"].transform("mean")
    core = x["state"].isin(["VIC", "SA", "QLD"])
    # (a) fitted on VIC/SA/QLD, scored on all: fit per year on core rows, apply to every row of the test year
    pa = pd.Series(np.nan, index=x.index)
    for y in (2024, 2025, 2026):
        tr = x[(x["year"] < y) & core]
        b = clogit.fit(tr[vl.COLS].to_numpy(float), pd.factorize(tr["race_id"])[0], tr["won"].to_numpy(), l2=1e-3)
        te = x[x["year"] == y]
        pa[te.index] = clogit.probs(te[vl.COLS].to_numpy(float), pd.factorize(te["race_id"])[0], b)
    pb, _ = walk(x, vl.COLS)                       # (b) fitted on all five states
    te = x["year"] >= 2024
    weeks = (x.loc[te, "race_date"].max() - x.loc[te, "race_date"].min()).days / 7
    rows = []
    for lab, pr in (("fit VIC/SA/QLD", pa), ("fit all 5 states", pb)):
        v = pr * x["sp"]
        for st in ("VIC/SA/QLD", "NSW", "WA", "NSW + WA", "all 5"):
            sm = {"VIC/SA/QLD": core, "NSW": x["state"] == "NSW", "WA": x["state"] == "WA",
                  "NSW + WA": x["state"].isin(["NSW", "WA"]), "all 5": x["state"].notna()}[st]
            b = x[te & sm & (v >= 1.0) & (x["sp"] <= 51)]
            if len(b) < 30:
                continue
            yrs = {str(y): round(100 * ((t["won"] * t["sp"]).mean() - 1), 1) for y, t in b.groupby("year")}
            rows.append({"model": lab, "states": st, "bets": len(b), "per week": round(len(b) / weeks, 1),
                         "A/E pm": round(b["won"].sum() / b["p_ctl"].sum(), 3),
                         "ROI %": round(100 * ((b["won"] * b["sp"]).mean() - 1), 1), "95%": roi_ci(b), **yrs})
    t = pd.DataFrame(rows)
    L = [f"## NSW / WA (walk-forward 2024 to Sep 2026, value >= 1.0, SP <= $51)", "",
         f"- {x.loc[te, 'race_id'].nunique():,} test races ({x.loc[te & ~core, 'race_id'].nunique():,} NSW / WA).", "",
         t.to_markdown(index=False), ""]
    with OUT.open("a") as fh:
        fh.write("\n" + "\n".join(L) + "\n")
    print("\n".join(L))
