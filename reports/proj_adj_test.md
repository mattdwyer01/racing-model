# Proj input review (walk-forward 2023 to Sep 2026, VIC/SA/QLD, front-weighted WPR model)

- 38,310 races. Lines set per variant to hold the dashboard's runner counts (3.03 / 4.62 a
  race for the 3 / 5 lines). 'vs full' = winners inside 3 per 100 races vs the live recipe (95% race bootstrap):
  negative for a '- group' row means the group HELPS. MAE = WPR error, runners with prior form.

| variant                   |   winners inside 3 % | vs full (pts)          |   winners inside 5 % |   top pick % |   MAE |
|:--------------------------|---------------------:|:-----------------------|---------------------:|-------------:|------:|
| full                      |                60.64 | +0.00 (+0.00 to +0.00) |                77.03 |        28.35 | 6.479 |
| - ability                 |                59.58 | -1.06 (-1.36 to -0.73) |                76.3  |        27.82 | 6.517 |
| - form shape              |                60.21 | -0.43 (-0.70 to -0.15) |                76.89 |        28.32 | 6.499 |
| - distance / going        |                60.52 | -0.12 (-0.38 to +0.15) |                76.99 |        28.1  | 6.49  |
| - prep                    |                60.36 | -0.28 (-0.53 to +0.00) |                76.92 |        28.26 | 6.491 |
| - race-day projection     |                60.69 | +0.05 (-0.24 to +0.35) |                77.18 |        28.43 | 6.481 |
| - track bias              |                60.46 | -0.18 (-0.44 to +0.07) |                77.05 |        28.69 | 6.483 |
| - jockey / trainer        |                60.45 | -0.19 (-0.46 to +0.09) |                76.97 |        28.37 | 6.487 |
| - comments                |                60.75 | +0.11 (-0.22 to +0.42) |                77.34 |        28.59 | 6.468 |
| - ground loss (past runs) |                60.66 | +0.02 (-0.25 to +0.28) |                77.51 |        28.53 | 6.484 |
| - age / sex / weight      |                60.82 | +0.19 (-0.09 to +0.46) |                77.18 |        28.6  | 6.488 |
| - race context            |                60.29 | -0.35 (-0.63 to -0.05) |                77.05 |        28.44 | 6.532 |
| + excuses                 |                60.7  | +0.06 (-0.22 to +0.34) |                77.13 |        28.57 | 6.472 |
| + class                   |                60.73 | +0.09 (-0.16 to +0.35) |                77.03 |        28.33 | 6.473 |
| + both                    |                60.71 | +0.07 (-0.21 to +0.35) |                77.24 |        28.41 | 6.466 |

## Winners inside 3, by year (%)

|                           |   2023 |   2024 |   2025 |   2026 |
|:--------------------------|-------:|-------:|-------:|-------:|
| full                      |   60   |   60.8 |   60.9 |   61.1 |
| - ability                 |   59.6 |   59.5 |   60.1 |   60.3 |
| - form shape              |   60.3 |   60.3 |   60.7 |   60.7 |
| - distance / going        |   60   |   60.5 |   60.7 |   60.9 |
| - prep                    |   60   |   60.5 |   60.4 |   60.6 |
| - race-day projection     |   59.9 |   60.6 |   60.7 |   61.4 |
| - track bias              |   60.2 |   60.5 |   60.7 |   61.2 |
| - jockey / trainer        |   59.9 |   60.5 |   60.9 |   60.9 |
| - comments                |   60.5 |   60.7 |   60.9 |   61.1 |
| - ground loss (past runs) |   60.5 |   60.2 |   61   |   60.9 |
| - age / sex / weight      |   60.3 |   60.6 |   60.8 |   60.9 |
| - race context            |   59.8 |   60.2 |   60.8 |   60.6 |
| + excuses                 |   60   |   61.3 |   61   |   61.3 |
| + class                   |   60.1 |   60.1 |   61.1 |   60.9 |
| + both                    |   60.1 |   61   |   60.9 |   61.2 |

