# Settle forecast: placing each horse more precisely (walk-forward 2023 to Sep 2026)

- 64,621 races, 621,812 runs with an 800m position (all states in the frame).
- R2 on the 800m settle share; Spearman = within-race rank correlation; leader leads % = the projected leader is
  first at the 800m. 'as rank' = the same forecast turned into its rank share within the race.

## Mean over folds

| variant      |     R2 |   Spearman in race |   leader leads % |
|:-------------|-------:|-------------------:|-----------------:|
| both         | 0.3301 |             0.5633 |           39.85  |
| both as rank | 0.1075 |             0.5633 |           39.85  |
| early200     | 0.3295 |             0.5626 |           39.85  |
| rank (both)  | 0.1111 |             0.5643 |           40.1   |
| slow         | 0.3303 |             0.5633 |           39.775 |
| v3 (live)    | 0.3299 |             0.5628 |           39.9   |
| v3 as rank   | 0.1066 |             0.5628 |           39.9   |

## R2 by year

| variant      |   2023 |   2024 |   2025 |   2026 |
|:-------------|-------:|-------:|-------:|-------:|
| both         | 0.3271 | 0.3356 | 0.3287 | 0.3289 |
| both as rank | 0.1017 | 0.1147 | 0.1049 | 0.1087 |
| early200     | 0.3264 | 0.3349 | 0.3282 | 0.3285 |
| rank (both)  | 0.1048 | 0.1204 | 0.1077 | 0.1115 |
| slow         | 0.327  | 0.336  | 0.3289 | 0.3292 |
| v3 (live)    | 0.3268 | 0.3351 | 0.3286 | 0.329  |
| v3 as rank   | 0.1012 | 0.1137 | 0.1029 | 0.1087 |

## Spread model (per-horse uncertainty of 'both'), by predicted-spread fifth

|   q |   spread |   mean_abs_error |   runners |
|----:|---------:|-----------------:|----------:|
|   0 |    0.133 |            0.155 |    124363 |
|   1 |    0.168 |            0.188 |    124362 |
|   2 |    0.191 |            0.211 |    124362 |
|   3 |    0.218 |            0.236 |    124362 |
|   4 |    0.266 |            0.275 |    124363 |

## TopRate pre-race fields (fit 26 Apr to 31 Jul 2026, score 1 Aug on)

| variant        |     R2 |   Spearman in race |   leader leads % |   train runs |   test runs |
|:---------------|-------:|-------------------:|-----------------:|-------------:|------------:|
| v3 (live)      | 0.272  |             0.5485 |             39.1 |        34355 |       26584 |
| both           | 0.2716 |             0.5472 |             39.1 |        34355 |       26584 |
| both + TopRate | 0.2788 |             0.5521 |             40.3 |        34355 |       26584 |

