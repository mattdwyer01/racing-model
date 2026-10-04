"""Live 'Proj value' model: where the market (SP / fixed price) is wrong, from pre-race flags.

Fitted by tools/value_model.py --fit-live (params in model/value_params.json); scored in tools/race_card.score and
exported to TopRate's racing_model.json as per-runner `vu` (value utility) and per-race `vs` (price slope). The win
chance at a price is p = softmax(vs x log p_price + vu) within the race, p_price = normalised 1 / fixed price; value =
p x fixed price. Test (tools/value_model.py, walk-forward 2024 to Sep 2026, SP): value >= 1.0 and SP <= $21 made
+2.4% over 1,892 bets.

Inputs (all known before the race): barrier, distance change, days since last start, prep run, age, jockey 365-day
strike rate, apprentice (jockey claimed in the last 120 days: the live runners carry no claim), last start's stewards /
video comments, GPS extra ground and L600 vs that race's field, sire wet / staying index (progeny strike rates on
earlier dates), the race-day projection (proj_adj + bias_adj), prior WPR level, debutant; race conditions enter as
interactions with the log price (field 13+, wet 7+, QLD, a first starter in the race, sprint < 1200m).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

PARAMS = Path(__file__).with_name("value_params.json")
STEW = {"wide": r"wide throughout|raced wide|without cover|three wide|four wide|3 wide|4 wide",
        "heldup": r"held up|checked|hampered|crowded|struck interference|inconvenienced|blocked|steadied",
        "laid": r"laid in|laid out|hung out|hung in|shifted",
        "vet": r"lame|bled|blood|heart|cardiac|respirat|soreness|sore "}
EVERY = r"every chance|had its chance"
COLS = ["lsp", "wpr_r", "adj_r", "bias_r", "debut", "f_barrier10", "f_dist_down", "f_dist_up", "f_back14", "f_4thup",
        "f_age6", "f_weak_jockey", "f_sm", "f_bias", "f_wide", "f_gps_ground", "f_heldup", "f_laid", "f_vet",
        "f_l600_worst", "f_wet_poor_sire", "n_top_jockey", "n_apprentice", "n_every_chance", "n_stay_poor_sire",
        "lsp_x_field13", "lsp_x_wet", "lsp_x_qld", "lsp_x_fs_race", "lsp_x_sprint"]
SLOPE = {"lsp": None, "lsp_x_field13": "field13", "lsp_x_wet": "wet", "lsp_x_qld": "qld", "lsp_x_fs_race": "fs_race",
         "lsp_x_sprint": "sprint"}


def _strike(r, key):
    x = r[r["res_won"].notna()].groupby([key, "race_date"]).agg(w=("res_won", "sum"), n=("res_won", "size")).reset_index()
    out = []
    for k, g in x.sort_values([key, "race_date"]).groupby(key, sort=False):
        t = g.set_index("race_date")[["w", "n"]].rolling("365D").sum().shift(1)
        t[key] = k
        out.append(t.reset_index())
    s = pd.concat(out, ignore_index=True)
    s[key + "_sr"], s[key + "_n"] = s["w"] / s["n"], s["n"]
    # carry each jockey's latest window forward to dates without a ride that day (upcoming races)
    return s[[key, "race_date", key + "_sr", key + "_n"]]


def facts(con, out_from):
    """Per-run inputs for every run on or after out_from (resulted or upcoming), from the DB's earlier runs."""
    r = con.sql("""select cast(u.run_id as varchar) run_id, u.race_id, u.horse_id, u.race_date, u.barrier, u.jockey,
                          u.sire_id, u.age, u.prep_run, u.days_since_start, u.weight_claim_kg, u.res_won, u.res_finish,
                          u.res_s_l600, u.res_stewards, u.res_video, r.going_num, r.distance, r.state
                   from runs u join races r using (race_id)
                   where u.race_date >= date '2018-01-01' and not coalesce(u.is_trial_or_jumpout, false)""").df()
    r["race_date"] = pd.to_datetime(r["race_date"])
    r["res_won"] = r["res_won"].astype(float)
    gx = con.sql("select cast(run_id as varchar) run_id, res_gps_extra_m from gps_runs").df().drop_duplicates("run_id")
    r = r.merge(gx, on="run_id", how="left")
    g = r.groupby("race_id")
    r["gps_rel"] = r["res_gps_extra_m"] - g["res_gps_extra_m"].transform("mean")
    l6 = pd.to_numeric(r["res_s_l600"], errors="coerce")
    r["l600_rel"] = l6 - l6.groupby(r["race_id"]).transform("mean")
    ok = r["l600_rel"].notna() & r["res_finish"].notna()
    if np.corrcoef(r.loc[ok, "l600_rel"], -pd.to_numeric(r.loc[ok, "res_finish"], errors="coerce"))[0, 1] < 0:
        r["l600_rel"] = -r["l600_rel"]                      # higher = closed better
    stew, vid = r["res_stewards"].fillna("").str.lower(), r["res_video"].fillna("").str.lower()
    for k, pat in STEW.items():
        r["cs_" + k] = stew.str.contains(pat, regex=True).astype(float)
    r["cs_every"] = vid.str.contains(EVERY, regex=True).astype(float)
    r = r.sort_values(["horse_id", "race_date", "run_id"]).reset_index(drop=True)
    # last start = the latest earlier row that was actually run: an upcoming entry (no result, no SP, today or later) is
    # never a horse's last start, so a horse entered on several upcoming days keeps its real last run
    upcoming = r["res_finish"].isna() & r["res_won"].isna() & (r["race_date"] >= pd.Timestamp.today().normalize())
    pos = pd.Series(np.where(upcoming, np.nan, np.arange(len(r))), index=r.index)
    prev = pos.groupby(r["horse_id"]).transform(lambda s: s.shift(1).ffill())
    ok = prev.notna()
    idx = prev[ok].astype(int).to_numpy()
    for c in ["distance", "gps_rel", "l600_rel", "cs_wide", "cs_heldup", "cs_laid", "cs_vet", "cs_every"]:
        name = "last_distance" if c == "distance" else "last_" + c
        r[name] = np.nan
        r.loc[ok, name] = r[c].to_numpy()[idx]
    # sire progeny strike rates on earlier dates (wet 7+, 1600m+, all)
    r = r.sort_values("race_date")
    res = r[r["res_won"].notna()]
    for tag, m in (("wet", res["going_num"] >= 7), ("stay", res["distance"] >= 1600), ("all", res["res_won"].notna())):
        x = res[m.fillna(False)].groupby(["sire_id", "race_date"]).agg(w=("res_won", "sum"), n=("res_won", "size")).reset_index()
        x = x.sort_values(["sire_id", "race_date"])
        gg = x.groupby("sire_id")
        x[f"sw_{tag}"], x[f"sn_{tag}"] = gg["w"].cumsum(), gg["n"].cumsum()
        r = pd.merge_asof(r.sort_values("race_date"), x[["sire_id", "race_date", f"sw_{tag}", f"sn_{tag}"]].sort_values("race_date"),
                          on="race_date", by="sire_id", direction="backward", allow_exact_matches=False)
    for tag in ("wet", "stay"):
        idx = (r[f"sw_{tag}"] / r[f"sn_{tag}"]) / (r["sw_all"] / r["sn_all"])
        r[f"sire_{tag}_idx"] = idx.where(r[f"sn_{tag}"] >= 50)
    # jockey 365-day strike rate up to the day before; apprentice = claimed on any ride in the previous 120 days
    out = r[r["race_date"] >= pd.Timestamp(out_from)].copy()
    js = _strike(r[r["race_date"] >= pd.Timestamp(out_from) - pd.Timedelta(days=400)], "jockey")
    out = pd.merge_asof(out.sort_values("race_date"), js.sort_values("race_date"), on="race_date", by="jockey",
                        direction="backward")
    cl = r.loc[r["weight_claim_kg"].fillna(0) > 0, ["jockey", "race_date"]].drop_duplicates().rename(columns={"race_date": "claim_date"})
    cl["race_date"] = cl["claim_date"]
    out = pd.merge_asof(out.sort_values("race_date"), cl.sort_values("race_date"), on="race_date", by="jockey",
                        direction="backward", allow_exact_matches=False)
    out["appr"] = ((out["race_date"] - out["claim_date"]).dt.days <= 120).astype(float)
    keep = ["run_id", "barrier", "distance", "last_distance", "days_since_start", "prep_run", "age", "jockey_sr",
            "jockey_n", "appr", "going_num", "state"] + [c for c in out if c.startswith("last_") and c != "last_distance"] + \
        ["sire_wet_idx", "sire_stay_idx"]
    return out[keep]


def design(x, thr):
    """Model inputs. x: one row per runner with race_id, sp-free market column `lsp` (optional), proj_adj, bias_adj,
    h_wpr, h_none, dist, plus facts(). thr: thresholds (sm, bias, gps, l600)."""
    x = x.copy()
    g = x.groupby("race_id")
    x["n"] = g["run_id"].transform("size")
    adj = x["proj_adj"].fillna(0) + x["bias_adj"].fillna(0)
    x["adj_r"] = adj - adj.groupby(x["race_id"]).transform("mean")
    x["bias_r"] = (x["bias_adj"] - g["bias_adj"].transform("mean")).fillna(0)
    x["wpr_r"] = (x["h_wpr"] - g["h_wpr"].transform("mean")).fillna(0)
    x["debut"] = x["h_none"].fillna(0).astype(float)
    b = lambda c: pd.to_numeric(x[c], errors="coerce").fillna(0) > 0  # noqa: E731
    F = {"f_barrier10": x["barrier"] >= 10, "f_dist_down": x["distance"] <= x["last_distance"] - 200,
         "f_dist_up": x["distance"] >= x["last_distance"] + 200, "f_back14": x["days_since_start"] <= 14,
         "f_4thup": x["prep_run"] >= 4, "f_age6": x["age"] >= 6,
         "f_weak_jockey": (x["jockey_sr"] < 0.07) & (x["jockey_n"] >= 50),
         "f_sm": x["adj_r"] >= thr["sm"], "f_bias": x["bias_adj"] >= thr["bias"],
         "f_wide": b("last_cs_wide"), "f_gps_ground": x["last_gps_rel"] >= thr["gps"],
         "f_heldup": b("last_cs_heldup"), "f_laid": b("last_cs_laid"), "f_vet": b("last_cs_vet"),
         "f_l600_worst": x["last_l600_rel"] <= thr["l600"],
         "f_wet_poor_sire": (x["going_num"] >= 7) & (x["sire_wet_idx"] <= 0.8),
         "n_top_jockey": (x["jockey_sr"] >= 0.18) & (x["jockey_n"] >= 50), "n_apprentice": x["appr"] > 0,
         "n_every_chance": b("last_cs_every"), "n_stay_poor_sire": (x["dist"] >= 1600) & (x["sire_stay_idx"] <= 0.8)}
    for k, v in F.items():
        x[k] = pd.Series(v, index=x.index).fillna(False).astype(float)
    x["field13"] = (x["n"] >= 13).astype(float)
    x["wet"] = (x["going_num"].fillna(4) >= 7).astype(float)
    x["qld"] = (x["state"] == "QLD").astype(float)
    x["fs_race"] = (g["h_none"].transform("max").fillna(0) > 0).astype(float)
    x["sprint"] = (x["dist"] < 1200).astype(float)
    if "lsp" in x:
        for c, cond in SLOPE.items():
            if cond:
                x[c] = x["lsp"] * x[cond]
    return x


def load():
    return json.loads(PARAMS.read_text()) if PARAMS.exists() else None


def score(x, params):
    """Per-runner value utility `vu` and per-runner (race-constant) price slope `vs`."""
    beta = params["beta"]
    vu = sum(beta[c] * x[c] for c in COLS if c in beta and c not in SLOPE)
    vs = beta["lsp"] + sum(beta[c] * x[cond] for c, cond in SLOPE.items() if cond)
    return pd.DataFrame({"run_id": x["run_id"], "vu": vu, "vs": vs})


# Signals shown on the dashboard (green / red count badges): the user's chosen set (5 Oct 2026) from the filter screens
# (reports/filter_screen*.md): positive = back within 14 days, 4th+ up, speed map favoured, track bias helps, raced
# wide / held up / laid or hung / vet issue last start; negative = apprentice, 'every chance' last start, staying trip
# with a weak staying sire. Independent of the value model's weights (the V badge uses the value model).
SIGNALS = ["f_back14", "f_4thup", "f_sm", "f_bias", "f_wide", "f_heldup", "f_laid", "f_vet",
           "n_apprentice", "n_every_chance", "n_stay_poor_sire"]


def signals(x, params=None):
    """Per runner: '|'-joined codes of the active signals (SIGNALS)."""
    keep = [c for c in SIGNALS if c in x]
    on = x[keep].to_numpy() > 0
    codes = np.array(keep)
    return pd.Series(["|".join(codes[row]) for row in on], index=x.index)
