# racing-model: context for Claude Code sessions

Owner: Matt. Style: direct, concise dot points, no em dashes in any output.

## Goal
Win-probability model for VIC, SA and QLD thoroughbred races, bet on TAB fixed odds.
Structure: per-run performance figure -> current ability per horse -> race-day projection
(settle position, width, ground loss) -> conditional logit -> blend with market -> fractional Kelly.

## Data sources (decided)
- TopRate yearly results files (backbone, 2017 on; near-complete for all AU from 2022; sectionals from 2019).
  Raw files are NOT in git (in `data/raw/toprate/`, to be uploaded to the `data` release).
- GPS (Triple S): QLD via RQ meeting ZIP XML (Oct 2022 on, per-200m rail distance);
  VIC/SA via racing.com GraphQL getRaceForm (Triple S VIC metro from Aug 2021; whole-race avg rail distance).
  PDFs are a fallback only (`ingest/tsd_gps_pdf.py`).
- TAB fixed odds: the TopRate repo's poller logs every read on the Vultr box (`~/racing-data/tab_prices/`);
  `tab_price_archive.yml` ships it to the store. Pre-Sep 2026 prices: `fixed_prices_final` (dashboard
  runners file, Apr 2026 on) and `tools/extract_prices_from_git.py` (git history of toprate_runners.csv).
- Punting Form: dropped (no lift over SP in testing, borrowed login).

## Future sources (not built)
- NSW metro (ATC) Swiss Timing sectional PDFs:
  `feed.australianturfclub.com.au/sectionals/swiss-timing/{year}/{DDMM}{TRACK}-{race}.pdf` (e.g. `1909RAND-1.pdf`).
  Per horse: DT-W (distance travelled vs winner, m), barrier, 200m cumulative times with positions,
  splits, top speed. No rail distance.
- WA sectional workbooks: times only, no distance travelled. Skip.

## Rules
- In `runs`, columns prefixed `res_` are in-race results: never inputs for the same race.
  TopRate `wpr` in the raw files is the rating OF that run (post-race).
- Train/test from 2022; walk-forward splits by date only; backtest at SP or captured fixed price, never top fluc.
- TopRate has no race number; `race_times` (from the dashboard runners file) has it from Apr 2026.
- RQ XML `DrawNumber` repeats the saddlecloth number; barrier comes from TopRate.

## Automation
- Data store = assets on the GitHub release tagged `data` (`pipeline/store.py`), not git.
- `gps_daily.yml` (06:00 AEST), `gps_backfill.yml` (manual), `tab_price_archive.yml` (Vultr runner).
- My workspace and GitHub-hosted runners may be blocked by TAB (confirmed) and possibly RQ / racing.com;
  set repo variable `SCRAPER_RUNNER=vultr-au` to move scraping to the Vultr self-hosted runner.

## Model status (log loss, 2023-2026 walk-forward, VIC/SA/QLD; SP calibrated = 1.786)
- Per-run figure (`model/figure.py`, `validate_figure.py`): WPR + sectionals + pace (settle x early shape).
  WPR is already weight adjusted; pace is the main lift. Figure alone 1.997; SP + figure beats SP by 0.001.
- Ability (`model/ability.py`): form, trials, distance change, age/sex. 1.968 alone; adds ~0 over SP + figure.
- Jockey/trainer (`model/jt.py`): A/E vs market, strike rates, jockey change/upgrade. ~0 in a logit;
  used by the GBM through interactions.
- Market-offset GBM (`model/offset_model.py`): calibrated SP + LightGBM trees (per-race softmax).
  Tuning grid did not help (off by default).
- Race-day projection v3 (`model/projection.py`, report `reports/projection_validation.md`):
  - settle (800m position share): settle and early-speed history matched to distance / first-up / going,
    speed map, barrier (+ by track and distance), jockey/trainer forward tendency, trials, weight/claim.
    R2 0.32-0.33 (debutants 0.08-0.12, first-up 0.26-0.27); projected leader leads at the 800m 39-40%.
  - pace (race early shape) R2 0.06-0.12; ground loss (QLD GPS) R2 0.17-0.19.
  - cost in WPR (stable): leader to last -2.6; on-pace per unit early shape -0.35; -0.14 to -0.21 per metre.
  - track bias from past meetings (settle and barrier slopes; long-run + same rail within 35 days) persists
    (corr 0.2-0.3) and is calibrated; the one addition that helped (-0.0023).
  - v3 + track bias vs figure: -0.0119 (se 0.0009). With SP: -0.0015 vs SP (se 0.0005), QLD -0.0032.
  - no gain: pace x running style, a separate GPS early-position model, and track x distance barrier /
    speed map as direct win-model terms (their value comes through the settle / gl models).
- Ground loss (`ingest/gps_link.py` -> `gps_runs`): +0.21 WPR per extra metre as a figure input; adds
  nothing over SP from past runs (market prices it).
- Prices (parked): `fixed_prices_final` looks written after the jump (about SP). Git history of
  toprate_runners.csv (`tools/extract_prices_from_git.py`) gives sparse pre-jump snapshots from Apr 2026;
  model picks show large CLV there but prices may be stale dashboard values. Verify against the Vultr log.
- Data issues: RQ distance travelled at Doomben and Ipswich from 2026 no longer tracks barrier or settle
  (masked in `gps_link.SUSPECT_DIST`); 2026 ground-loss R2 falls elsewhere too. RQ `race_time_s` is about
  1.9s longer than the official time; use the winner's `time_s`.

## Next build step
Stage B: v3 projection in the market-offset GBM; QLD-only vs all-state fits on QLD races.
Then VIC/SA ground loss once the racing.com backfill is in the store.
