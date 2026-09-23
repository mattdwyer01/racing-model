"""Race card: speed map, projected rating (ability + bonuses / penalties in WPR points) and prices vs the market.

    python tools/race_card.py --date 2026-08-15 --track "Rockhampton"
    python tools/race_card.py --date 2026-08-15                 # every VIC/SA/QLD meeting that day

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
from model import figure, production, race_sim  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import eval_set  # noqa: E402

INFO_SQL = """
select r.run_id, r.horse, r.barrier, r.jockey, r.trainer, r.weight_kg, ra.track, ra.distance, ra.race_class,
  ra.going, ra.race_id, t.race_no, l.fixed_win_price, l.open_price
from runs r join races ra using (race_id) left join race_times t on t.race_id = ra.race_id
left join live_runners l on l.run_id = r.run_id
where r.race_date = date '{d}' and not r.is_trial_or_jumpout
"""
SHOW = ["ability", "form shape", "distance / going", "prep", "race-day projection", "track bias",
        "jockey / trainer", "comments", "ground loss (past runs)", "position value", "age / sex / weight"]
PACE_NAMES = ["slow", "even", "fast"]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--track", default=None, help="substring of the track name")
    a = ap.parse_args()
    con = duckdb.connect(str(figure.DB), read_only=True)
    om.EXTRA_PROJ, om.KEEP_SIM = True, True
    raw = om.build_features(con, a.date)
    m, _ = production.train(con, a.date, e=om.add_context(eval_set(raw)))
    info = con.sql(INFO_SQL.format(d=a.date)).df()
    if a.track:
        info = info[info["track"].str.contains(a.track, case=False)]
    rows = raw[raw["run_id"].isin(info["run_id"]) & raw["in_scope"]]
    if rows.empty:
        sys.exit("no VIC/SA/QLD races found for that date / track")
    rows = rows.merge(info[["run_id", "fixed_win_price", "open_price"]], on="run_id", how="left")
    pr = prep(rows)
    c = production.card(m, pr, market="log_p_mkt").merge(info, on=["run_id", "race_id"])
    c = c.merge(pr[["run_id", "h_wpr", "h_none", "proj_gl_v4"]], on="run_id", how="left")
    sm = speed_map(rows, a.date)
    c = c.merge(sm, on="run_id", how="left")
    # projected rating: field's average decayed WPR (horses with history) + rating vs field
    lvl = c["h_wpr"].where(c["h_none"] == 0).groupby(c["race_id"]).transform("mean")
    c["projected rating"] = lvl + c["rating vs field"]
    c["race-day adj"] = c.get("race-day projection", 0) + c.get("track bias", 0)
    for price, lab in [("SP", "edge vs SP"), ("fixed_win_price", "edge vs fixed")]:
        if "blend %" in c:
            c[lab] = c["blend %"] / 100 * c[price] - 1
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
