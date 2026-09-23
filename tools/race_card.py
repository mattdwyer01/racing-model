"""Race card: each horse's rating as ability + bonuses / penalties in WPR points, with model and blend prices.

    python tools/race_card.py --date 2026-08-15 --track "Rockhampton"
    python tools/race_card.py --date 2026-08-15                 # every VIC/SA/QLD meeting that day

Trains the production logit (model/production.py) on races before --date only, then scores that day's races.
Works for races without results (upcoming): features never use the race's own result. The blend and 'edge vs SP'
need an SP; for upcoming races they are blank until a market price is supplied.
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
from model import figure, production  # noqa: E402
from model import offset_model as om  # noqa: E402
from model.validate_figure import eval_set  # noqa: E402

INFO_SQL = """
select r.run_id, r.horse, r.barrier, r.jockey, r.trainer, r.weight_kg, ra.track, ra.distance, ra.race_class,
  ra.going, ra.race_id, t.race_no
from runs r join races ra using (race_id) left join race_times t on t.race_id = ra.race_id
where r.race_date = date '{d}' and not r.is_trial_or_jumpout
"""
SHOW = ["ability", "form shape", "distance / going", "prep", "race-day projection", "track bias",
        "jockey / trainer", "comments", "ground loss (past runs)", "position value", "age / sex / weight"]


def prep(rows):
    """The derived columns eval_set adds, without dropping races that have no result yet."""
    rows = rows.copy()
    inv = 1 / rows["sp"].where(rows["sp"] > 1)
    rows["p_sp"] = inv / inv.groupby(rows["race_id"]).transform("sum")
    rows["log_p_sp"] = np.log(rows["p_sp"])
    rows["log_n"] = np.log1p(rows["h_n"])
    rows["log_days"] = np.log1p(rows["days_since_start"].fillna(0))
    rows["first_up"] = (rows["days_since_start"].fillna(999) >= 60).astype(float)
    return om.add_context(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--track", default=None, help="substring of the track name")
    a = ap.parse_args()
    con = duckdb.connect(str(figure.DB), read_only=True)
    raw = om.build_features(con, a.date)
    m, _ = production.train(con, a.date, e=om.add_context(eval_set(raw)))
    info = con.sql(INFO_SQL.format(d=a.date)).df()
    if a.track:
        info = info[info["track"].str.contains(a.track, case=False)]
    rows = raw[raw["run_id"].isin(info["run_id"]) & raw["in_scope"]]
    if rows.empty:
        sys.exit("no VIC/SA/QLD races found for that date / track")
    c = production.card(m, prep(rows)).merge(info, on=["run_id", "race_id"])
    L = [f"# Race card {a.date}{' ' + a.track if a.track else ''}", "",
         f"- Model trained on races before {a.date} (blend a = {m['a']:.3f}, b = {m['b']:.3f}). Contributions are WPR"
         " points vs the field average; 'rating vs field' is their sum. Prices are fair (no overround)", ""]
    for rid, g in c.groupby("race_id", sort=False):
        r0 = g.iloc[0]
        rn = f"R{int(r0.race_no)} " if pd.notna(r0.race_no) else ""
        L += [f"## {r0.track} {rn}{int(r0.distance)}m {r0.race_class} ({r0.going})", ""]
        cols = ["horse", "barrier", "jockey"] + [s for s in SHOW if s in g] + ["rating vs field", "model $"] + \
            [x for x in ["blend $", "SP", "edge vs SP"] if x in g]
        t = g.sort_values("rating vs field", ascending=False)[cols]
        L += [t.to_markdown(index=False, floatfmt=".2f"), ""]
    out = ROOT / f"reports/cards/{a.date}_{(a.track or 'all').replace(' ', '_')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
