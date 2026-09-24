# Figure diagnostic

- Figure weights fitted on races before 2025-01-01; all tests on runs whose next start is in 2025-26 (VIC/SA/QLD next races)
- Next-run target: WPR of the horse's next start. Linear predictors fitted on 2022-2024 pairs

## 1. Predicting the next start's WPR

| predictor                      |   slope |   R2 on 2025-26 |   within-race rank corr |   pairs |
|:-------------------------------|--------:|----------------:|------------------------:|--------:|
| this run WPR                   |   0.636 |           0.363 |                   0.387 |  155043 |
| this run figure                |   0.569 |           0.352 |                   0.379 |  155043 |
| decayed mean WPR (pre-race)    |   0.868 |           0.458 |                   0.445 |  155043 |
| decayed mean figure (pre-race) |   0.792 |           0.452 |                   0.442 |  155043 |

Rank corr = mean within-race Spearman correlation between the prediction and the next race's WPR.

|     year |     pairs |   R2 decayed mean WPR |   R2 decayed mean figure |   rank corr WPR |   rank corr figure |
|---------:|----------:|----------------------:|-------------------------:|----------------:|-------------------:|
| 2025.000 | 92344.000 |                 0.467 |                    0.461 |           0.448 |              0.446 |
| 2026.000 | 62699.000 |                 0.444 |                    0.438 |           0.440 |              0.436 |

## 2. Bias by conditions of this run (mean residual of next WPR, WPR points)

Positive = the horse ran better next time than predicted (the run was under-rated).

Spread (max group minus min group) per condition:

| condition                        |   wpr_spread |   fig_spread |
|:---------------------------------|-------------:|-------------:|
| WPR status                       |         3.65 |         3.86 |
| age                              |         2.05 |         2.18 |
| beaten margin                    |         3.34 |         3.39 |
| class type                       |         8.04 |         8.51 |
| days to next start               |         0.52 |         0.54 |
| distance                         |         1.09 |         1.42 |
| field size                       |         3.19 |         3.09 |
| going                            |         1.54 |         1.65 |
| location class                   |         5.34 |         5.83 |
| on-pace runners by early shape   |         1.43 |         1.36 |
| race early shape                 |         1.68 |         1.69 |
| sectionals                       |         3.39 |         3.59 |
| settle position (share of field) |         0.66 |         2.48 |
| state                            |         1.31 |         1.52 |

| condition                        | group               |      n |   resid, WPR-based |   resid, figure-based |   se |
|:---------------------------------|:--------------------|-------:|-------------------:|----------------------:|-----:|
| settle position (share of field) | leader (0-0.1)      |  20216 |              -0.28 |                 -1.25 | 0.08 |
| settle position (share of field) | 0.1-0.3             |  26616 |               0.18 |                 -0.42 | 0.07 |
| settle position (share of field) | 0.3-0.5             |  27628 |               0.05 |                 -0.10 | 0.07 |
| settle position (share of field) | 0.5-0.7             |  22723 |               0.22 |                  0.50 | 0.07 |
| settle position (share of field) | back (0.7-1)        |  43958 |               0.38 |                  1.23 | 0.05 |
| race early shape                 | slow <-3            |  23944 |               0.19 |                  0.37 | 0.07 |
| race early shape                 | -3 to -1            |  26400 |               0.07 |                  0.11 | 0.06 |
| race early shape                 | -1 to 1             |  56496 |              -0.96 |                 -1.00 | 0.05 |
| race early shape                 | 1 to 3              |  25485 |               0.25 |                  0.23 | 0.07 |
| race early shape                 | fast >3             |  22718 |               0.73 |                  0.69 | 0.08 |
| on-pace runners by early shape   | not on pace         | 120584 |              -0.18 |                  0.07 | 0.03 |
| on-pace runners by early shape   | on pace, even       |  17830 |              -0.38 |                 -1.28 | 0.08 |
| on-pace runners by early shape   | on pace, fast early |   7971 |               0.97 |                 -0.56 | 0.13 |
| on-pace runners by early shape   | on pace, slow early |   8658 |              -0.45 |                 -0.57 | 0.11 |
| distance                         | <=1100              |  37154 |              -0.88 |                 -0.98 | 0.06 |
| distance                         | 1101-1300           |  42686 |              -0.09 |                 -0.12 | 0.05 |
| distance                         | 1301-1600           |  46765 |               0.17 |                  0.20 | 0.05 |
| distance                         | 1601-2000           |  17712 |               0.10 |                  0.22 | 0.08 |
| distance                         | 2000+               |  10660 |               0.21 |                  0.44 | 0.13 |
| going                            | good (<=4)          |  98924 |              -0.43 |                 -0.44 | 0.03 |
| going                            | soft 5-6            |  34657 |               0.02 |                  0.03 | 0.06 |
| going                            | soft 7-heavy 8      |  15435 |               0.70 |                  0.77 | 0.09 |
| going                            | heavy 9-10          |   6027 |               1.10 |                  1.21 | 0.16 |
| state                            | NSW                 |   7391 |              -0.08 |                 -0.13 | 0.14 |
| state                            | QLD                 |  62248 |              -0.73 |                 -0.81 | 0.04 |
| state                            | SA                  |  23441 |              -0.57 |                 -0.64 | 0.07 |
| state                            | VIC                 |  61546 |               0.58 |                  0.71 | 0.05 |
| location class                   | C                   |  59254 |              -2.13 |                 -2.30 | 0.05 |
| location class                   | M                   |  31047 |               3.21 |                  3.53 | 0.05 |
| location class                   | P                   |  64742 |               0.03 |                  0.05 | 0.04 |
| class type                       | BM                  |  60584 |               0.63 |                  0.72 | 0.04 |
| class type                       | CLS                 |  13653 |              -0.23 |                 -0.23 | 0.09 |
| class type                       | MAIH                |    238 |              -1.40 |                 -1.12 | 1.66 |
| class type                       | MDN                 |  43608 |              -1.95 |                 -2.13 | 0.06 |
| class type                       | OPEN                |  18413 |               2.81 |                  3.14 | 0.08 |
| class type                       | REST                |    625 |              -5.22 |                 -5.37 | 0.45 |
| class type                       | RMW                 |    620 |               1.96 |                  2.09 | 0.40 |
| class type                       | RST                 |  16864 |              -1.42 |                 -1.59 | 0.08 |
| class type                       | Steeple             |    208 |              -3.82 |                 -3.24 | 2.12 |
| days to next start               | <=14d               |  54771 |              -0.37 |                 -0.37 | 0.05 |
| days to next start               | 15-28d              |  60753 |               0.08 |                  0.10 | 0.04 |
| days to next start               | 29-60d              |  15449 |              -0.20 |                 -0.21 | 0.10 |
| days to next start               | 61-120d             |   7158 |              -0.44 |                 -0.44 | 0.15 |
| days to next start               | 120d+               |  16912 |              -0.20 |                 -0.17 | 0.10 |
| age                              | 2                   |   5130 |               1.31 |                  1.52 | 0.15 |
| age                              | 3                   |  32954 |               0.15 |                  0.16 | 0.06 |
| age                              | 4                   |  41280 |              -0.30 |                 -0.39 | 0.05 |
| age                              | 5                   |  33707 |              -0.17 |                 -0.16 | 0.06 |
| age                              | 6                   |  21714 |              -0.15 |                 -0.08 | 0.08 |
| age                              | 7+                  |  20258 |              -0.74 |                 -0.66 | 0.08 |
| field size                       | <=7                 |  23032 |              -1.44 |                 -1.33 | 0.08 |
| field size                       | 8-10                |  65589 |              -0.38 |                 -0.36 | 0.04 |
| field size                       | 11-13               |  53995 |               0.22 |                  0.16 | 0.05 |
| field size                       | 14+                 |  12427 |               1.75 |                  1.77 | 0.10 |
| beaten margin                    | won/<=0.5L          |  25602 |              -0.20 |                 -0.30 | 0.07 |
| beaten margin                    | 0.5-2L              |  22536 |              -0.67 |                 -0.70 | 0.06 |
| beaten margin                    | 2-5L                |  47116 |              -0.62 |                 -0.57 | 0.05 |
| beaten margin                    | 5-10L               |  40685 |              -0.65 |                 -0.60 | 0.06 |
| beaten margin                    | 10L+                |  19104 |               2.67 |                  2.69 | 0.11 |
| sectionals                       | sectionals missing  |  15845 |              -3.20 |                 -3.37 | 0.11 |
| sectionals                       | sectionals present  | 139198 |               0.19 |                  0.22 | 0.03 |
| WPR status                       | Final               | 141472 |               0.16 |                  0.19 | 0.03 |
| WPR status                       | Preliminary         |  13571 |              -3.49 |                 -3.67 | 0.11 |

## 3. Figure weights by training cut-off (WPR points per unit)

|         |   2023 |   2024 |   2025 |   2026 |
|:--------|-------:|-------:|-------:|-------:|
| wpr     |  1.000 |  1.000 |  1.000 |  1.000 |
| s_early | -0.126 | -0.084 | -0.046 | -0.026 |
| s_l600  |  0.236 |  0.218 |  0.241 |  0.269 |
| wt_rel  |  0.133 |  0.046 |  0.049 |  0.026 |
| settle  | -6.538 | -5.675 | -5.598 | -5.566 |
| shape   |  0.081 | -0.044 | -0.054 | -0.066 |
| pace    |  0.599 |  0.588 |  0.592 |  0.651 |
