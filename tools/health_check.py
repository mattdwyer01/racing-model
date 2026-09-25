"""Daily data health check for the dashboard pipeline: fails loudly when an input the models rely on is broken.

    python tools/health_check.py                 # prints the report; exit 1 if any check fails
    python tools/health_check.py --report out.md

Every check here is a real failure from 25 Sep 2026 that nothing flagged at the time:
  results_fresh / results_final    TopRate race_results_<year>.csv.gz stopped at 13 Sep and kept PRELIMINARY WPRs
  weights_today                    carried weights missing (TopRate stopped sending them; TAB / runner-page fallbacks)
  model_fit                        a NaN figure fit scored every horse as a debutant (dm = 0, debut trial terms on)
  model_fresh / model_coverage     racing_model.json stale or missing today's races
  payload_fresh / payload_weights  toprate_data.json not refreshed, or refreshed without weights / projections
  model_adjustments                the race-day adjustment the Combo view swaps in is missing
Reads the published files from GitHub (TopRate repo, public), so it checks what the dashboard actually serves.
"""
import argparse
import datetime as dt
import gzip
import io
import json
import sys
from zoneinfo import ZoneInfo

import pandas as pd
import requests

TR = "https://raw.githubusercontent.com/mattdwyer01/toprate/main/"
MEL = ZoneInfo("Australia/Melbourne")
CORE = {"VIC", "SA", "QLD"}


def get(name, gz=False):
    r = requests.get(TR + name, timeout=180)
    r.raise_for_status()
    return gzip.decompress(r.content) if gz else r.content


def hours_since(iso):
    t = pd.Timestamp(iso)
    t = t.tz_localize("UTC") if t.tzinfo is None else t
    return (pd.Timestamp.now(tz="UTC") - t).total_seconds() / 3600


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default=None)
    a = ap.parse_args()
    now = dt.datetime.now(MEL)
    today = now.date().isoformat()
    results = []

    def check(name, ok, detail):
        results.append((name, bool(ok), detail))

    def guard(name, fn):
        try:
            fn()
        except Exception as e:
            check(name, False, f"could not run: {type(e).__name__}: {str(e)[:160]}")

    def results_checks():
        d = pd.read_csv(io.BytesIO(get(f"race_results_{now.year}.csv.gz", gz=True)), low_memory=False,
                        usecols=["date", "wprStatus"])
        d["date"] = d["date"].astype(str).str[:10]
        last = d["date"].max()
        lag = (now.date() - dt.date.fromisoformat(last)).days
        check("results_fresh", lag <= 2, f"latest race in race_results_{now.year}: {last} ({lag} days old; limit 2)")
        old = d[d["date"] <= (now.date() - dt.timedelta(days=7)).isoformat()]
        old = old[old["date"] >= (now.date() - dt.timedelta(days=60)).isoformat()]
        share = (old["wprStatus"].astype(str).str.lower() == "preliminary").mean() if len(old) else 0.0
        check("results_final", share <= 0.02, f"{share:.1%} of runs 7 to 60 days old still Preliminary (limit 2%)")

    def runners_checks():
        d = pd.read_csv(io.BytesIO(get("toprate_runners.csv")), low_memory=False, dtype=str, keep_default_na=False,
                        usecols=["date", "state", "weight_carried", "scratched"])
        t = d[(d["date"] == today) & (d["scratched"] != "1") & (d["scratched"] != "1.0")]
        if len(t) == 0:
            check("weights_today", True, "no runners today")
            return
        fill = (t["weight_carried"].str.strip() != "").mean()
        check("weights_today", fill >= 0.8, f"{fill:.0%} of today's {len(t):,} runners have a carried weight (limit 80%)")

    def model_checks():
        m = json.loads(get("racing_model.json"))
        age = hours_since(m["generated"])
        check("model_fresh", age <= 26, f"racing_model.json generated {age:.1f} h ago (limit 26 h)")
        h = m.get("health") or {}
        if h.get("error"):
            check("model_fit", False, f"model health numbers failed to compute: {h['error']}")
            h = {}
        dz, dt_on = h.get("dm_zero_share"), h.get("debut_trial_on_runners")
        ok = dz is not None and dz <= 0.2 and (dt_on or 0) <= 0.01
        check("model_fit", ok, f"runs with history but no form figure {dz}, non-debutants with debut trial terms "
              f"{dt_on} (limits 0.2 / 0.01); card runners without weight {h.get('card_no_weight_share')}")
        races = {k: v for k, v in m["races"].items()}
        check("model_coverage", len(m["runners"]) > 0 and len(races) > 0,
              f"{len(races):,} races, {len(m['runners']):,} runners projected")
        d = [r.get("d") for r in m["runners"].values()]
        share = sum(x is not None for x in d) / max(len(d), 1)
        check("model_adjustments", share >= 0.9, f"{share:.0%} of projected runners have a race-day adjustment (limit 90%)")

    def payload_checks():
        p = json.loads(get("toprate_data.json.gz", gz=True))
        age = hours_since(p["RUN_ISO"])
        racing = 10 <= now.hour <= 18
        check("payload_fresh", age <= (2 if racing else 14),
              f"toprate_data.json refreshed {age:.1f} h ago (limit {2 if racing else 14} h {'in' if racing else 'outside'} racing hours)")
        check("payload_split", bool(p.get("HISTORY_ISO")), "HISTORY_ISO present (history split file written)")
        rs = [ru for r in p["RACES"] if r.get("date") == today and r.get("state") in CORE for ru in r.get("runners", [])
              if not ru.get("scr")]
        if rs:
            wt = sum(ru.get("wt") is not None for ru in rs) / len(rs)
            pj = sum(ru.get("wpjp") is not None for ru in rs) / len(rs)
            check("payload_weights", wt >= 0.7 and pj >= 0.8,
                  f"today's VIC/SA/QLD runners in the payload: {wt:.0%} with a weight (limit 70%), "
                  f"{pj:.0%} with a WPR projection (limit 80%)")

    guard("results", results_checks)
    guard("runners", runners_checks)
    guard("model", model_checks)
    guard("payload", payload_checks)

    bad = [r for r in results if not r[1]]
    lines = [f"# Data health {now:%Y-%m-%d %H:%M} AEST: {'OK' if not bad else f'{len(bad)} FAILED'}", "",
             "| check | ok | detail |", "|---|---|---|"]
    lines += [f"| {n} | {'yes' if ok else '**NO**'} | {d} |" for n, ok, d in results]
    text = "\n".join(lines) + "\n"
    print(text)
    if a.report:
        open(a.report, "w").write(text)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
