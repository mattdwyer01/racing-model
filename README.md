# racing-model

Horse rating and win-probability model for VIC, SA and QLD thoroughbred racing.

## Sources
| Source | Role | Coverage |
|---|---|---|
| TopRate yearly results (`data/raw/toprate/`) | Backbone: results, sectional ratings, WPR, positions, comments | 2017 to now; near-complete for all AU from 2022 |
| RQ GPS XML (`ingest/rq_sectionals.py`) | QLD: per-200m distance run, speed, stride, distance to rail | Oct 2022 onward |
| racing.com GraphQL (`ingest/racingcom_sectionals.py`) | VIC/SA: distance run, average rail distance, 200m splits, early/mid/late speed | Triple S VIC metro from Aug 2021 |
| TAB fixed odds | Bet-time prices and start times | Captured from now on |

## Build
```
pip install -r requirements.txt
python pipeline/bootstrap.py       # pull raw files from the store, then build data/db/racing.duckdb
python ingest/build_core.py        # rebuild only (raw files already in data/raw/)
```

## Automation (GitHub Actions)
- `gps_daily.yml`: every morning, pulls the last week of RQ and racing.com GPS data and merges it into the data store.
- `gps_backfill.yml`: manual, pulls full history (RQ from Oct 2022, racing.com from a chosen date).
- `tab_price_archive.yml`: nightly, ships the Vultr box's TAB price log to the store (needs the Vultr runner).
- Data store: assets on the `data` release. `python pipeline/store.py list` shows what's there.

## Tools
- `tools/for_toprate_repo/`: copy both files into the TopRate repo. The poller then writes every TAB fixed-odds read to `~/racing-data/tab_prices/` on the Vultr box, permanently.
- `tools/extract_prices_from_git.py`: rebuilds price history from the git history of `toprate_runners.csv` (usage in the file header).

## Tables (`data/db/racing.duckdb`)
- `tr_raw`: every TopRate row, untouched
- `tracks`: track -> venue, state, location class (M/P/C), surface, in_scope (from `ingest/tracks.csv`)
- `races`: one row per race or trial; parsed class, rail offset, surface, `full_coverage` flag
- `runs`: one row per runner
- `gps_runs`: GPS ground loss and rail distance per run, linked to TopRate `run_id` (`ingest/gps_link.py`; built when `rq_`/`rc_gps_*.parquet` are in `data/interim/`)
- `live_runners`, `race_times`, `fixed_prices_final`: from the dashboard's `toprate_runners.csv` (put a copy in `data/raw/live/`); race number, start time and near-jump fixed price from Apr 2026

Naming rule in `runs`: columns without a prefix are known before the race. Columns starting `res_` are
results or in-race measurements and must never be used as inputs for the same race.

## Data notes
- TopRate `wpr` in the raw file is the rating of that run (post-race). Pre-race use = prior runs only.
- Sectional ratings: lengths vs TopRate benchmark, positive = faster; already pace/wind/rain adjusted, not weight adjusted.
- Coverage before 2022 is partial (mostly metro/provincial). Sectionals start in 2019. Training starts 2022; earlier years are form history only.
- TopRate has no race number; `race_id` order is not race order.
- About 8% of 2024-2026 WPRs are still `Preliminary`.
