# Picking more winners: Combo vs alternatives (pre-race dashboard values)

- 1,753 races, 22 Aug to 03 Oct 2026, all states. SP favourite won 34.4% (ROI -13.2%). Fitted mixes: weights fitted on one half of the dates, scored on the other.

| ranking                                       |   races |   top pick win % |   winner in top 2 % |   winner in top 3 % |   top pick A/E vs SP |   top pick ROI at SP % |   top pick median SP | win % vs Combo      |
|:----------------------------------------------|--------:|-----------------:|--------------------:|--------------------:|---------------------:|-----------------------:|---------------------:|:--------------------|
| Combo (dashboard now)                         |    1753 |            30.75 |               50.26 |               65.26 |                 1.09 |                 -14.02 |                  3   | +0.0 (+0.0 to +0.0) |
| adjusted WPR projection only                  |    1753 |            26.64 |               45.46 |               59.27 |                 1.08 |                 -17.25 |                  3.5 | -4.1 (-5.6 to -2.7) |
| TopRate rating only                           |    1753 |            33.26 |               54.14 |               67.08 |                 1.1  |                 -11.04 |                  2.8 | +2.5 (+0.9 to +4.1) |
| TopRate wpr_nett only                         |    1753 |            24.47 |               41.93 |               56.47 |                 1.06 |                 -17.32 |                  3.8 | -6.3 (-8.4 to -4.2) |
| Racing Model chance only                      |    1753 |            29.09 |               50.14 |               62.64 |                 1.08 |                 -13.82 |                  3.2 | -1.7 (-3.6 to +0.3) |
| Combo, refitted scale                         |    1753 |            30.75 |               50.26 |               65.26 |                 1.09 |                 -14.02 |                  3   | +0.0 (+0.0 to +0.0) |
| projection + TopRate rating (fitted weights)  |    1753 |            33.43 |               53.57 |               66.8  |                 1.12 |                  -9.53 |                  2.9 | +2.7 (+1.1 to +4.2) |
| Combo + Racing Model                          |    1753 |            31.09 |               50.66 |               65.26 |                 1.1  |                 -11.56 |                  3   | +0.3 (-0.9 to +1.5) |
| projection + rating + Racing Model            |    1753 |            32.34 |               53.51 |               66.29 |                 1.08 |                 -13.64 |                  2.9 | +1.6 (-0.2 to +3.4) |
| projection + rating + Racing Model + wpr_nett |    1753 |            32.46 |               53.62 |               66.06 |                 1.08 |                 -13.21 |                  2.9 | +1.7 (-0.1 to +3.4) |

- Combo, refitted scale: weights combo_r +0.157
- projection + TopRate rating (fitted weights): weights proj_r +0.024, trr_r +0.109
- Combo + Racing Model: weights combo_r +0.111, lrm +0.374
- projection + rating + Racing Model: weights proj_r -0.010, trr_r +0.095, lrm +0.369
- projection + rating + Racing Model + wpr_nett: weights proj_r -0.014, trr_r +0.095, lrm +0.367, wpr_nett_r +0.007
- Combo + fixed price: weights combo_r +0.010, lfx +1.100
- projection + rating + Racing Model + fixed price: weights proj_r -0.010, trr_r +0.013, lrm +0.148, lfx +0.964

## With the market (1,586 races with a full fixed-price snapshot)

| ranking                                          |   races |   top pick win % |   winner in top 2 % |   winner in top 3 % |   top pick A/E vs SP |   top pick ROI at SP % |   top pick median SP |
|:-------------------------------------------------|--------:|-----------------:|--------------------:|--------------------:|---------------------:|-----------------------:|---------------------:|
| Combo                                            |    1586 |            31.34 |               50.5  |               65.13 |                 1.1  |                 -11.68 |                  3.1 |
| fixed price favourite                            |    1586 |            34.74 |               55.23 |               67.91 |                 1.1  |                  -7.56 |                  2.8 |
| Combo + fixed price                              |    1586 |            34.17 |               54.98 |               67.28 |                 1.09 |                 -10    |                  2.8 |
| projection + rating + Racing Model + fixed price |    1586 |            33.8  |               54.6  |               67.4  |                 1.08 |                 -11.04 |                  2.8 |

