# Race-day projection: walk-forward

- Every model fitted on 2019 to Y-1 and tested on year Y (VIC/SA/QLD races)
- v2 = settle / pace / ground-loss projections + WPR cost adjustment; additions: pace x running style, track bias from past meetings, GPS early position (QLD)

## Projection accuracy

| metric                                         |   2023 |   2024 |   2025 |   2026 |
|:-----------------------------------------------|-------:|-------:|-------:|-------:|
| QLD early position (GPS 400m) R2: early model  |  0.270 |  0.310 |  0.317 |  0.313 |
| QLD early position (GPS 400m) R2: settle model |  0.316 |  0.334 |  0.324 |  0.317 |
| ground loss R2 (QLD GPS)                       |  0.170 |  0.186 |  0.165 |  0.077 |
| pace R2: early shape                           |  0.050 |  0.097 |  0.113 |  0.114 |
| projected leader led at 800m                   |  0.391 |  0.393 |  0.393 |  0.395 |
| settle R2                                      |  0.311 |  0.322 |  0.313 |  0.319 |
| settle in-race rank corr                       |  0.533 |  0.541 |  0.534 |  0.543 |

## Cost of race shape in WPR points (within-race regression, by fold)

|        |   2023 |   2024 |   2025 |   2026 |
|:-------|-------:|-------:|-------:|-------:|
| settle | -2.583 | -2.569 | -2.597 | -2.585 |
| pace   | -0.348 | -0.333 | -0.349 | -0.359 |
| gl     | -0.206 | -0.177 | -0.157 | -0.143 |
| late_x |  0.006 |  0.007 |  0.008 |  0.009 |

settle: leader (0) to last (1); pace: per unit of early shape x (1 - settle); gl: per metre of extra ground; late_x: per unit of early shape x late-sectional strength vs field (lengths)

Global settle / barrier slopes used for track bias (2019-2021): -2.55 / -1.24 WPR per unit share

## Win model log loss (conditional logit)

|                               |       2023 |       2024 |       2025 |      2026 |     pooled |
|:------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                         | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| figure                        |     1.9966 |     1.9992 |     1.9971 |    1.9958 |     1.9973 |
| figure + projection v2        |     1.9888 |     1.9922 |     1.9925 |    1.9902 |     1.9910 |
| + pace x style                |     1.9889 |     1.9922 |     1.9924 |    1.9901 |     1.9910 |
| + track bias                  |     1.9858 |     1.9904 |     1.9907 |    1.9873 |     1.9886 |
| + early position              |     1.9889 |     1.9918 |     1.9923 |    1.9895 |     1.9907 |
| + all three                   |     1.9861 |     1.9900 |     1.9904 |    1.9864 |     1.9884 |
| SP                            |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| SP + figure + projection v2   |     1.7889 |     1.7869 |     1.7851 |    1.7749 |     1.7847 |
| SP + figure + projection, all |     1.7893 |     1.7868 |     1.7849 |    1.7745 |     1.7847 |

## Paired differences (pooled; negative = first is better)

| model | vs | all: diff | se | QLD only: diff | se |
|---|---|---|---|---|---|
| figure + projection v2 | figure | -0.0063 | 0.0006 | -0.0074 | 0.0010 |
| + pace x style | figure + projection v2 | -0.0000 | 0.0000 | -0.0000 | 0.0000 |
| + track bias | figure + projection v2 | -0.0023 | 0.0004 | -0.0018 | 0.0006 |
| + early position | figure + projection v2 | -0.0003 | 0.0002 | -0.0004 | 0.0003 |
| + all three | figure + projection v2 | -0.0026 | 0.0005 | -0.0022 | 0.0007 |
| SP + figure + projection, all | SP + figure + projection v2 | -0.0000 | 0.0003 | -0.0002 | 0.0004 |
| SP + figure + projection, all | SP | -0.0010 | 0.0005 | -0.0034 | 0.0008 |

## Projection terms in the '+ all three' logit (fit on all 2022 on, raw units)

| feature | beta |
|---|---|
| barrier_pct | -0.0500 |
| proj_settle | +0.0095 |
| proj_pace | -0.0849 |
| proj_gl | +0.0153 |
| proj_adj | +0.0436 |
| pace_x_late | +0.0011 |
| adj_late | +0.1151 |
| tbx_settle_long | +0.0678 |
| tbx_settle_recent | +0.0707 |
| tbx_bar_long | +0.0687 |
| tbx_bar_recent | +0.0639 |
| bias_adj | +0.0633 |
| proj_early | -1.3245 |
