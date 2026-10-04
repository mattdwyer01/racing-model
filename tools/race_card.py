"""Race card: speed map, projected rating (ability + bonuses / penalties in WPR points) and prices vs the market.

    python tools/race_card.py --date 2026-08-15 --track "Rockhampton"
    python tools/race_card.py --date 2026-08-15                 # every meeting that day (all states in scope)

Trains the production logit (model/production.py) on races before --date only, then scores that day's races.
Works for races without results (upcoming): features never use the race's own result.
Per race:
  speed map   projected settle (v4 model: share of the field, 0 = leader, and rank), P(leads) and pace
              chances from the race simulation (model/race_sim.py, 400 joint draws of positions and GPS pace),
              projected extra ground (m vs the field), race-day adjustment (WPR points)
  ratings     projected rating = field's average decayed WPR + the horse's rating vs the field (WPR points),
              split into bonuses / penalties; model $ (model alone), blend $ (model + market); market prices:
              SP, TopRate fixed price and opening price (live_runners, Apr 2026 on); edge = p_blend x price - 1
The blend uses SP when the race has one, else the fixed price (the blend weights were fitted with SP).
Writes reports/cards/<date>_<track>.md and prints it.
"""
import argparse
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, production, race_sim, value_live, wpr_model, wpr_nett_layer  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import eval_set  # noqa: E402

INFO_SQL = """
select r.run_id, r.horse, r.barrier, r.jockey, r.trainer, r.weight_kg, ra.track, ra.distance, ra.race_class,
  ra.going, ra.race_id, t.race_no, l.fixed_win_price, l.open_price, l.wpr_nett
from runs r join races ra using (race_id) left join race_times t on t.race_id = ra.race_id
left join live_runners l on l.run_id = r.run_id
where r.race_date in ({d}) and not r.is_trial_or_jumpout
"""
SHOW = ["ability", "form shape", "distance / going", "prep", "race-day projection", "track bias",
        "jockey / trainer", "comments", "ground loss (past runs)", "position value", "age / sex / weight"]
PACE_NAMES = ["slow", "even", "fast"]
POS_FEATS = ["pv_adj", "pw_adj"]
# "lite": speed map from production's v3 settle projection (low memory, for GitHub's free runner); set
# RACING_SPEEDMAP=v4 for the v4 settle model (9.3 GB peak with 5-state training; the dashboard job uses it)
import os  # noqa: E402
LITE = "lite" if os.environ.get("RACING_SPEEDMAP", "lite") != "v4" else False


def prep(rows):
    """The derived columns eval_set adds, without dropping races that have no result yet. Market = SP when
    every runner has one, else the fixed price."""
    rows = rows.copy()
    for src, col in [("sp", "p_sp"), ("fixed_win_price", "p_fixed")]:
        inv = 1 / rows[src].where(rows[src] > 1)
        rows[col] = inv / inv.groupby(rows["race_id"]).transform("sum")
    has_sp = rows.groupby("race_id")["p_sp"].transform(lambda s: s.notna().all())
    rows["log_p_mkt"] = np.log(rows["p_sp"].where(has_sp, rows["p_fixed"]))
    rows["log_p_sp"] = rows["log_p_mkt"]
    rows["log_n"] = np.log1p(rows["h_n"])
    rows["log_days"] = np.log1p(rows["days_since_start"].fillna(0))
    rows["first_up"] = (rows["days_since_start"].fillna(999) >= 60).astype(float)
    return om.add_context(rows)


def speed_map(rows, date):
    """Speed map per runner from the race simulation (fitted on races before date)."""
    px, rr = om.LAST_PX.pop("sim_px"), om.LAST_PX.pop("sim_rr")
    parts = race_sim.SimParts().fit(px, rr, date)
    x = px[px["run_id"].isin(rows["run_id"])].sort_values(["race_id", "run_id"]).reset_index(drop=True)
    x["sim_pace0"] = x["race_id"].map(parts.pace_proj(rr)).to_numpy()
    _, lead, pace_p = race_sim.draws(x, parts)
    band = pd.cut(x["dist"], race_sim.DIST_BANDS, labels=False)
    out = pd.DataFrame({"run_id": x["run_id"], "settle": x["sim_settle"], "P(leads)": lead,
                        "pace vs distance avg": x["sim_pace0"]})
    for b, name in enumerate(PACE_NAMES):
        out[f"P({name})"] = pace_p[:, b]
    out["_band"] = band.to_numpy()
    return out


def model_health(raw, rows, train_end):
    """Sanity numbers for tools/health_check.py (written into racing_model.json). Each would have caught a real
    failure: the v1 figure fit going NaN when a carried weight was missing (every horse scored as a debutant, 25 Sep
    2026) shows as dm_zero_share ~1 and debut_trial_on_runners > 0."""
    recent = raw[(raw["race_date"] < train_end) & (raw["race_date"] >= pd.Timestamp(train_end) - pd.Timedelta(days=60))]
    has_hist = recent["h_none"] == 0
    out = {"dm_zero_share": float((recent.loc[has_hist, "dm"] == 0).mean()) if has_hist.any() else None,
           "debut_trial_on_runners": float(((recent["trial_pos_debut"] != 0) & has_hist).mean()),
           "card_runners": int(len(rows))}
    if len(rows):
        out["card_no_weight_share"] = float(rows["wt_rel_today"].isna().mean()) if "wt_rel_today" in rows else None
        out["card_h_none_share"] = float((rows["h_none"] == 1).mean())
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}


def wpr_nett_on_top(c, pr, m):
    """TopRate wpr_nett layer on the model's chances (model/wpr_nett_layer.py); the blend is re-formed from the
    layered chance with the production weights. `model % (base)` keeps the production model's own chance."""
    if not wpr_nett_layer.ENABLED or "wpr_nett" not in c or c["wpr_nett"].notna().sum() == 0:
        return c
    c = c.copy()
    c["model % (base)"] = c["model %"]
    p = wpr_nett_layer.apply(c["race_id"], c["model %"] / 100, c["wpr_nett"])
    c["model %"], c["model $"] = 100 * p, 1 / p
    if "blend %" in c and "log_p_mkt" in pr:
        mk = pd.to_numeric(c["run_id"].map(pr.drop_duplicates("run_id").set_index("run_id")["log_p_mkt"]), errors="coerce")
        has = mk.notna().groupby(c["race_id"]).transform("all")
        z = m["a"] * np.log(np.clip(p, 1e-12, 1)) + m["b"] * mk.fillna(0)
        e = np.exp(z - z.groupby(c["race_id"]).transform("max"))
        pb = (e / e.groupby(c["race_id"]).transform("sum")).where(has)
        c["blend %"], c["blend $"] = 100 * pb, 1 / pb
        if "SP" in c:
            c["edge vs SP"] = pb * c["SP"] - 1
    return c


def add_value(con, c, rows, raw, train_end):
    """Per-runner value utility `vu` and price slope `vs` (model/value_live.py): p = softmax(vs x log p_price + vu).
    The race-day projection thresholds are re-set from this build's own training rows (same quantiles as the fit),
    so a change of projection scale cannot shift the flags."""
    params = value_live.load()
    if params is None or c.empty:
        return c
    x = rows[["run_id", "race_id", "race_date", "proj_adj", "bias_adj", "h_wpr", "h_none", "dist"]].copy()
    f = value_live.facts(con, str(pd.Timestamp(x["race_date"].min()).date()))
    key = x["run_id"]
    x["run_id"] = x["run_id"].astype(str)
    x = x.merge(f, on="run_id", how="left")
    x["run_id"] = key.to_numpy()
    thr = dict(params["thresholds"])
    tr = raw[raw["core_scope"] & (raw["race_date"] < train_end) &
             (raw["race_date"] >= pd.Timestamp(train_end) - pd.Timedelta(days=730))]
    if len(tr) > 10000:
        adj = tr["proj_adj"].fillna(0) + tr["bias_adj"].fillna(0)
        thr["sm"] = float((adj - adj.groupby(tr["race_id"]).transform("mean")).quantile(0.82))
        thr["bias"] = float(tr["bias_adj"].quantile(0.8))
    xd = value_live.design(x, thr)
    v = value_live.score(xd, params)
    v["signals"] = value_live.signals(xd, params).to_numpy()
    return c.merge(v, on="run_id", how="left")


def score(con, train_end, dates, track=None):
    """Card rows for every in-scope race on `dates` (all states, production.CARD_ALL_STATES) with the production model trained on races before
    train_end: speed map, projected rating and breakdown, prices. Returns (DataFrame, model)."""
    om.EXTRA_PROJ, om.KEEP_SIM = LITE or True, True
    production.use_training_scope()      # VIC/SA/QLD + production.TRAIN_EXTRA_STATES (all states)
    raw = om.build_features(con, train_end, light="no_posmap", lean=True)
    m, e_train = production.train(con, train_end, e=om.add_context(eval_set(raw)))
    info = con.sql(INFO_SQL.format(d=", ".join(f"date '{x}'" for x in dates))).df()
    if track:
        info = info[info["track"].str.contains(track, case=False)]
    card_scope = raw["in_scope"] if production.CARD_ALL_STATES else raw["core_scope"]
    rows = raw[raw["run_id"].isin(info["run_id"]) & card_scope]
    if rows.empty:
        return pd.DataFrame(), m
    rows = rows.merge(info[["run_id", "fixed_win_price", "open_price"]], on="run_id", how="left")
    try:
        m["health"] = model_health(raw, rows, train_end)
    except Exception as e:          # the health numbers must never break a card / dashboard build
        m["health"] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
    pr = prep(rows)
    c = production.card(m, pr, market="log_p_mkt").merge(info, on=["run_id", "race_id"])
    c = wpr_nett_on_top(c, pr, m)
    c = c.merge(pr[["run_id", "race_date", "h_wpr", "h_none", "proj_gl_v4"] + [f for f in POS_FEATS if f in pr]],
                on="run_id", how="left")
    # position value (position map: expected value of the projected position and width, WPR points vs the race)
    # and its flag: top 10% of runners over the last two years of training races (the disagreement test group
    # the market underrates)
    if all(f in raw for f in POS_FEATS):
        pv_all = raw[POS_FEATS].fillna(0).sum(1)
        recent = raw["core_scope"] & (raw["race_date"] < train_end) & \
            (raw["race_date"] >= pd.Timestamp(train_end) - pd.Timedelta(days=730))
        m["pos_flag_thr"] = float(pv_all[recent].quantile(0.9))
        c["pos value"] = c[POS_FEATS].fillna(0).sum(1)
        c["pos flag"] = c["pos value"] >= m["pos_flag_thr"]
    c = c.merge(speed_map(rows, train_end), on="run_id", how="left")
    # projected rating: field's average decayed WPR (horses with history) + rating vs field
    lvl = c["h_wpr"].where(c["h_none"] == 0).groupby(c["race_id"]).transform("mean")
    c["projected rating"] = lvl + c["rating vs field"]
    c["race-day adj"] = c.get("race-day projection", 0) + c.get("track bias", 0)
    try:                                 # WPR projection v2 (model/wpr_model.py): the WPR each horse should run, +/- sd
        wm = wpr_model.fit_live(e_train, m["rating"], train_end)
        c = c.merge(wpr_model.predict(wm, pr, m["rating"]), on="run_id", how="left")
        del wm
    except Exception as e:  # noqa: BLE001
        print(f"WPR projection skipped: {type(e).__name__}: {str(e)[:160]}", flush=True)
    del e_train
    try:                                 # value model (model/value_live.py); never breaks a card / dashboard build
        c = add_value(con, c, rows, raw, train_end)
    except Exception as e:  # noqa: BLE001
        print(f"value model skipped: {type(e).__name__}: {str(e)[:160]}", flush=True)
    for price, lab in [("SP", "edge vs SP"), ("fixed_win_price", "edge vs fixed")]:
        if "blend %" in c:
            c[lab] = c["blend %"] / 100 * c[price] - 1
    return c, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--track", default=None, help="substring of the track name")
    a = ap.parse_args()
    con = duckdb.connect(str(figure.DB), read_only=True)
    c, m = score(con, a.date, [a.date], a.track)
    if c.empty:
        sys.exit("no in-scope races found for that date / track")
    L = [f"# Race card {a.date}{' ' + a.track if a.track else ''}", "",
         f"- Model trained on races before {a.date} (blend a = {m['a']:.3f}, b = {m['b']:.3f}). Contributions are WPR"
         " points vs the field average; projected rating = field's average rating + rating vs field. Model and blend"
         " prices are fair (no overround); the blend uses SP, or the fixed price when there is no SP",
         "- Speed map: v4 settle projection and the race simulation (candidate models; the ratings use the current"
         " production model). Settle 0 = leader, 1 = last at the 800m", ""]
    for rid, g in c.groupby("race_id", sort=False):
        r0 = g.iloc[0]
        rn = f"R{int(r0.race_no)} " if pd.notna(r0.race_no) else ""
        pace = " / ".join(f"{n} {g[f'P({n})'].iloc[0]:.0%}" for n in PACE_NAMES)
        L += [f"## {r0.track} {rn}{int(r0.distance)}m {r0.race_class} ({r0.going})", "",
              f"Projected pace: {g['pace vs distance avg'].iloc[0]:+.1f} vs the average for the distance (GPS pace"
              f" units); chances {pace}", "", "### Speed map", ""]
        s = g.sort_values("settle").assign(**{"settle rank": lambda t: np.arange(1, len(t) + 1)})
        s = s.rename(columns={"proj_gl_v4": "extra ground (m)"})
        L += [s[["horse", "barrier", "settle rank", "settle", "P(leads)", "extra ground (m)", "race-day adj"]]
              .to_markdown(index=False, floatfmt=".2f"), "", "### Ratings and prices", ""]
        cols = ["horse", "projected rating", "rating vs field"] + [x for x in SHOW if x in g] + ["model $"] + \
            [x for x in ["blend $", "SP", "fixed_win_price", "open_price", "edge vs SP", "edge vs fixed"] if x in g]
        t = g.sort_values("projected rating", ascending=False)[cols].rename(
            columns={"fixed_win_price": "fixed $", "open_price": "open $"})
        L += [t.to_markdown(index=False, floatfmt=".2f"), ""]
    out = ROOT / f"reports/cards/{a.date}_{(a.track or 'all').replace(' ', '_')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
