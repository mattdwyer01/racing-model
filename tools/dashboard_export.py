"""Dashboard export: the Racing Model layer for the TopRate dashboard (racing_model.json).

    python tools/dashboard_export.py --toprate-dir ../toprate      # today (Melbourne)
    python tools/dashboard_export.py --date 2026-09-24 --no-store --toprate-dir /tmp/tr

Writes <toprate-dir>/racing_model.json (read by TopRate's frontend/src/lib/racingModel.ts): per runner the
model's win probability, projected rating and breakdown, v4 settle, P(leads) and extra ground; per race the pace
chances and when the projection was made; the blend weights (the frontend blends with the live fixed price);
and a tracking summary (model, blend and SP log loss on resulted races). Optional --site-dir also writes the
per-day JSON (index.json, day/<date>.json, tracking.json) used by the earlier static site.
Projections are archived (data/interim/dash_projections.csv.gz, synced to the store) the day they are made, so a
past race always shows the projection made BEFORE it ran, next to what happened. Days with no archived
projection (first run) are backfilled with a model trained before the earliest such day (still pre-race).
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, production  # noqa: E402
from pipeline import store  # noqa: E402
sys.path.insert(0, str(ROOT / "tools"))
import race_card  # noqa: E402

ARCHIVE = ROOT / "data/interim/dash_projections.csv.gz"
AHEAD, BACK = 2, 7
GROUPS = [g for g in race_card.SHOW]
KEEP = ["race_id", "run_id", "race_date", "horse", "barrier", "jockey", "trainer", "weight_kg", "track",
        "distance", "race_class", "going", "race_no", "settle", "P(leads)", "pace vs distance avg", "P(slow)",
        "P(even)", "P(fast)", "proj_gl_v4", "race-day adj", "projected rating", "rating vs field", "model %",
        "model $", "blend %", "blend $", "fixed_win_price", "open_price", "edge vs fixed", "pos value",
        "pos flag"] + GROUPS

RESULT_SQL = """
select r.run_id, r.res_finish finish, r.res_margin_l margin, r.res_wpr wpr, r.sp, r.res_pos800 pos800,
  r.res_marg800 marg800, r.res_stewards stewards, g.res_gps_extra_m gps_extra_m
from runs r left join gps_runs g using (run_id)
where r.race_date in ({d})
"""
META_SQL = """
select ra.race_id, ra.state, ra.rail_text, ra.res_shape_early shape_early, t.start_utc
from races ra left join race_times t using (race_id) where ra.race_date in ({d})
"""


def _started_races(con):
    """race_ids whose start time has passed (race_times, from the TopRate runners file)."""
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    try:
        return set(con.sql(f"select race_id from race_times where epoch(start_utc) <= {now}").df()["race_id"])
    except duckdb.Error:
        return set()


def _missing_days(con, arch, days):
    """Recent days with a state that raced but has nothing archived (a new day, or a state added to scope)."""
    if not days:
        return []
    states = ["VIC", "SA", "QLD"] + (production.TRAIN_EXTRA_STATES if production.CARD_ALL_STATES else [])
    ran = con.sql(f"""select race_date::date d, state, race_id from races
                      where race_date::date in ({", ".join(f"date '{x}'" for x in days)})
                        and state in ({", ".join(f"'{x}'" for x in states)}) and not coalesce(is_trial, false)""").df()
    got = set(arch["race_id"].astype("int64")) if len(arch) else set()
    out = []
    for d in days:
        r = ran[ran["d"] == pd.Timestamp(d)]
        if set(r["state"]) - set(r.loc[r["race_id"].isin(got), "state"]):
            out.append(d)
    return out


def _dates(d0, n, step):
    return [d0 + dt.timedelta(days=step * i) for i in range(1, n + 1)]


def _sql_dates(ds):
    return ", ".join(f"date '{d}'" for d in ds)


def _clean(v):
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else round(float(v), 4)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (pd.Timestamp, dt.date)):
        return str(v)[:19]
    return v


def _archive_rows(c, m, scored_on):
    if c.empty:
        return pd.DataFrame(columns=KEEP)
    a = c[[k for k in KEEP if k in c]].copy()
    a["scored_on"], a["train_end"] = str(scored_on), m["train_end"]
    a["blend_a"], a["blend_b"], a["cal_c"] = m["a"], m["b"], m["c"]
    return a


def day_json(d, rows, results, meta):
    rows = rows.merge(results, on="run_id", how="left") if len(results) else rows
    rows = rows.merge(meta, on="race_id", how="left")
    races = []
    for rid, g in rows.groupby("race_id", sort=False):
        g = g.sort_values("settle")
        g = g.assign(settle_rank=np.arange(1, len(g) + 1))
        r0 = g.iloc[0]
        resulted = "finish" in g and g["finish"].notna().any()
        runners = []
        for _, x in g.sort_values("projected rating", ascending=False).iterrows():
            run = {"run_id": x["run_id"], "horse": x["horse"], "barrier": x.get("barrier"), "jockey": x.get("jockey"),
                   "trainer": x.get("trainer"), "weight": x.get("weight_kg"), "settle": x.get("settle"),
                   "settle_rank": x["settle_rank"], "p_lead": x.get("P(leads)"), "extra_ground": x.get("proj_gl_v4"),
                   "raceday_adj": x.get("race-day adj"), "rating": x.get("projected rating"),
                   "vs_field": x.get("rating vs field"), "groups": {k: _clean(x.get(k)) for k in GROUPS if k in x},
                   "model_price": x.get("model $"), "blend_price": x.get("blend $"), "fixed": x.get("fixed_win_price"),
                   "open": x.get("open_price"), "edge_fixed": x.get("edge vs fixed")}
            if resulted:
                run["result"] = {"finish": x.get("finish"), "margin": x.get("margin"), "wpr": x.get("wpr"),
                                 "sp": x.get("sp"), "pos800": x.get("pos800"), "gps_extra_m": x.get("gps_extra_m"),
                                 "stewards": x.get("stewards")}
            runners.append({k: _clean(v) if not isinstance(v, dict) else
                            {kk: _clean(vv) for kk, vv in v.items()} for k, v in run.items()})
        races.append({"race_id": int(rid), "race_no": _clean(r0.get("race_no")), "track": r0["track"],
                      "state": r0.get("state"), "start_utc": _clean(r0.get("start_utc")),
                      "distance": _clean(r0.get("distance")), "class": r0.get("race_class"), "going": r0.get("going"),
                      "rail": r0.get("rail_text"), "resulted": bool(resulted),
                      "pace": {"vs_avg": _clean(r0.get("pace vs distance avg")), "slow": _clean(r0.get("P(slow)")),
                               "even": _clean(r0.get("P(even)")), "fast": _clean(r0.get("P(fast)")),
                               "actual_shape_early": _clean(r0.get("shape_early"))},
                      "scored_on": r0.get("scored_on"), "runners": runners})
    races.sort(key=lambda r: (r["track"], r["race_no"] or 0))
    meetings = {}
    for r in races:
        meetings.setdefault((r["track"], r["state"]), []).append(r)
    return {"date": str(d), "meetings": [{"track": t, "state": s, "races": rs} for (t, s), rs in meetings.items()]}


def race_bias(rows):
    """Projected track bias per race, as the model applies it: the runners' "track bias" contribution (WPR
    points, from past meetings at the track: long-run and recent same-rail) regressed within the race on
    projected settle share (0 leader, 1 last) and barrier share (0 inside, 1 outside).
    lead = WPR edge of a leader over a backmarker; inside = of the inside draw over the outside draw."""
    out = {}
    if "track bias" not in rows:
        return out
    for rid, g in rows.groupby("race_id"):
        g = g.dropna(subset=["track bias", "settle", "barrier"])
        if len(g) < 4:
            continue
        bar = (g["barrier"].rank(method="first") - 1) / max(len(g) - 1, 1)
        X = np.column_stack([np.ones(len(g)), g["settle"].to_numpy(float), bar.to_numpy(float)])
        if np.linalg.matrix_rank(X) < 3:
            continue
        b = np.linalg.lstsq(X, g["track bias"].to_numpy(float), rcond=None)[0]
        out[int(rid)] = {"lead": round(float(-b[1]), 2), "inside": round(float(-b[2]), 2)}
    return out


def write_toprate(dest, rows, m, track):
    """racing_model.json for TopRate's frontend (compact keys, see its lib/racingModel.ts)."""
    def f(v):
        v = _clean(v)
        return None if isinstance(v, str) else v
    runners, races = {}, {}
    bias = race_bias(rows)
    for _, x in rows.iterrows():
        runners[str(int(x["run_id"]))] = {
            "r": f(x.get("projected rating")), "v": f(x.get("rating vs field")),
            "p": f(x["model %"] / 100 if pd.notna(x.get("model %")) else None), "s": f(x.get("settle")),
            "l": f(x.get("P(leads)")), "g": f(x.get("proj_gl_v4")), "d": f(x.get("race-day adj")),
            "ab": f(x.get("ability")), "jt": f(x.get("jockey / trainer")), "pv": f(x.get("pos value")),
            "pf": 1 if str(x.get("pos flag")) in ("True", "1", "1.0") else 0,
            # rating breakdown (WPR points vs the field) for the runner detail popup
            "gb": {k: round(v, 2) for k in GROUPS if (v := f(x.get(k))) is not None and abs(v) >= 0.005}}
        rid = str(int(x["race_id"]))
        if rid not in races:
            pace = [f(x.get("P(slow)")), f(x.get("P(even)")), f(x.get("P(fast)"))]
            races[rid] = {"pace": pace if None not in pace else None, "pv": f(x.get("pace vs distance avg")),
                          "on": str(x.get("scored_on"))[:10], "bias": bias.get(int(x["race_id"]))}
    payload = {"generated": dt.datetime.now(dt.timezone.utc).isoformat()[:19] + "Z", "trainEnd": str(m["train_end"])[:10],
               "a": float(m["a"]), "b": float(m["b"]), "posFlagThreshold": f(m.get("pos_flag_thr")),
               "races": races, "runners": runners,
               "tracking": track.get("total")}
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "racing_model.json").write_text(json.dumps(payload, separators=(",", ":")))
    print(f"racing_model.json: {len(races)} races, {len(runners)} runners", flush=True)


def tracking(arch, res):
    """Model vs market on resulted races, using the projections archived before each race."""
    x = arch.merge(res[["run_id", "finish", "sp"]], on="run_id", how="inner")
    for c in ["model %", "blend_a", "blend_b", "projected rating", "finish", "sp"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")      # object dtype after a concat with an empty archive
    x = x[x["finish"].notna() & (x["sp"] > 1)]
    x = x[~x["race_id"].isin(x.loc[x["model %"].isna(), "race_id"])]   # a runner without a projection
    ok = x.groupby("race_id").agg(n=("run_id", "size"), w=("finish", lambda s: (s == 1).sum()))
    x = x[x["race_id"].isin(ok.index[(ok.n >= 2) & (ok.w == 1)])].copy()
    if x.empty:
        return {"days": []}
    x = x.sort_values(["race_id", "run_id"])
    inv = 1 / x["sp"]
    x["p_sp"] = inv / inv.groupby(x["race_id"]).transform("sum")
    pm = (x["model %"] / 100).clip(1e-9)
    s = x["blend_a"] * np.log(pm) + x["blend_b"] * np.log(x["p_sp"])
    x["p_blend"] = np.exp(s - s.groupby(x["race_id"]).transform("max"))
    x["p_blend"] /= x.groupby("race_id")["p_blend"].transform("sum")
    x["p_model"] = pm / pm.groupby(x["race_id"]).transform("sum")
    w = x[x["finish"] == 1]
    rank = x.groupby("race_id")["projected rating"].rank(ascending=False)
    top_won = (x.assign(r=rank)[lambda t: t["r"] == 1].groupby("race_id")["finish"].min() == 1)
    days = []
    for d, g in w.groupby("race_date"):
        days.append({"date": str(d)[:10], "races": int(len(g)),
                     "ll_model": float(-np.log(g["p_model"]).mean()), "ll_blend": float(-np.log(g["p_blend"]).mean()),
                     "ll_sp": float(-np.log(g["p_sp"]).mean()),
                     "top_rated_won": float(top_won.reindex(g["race_id"]).mean())})
    return {"days": days, "total": {"races": int(len(w)), "ll_model": float(-np.log(w["p_model"]).mean()),
                                    "ll_blend": float(-np.log(w["p_blend"]).mean()),
                                    "ll_sp": float(-np.log(w["p_sp"]).mean()),
                                    "top_rated_won": float(top_won.mean())}}


def rescore(con, arch, since, today):
    """Past races archived by a model trained on or after `since` (e.g. a model hit by a bug), re-projected with
    one model trained before `since` (still pre-race). Market columns keep their archived pre-race fixed prices:
    the blend and edge are recomputed from those, never from SP or a post-race price."""
    old = arch[(arch["train_end"].astype(str) >= since) & (arch["race_date"].dt.date < today)]
    if old.empty:
        return old
    days = sorted(old["race_date"].dt.date.unique())
    c, m = race_card.score(con, since, [str(d) for d in days])
    c = c[c["run_id"].isin(old["run_id"])].copy()
    if c.empty:
        return c
    o = old.set_index("run_id")
    for k in ["fixed_win_price", "open_price"]:
        c[k] = pd.to_numeric(c["run_id"].map(o[k]), errors="coerce")
    inv = 1 / c["fixed_win_price"].where(c["fixed_win_price"] > 1)
    full = inv.notna().groupby(c["race_id"]).transform("all")
    s = m["a"] * np.log((c["model %"] / 100).clip(1e-12)) + m["b"] * np.log(inv / inv.groupby(c["race_id"]).transform("sum"))
    e = np.exp(s - s.groupby(c["race_id"]).transform("max"))
    pb = (e / e.groupby(c["race_id"]).transform("sum")).where(full)
    c["blend %"], c["blend $"] = 100 * pb, 1 / pb
    c["edge vs fixed"] = pb * c["fixed_win_price"] - 1
    print(f"rescored {len(c):,} runners on {len(days)} days (archived with train_end >= {since})", flush=True)
    return _archive_rows(c, m, since)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--no-store", action="store_true")
    ap.add_argument("--toprate-dir", default=None, help="write racing_model.json here (a TopRate checkout)")
    ap.add_argument("--site-dir", default=None, help="also write the per-day JSON for a static site")
    ap.add_argument("--rescore-from", default=None,
                    help="YYYY-MM-DD: re-project past races archived by a model trained on or after this date")
    a = ap.parse_args()
    today = dt.date.fromisoformat(a.date) if a.date else dt.datetime.now(ZoneInfo("Australia/Melbourne")).date()
    con = duckdb.connect(str(figure.DB), read_only=True)
    have = {r[0] for r in con.sql("select distinct race_date from races").fetchall()}
    upcoming = [d for d in [today] + _dates(today, AHEAD, 1) if d in have]
    recent = [d for d in _dates(today, BACK, -1) if d in have]
    if not a.no_store:
        store.get(ARCHIVE.name, ARCHIVE)
    arch = pd.read_csv(ARCHIVE, parse_dates=["race_date"]) if ARCHIVE.exists() else pd.DataFrame(columns=KEEP)
    arch["race_date"] = pd.to_datetime(arch["race_date"])   # an empty archive reads as object dtype

    if a.rescore_from:
        fixed = rescore(con, arch, a.rescore_from, today)
        fixed["race_date"] = pd.to_datetime(fixed["race_date"])
        arch = pd.concat([arch[~arch["run_id"].isin(fixed["run_id"])], fixed], ignore_index=True)
    c, m = race_card.score(con, str(today), [str(d) for d in upcoming])
    new = _archive_rows(c, m, today)
    missing = _missing_days(con, arch, recent)
    if missing:                      # one model trained before the earliest missing day (pre-race); rows already
                                     # archived keep their earlier projection (drop_duplicates below keeps first)
        cb, mb = race_card.score(con, str(min(missing)), [str(d) for d in missing])
        new = pd.concat([new, _archive_rows(cb, mb, min(missing))], ignore_index=True)
    new["race_date"] = pd.to_datetime(new["race_date"])
    # keep the earliest projection for past days and for races that have already started (a later run must not
    # overwrite a pre-race projection with one made after the jump); races still to run are replaced by this run
    started = _started_races(con)
    replace = arch["race_date"].dt.date.isin(upcoming) & ~arch["race_id"].astype("int64").isin(started)
    arch = arch[~replace]
    arch = pd.concat([arch, new], ignore_index=True).drop_duplicates(["run_id"], keep="first")
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    arch.to_csv(ARCHIVE, index=False, compression="gzip")
    if not a.no_store:
        store.put(ARCHIVE, ARCHIVE.name)

    days = sorted(set(upcoming) | set(recent))
    all_res = con.sql(RESULT_SQL.replace("where r.race_date in ({d})", "where r.race_date >= date '2026-01-01'")).df()
    track = tracking(arch, all_res)
    if a.toprate_dir:
        write_toprate(Path(a.toprate_dir), arch[arch["race_date"].dt.date.isin(days)], m, track)
    if not a.site_dir:
        return
    out = Path(a.site_dir)
    (out / "day").mkdir(parents=True, exist_ok=True)
    res = con.sql(RESULT_SQL.format(d=_sql_dates(days))).df()
    meta = con.sql(META_SQL.format(d=_sql_dates(days))).df()
    index = {"generated_utc": dt.datetime.now(dt.timezone.utc).isoformat()[:19], "today": str(today),
             "model": {"train_end": m["train_end"], "blend_a": m["a"], "blend_b": m["b"]}, "days": []}
    for d in days:
        rows = arch[arch["race_date"].dt.date == d]
        if rows.empty:
            continue
        j = day_json(d, rows, res, meta)
        (out / "day" / f"{d}.json").write_text(json.dumps(j, separators=(",", ":")))
        index["days"].append({"date": str(d), "kind": "upcoming" if d >= today else "recent",
                              "meetings": [{"track": mt["track"], "state": mt["state"], "races": len(mt["races"])}
                                           for mt in j["meetings"]]})
    (out / "tracking.json").write_text(json.dumps(track))
    (out / "index.json").write_text(json.dumps(index, default=_clean))
    print(f"exported {len(index['days'])} days; archive {len(arch):,} runners", flush=True)


if __name__ == "__main__":
    main()
