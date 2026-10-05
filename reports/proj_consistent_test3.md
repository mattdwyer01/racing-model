# Proj: every race-day adjustment applied the same way (walk-forward 2023 to Sep 2026, VIC/SA/QLD)

- 38,310 races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5 lines).
- Each adjustment = term in WPR vs the race mean x weight b >= 0 fitted jointly on the later 25% of training dates
  against the form model's residual. 'form' = no race-day, age / sex / weight or track bias groups.

## Versions vs form only (winners per 100 races, 95% race bootstrap)

| variant         |   inside 3 % |   inside 5 % | vs form, inside 3      | vs form, inside 5      |   top pick % |
|:----------------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| form            |        60.47 |        77.31 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.55 |
| current         |        60.75 |        77.24 | +0.27 (+0.01 to +0.56) | -0.07 (-0.30 to +0.15) |        28.68 |
| consistent      |        60.97 |        77.5  | +0.49 (+0.32 to +0.68) | +0.18 (+0.02 to +0.33) |        28.67 |
| all             |        60.89 |        77.49 | +0.42 (+0.24 to +0.61) | +0.17 (+0.02 to +0.32) |        28.68 |
| win: consistent |        60.67 |        77.41 | +0.20 (-0.02 to +0.42) | +0.10 (-0.09 to +0.29) |        28.63 |
| win: all        |        61.02 |        77.36 | +0.55 (+0.32 to +0.77) | +0.05 (-0.15 to +0.24) |        28.65 |

## Each adjustment left out of 'all' (negative = the adjustment adds winners)

| variant                 |   inside 3 % |   inside 5 % | vs all, inside 3       | vs all, inside 5       |   top pick % |
|:------------------------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|
| all - proj_adj          |        60.88 |        77.29 | -0.14 (-0.34 to +0.08) | -0.08 (-0.25 to +0.10) |        28.57 |
| all - pos_chg           |        60.66 |        77.44 | -0.37 (-0.45 to -0.28) | +0.08 (+0.02 to +0.13) |        28.65 |
| all - trip_undo         |        61.06 |        77.33 | +0.04 (-0.03 to +0.10) | -0.03 (-0.09 to +0.02) |        28.69 |
| all - lv_x              |        61.04 |        77.42 | +0.02 (-0.05 to +0.08) | +0.06 (+0.01 to +0.11) |        28.63 |
| all - sx_wet            |        60.97 |        77.3  | -0.05 (-0.14 to +0.04) | -0.06 (-0.15 to +0.02) |        28.77 |
| all - tbx_settle_recent |        61.03 |        77.37 | +0.01 (-0.02 to +0.03) | +0.01 (-0.01 to +0.02) |        28.65 |
| all - tbx_bar_recent    |        61.06 |        77.36 | +0.04 (+0.01 to +0.06) | -0.01 (-0.03 to +0.01) |        28.64 |
| all - tbx_settle_long   |        61.02 |        77.36 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.65 |
| all - tbx_bar_long      |        61.03 |        77.36 | +0.01 (-0.01 to +0.03) | -0.01 (-0.02 to +0.01) |        28.67 |
| all - tbx_settle_r90    |        61.03 |        77.36 | +0.01 (-0.02 to +0.03) | -0.01 (-0.03 to +0.02) |        28.66 |
| all - tbx_bar_r90       |        61.02 |        77.37 | +0.00 (-0.01 to +0.01) | +0.01 (+0.00 to +0.01) |        28.66 |
| all - tbx_settle_r365   |        61.02 |        77.36 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.65 |
| all - tbx_bar_r365      |        61.02 |        77.36 | -0.01 (-0.05 to +0.04) | +0.00 (-0.04 to +0.04) |        28.64 |
| all - tbx_settle_rdecay |        61.02 |        77.36 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.65 |
| all - tbx_bar_rdecay    |        61.03 |        77.36 | +0.01 (-0.02 to +0.03) | -0.01 (-0.03 to +0.01) |        28.67 |
| all - tbx_settle_any60  |        61.04 |        77.38 | +0.02 (-0.03 to +0.07) | +0.01 (-0.03 to +0.06) |        28.68 |
| all - tbx_bar_any60     |        61.08 |        77.36 | +0.06 (-0.01 to +0.14) | -0.00 (-0.06 to +0.06) |        28.68 |

## Inside 3 by year (%)

|                 |   2023 |   2024 |   2025 |   2026 |
|:----------------|-------:|-------:|-------:|-------:|
| form            |   59.9 |   61   |   61.1 |   61.5 |
| current         |   60.8 |   61.1 |   60.9 |   61.2 |
| consistent      |   60.1 |   61   |   61   |   61.6 |
| all             |   60.1 |   60.8 |   61   |   61.6 |
| win: consistent |   60.4 |   61   |   61   |   61.7 |
| win: all        |   60.3 |   60.8 |   61   |   61.8 |

## Fitted weights b (1 = the term at face value)

|                                   |    2023 |    2024 |    2025 |    2026 |
|:----------------------------------|--------:|--------:|--------:|--------:|
| consistent:proj_adj               |   0.972 |   0.445 |   0.72  |   0.279 |
| consistent:pos_chg                |   0.45  |   1.772 |   0.745 |   1.364 |
| consistent:trip_undo              |   0.511 |   0     |   0.292 |   0     |
| consistent:lv_x                   |   0     |   0     |   0.215 |   0.211 |
| consistent:sx_wet                 |   0.447 |   0.43  |   0     |   0.105 |
| consistent:tbx_settle_recent      |   0.121 |   0     |   0.922 |   0.252 |
| consistent:tbx_bar_recent         |   0     |   0.304 |   0     |   0.289 |
| all:proj_adj                      |   0.972 |   0.439 |   0.718 |   0.289 |
| all:pos_chg                       |   0.45  |   1.754 |   0.757 |   1.359 |
| all:trip_undo                     |   0.511 |   0     |   0.288 |   0     |
| all:lv_x                          |   0     |   0     |   0.178 |   0.168 |
| all:sx_wet                        |   0.447 |   0.411 |   0     |   0.108 |
| all:tbx_settle_recent             |   0.121 |   0     |   0.81  |   0.144 |
| all:tbx_bar_recent                |   0     |   0.137 |   0     |   0.183 |
| all:tbx_settle_long               |   0     |   0.047 |   0     |   0     |
| all:tbx_bar_long                  |   0     |   0     |   0     |   0     |
| all:tbx_settle_r90                |   0     |   0     |   0     |   0     |
| all:tbx_bar_r90                   |   0     |   0.057 |   0     |   0     |
| all:tbx_settle_r365               |   0     |   0.024 |   0.116 |   0.142 |
| all:tbx_bar_r365                  |   0     |   0     |   0     |   0.017 |
| all:tbx_settle_rdecay             |   0     |   0     |   0     |   0     |
| all:tbx_bar_rdecay                |   0     |   0     |   0.079 |   0.133 |
| all:tbx_settle_any60              |   0     |   0     |   0.039 |   0     |
| all:tbx_bar_any60                 |   0     |   0.162 |   0     |   0     |
| win: consistent:proj_adj          |   1.216 |   1.206 |   1.112 |   0.632 |
| win: consistent:trip_undo         |   0.206 |   0.138 |   0.255 |   0.008 |
| win: consistent:tbx_bar_recent    |   0.11  |   0.299 | nan     |   0.128 |
| win: all:proj_adj                 |   1.27  |   1.196 |   1.112 |   0.63  |
| win: all:trip_undo                |   0.203 |   0.133 |   0.255 |   0.005 |
| win: all:sx_wet                   |   0.034 |   1.134 |   0.283 |   0.376 |
| win: all:tbx_bar_long             |   0.056 | nan     | nan     | nan     |
| win: all:tbx_settle_r90           |   0.115 | nan     | nan     | nan     |
| win: all:tbx_bar_r365             |   0.2   | nan     | nan     | nan     |
| win: all:tbx_settle_any60         |   0.449 | nan     | nan     | nan     |
| win: all:tbx_bar_any60            |   0.211 |   0.298 | nan     | nan     |
| win: consistent:pos_chg           | nan     |   1.285 |   0.549 |   1.147 |
| win: consistent:sx_wet            | nan     |   1.157 |   0.283 |   0.376 |
| win: all:pos_chg                  | nan     |   1.262 |   0.549 |   1.151 |
| win: all:tbx_bar_recent           | nan     |   0.081 | nan     |   0.048 |
| win: consistent:lv_x              | nan     | nan     |   0.247 |   0.146 |
| win: consistent:tbx_settle_recent | nan     | nan     |   0.203 | nan     |
| win: all:lv_x                     | nan     | nan     |   0.247 |   0.144 |
| win: all:tbx_settle_recent        | nan     | nan     |   0.203 | nan     |
| win: all:tbx_bar_r90              | nan     | nan     | nan     |   0.013 |
| win: all:tbx_bar_rdecay           | nan     | nan     | nan     |   0.098 |

