# Projection improvement tests (4 Oct 2026)

Pre-race dashboard values: 1,753 races 22 Aug to 3 Oct 2026, all states (tools/combo_strike_test data). History: racing-model DB.

## 1. Racing Model in Combo (RM chance on the WPR scale, 6.843 x ln p, in place of part / all of the projection's 0.45)
- Top pick win %: current 29.7, RM 0.15 29.3, RM 0.30 29.7, RM replaces projection 29.6, RM only 29.1, projection only 26.6.
  None differ from current (95% about +/-1.3 pts). Top pick moves toward the SP favourite (54% -> 59%), non-fav A/E 1.10 -> 1.04.
- Win rule (4+ clear, SM >= 1, no FS): current 179 bets +6.9%; RM 0.30 -0.8%, RM replaces projection -6.4%.
- Lines at equal runner count (2.48 inside): winners inside +2.2 per 100 races with RM replacing the projection
  (+0.6 to +3.8), +1.8 at RM 0.30, +1.2 at 0.15; A/E vs SP inside 1.041 -> 1.062. Helps exotic coverage, hurts the win rule.

## 2. Projection adjustments on top of the Racing Model
- Most adjustments are already fitted (LightGBM to next WPR) in wpr_projection.py; own_* terms are hand-set shrinks.
- Clogit (2-fold by date): RM alone 1.9086; + projection adj sum (8 live terms excl. speed map) +0.0004 (-0.0009 to
  +0.0017), weight 0.01; each term free +0.0022 (worse). With SP + RM: +0.0003 n.s. The RM already holds what they carry.

## 3. Speed map corrections (walk-forward v3 race-day adj, 24,353 races 2024 to Sep 2026, cells fitted on earlier years)
- Surprise cells (projected settle band x barrier band / going) added to the adj: model alone +0.0051 (barrier), +0.0037
  (going), +0.0047 (both), all worse; with SP +0.0003 / -0.0001 / +0.0003; top pick 26.9% -> 26.7%.
- The WPR-level over-credit of wide leaders is real but does not carry into who wins (wide leaders run A/E 1.05-1.08 at SP).

## 4. Base inputs
- Dated WPRs: pipeline/pull_toprate.py now archives every run's WPR / status the day it is first seen and on each revision
  (store asset wpr_dated.csv.gz, `wpr_asof(date)`), current + last year's results files. Point-in-time WPRs from 4 Oct 2026.
- Base formula (54,905 races 2023 to Sep 2026, all states, every runner rated before; leave-one-year-out, current WPRs):
  TopRate base ewm7 (by run) 2.0176 alone, top pick 25.3%. ewm5 -0.0040, date-decay half-life 90 days -0.0068, ewm12
  +0.0134, last start +0.0520, career +0.0696. Fitted mix 0.26 dt180 + 0.42 ewm3 + 0.32 max5 - 1.83 ln(1 + runs):
  -0.0289 alone, top pick 26.3%; with SP -0.0005 (-0.0008 to -0.0002). Fewer runs = better (improvers).
- In Combo (1,350 of the pre-race races, projection base swapped): top pick 28.4% both (-0.1, -1.3 to +1.0); projection
  alone 25.6% -> 25.9% n.s. wpr_nett / rating / form factor already carry it. Not worth changing TopRate's base.
- Rating mu / excuse runs: these are Racing Model inputs; their route into Combo is test 1.
