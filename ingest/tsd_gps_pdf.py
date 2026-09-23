"""Parse Triple S Data GPS sectional PDFs (racing.com VIC/SA, Racing Queensland).

One PDF = one race (racing.com) or one meeting (RQ). Same template for both.

Outputs two tidy tables:
  runs      one row per runner: finish, time, margin, distance travelled, top speed, stride summary
  sections  one row per runner per 200m section: section time, cumulative time, rank,
            speed, stride length, stride rate, distance from rail
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import pdfplumber

logging.getLogger("pdfminer").setLevel(logging.ERROR)

TIME = r"\d+:\d{2}\.\d{2}"
NUM = r"-?\d+(?:\.\d+)?"


def _t(s: str | None) -> float | None:
    """'1:21.29' -> 81.29 seconds."""
    if not s or "-" in s and ":" in s and s.startswith("-"):
        return None
    m, s2 = s.split(":")
    return int(m) * 60 + float(s2)


# ---------------------------------------------------------------- header

def _header(text: str) -> dict:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    h = {"track": lines[1].title()}
    m = re.search(r"^(.*?)\s*●\s*\w{3}\s+(\d{1,2}\s+\w{3}\s+\d{4})", lines[2])
    h["state"] = m.group(1).strip().title()
    h["date"] = datetime.strptime(m.group(2).title(), "%d %b %Y").date()
    m = re.search(r"TRACK - (.*?)\s+WEATHER - (.*?)\s+RAIL - (.*?)\s+TELEMETRY", text)
    if m:
        h["going"], h["weather"], h["rail"] = (x.strip() for x in m.groups())
    m = re.search(r"TELEMETRY · (\d+) RUNNERS", text)
    h["telemetry_runners"] = int(m.group(1)) if m else None
    m = re.search(r"^(\d{1,2}:\d{2} [AP]M)$", text, re.M)
    h["start_time"] = m.group(1) if m else None
    m = re.search(r"SCRATCHED.*?\n(.*?)\s+\[ \]", text, re.S)
    h["scratched"] = m.group(1).strip() if m else ""
    return h


def _race_no_name_dist(text: str) -> tuple[int, str, int]:
    # summary page: "9 1400\nRACE Sportsbet Sir Rupert Clarke Stakes m"
    m = re.search(r"^(\d{1,2}) (\d{3,4})\nRACE (.*?) m$", text, re.M)
    return int(m.group(1)), m.group(3).strip(), int(m.group(2))


# ---------------------------------------------------------------- summary pages

ROW1 = re.compile(
    rf"^(\d+|DNF|DNT) (\d+) (.+?) ({TIME}|-:--\.--) (—|[\d.]+L) ([\d.]+) ([\d.]+) ((?:{TIME}|-:--\.--)(?: (?:{TIME}|-:--\.--))*)$"
)
ROW2 = re.compile(rf"^(\d+) (.+?) (\d+)(?: \(([+-]?\d+)\))? ([\d.]+) (\d+-\d+) (.*)$")
SPLIT = re.compile(r"\(([\d.]+|-\.--)\)(?:\[(\d+)\])?")


def _parse_summary(text: str, hdr: dict, race_no: int, dist: int) -> list[dict]:
    lines = text.splitlines()
    head = next(l for l in lines if l.startswith("RANK BAR"))
    marks = [int(x) for x in re.findall(r"L(\d+)", next(l for l in lines if l.startswith("TAB MARGIN")))]
    out = []
    for i, l in enumerate(lines):
        m1 = ROW1.match(l)
        if not m1 or i + 1 >= len(lines):
            continue
        m2 = ROW2.match(lines[i + 1])
        if not m2:
            continue
        rank, tab, horse, t, marg, first400, top, cum = m1.groups()
        bar, jockey, dt, dtw, last600, topsect, splits = m2.groups()
        cum_t = cum.split()
        sp = SPLIT.findall(splits)
        row = dict(
            **{k: hdr[k] for k in ("date", "track", "state")},
            race_no=race_no, distance=dist, finish=rank, tab_no=int(tab), barrier=int(bar),
            horse=horse.strip(), jockey=jockey.strip(), time_s=_t(t) if ":" in t and "-" not in t else None,
            margin_l=0.0 if marg == "—" else float(marg[:-1]), dist_travelled_m=int(dt),
            dist_vs_winner_m=int(dtw) if dtw else 0, first400_s=float(first400), last600_s=float(last600),
            top_speed_kmh=float(top), top_speed_section=topsect,
        )
        row["_sections"] = [
            dict(mark=mk, cum_s=_t(c) if "-" not in c else None,
                 split_s=float(s) if s != "-.--" else None, rank=int(r) if r else None)
            for mk, c, (s, r) in zip(marks, cum_t, sp)
        ]
        out.append(row)
    return out


# ---------------------------------------------------------------- horse pages

PANELS = {  # quadrant -> metric
    ("L", "T"): "speed_kmh", ("R", "T"): "stride_m",
    ("L", "B"): "stride_hz", ("R", "B"): "rail_m",
}


def _parse_horse_page(page) -> dict | None:
    p = page.dedupe_chars()
    words = p.extract_words()
    text = p.extract_text()
    if "Distance from Rail" not in text:
        return None
    lines = [l for l in text.splitlines() if l.strip()]
    horse = lines[4].strip()
    tab = int(re.search(r"TAB (\d+)", text).group(1))
    W, H = p.width, p.height
    # axis labels: numeric words that are multiples of 200 sitting on panel baselines
    axes = [w for w in words if re.fullmatch(r"\d{3,4}", w["text"]) and int(w["text"]) % 200 == 0
            and w["top"] > H * 0.45]
    vals = [w for w in words if re.fullmatch(rf"{NUM}m?", w["text"]) and w["top"] > H * 0.45
            and w not in axes]
    out = {}
    for v in vals:
        qx = "L" if v["x0"] < W / 2 else "R"
        # the baseline row directly below this value, within the same quadrant
        cand = [a for a in axes if a["top"] > v["top"] and (a["x0"] < W / 2) == (qx == "L")]
        if not cand:
            continue
        base = min(a["top"] for a in cand)
        row = [a for a in cand if abs(a["top"] - base) < 3]
        qy = "T" if base < H * 0.75 else "B"
        xc = (v["x0"] + v["x1"]) / 2
        a = min(row, key=lambda a: abs((a["x0"] + a["x1"]) / 2 - xc))
        out[(int(a["text"]), PANELS[(qx, qy)])] = float(v["text"].rstrip("m"))
    return {"horse": horse, "tab_no": tab, "vals": out}


# ---------------------------------------------------------------- driver

def parse_pdf(path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    runs, secs = [], []
    with pdfplumber.open(path) as pdf:
        race = None
        for page in pdf.pages:
            text = page.dedupe_chars().extract_text()
            if "RANK BAR" in text:
                hdr = _header(text)
                race_no, name, dist = _race_no_name_dist(text)
                if race is None or race["race_no"] != race_no:
                    race = dict(hdr, race_no=race_no, race_name=name, distance=dist, runners={})
                for r in _parse_summary(text, hdr, race_no, dist):
                    prev = race["runners"].get(r["tab_no"])
                    if prev is not None:  # long races continue sections on a second page set
                        seen = {s["mark"] for s in prev["_sections"]}
                        prev["_sections"] += [s for s in r["_sections"] if s["mark"] not in seen]
                        continue
                    r["race_name"], r["going"], r["rail"] = name, hdr.get("going"), hdr.get("rail")
                    r["weather"], r["start_time"] = hdr.get("weather"), hdr.get("start_time")
                    race["runners"][r["tab_no"]] = r
                    runs.append(r)
            else:
                hp = _parse_horse_page(page)
                if hp and race and hp["tab_no"] in race["runners"]:
                    race["runners"][hp["tab_no"]].setdefault("_detail", {}).update(hp["vals"])
    for r in runs:
        det = r.pop("_detail", {})
        for s in r.pop("_sections"):
            # horse-page axis labels mark the section START (1400 = start-1200)
            s.update({m: det.get((s["mark"], m)) for m in ("speed_kmh", "stride_m", "stride_hz", "rail_m")})
            secs.append(dict(date=r["date"], track=r["track"], race_no=r["race_no"],
                             tab_no=r["tab_no"], horse=r["horse"], **s))
    runs, secs = pd.DataFrame(runs), pd.DataFrame(secs)
    if secs.empty:
        return runs, secs
    # elapsed time from the start to the START of each section; position there = rank of elapsed.
    # Printed [rank] is at the END of the section; SA reports omit it, so derive both consistently.
    secs = secs.merge(runs[["race_no", "tab_no", "time_s"]], on=["race_no", "tab_no"], how="left")
    secs["elapsed_at_mark_s"] = secs["time_s"] - secs["cum_s"]
    secs["pos_at_mark"] = secs.groupby(["race_no", "mark"])["elapsed_at_mark_s"].rank(method="min")
    secs["pos_at_mark_to_leader_s"] = secs["elapsed_at_mark_s"] - secs.groupby(["race_no", "mark"])["elapsed_at_mark_s"].transform("min")
    return runs, secs.drop(columns="time_s")


if __name__ == "__main__":
    import sys
    rs, ss = zip(*(parse_pdf(f) for f in sys.argv[1:]))
    runs, secs = pd.concat(rs), pd.concat(ss)
    print(runs.shape, secs.shape)
