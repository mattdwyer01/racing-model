"""GPS race pace target and VIC/SA ground loss in the race-day projection.

    python model/projection_gps.py      # walk-forward -> reports/projection_gps.md

GPS pace (per race, QLD RQ and VIC/SA racing.com Triple S, races >= 1000m):
  E = mean speed of the 3 leaders (positions about 200m after the start) over the 2 sections after the first
      (the first 200m includes the standing start)
  L = median speed of the field over the last 400m
  gps_pace = 100 * log(E / L): how much faster the leaders went early than the field finished. Self-normalising
  for track, going and class, unlike raw times
Pace projection: the v3 pace inputs (projection.PACE_X), target gps_pace, fitted on GPS races before the fold;
  projected for every race. Compared with the v3 projection (target TopRate early shape) on how well each
  predicts the actual GPS pace.
Ground loss: the ground-loss model (projection.GL_X) now trains on QLD + VIC/SA GPS (gps_runs was rebuilt with
  racing.com Triple S). Compared with a QLD-only fit on VIC, SA and QLD test runs.
Win logit (figure + projection, as projection.py) per fold, paired by race:
  v3              projection v3 (ground loss fitted on all GPS states)
  gl QLD only     ground loss fitted on QLD GPS only (the pre-rebuild state)
  + GPS pace      v3 + projected GPS pace and projected GPS pace x (1 - projected settle)
"""
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model import figure, projection  # noqa: E402
from model.projection import GL_X, PACE_X, _fit, _r2  # noqa: E402

FOLDS = [2023, 2024, 2025, 2026]
GPS_PACE = ["proj_gps_pace", "proj_gps_pace_x"]
SPEED_OK = (8.0, 22.0)


def _race_pace(s, key, early_mask, lead_rank, late_mask):
    """s: one row per runner x section with columns key, run, speed. Returns gps_pace per race key."""
    e = s[early_mask].groupby([key, "run"])["speed"].mean()
    lead = lead_rank.groupby(level=0, group_keys=False).nsmallest(3)
    lead_idx = pd.MultiIndex.from_arrays([lead.index.get_level_values(key), lead.index.get_level_values("run")])
    E = e.reindex(lead_idx).groupby(level=0).mean()
    L = s[late_mask].groupby([key, "run"])["speed"].mean().groupby(level=0).median()
    return (100 * np.log(E / L)).dropna()


def gps_pace(con):
    """gps_pace per race_id (QLD RQ + VIC/SA racing.com Triple S)."""
    from model.extra_history import RC_SECTIONS, SECTIONS
    out = []
    if SECTIONS.exists():
        s = pd.read_parquet(SECTIONS, columns=["race_code", "tab_no", "cum_dist_m", "rank", "avg_speed_ms"])
        s["race_code"] = s["race_code"].astype(str)
        s = s.rename(columns={"avg_speed_ms": "speed", "tab_no": "run"})
        s = s[s["speed"].between(*SPEED_OK)]
        first = s.groupby("race_code")["cum_dist_m"].transform("min")
        last = s.groupby("race_code")["cum_dist_m"].transform("max")
        s = s[last >= 1000]
        first, last = first[s.index], last[s.index]
        at = s[(s["cum_dist_m"] == first + 200) & s["rank"].between(1, 30)].set_index(["race_code", "run"])["rank"]
        p = _race_pace(s, "race_code", (s["cum_dist_m"] > first) & (s["cum_dist_m"] <= first + 400), at,
                       s["cum_dist_m"] > last - 400)
        key = con.sql("select distinct race_id, src_race race_code from gps_runs where source = 'rq'").df()
        key["race_code"] = key["race_code"].astype(str)
        out.append(key.join(p.rename("gps_pace"), on="race_code"))
    if RC_SECTIONS.exists():
        s = pd.read_parquet(RC_SECTIONS, columns=["meet_code", "race_no", "tab_no", "from_m", "to_m", "pos", "avg_speed_ms"])
        s["race_code"] = s["meet_code"].astype(str) + "_" + s["race_no"].astype(str)
        tri = con.sql("select distinct src_race race_code from gps_runs where source = 'rc' and res_gps_dist_m is not null").df()
        s = s[s["race_code"].isin(tri["race_code"])]            # Triple S: whole race covered
        s = s.rename(columns={"avg_speed_ms": "speed", "tab_no": "run"})
        s = s[s["speed"].between(*SPEED_OK)]
        start = s.groupby("race_code")["from_m"].transform("max")
        s = s[start >= 1000]
        start = start[s.index]
        at = s[(s["to_m"] == start - 200) & s["pos"].between(1, 30)].set_index(["race_code", "run"])["pos"]
        p = _race_pace(s, "race_code", (s["to_m"] >= start - 600) & (s["to_m"] <= start - 400), at, s["to_m"] < 400)
        key = con.sql("select distinct race_id, src_race race_code from gps_runs where source = 'rc'").df()
        out.append(key.join(p.rename("gps_pace"), on="race_code"))
    g = pd.concat(out, ignore_index=True).dropna(subset=["gps_pace"])
    g = g[g["gps_pace"].between(-30, 30)]
    return g.groupby("race_id")["gps_pace"].mean()


def _with_gl(x, extras, mask_fit):
    """Refit the ground-loss model on mask_fit rows and recompute proj_gl / proj_adj."""
    x = x.copy()
    x["proj_gl"] = _fit(x.loc[mask_fit, GL_X], x.loc[mask_fit, "y_gl"]).predict(x[GL_X].to_numpy(float))
    x["proj_gl"] -= x.groupby("race_id")["proj_gl"].transform("mean")
    c = extras["cost"]
    adj = c["settle"] * x["proj_settle"] + c["pace"] * x["proj_pace"] + c["gl"] * x["proj_gl"]
    x["proj_adj"] = adj - adj.groupby(x["race_id"]).transform("mean")
    return x


def main():
    from model.validate_figure import FIG, eval_set, fit_eval, race_ll
    con = duckdb.connect(str(figure.DB), read_only=True)
    x0 = projection.frame(con)
    gp = gps_pace(con)
    print("frame", len(x0), "gps pace races", len(gp), flush=True)
    WIN = FIG + ["barrier_pct", "proj_settle", "proj_pace", "proj_gl", "proj_adj"] + projection.BIAS
    variants = {"v3": WIN, "gl QLD only": WIN, "+ GPS pace": WIN + GPS_PACE}
    acc, per, states, cost = [], {}, [], {}
    for y in FOLDS:
        te_end = f"{y}-01-01"
        x, r, ex = projection.project(x0, te_end)
        r = r.join(gp.rename("gps_pace"))
        rtr = (r["race_date"] < te_end) & r["gps_pace"].notna()
        r["proj_gps_pace"] = _fit(r.loc[rtr, PACE_X], r.loc[rtr, "gps_pace"]).predict(r[PACE_X].to_numpy(float))
        rte = r[(r["race_date"].dt.year == y) & r["gps_pace"].notna()]
        acc += [{"fold": y, "metric": "GPS pace R2: GPS pace model", "v": _r2(rte.gps_pace, rte.proj_gps_pace)},
                {"fold": y, "metric": "GPS pace corr: v3 shape projection", "v": rte[["gps_pace", "proj_shape"]].corr().iloc[0, 1]},
                {"fold": y, "metric": "GPS pace corr: GPS pace model", "v": rte[["gps_pace", "proj_gps_pace"]].corr().iloc[0, 1]},
                {"fold": y, "metric": "GPS pace vs actual TopRate shape corr", "v": rte[["gps_pace", "y_shape"]].corr().iloc[0, 1]},
                {"fold": y, "metric": "GPS pace races in test", "v": len(rte)}]
        x = x.join(r[["proj_gps_pace", "gps_pace"]], on="race_id")
        x["proj_gps_pace_x"] = x["proj_gps_pace"] * (1 - x["proj_settle"])
        # WPR cost of GPS pace for on-pace runners (within race, GPS races before the fold)
        t = x[(x.race_date < te_end) & x.gps_pace.notna() & (x.h_none == 0) & x.y_settle.notna() & x.wpr.notna()]
        z = pd.DataFrame({"perf": t.wpr - t.h_wpr, "on_pace": t.gps_pace * (1 - t.y_settle), "settle": t.y_settle})
        z = z - z.groupby(t["race_id"].to_numpy()).transform("mean")
        cost[y] = dict(zip(["on_pace x gps_pace", "settle"], np.linalg.lstsq(
            z[["on_pace", "settle"]].to_numpy(float), z["perf"].to_numpy(float), rcond=None)[0]))
        # ground loss: all GPS states (v3 now) vs QLD only
        trm = (x.race_date < te_end) & (x.race_date >= "2019-01-01") & x.y_gl.notna()
        xq = _with_gl(x, ex, trm & (x.state == "QLD"))
        te = x[(x.race_date.dt.year == y) & x.in_scope]
        teq = xq[(xq.race_date.dt.year == y) & xq.in_scope]
        for st in ["QLD", "VIC", "SA"]:
            a, b = te[te.state == st], teq[teq.state == st]
            acc += [{"fold": y, "metric": f"ground loss R2 {st}: fit on all GPS", "v": _r2(a.y_gl, a.proj_gl)},
                    {"fold": y, "metric": f"ground loss R2 {st}: fit on QLD only", "v": _r2(b.y_gl, b.proj_gl)}]
        for name, cols in variants.items():
            e = eval_set(xq if name == "gl QLD only" else x)
            tr, tt = e[e.race_date < te_end], e[e.race_date.dt.year == y]
            per.setdefault(name, []).append(race_ll(fit_eval(tr, tt, cols)[0], tt))
            if name == "v3":
                states.append(tt.loc[tt.won == 1, "state"].to_numpy())
        print(y, {k: round(float(v[-1].mean()), 4) for k, v in per.items()}, flush=True)

    st = np.concatenate(states)
    P = {k: np.concatenate(v) for k, v in per.items()}
    rng = np.random.default_rng(0)

    def ci(z):
        b = [z[rng.integers(0, len(z), len(z))].mean() for _ in range(2000)]
        return f"{z.mean():+.4f} ({np.percentile(b, 2.5):+.4f} to {np.percentile(b, 97.5):+.4f})"
    rows = []
    for a, b in [("v3", "gl QLD only"), ("+ GPS pace", "v3")]:
        d = P[a] - P[b]
        rows.append({"model": a, "vs": b, "all": ci(d), "QLD": ci(d[st == "QLD"]), "VIC": ci(d[st == "VIC"]),
                     "SA": ci(d[st == "SA"])})
    A = pd.DataFrame(acc).pivot(index="metric", columns="fold", values="v")
    L = ["# GPS pace target and VIC/SA ground loss", "",
         "- gps_pace = 100 x log(leaders' speed 200 to 600m after the start / field median speed over the last 400m);"
         " QLD RQ and VIC/SA racing.com Triple S races of 1000m+", "",
         "## Projection accuracy (test year)", "", A.to_markdown(floatfmt=".3f"), "",
         "## WPR cost of GPS pace (within race, fitted before each fold)", "",
         "on_pace x gps_pace: WPR per unit of gps_pace x (1 - settle share); negative = a hot pace costs on-pace runners",
         "", pd.DataFrame(cost).to_markdown(floatfmt=".3f"), "",
         "## Win logit, figure + projection (pooled race log loss)", "",
         pd.Series({k: v.mean() for k, v in P.items()}).to_frame("log loss").to_markdown(floatfmt=".4f"), "",
         "## Paired differences (negative = first is better; 95% race bootstrap; state of the race)", "",
         pd.DataFrame(rows).to_markdown(index=False)]
    out = ROOT / "reports/projection_gps.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
