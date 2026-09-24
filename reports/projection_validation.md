# Race-day projection v3: walk-forward

- Every model fitted on 2019 to Y-1 and tested on year Y (VIC/SA/QLD races)
- v3 settle model adds: early-speed history matched to distance / first-up / going, speed map (early speed vs neighbours, faster rivals inside, wide x slow), barrier effect by track and distance, trials, weight and apprentice claim; track as a categorical. 'previous' = the v2 settle model

## Projection accuracy

| metric                                 |   2023 |   2024 |   2025 |   2026 |
|:---------------------------------------|-------:|-------:|-------:|-------:|
| ground loss R2 (QLD GPS)               |  0.166 |  0.187 |  0.169 |  0.073 |
| pace R2: early shape                   |  0.057 |  0.103 |  0.119 |  0.121 |
| projected leader led at 800m: previous |  0.386 |  0.394 |  0.393 |  0.394 |
| projected leader led at 800m: v3       |  0.390 |  0.394 |  0.395 |  0.397 |
| settle R2, debutants: previous         |  0.054 |  0.064 |  0.051 |  0.060 |
| settle R2, debutants: v3               |  0.081 |  0.104 |  0.085 |  0.119 |
| settle R2, first-up runners: previous  |  0.242 |  0.242 |  0.237 |  0.249 |
| settle R2, first-up runners: v3        |  0.256 |  0.259 |  0.255 |  0.270 |
| settle R2: previous                    |  0.312 |  0.321 |  0.313 |  0.318 |
| settle R2: v3                          |  0.317 |  0.326 |  0.317 |  0.325 |
| settle in-race rank corr: previous     |  0.534 |  0.541 |  0.535 |  0.542 |
| settle in-race rank corr: v3           |  0.538 |  0.545 |  0.539 |  0.548 |

## Cost of race shape in WPR points (within-race regression, by fold)

|        |   2023 |   2024 |   2025 |   2026 |
|:-------|-------:|-------:|-------:|-------:|
| settle | -2.577 | -2.563 | -2.590 | -2.577 |
| pace   | -0.358 | -0.344 | -0.361 | -0.373 |
| gl     | -0.205 | -0.177 | -0.157 | -0.143 |

Global slopes (2019-2021), WPR per unit share: settle -2.55, barrier -1.24; barrier on settle share 0.157, barrier on performance -1.22

## Win model log loss (conditional logit)

|                                 |       2023 |       2024 |       2025 |      2026 |     pooled |
|:--------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                           | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| figure                          |     1.9966 |     1.9992 |     1.9971 |    1.9958 |     1.9973 |
| projection v3 + track bias      |     1.9822 |     1.9873 |     1.9877 |    1.9841 |     1.9854 |
| + track x distance barrier      |     1.9825 |     1.9874 |     1.9874 |    1.9842 |     1.9855 |
| + speed map                     |     1.9822 |     1.9873 |     1.9879 |    1.9841 |     1.9855 |
| + both                          |     1.9825 |     1.9873 |     1.9876 |    1.9841 |     1.9855 |
| SP                              |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| SP + projection v3 + track bias |     1.7877 |     1.7869 |     1.7848 |    1.7744 |     1.7842 |
| SP + all                        |     1.7883 |     1.7872 |     1.7848 |    1.7745 |     1.7845 |

## Paired differences (pooled; negative = first is better)

| model | vs | all: diff | se | QLD only: diff | se |
|---|---|---|---|---|---|
| projection v3 + track bias | figure | -0.0119 | 0.0009 | -0.0131 | 0.0014 |
| + track x distance barrier | projection v3 + track bias | +0.0000 | 0.0001 | +0.0000 | 0.0002 |
| + speed map | projection v3 + track bias | +0.0000 | 0.0001 | +0.0001 | 0.0001 |
| + both | projection v3 + track bias | +0.0001 | 0.0002 | +0.0001 | 0.0002 |
| SP + projection v3 + track bias | SP | -0.0015 | 0.0005 | -0.0032 | 0.0008 |
| SP + all | SP + projection v3 + track bias | +0.0002 | 0.0001 | +0.0001 | 0.0002 |
| SP + all | SP | -0.0013 | 0.0005 | -0.0031 | 0.0008 |

## Projection terms in the '+ both' logit (fit on all 2022 on, raw units)

| feature | beta |
|---|---|
| barrier_pct | -0.0599 |
| proj_settle | -1.1308 |
| proj_pace | -0.0232 |
| proj_gl | +0.0445 |
| proj_adj | +0.2583 |
| tbx_settle_long | +0.0967 |
| tbx_settle_recent | +0.0576 |
| tbx_bar_long | +0.0329 |
| tbx_bar_recent | +0.0641 |
| bias_adj | +0.0519 |
| tdx_settle | -0.0340 |
| tdx_perf | +0.0502 |
| early_rank2 | -0.0687 |
| wide_x_slow | +0.1379 |
| nb_diff_in | +0.0003 |
| nb_diff_out | +0.0008 |
