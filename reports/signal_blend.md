# Signal blend: position map and past ground loss as their own blend weights

- Base: the out-of-sample prod2 blend (prod2 + SP). Signals: the position map's and past ground loss's shifts to the prod2 blend (from the prod2 disagreement test)
- Weights for year Y fitted on the earlier test years only; evaluated 2024 to 2026, VIC/SA/QLD

## Mean race log loss

|                 |   2024 |   2025 |   2026 |   pooled |
|:----------------|-------:|-------:|-------:|---------:|
| base            | 1.7896 | 1.7845 | 1.7758 |   1.7842 |
| + position map  | 1.7896 | 1.7845 | 1.7758 |   1.7842 |
| + ground loss   | 1.7896 | 1.7845 | 1.7758 |   1.7842 |
| + both          | 1.7896 | 1.7845 | 1.7758 |   1.7842 |
| + both by state | 1.7896 | 1.7845 | 1.7758 |   1.7842 |

## Paired differences vs the base (negative = better; 95% race bootstrap)

| variant         | minus   | all                          | QLD                          | VIC/SA                       |
|:----------------|:--------|:-----------------------------|:-----------------------------|:-----------------------------|
| + position map  | base    | +0.0000 (-0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) |
| + ground loss   | base    | +0.0000 (+0.0000 to +0.0000) | +0.0000 (+0.0000 to +0.0000) | +0.0000 (+0.0000 to +0.0000) |
| + both          | base    | +0.0000 (+0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) | +0.0000 (+0.0000 to +0.0000) |
| + both by state | base    | +0.0000 (-0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) |

## Fitted weights by test year

|                 | 2024                                                                                                                                             | 2025                                                                                                                                           | 2026                                                                                                                                            |
|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| + both          | {'lp': np.float64(0.928), 'd_pm': np.float64(0.201), 'd_gl': np.float64(-0.11)}                                                                  | {'lp': np.float64(0.974), 'd_pm': np.float64(0.076), 'd_gl': np.float64(0.227)}                                                                | {'lp': np.float64(0.973), 'd_pm': np.float64(0.001), 'd_gl': np.float64(0.0)}                                                                   |
| + both by state | {'lp': np.float64(0.928), 'd_pm_q': np.float64(0.311), 'd_pm_v': np.float64(-0.067), 'd_gl_q': np.float64(-0.081), 'd_gl_v': np.float64(-0.089)} | {'lp': np.float64(0.974), 'd_pm_q': np.float64(0.168), 'd_pm_v': np.float64(-0.088), 'd_gl_q': np.float64(0.197), 'd_gl_v': np.float64(0.037)} | {'lp': np.float64(0.972), 'd_pm_q': np.float64(0.199), 'd_pm_v': np.float64(-0.122), 'd_gl_q': np.float64(0.101), 'd_gl_v': np.float64(-0.073)} |
| + ground loss   | {'lp': np.float64(0.928), 'd_gl': np.float64(-0.15)}                                                                                             | {'lp': np.float64(0.974), 'd_gl': np.float64(0.237)}                                                                                           | {'lp': np.float64(0.973), 'd_gl': np.float64(0.0)}                                                                                              |
| + position map  | {'lp': np.float64(0.928), 'd_pm': np.float64(0.183)}                                                                                             | {'lp': np.float64(0.974), 'd_pm': np.float64(0.001)}                                                                                           | {'lp': np.float64(0.973), 'd_pm': np.float64(0.001)}                                                                                            |
| base            | {'lp': np.float64(0.928)}                                                                                                                        | {'lp': np.float64(0.974)}                                                                                                                      | {'lp': np.float64(0.973)}                                                                                                                       |

## Overlay at SP, flat stakes, SP <= 21 (quick look)

| variant         |   edge > |   bets |   ROI at SP | 95%              |
|:----------------|---------:|-------:|------------:|:-----------------|
| base            |    0.000 |    398 |       0.011 | -0.173 to +0.209 |
| base            |    0.050 |     84 |       0.271 | -0.195 to +0.823 |
| base            |    0.100 |     20 |       0.685 | -0.490 to +2.240 |
| + position map  |    0.000 |    399 |       0.016 | -0.165 to +0.216 |
| + position map  |    0.050 |     87 |       0.457 | -0.096 to +1.088 |
| + position map  |    0.100 |     21 |       0.833 | -0.333 to +2.329 |
| + ground loss   |    0.000 |    398 |      -0.013 | -0.188 to +0.180 |
| + ground loss   |    0.050 |     84 |       0.271 | -0.215 to +0.836 |
| + ground loss   |    0.100 |     20 |       0.685 | -0.455 to +2.270 |
| + both          |    0.000 |    404 |       0.010 | -0.170 to +0.206 |
| + both          |    0.050 |     89 |       0.425 | -0.127 to +1.030 |
| + both          |    0.100 |     21 |       0.833 | -0.352 to +2.386 |
| + both by state |    0.000 |    401 |      -0.013 | -0.194 to +0.179 |
| + both by state |    0.050 |     85 |       0.433 | -0.131 to +1.086 |
| + both by state |    0.100 |     20 |       0.685 | -0.435 to +2.275 |
