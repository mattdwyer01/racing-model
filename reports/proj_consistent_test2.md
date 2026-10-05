# Proj: every race-day adjustment applied the same way (walk-forward 2023 to Sep 2026, VIC/SA/QLD)

- 38,310 races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5 lines).
- Each adjustment = term in WPR vs the race mean x weight b >= 0 fitted jointly on the later 25% of training dates
  against the form model's residual. 'form' = no race-day, age / sex / weight or track bias groups.

## Versions vs form only (winners per 100 races, 95% race bootstrap)

| variant         |   inside 3 % |   inside 5 % | vs form, inside 3      | vs form, inside 5      |   top pick % |
|:----------------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| form            |        60.69 |        77.13 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.61 |
| current         |        60.89 |        77.36 | +0.20 (-0.07 to +0.46) | +0.23 (+0.00 to +0.46) |        28.68 |
| consistent      |        60.93 |        77.33 | +0.24 (+0.08 to +0.43) | +0.20 (+0.04 to +0.34) |        28.8  |
| all             |        61    |        77.14 | +0.31 (+0.12 to +0.50) | +0.01 (-0.15 to +0.17) |        28.73 |
| win: consistent |        60.97 |        77.17 | +0.28 (+0.05 to +0.52) | +0.04 (-0.15 to +0.22) |        28.71 |
| win: all        |        61.21 |        77.14 | +0.52 (+0.30 to +0.77) | +0.01 (-0.18 to +0.19) |        28.68 |

## Each adjustment left out of 'all' (negative = the adjustment adds winners)

| variant                 |   inside 3 % |   inside 5 % | vs all, inside 3       | vs all, inside 5       |   top pick % |
|:------------------------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| all - proj_adj          |        60.86 |        77.12 | -0.14 (-0.27 to +0.00) | -0.02 (-0.12 to +0.09) |        28.69 |
| all - lv_x              |        61.02 |        77.14 | +0.02 (-0.03 to +0.06) | +0.01 (-0.02 to +0.04) |        28.72 |
| all - sx_wet            |        60.99 |        77.11 | -0.00 (-0.07 to +0.07) | -0.03 (-0.08 to +0.03) |        28.74 |
| all - tbx_settle_long   |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - tbx_settle_recent |        60.93 |        77.13 | -0.07 (-0.14 to -0.01) | -0.01 (-0.06 to +0.05) |        28.68 |
| all - tbx_bar_long      |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - tbx_bar_recent    |        60.98 |        77.12 | -0.02 (-0.09 to +0.06) | -0.01 (-0.07 to +0.04) |        28.76 |
| all - tdx_perf          |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - cbx_dist_settle   |        61.01 |        77.12 | +0.01 (-0.03 to +0.05) | -0.02 (-0.05 to +0.02) |        28.72 |
| all - cbx_dist_bar      |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - cbx_going_settle  |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - cbx_going_bar     |        61    |        77.14 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.73 |
| all - cbx_rail_settle   |        61.01 |        77.16 | +0.02 (-0.01 to +0.04) | +0.02 (-0.00 to +0.05) |        28.71 |
| all - cbx_rail_bar      |        61.03 |        77.18 | +0.04 (-0.01 to +0.08) | +0.05 (+0.01 to +0.09) |        28.71 |
| all - pos_chg           |        61.08 |        77.29 | +0.08 (+0.00 to +0.17) | +0.15 (+0.08 to +0.22) |        28.74 |
| all - bar_chg           |        60.93 |        77.13 | -0.07 (-0.13 to -0.00) | -0.01 (-0.07 to +0.05) |        28.72 |
| all - trip_undo         |        61    |        77.17 | +0.00 (-0.07 to +0.08) | +0.03 (-0.03 to +0.10) |        28.7  |
| all - style_x           |        61.05 |        77.16 | +0.06 (+0.00 to +0.11) | +0.02 (-0.02 to +0.06) |        28.74 |
| all - posv_td           |        60.98 |        77.15 | -0.01 (-0.07 to +0.04) | +0.01 (-0.03 to +0.05) |        28.72 |

## Inside 3 by year (%)

|                 |   2023 |   2024 |   2025 |   2026 |
|:----------------|-------:|-------:|-------:|-------:|
| form            |   60.3 |   60.9 |   61   |   61.2 |
| current         |   60.7 |   61.2 |   60.8 |   61.5 |
| consistent      |   60.3 |   60.8 |   61.3 |   61.4 |
| all             |   60.4 |   60.9 |   61.4 |   60.9 |
| win: consistent |   60.8 |   61.3 |   61   |   61.1 |
| win: all        |   60.7 |   60.8 |   61.3 |   61.1 |

## Fitted weights b (1 = the term at face value)

|                                   |    2023 |    2024 |    2025 |    2026 |
|:----------------------------------|--------:|--------:|--------:|--------:|
| consistent:proj_adj               |   0.526 |   0.512 |   0.508 |   0.305 |
| consistent:lv_x                   |   0.04  |   0     |   0.214 |   0.198 |
| consistent:sx_wet                 |   0.404 |   0.437 |   0     |   0.084 |
| consistent:tbx_settle_long        |   0     |   0.1   |   0.074 |   0.018 |
| consistent:tbx_settle_recent      |   0.215 |   0     |   0.926 |   0.386 |
| consistent:tbx_bar_long           |   0     |   0     |   0     |   0     |
| consistent:tbx_bar_recent         |   0     |   0.403 |   0.164 |   0.463 |
| consistent:tdx_perf               |   0     |   0     |   0     |   0.062 |
| all:proj_adj                      |   0.856 |   0.38  |   0.677 |   0.269 |
| all:lv_x                          |   0     |   0     |   0.13  |   0.091 |
| all:sx_wet                        |   0.407 |   0.415 |   0     |   0.079 |
| all:tbx_settle_long               |   0     |   0     |   0     |   0     |
| all:tbx_settle_recent             |   0.194 |   0     |   0.867 |   0.313 |
| all:tbx_bar_long                  |   0     |   0     |   0     |   0     |
| all:tbx_bar_recent                |   0     |   0.398 |   0.13  |   0.399 |
| all:tdx_perf                      |   0     |   0     |   0     |   0     |
| all:cbx_dist_settle               |   0     |   0.121 |   0     |   0.248 |
| all:cbx_dist_bar                  |   0     |   0     |   0     |   0     |
| all:cbx_going_settle              |   0     |   0     |   0     |   0     |
| all:cbx_going_bar                 |   0     |   0     |   0     |   0     |
| all:cbx_rail_settle               |   0     |   0     |   0.234 |   0     |
| all:cbx_rail_bar                  |   0     |   0     |   0.049 |   0.197 |
| all:pos_chg                       |   0     |   1.71  |   0.773 |   1.413 |
| all:bar_chg                       |   0.418 |   0     |   0     |   0     |
| all:trip_undo                     |   0.561 |   0     |   0.262 |   0     |
| all:style_x                       |   0     |   0.095 |   0.04  |   0.043 |
| all:posv_td                       |   0.174 |   0.084 |   0     |   0     |
| win: consistent:proj_adj          |   1.05  |   1.102 |   0.905 |   0.616 |
| win: consistent:tbx_settle_long   |   0.233 | nan     | nan     | nan     |
| win: consistent:tbx_bar_recent    |   0.083 |   0.377 |   0.018 |   0.283 |
| win: consistent:tdx_perf          |   0.513 | nan     | nan     | nan     |
| win: all:proj_adj                 |   1.149 |   1.194 |   1.069 |   0.645 |
| win: all:tbx_settle_long          |   0.159 | nan     | nan     | nan     |
| win: all:tbx_bar_recent           |   0.086 |   0.364 |   0.008 |   0.215 |
| win: all:tdx_perf                 |   0.47  | nan     | nan     | nan     |
| win: all:cbx_dist_bar             |   0.071 | nan     | nan     | nan     |
| win: all:bar_chg                  |   0.107 | nan     | nan     | nan     |
| win: all:trip_undo                |   0.202 |   0.167 |   0.229 |   0.064 |
| win: all:style_x                  |   0.001 |   0.031 | nan     | nan     |
| win: all:posv_td                  |   0.102 |   0.031 | nan     |   0.015 |
| win: consistent:sx_wet            | nan     |   1.141 |   0.311 |   0.349 |
| win: all:sx_wet                   | nan     |   1.103 |   0.272 |   0.328 |
| win: all:cbx_going_bar            | nan     |   0.064 | nan     | nan     |
| win: all:pos_chg                  | nan     |   1.1   |   0.581 |   0.968 |
| win: consistent:lv_x              | nan     | nan     |   0.257 |   0.132 |
| win: consistent:tbx_settle_recent | nan     | nan     |   0.226 | nan     |
| win: all:lv_x                     | nan     | nan     |   0.245 |   0.113 |
| win: all:tbx_settle_recent        | nan     | nan     |   0.241 | nan     |
| win: all:cbx_rail_bar             | nan     | nan     | nan     |   0.194 |

