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

## Model status
- Per-run figure (`model/figure.py`, `validate_figure.py`): WPR + sectionals + pace (settle x early shape).
  WPR is already weight adjusted; pace is the main lift. Figure alone 1.997 log loss vs SP 1.786;
  SP + figure beats calibrated SP by 0.001 (2023-2026 walk-forward).
- Ground loss (`ingest/gps_link.py` -> `gps_runs`, `validate_gps.py`): +0.21 WPR per extra metre;
  improves the figure on QLD but adds nothing over SP (market prices past ground loss).
- RQ `race_time_s` is about 1.9s longer than the official time; use the winner's `time_s`.

## Next build step
Current-ability model (`model/ability.py`): recent form from figures, spell/prep pattern, trials,
distance and going suitability, class moves. Then race-day projection (settle, width, expected
ground loss) and VIC/SA ground loss once the racing.com backfill is in the store.
