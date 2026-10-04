# Replacing Combo with one rating (pre-race dashboard values, all states)

- 1,753 races 22 Aug to 03 Oct 2026. Lines are set to hold the same number of runners as Combo's 4 / 8, so 'winners inside' compares like with like. Log loss: each rating with one fitted scale (2-fold by date).

|                        | 0                   | 1                           | 2                    | 3                              | 4                                     | 5                   | 6                   |
|:-----------------------|:--------------------|:----------------------------|:---------------------|:-------------------------------|:--------------------------------------|:--------------------|:--------------------|
| rating                 | Combo now           | Projection (dashboard Proj) | Projection, new base | Projection + WPR Nett (fitted) | Proj v2: new base + WPR Nett (fitted) | RM rating           | RM + WPR Nett       |
| top pick win %         | 29.3                | 26.6                        | 27.2                 | 27.4                           | 27.8                                  | 29.1                | 29.5                |
| winner in top 2 %      | 50.1                | 45.5                        | 45.6                 | 46.4                           | 45.6                                  | 50.1                | 49.8                |
| winner in top 3 %      | 63.9                | 59.3                        | 58.2                 | 60.0                           | 59.4                                  | 62.6                | 62.0                |
| top = SP fav %         | 57                  | 45                          | 46                   | 46                             | 47                                    | 54                  | 55                  |
| log loss               | 1.8986              | 1.9844                      | 1.9842               | 2.012                          | 2.0159                                | 1.9086              | 1.9017              |
| inner line (Combo 4)   | 4.0                 | 3.1                         | 3.3                  | 4.2                            | 4.4                                   | 3.9                 | 4.5                 |
| winners inside %       | 54.9                | 50.1                        | 49.4                 | 49.7                           | 50.9                                  | 54.5                | 54.4                |
| A/E vs SP inside       | 1.052               | 1.047                       | 1.038                | 1.036                          | 1.055                                 | 1.06                | 1.059               |
| outer line (Combo 8)   | 8.0                 | 6.7                         | 7.1                  | 9.1                            | 9.5                                   | 8.1                 | 9.6                 |
| winners inside outer % | 80.6                | 76.4                        | 76.1                 | 75.9                           | 76.4                                  | 79.1                | 79.2                |
| win rule bets          | 179                 | 231                         | 239                  | 227                            | 228                                   | 177                 | 175                 |
| win rule win %         | 43.6                | 36.4                        | 36.8                 | 35.2                           | 36.4                                  | 40.7                | 40.0                |
| win rule ROI SP %      | 6.5                 | -0.3                        | 7.5                  | -5.3                           | 2.4                                   | -3.8                | -8.3                |
| win % vs Combo         | +0.0 (+0.0 to +0.0) | -2.7 (-4.3 to -1.1)         | -2.2 (-4.0 to -0.5)  | -1.9 (-3.5 to -0.4)            | -1.5 (-3.1 to +0.1)                   | -0.2 (-2.1 to +1.5) | +0.2 (-1.5 to +1.8) |

- Fitted weights (logit per WPR point): Proj v2 new-base projection +0.108, WPR Nett +0.062 (Nett share 0.37); projection + Nett +0.110 / +0.065 (Nett share 0.37).

