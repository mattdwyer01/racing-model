"""Current-ability model: pre-race features from each horse's figure history.

    python model/ability.py      # walk-forward validation -> reports/ability_validation.md

Per fold (test year Y, trained on 2022..Y-1) the figure weights are refitted on training
races only, then every feature below is built from prior starts only:
    form      decayed mean figure (dm), last, best of last 3 / 10, mean of last 3, trend (last - dm)
    class     decayed mean strength of past races (mean WPR of the field), today's vs it is a
              race constant so only the horse's side enters
    distance  log(today / decayed mean past distance) and its abs; distance fit = shrunk mean
              deviation (fig - dm at the time) over past runs within 10% of today's distance
    going     same, over past runs on the same wet/dry band (wet = going 7+)
    surface   same, over past runs on the same surface class (synthetic vs not)
    prep      first-up / second-up / third-up flags, log days since last start, and the horse's
              own first-up and second-up aptitude (shrunk mean deviation on past such runs)
    trials    trial since last start, its finish position share and margin (first-up and debut)
    other     age and sex flags, weight vs field
Deviations are shrunk as sum(dev) / (n + 2).
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure  # noqa: E402
from model.validate_figure import FIG, eval_set, fit_eval, race_ll  # noqa: E402

K = 10
SHRINK = 2.0

EXTRA_SQL = """
select r.run_id, ra.going_num, ra.surface, r.age, r.sex,
  avg(r.res_wpr) over (partition by r.race_id) race_str
from runs r join races ra using (race_id) where not r.is_trial_or_jumpout
"""

TRIAL_SQL = """
with t as (   -- one row per horse per trial day (a horse can trial / jump out twice in a day)
  select r.horse_id, r.race_date tdate,
    min((r.res_finish - 1) / greatest(ra.field_size - 1, 1)) pos, min(r.res_margin_l) marg
  from runs r join races ra using (race_id) where r.is_trial_or_jumpout
  group by 1, 2
), s as (
  select run_id, horse_id, race_date, prev_start_date from runs where not is_trial_or_jumpout
)
select s.run_id,
  (t.tdate > coalesce(s.prev_start_date, date '1900-01-01'))::int t_trial_since,
  (s.race_date - t.tdate) t_trial_days,
  t.pos t_trial_pos,
  least(coalesce(t.marg, 10), 10) t_trial_marg
from s asof left join t on s.horse_id = t.horse_id and s.race_date > t.tdate
"""


def load(con):
    d = figure.components(con)
    d = d.merge(con.sql(EXTRA_SQL).df(), on="run_id", how="left")
    d = d.merge(con.sql(TRIAL_SQL).df(), on="run_id", how="left")
    d["wet"] = (d["going_num"].fillna(4) >= 7).astype(float)
    d["synth"] = d["surface"].isin(["Synthetic", "Sand", "Dirt"]).astype(float)
    return d.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)


def fit_coef(h, train_end):
    e = eval_set(h)
    tr = e[e.race_date < train_end]
    _, b = fit_eval(tr, tr.iloc[:0], FIG)
    comps = ["s_early", "s_l600", "wt_rel", "settle", "shape", "pace"]
    return {"wpr": 1.0, **{c: float(b["h_" + c] / b["h_wpr"]) for c in comps}}


def features(d, coef):
    d = d.copy()
    d["fig"] = figure.figure(d, coef)
    g = d.groupby("horse_id", sort=False)
    n = len(d)
    lag = {c: np.stack([g[c].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
           for c in ["fig", "dist", "wet", "synth"]}
    days = np.stack([(d["race_date"] - g["race_date"].shift(j)).dt.days.to_numpy(float) for j in range(1, K + 1)], 1)
    ok = ~np.isnan(days) & ~np.isnan(lag["fig"])   # prior starts with a result only
    w = np.where(ok, 0.5 ** (np.arange(K) / figure.HALF_LIFE_RUNS) * 0.5 ** (np.nan_to_num(days) / figure.HALF_LIFE_DAYS), 0)
    den = w.sum(1)
    has = den > 0
    sdiv = np.where(has, den, 1)
    fig = np.nan_to_num(lag["fig"])

    f = pd.DataFrame(index=d.index)
    f["dm"] = np.where(has, (w * fig).sum(1) / sdiv, 0)
    f["fig_last"] = np.where(has, fig[np.arange(n), np.argmax(ok, 1)], 0)
    with np.errstate(all="ignore"):
        f["best3"] = np.where(has, np.nanmax(np.where(ok[:, :3], lag["fig"][:, :3], -np.inf), 1), 0)
        f["best10"] = np.where(has, np.nanmax(np.where(ok, lag["fig"], -np.inf), 1), 0)
        k3 = ok[:, :3].sum(1)
        f["mean3"] = np.where(has, np.where(ok[:, :3], fig[:, :3], 0).sum(1) / np.maximum(k3, 1), 0)
    f["trend"] = f["fig_last"] - f["dm"]
    rs = np.stack([g["race_str"].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
    f["h_class"] = np.where(has, (w * np.nan_to_num(rs)).sum(1) / sdiv, 0)
    hd = np.where(has, (w * np.nan_to_num(lag["dist"])).sum(1) / sdiv, d["dist"])
    f["dist_ratio"] = np.log(d["dist"] / hd)
    f["dist_abs"] = f["dist_ratio"].abs()

    # deviation of each past run from the horse's pre-race dm at that time
    dev = (d["fig"] - f["dm"]).where(has, np.nan)
    d["_dev"] = dev
    devlag = np.stack([g["_dev"].shift(j).to_numpy(float) for j in range(1, K + 1)], 1)
    valid = ok & ~np.isnan(devlag)
    dv = np.nan_to_num(devlag)

    def fit_dev(mask):
        m = valid & mask
        return (m * dv).sum(1) / (m.sum(1) + SHRINK)

    f["dist_fit"] = fit_dev(np.abs(np.log(np.nan_to_num(lag["dist"], nan=1) / d["dist"].to_numpy()[:, None])) < 0.1)
    f["going_fit"] = fit_dev(lag["wet"] == d["wet"].to_numpy()[:, None])
    f["surface_fit"] = fit_dev(lag["synth"] == d["synth"].to_numpy()[:, None])

    # prep pattern: horse's own first-up / second-up aptitude over its whole career
    for k, name in [(1, "fu"), (2, "su")]:
        is_k = (d["prep_run"] == k) & dev.notna()
        s = (dev.where(is_k, 0)).groupby(d["horse_id"]).cumsum() - dev.where(is_k, 0)
        c = is_k.astype(int).groupby(d["horse_id"]).cumsum() - is_k.astype(int)
        f[name + "_apt"] = np.where(d["prep_run"] == k, s / (c + SHRINK), 0)
        f[name] = (d["prep_run"] == k).astype(float)
    f["up3"] = (d["prep_run"] == 3).astype(float)

    # trials
    ts = d["t_trial_since"].fillna(0).astype(float)
    f["trial_since"] = ts
    f["trial_pos"] = np.where(ts > 0, d["t_trial_pos"].fillna(0.5) - 0.5, 0)
    f["trial_marg"] = np.where(ts > 0, d["t_trial_marg"].fillna(5) - 3, 0)
    deb = (~has).astype(float)
    f["trial_pos_debut"] = f["trial_pos"] * deb
    f["trial_marg_debut"] = f["trial_marg"] * deb

    # other
    f["age2"] = (d["age"] <= 2).astype(float)
    f["age3"] = (d["age"] == 3).astype(float)
    f["age7"] = (d["age"] >= 7).astype(float)
    f["female"] = d["sex"].isin(["F", "M"]).astype(float)
    return pd.concat([d.drop(columns=["_dev"]), f], axis=1)


GROUPS = {
    "form": ["dm", "fig_last", "best3", "best10", "mean3", "trend"],
    "class": ["h_class"],
    "distance/going/surface": ["dist_ratio", "dist_abs", "dist_fit", "going_fit", "surface_fit"],
    "prep": ["fu", "su", "up3", "fu_apt", "su_apt"],
    "trials": ["trial_since", "trial_pos", "trial_marg", "trial_pos_debut", "trial_marg_debut"],
    "age/sex/weight": ["age2", "age3", "age7", "female", "wt_rel_today"],
}
BASE = ["h_none", "log_n", "log_days", "first_up"]
ALL = BASE + [c for v in GROUPS.values() for c in v]
FOLDS = [2023, 2024, 2025, 2026]


def main():
    con = duckdb.connect(str(figure.DB), read_only=True)
    d = load(con)
    h = figure.history(d)            # component decayed means (for the figure baseline + coef fits)
    variants = {"figure (baseline)": FIG, "ability": ALL}
    variants.update({f"ability - {k}": [c for c in ALL if c not in v] for k, v in GROUPS.items()})
    variants["SP (calibrated)"] = ["log_p_sp"]
    variants["SP + figure"] = ["log_p_sp"] + FIG
    variants["SP + ability"] = ["log_p_sp"] + ALL

    rows, per, coefs = [], {}, {}
    for y in FOLDS:
        coef = fit_coef(h, f"{y}-01-01")
        coefs[y] = coef
        a = features(d, coef)
        hh = h.merge(a[["run_id"] + [c for c in ALL if c not in BASE and c != "wt_rel_today"]], on="run_id")
        e = eval_set(hh)
        tr = e[e.race_date < f"{y}-01-01"]
        te = e[e.race_date.dt.year == y]
        res = {"fold": y, "races": te.race_id.nunique()}
        for name, cols in variants.items():
            ll = race_ll(fit_eval(tr, te, cols)[0], te)
            res[name] = ll.mean()
            per.setdefault(name, []).append(ll)
        rows.append(res)
        print(y, {k: round(float(v), 4) for k, v in res.items() if k != "fold"}, flush=True)
    _, b_last = fit_eval(e, e.iloc[:0], ALL)

    tab = pd.DataFrame(rows).set_index("fold")
    pooled = {k: np.concatenate(v) for k, v in per.items()}
    tab.loc["pooled"] = [tab["races"].sum()] + [pooled[k].mean() for k in variants]

    def diff(a, b):
        x = pooled[a] - pooled[b]
        return x.mean(), x.std() / np.sqrt(len(x))
    comps = [("ability", "figure (baseline)")] + [(f"ability - {k}", "ability") for k in GROUPS] + \
            [("SP + figure", "SP (calibrated)"), ("SP + ability", "SP (calibrated)"), ("SP + ability", "SP + figure")]

    L = ["# Current-ability model: walk-forward validation", "",
         "- Eval set and folds as validate_figure.py (VIC/SA/QLD races, test 2023 to 2026 YTD, trained 2022 to Y-1)",
         "- Figure weights refitted on each fold's training races only", "",
         "## Log loss by fold (lower is better)", "", tab.T.to_markdown(floatfmt=".4f"), "",
         "## Paired differences (pooled; negative = first is better)", "",
         "| model | vs | diff | se |", "|---|---|---|---|"]
    L += [f"| {a} | {b} | {diff(a, b)[0]:+.4f} | {diff(a, b)[1]:.4f} |" for a, b in comps]
    L += ["", "## Coefficients (fit on all 2022 on, raw units)", "", "| feature | beta |", "|---|---|"]
    L += [f"| {k} | {v:+.4f} |" for k, v in b_last.items()]
    L += ["", "## Figure weights by fold", "", pd.DataFrame(coefs).to_markdown(floatfmt=".3f")]
    out = ROOT / "reports/ability_validation.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
