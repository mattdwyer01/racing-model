# Proj: every race-day adjustment applied the same way (walk-forward 2023 to Sep 2026, VIC/SA/QLD)

- 38,310 races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5 lines).
- Each adjustment = term in WPR vs the race mean x weight b >= 0 fitted jointly on the later 25% of training dates
  against the form model's residual. 'form' = no race-day, age / sex / weight or track bias groups.

## Versions vs form only (winners per 100 races, 95% race bootstrap)

| variant    |   inside 3 % |   inside 5 % | vs form, inside 3      | vs form, inside 5      |   top pick % |
|:-----------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| form       |        60.91 |        77.47 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.68 |
| current    |        60.67 |        77.2  | -0.25 (-0.51 to +0.02) | -0.27 (-0.49 to -0.05) |        28.78 |
| consistent |        61.12 |        77.19 | +0.21 (+0.04 to +0.39) | -0.28 (-0.43 to -0.14) |        28.79 |
| all        |        60.79 |        77.12 | -0.12 (-0.34 to +0.07) | -0.35 (-0.51 to -0.20) |        28.88 |

## Each adjustment left out of 'all' (negative = the adjustment adds winners)

| variant                 |   inside 3 % |   inside 5 % | vs all, inside 3       | vs all, inside 5       |   top pick % |
|:------------------------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| all - proj_adj          |        60.85 |        77.38 | +0.06 (-0.07 to +0.20) | +0.26 (+0.14 to +0.38) |        28.79 |
| all - lv_x              |        60.78 |        77.12 | -0.01 (-0.05 to +0.03) | -0.00 (-0.04 to +0.04) |        28.87 |
| all - sx_wet            |        60.82 |        77.08 | +0.03 (-0.05 to +0.09) | -0.04 (-0.09 to +0.02) |        28.9  |
| all - tbx_settle_long   |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - tbx_settle_recent |        60.79 |        77.11 | -0.01 (-0.06 to +0.05) | -0.01 (-0.06 to +0.04) |        28.87 |
| all - tbx_bar_long      |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - tbx_bar_recent    |        60.81 |        77.1  | +0.02 (-0.04 to +0.09) | -0.02 (-0.07 to +0.03) |        28.86 |
| all - tdx_perf          |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - cbx_dist_settle   |        60.77 |        77.14 | -0.02 (-0.07 to +0.03) | +0.02 (-0.02 to +0.07) |        28.86 |
| all - cbx_dist_bar      |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - cbx_going_settle  |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - cbx_going_bar     |        60.79 |        77.12 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.88 |
| all - cbx_rail_settle   |        60.81 |        77.13 | +0.02 (-0.01 to +0.04) | +0.02 (-0.01 to +0.04) |        28.88 |
| all - cbx_rail_bar      |        60.81 |        77.14 | +0.02 (-0.02 to +0.06) | +0.02 (-0.02 to +0.07) |        28.85 |
| all - pos_chg           |        61.12 |        77.03 | +0.33 (+0.21 to +0.46) | -0.08 (-0.19 to +0.02) |        28.85 |
| all - bar_chg           |        60.78 |        77.14 | -0.01 (-0.06 to +0.05) | +0.03 (-0.03 to +0.08) |        28.92 |

## Inside 3 by year (%)

|            |   2023 |   2024 |   2025 |   2026 |
|:-----------|-------:|-------:|-------:|-------:|
| form       |   60.5 |   60.6 |   61.3 |   60.9 |
| current    |   60.4 |   61.2 |   60.9 |   61   |
| consistent |   60.6 |   61.1 |   61.2 |   60.8 |
| all        |   60.8 |   60.7 |   61.1 |   60.8 |

## Fitted weights b (1 = the term at face value)

|                              |   2023 |   2024 |   2025 |   2026 |
|:-----------------------------|-------:|-------:|-------:|-------:|
| consistent:proj_adj          |  0.545 |  0.518 |  0.536 |  0.331 |
| consistent:lv_x              |  0.032 |  0.006 |  0.241 |  0.227 |
| consistent:sx_wet            |  0.454 |  0.452 |  0     |  0.127 |
| consistent:tbx_settle_long   |  0     |  0.112 |  0.092 |  0.012 |
| consistent:tbx_settle_recent |  0.181 |  0     |  0.924 |  0.351 |
| consistent:tbx_bar_long      |  0     |  0     |  0     |  0     |
| consistent:tbx_bar_recent    |  0     |  0.362 |  0.175 |  0.46  |
| consistent:tdx_perf          |  0     |  0     |  0     |  0.05  |
| all:proj_adj                 |  0.507 |  0.474 |  0.5   |  0.313 |
| all:lv_x                     |  0     |  0     |  0.167 |  0.114 |
| all:sx_wet                   |  0.486 |  0.419 |  0     |  0.123 |
| all:tbx_settle_long          |  0     |  0     |  0     |  0     |
| all:tbx_settle_recent        |  0.175 |  0     |  0.859 |  0.276 |
| all:tbx_bar_long             |  0     |  0     |  0     |  0     |
| all:tbx_bar_recent           |  0     |  0.357 |  0.151 |  0.398 |
| all:tdx_perf                 |  0     |  0     |  0     |  0     |
| all:cbx_dist_settle          |  0.085 |  0.213 |  0     |  0.257 |
| all:cbx_dist_bar             |  0     |  0     |  0     |  0     |
| all:cbx_going_settle         |  0     |  0     |  0     |  0     |
| all:cbx_going_bar            |  0     |  0     |  0     |  0     |
| all:cbx_rail_settle          |  0     |  0     |  0.263 |  0     |
| all:cbx_rail_bar             |  0     |  0     |  0.037 |  0.185 |
| all:pos_chg                  |  1.345 |  1.752 |  1.463 |  1.327 |
| all:bar_chg                  |  0.394 |  0     |  0     |  0     |

