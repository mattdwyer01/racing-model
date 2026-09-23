# Race-day projection v2: walk-forward

- Every model fitted on 2019 to Y-1 and tested on year Y (VIC/SA/QLD races); v1 = previous version

## Projection accuracy

| metric                           |   2023 |   2024 |   2025 |   2026 |
|:---------------------------------|-------:|-------:|-------:|-------:|
| ground loss R2 (QLD GPS): v1     |  0.165 |  0.172 |  0.160 |  0.073 |
| ground loss R2 (QLD GPS): v2     |  0.170 |  0.182 |  0.166 |  0.077 |
| pace R2: early shape             |  0.053 |  0.100 |  0.114 |  0.112 |
| pace R2: leader early rating     |  0.146 |  0.184 |  0.211 |  0.182 |
| projected leader led at 800m: v1 |  0.373 |  0.373 |  0.378 |  0.375 |
| projected leader led at 800m: v2 |  0.390 |  0.392 |  0.391 |  0.392 |
| settle R2: v1                    |  0.283 |  0.292 |  0.286 |  0.292 |
| settle R2: v2                    |  0.312 |  0.322 |  0.313 |  0.318 |
| settle in-race rank corr: v1     |  0.507 |  0.514 |  0.508 |  0.517 |
| settle in-race rank corr: v2     |  0.534 |  0.541 |  0.535 |  0.542 |

## Cost of race shape in WPR points (within-race regression, by fold)

|        |   2023 |   2024 |   2025 |   2026 |
|:-------|-------:|-------:|-------:|-------:|
| settle | -2.577 | -2.563 | -2.590 | -2.577 |
| pace   | -0.358 | -0.344 | -0.361 | -0.373 |
| gl     | -0.205 | -0.177 | -0.157 | -0.143 |

settle: per unit of settle share (leader 0 to last 1); pace: per unit of early shape x (1 - settle); gl: per metre of extra ground

## Win model log loss (conditional logit)

|                          |       2023 |       2024 |       2025 |      2026 |     pooled |
|:-------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                    | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| figure                   |     1.9966 |     1.9992 |     1.9971 |    1.9958 |     1.9973 |
| figure + barrier         |     1.9946 |     1.9968 |     1.9960 |    1.9949 |     1.9956 |
| figure + projection      |     1.9888 |     1.9922 |     1.9928 |    1.9904 |     1.9911 |
| SP                       |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| SP + figure              |     1.7894 |     1.7874 |     1.7844 |    1.7747 |     1.7848 |
| SP + figure + projection |     1.7888 |     1.7869 |     1.7851 |    1.7749 |     1.7847 |

## Paired differences (pooled, negative = first is better)

| model | vs | diff | se |
|---|---|---|---|
| figure + barrier | figure | -0.0017 | 0.0003 |
| figure + projection | figure + barrier | -0.0045 | 0.0006 |
| figure + projection | figure | -0.0062 | 0.0006 |
| SP + figure + projection | SP + figure | -0.0001 | 0.0003 |
| SP + figure + projection | SP | -0.0010 | 0.0004 |

## Projection terms in the figure + projection logit (fit on all 2022 on, raw units)

| feature | beta |
|---|---|
| barrier_pct | -0.0282 |
| proj_settle | -0.8315 |
| proj_pace | -0.0427 |
| proj_gl | +0.0299 |
| proj_adj | +0.1983 |
