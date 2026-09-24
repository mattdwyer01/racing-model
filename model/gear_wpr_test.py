"""Gear changes and TopRate's wpr_nett on top of the production model (Apr to Sep 2026 only).

    RACING_EXTRA_STATES=NSW,WA python model/gear_wpr_test.py      # -> reports/gear_wpr_test.md

Both inputs exist only in the TopRate dashboard runners file (live_runners, 26 Apr 2026 on): the results files
carry no gear data and no wpr_nett. So no 2023-2026 walk-forward; instead:
  1. production model trained on races before 26 Apr 2026 scores every race 26 Apr to 23 Sep out of sample
  2. offset logits on the window: log p_production (free weight) + the new inputs, fitted on one half of the
     window's race dates and tested on the other, then swapped; paired race log loss vs production alone
     (refitted the same way), model and blend with SP
Inputs:
  gear      first time: blinkers, blinkers off, winkers, tongue tie, ear muffs, other gear; gelded; count of changes
  wpr_nett  TopRate's own current rating: vs the field mean, and missing flag
Leakage check: wpr_nett alone (a one-input logit) vs SP. A pre-race rating should be well behind SP; if it is at
or beyond SP it probably includes the race's own result, and any 'gain' is not usable.
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
from model import clogit, figure  # noqa: E402
import race_card  # noqa: E402

START, END = "2026-04-26", "2026-09-23"
GEAR = {"g_blink_ft": "Blinkers First Time", "g_blink_off": "Blinkers Off", "g_winkers_ft": "Winkers First Time",
        "g_tongue_ft": "Tongue Tie First Time", "g_earmuff_ft": "Ear Muffs", "g_gelded": "Gelded"}
BOOT = 2000


def gear_features(s):
    try:
        items = json.loads(s) if isinstance(s, str) else []
    except ValueError:
        items = []
    out = {k: float(any(v in it for it in items)) for k, v in GEAR.items()}
    named = set().union(*[{it for it in items if v in it} for v in GEAR.values()]) if items else set()
    out["g_other_ft"] = float(any("First Time" in it and it not in named for it in items))
    out["g_n"] = float(len(items))
    return out


def _race(df):
    return df.assign(race=pd.factorize(df["race_id"])[0])


def fit_test(fit, test, cols):
    b = clogit.fit(fit[cols].to_numpy(float), fit["race"].to_numpy(), fit["won"].to_numpy())
    return clogit.probs(test[cols].to_numpy(float), test["race"].to_numpy(), b), b


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    dates = [r[0] for r in con.sql(f"select distinct race_date from races where race_date between date '{START}' "
                                   f"and date '{END}' order by 1").fetchall()]
    c, m = race_card.score(con, START, [str(d) for d in dates])
    live = con.sql("""select run_id, gear_changes, wpr_nett, finish_position fp, starting_price_sp sp_live
                      from live_runners where resulted = 1""").df()
    d = c.merge(live, on="run_id", how="inner").merge(con.sql("select race_id, state from races").df(),
                                                       on="race_id", how="left")
    d = d[d["sp_live"] > 1]
    ok = d.groupby("race_id").agg(n=("run_id", "size"), w=("fp", lambda s: (s == 1).sum()))
    d = d[d["race_id"].isin(ok.index[(ok.n >= 2) & (ok.w == 1)])].copy()
    d["won"] = (d["fp"] == 1).astype(int)
    d = d.sort_values(["race_id", "run_id"]).reset_index(drop=True)
    g = pd.DataFrame([gear_features(s) for s in d["gear_changes"]], index=d.index)
    d = pd.concat([d, g], axis=1)
    grp = d.groupby("race_id")
    d["wn_miss"] = d["wpr_nett"].isna().astype(float)
    wn = d["wpr_nett"].fillna(grp["wpr_nett"].transform("mean")).fillna(0)
    d["wn_rel"] = wn - wn.groupby(d["race_id"]).transform("mean")
    d["lp_model"] = np.log((d["model %"] / 100).clip(1e-9))
    inv = 1 / d["sp_live"]
    d["lp_sp"] = np.log(inv / inv.groupby(d["race_id"]).transform("sum"))
    gear_cols = list(GEAR) + ["g_other_ft", "g_n"]
    variants = {"production": ["lp_model"], "+ gear": ["lp_model"] + gear_cols,
                "+ wpr_nett": ["lp_model", "wn_rel", "wn_miss"],
                "+ both": ["lp_model", "wn_rel", "wn_miss"] + gear_cols,
                "wpr_nett alone": ["wn_rel", "wn_miss"], "SP alone": ["lp_sp"]}
    for v in list(variants):
        if v not in ("SP alone", "wpr_nett alone"):
            variants[f"{v} blend"] = variants[v] + ["lp_sp"]
    # two halves by date, fit on one test on the other
    mid = pd.Timestamp(dates[len(dates) // 2])
    halves = [d["race_date"] < mid, d["race_date"] >= mid]
    ll = {}
    coefs = {}
    for k, (fm, tm) in enumerate([(halves[0], halves[1]), (halves[1], halves[0])]):
        fit, test = _race(d[fm].copy()), _race(d[tm].copy())
        for v, cols in variants.items():
            p, b = fit_test(fit, test, cols)
            w = test["won"].to_numpy() == 1
            ll.setdefault(v, []).append(pd.Series(-np.log(np.clip(p[w], 1e-12, 1)), index=test.loc[w, "race_id"]))
            coefs[(v, k)] = dict(zip(cols, np.round(b, 3)))
    L_ = pd.DataFrame({v: pd.concat(x) for v, x in ll.items()})
    state = d.groupby("race_id")["state"].first() if "state" in d else None
    rng = np.random.default_rng(0)

    def boot(x):
        x = x.to_numpy()
        mm = x[rng.integers(0, len(x), (BOOT, len(x)))].mean(1)
        return f"{x.mean():+.4f} ({np.percentile(mm, 2.5):+.4f} to {np.percentile(mm, 97.5):+.4f})"
    rows = []
    for a, b in [("+ gear", "production"), ("+ wpr_nett", "production"), ("+ both", "production"),
                 ("+ gear blend", "production blend"), ("+ wpr_nett blend", "production blend"),
                 ("+ both blend", "production blend"), ("production blend", "SP alone"),
                 ("wpr_nett alone", "SP alone"), ("wpr_nett alone", "production")]:
        rows.append({"first": a, "minus": b, "races": len(L_), "diff": boot(L_[a] - L_[b])})
    counts = d[gear_cols].sum().astype(int).to_dict()
    L = ["# Gear changes and TopRate wpr_nett on top of the production model", "",
         f"- Window {START} to {END} (runners file only); production trained before {START}, scores every race out"
         f" of sample. States: {', '.join(sorted(d['state'].dropna().unique())) if 'state' in d else '?'}",
         "- Offset logits (log p_production + inputs) fitted on one half of the window, tested on the other, swapped",
         f"- Races {L_.shape[0]}, runners {len(d)}. Gear counts: {counts}", "",
         "## Mean race log loss", "", L_.mean().to_frame("log loss").to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap)", "",
         pd.DataFrame(rows).to_markdown(index=False), "",
         "Leakage check: 'wpr_nett alone - SP alone' well above 0 is expected for a pre-race rating; near or below 0"
         " suggests wpr_nett includes the race's own result.", "",
         "## Fitted weights (half 1 fit, half 2 fit)", "", pd.Series(coefs).unstack().to_markdown()]
    (ROOT / "reports/gear_wpr_test.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
