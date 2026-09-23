# racing-model

Horse rating and win-probability model for VIC, SA and QLD thoroughbred racing.

## Sources
| Source | Role | Coverage |
|---|---|---|
| TopRate yearly results (`data/raw/toprate/`) | Backbone: results, sectional ratings, WPR, positions, comments | 2017 to now; near-complete for all AU from 2022 |
| Triple S GPS reports (racing.com, RQ) | Distance travelled, distance from rail, speed and stride per 200m | Captured from now on (parser: `ingest/tsd_gps_pdf.py`) |
| TAB fixed odds | Bet-time prices and start times | Captured from now on |

## Build
```
pip install -r requirements.txt
python ingest/build_core.py        # raw TopRate files -> data/db/racing.duckdb
```

## Tables (`data/db/racing.duckdb`)
- `tr_raw`: every TopRate row, untouched
- `tracks`: track -> venue, state, location class (M/P/C), surface, in_scope (from `ingest/tracks.csv`)
- `races`: one row per race or trial; parsed class, rail offset, surface, `full_coverage` flag
- `runs`: one row per runner

Naming rule in `runs`: columns without a prefix are known before the race. Columns starting `res_` are
results or in-race measurements and must never be used as inputs for the same race.

## Data notes
- TopRate `wpr` in the raw file is the rating of that run (post-race). Pre-race use = prior runs only.
- Sectional ratings: lengths vs TopRate benchmark, positive = faster; already pace/wind/rain adjusted, not weight adjusted.
- Coverage before 2022 is partial (mostly metro/provincial). Sectionals start in 2019. Training starts 2022; earlier years are form history only.
- TopRate has no race number; `race_id` order is not race order.
- About 8% of 2024-2026 WPRs are still `Preliminary`.
