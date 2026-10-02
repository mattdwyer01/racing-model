# Exotic rules (dividends estimated from SP, calibrated on real TAB dividends)

- Test: 2026-08-22 to 2026-10-01, 265 meetings, pre-race dashboard values (all states on the dashboard). Calibration: real TAB dividends on 2026-10-02 (287 pool results). See the module docstring for the method.

## Calibration (real dividend vs 1 / chance of the winning combination)

| pool | n | median real x chance | geo mean | fitted b (1 = proportional) |
|---|---|---|---|---|
| DailyDouble | 5 | 1.11 | 1.04 | 1.00 |
| EarlyQuaddie | 6 | 1.02 | 0.98 | 1.00 |
| Exacta | 45 | 0.89 | 0.82 | 1.03 |
| FirstFour | 45 | 0.75 | 0.75 | 0.92 |
| Quaddie | 5 | 1.07 | 0.98 | 1.00 |
| Quinella | 45 | 0.82 | 0.83 | 1.00 |
| RunningDouble | 40 | 0.88 | 0.87 | 0.99 |
| Treble | 5 | 0.70 | 0.86 | 1.00 |
| Trifecta | 45 | 0.79 | 0.79 | 0.97 |
| Win | 46 | 0.83 | 0.85 | 1.01 |

- real x chance = what $1 returns relative to a fair price from SP (0.80 would be a 20% take with no bias). b < 1: long-odds combinations pay less than proportionally, short ones more.

## Rules on the test days (estimated dividends)

- ROI $1/combo: every combination $1 (big tickets weigh more). ROI flexi: the same stake per bet whatever the combinations (how a flexi punter bets). VIC/SA/QLD column is $1/combo.

| pool          | rule                                   |   bets |   hit % |   avg combos |   ROI $1/combo % | 95%         |   ROI flexi % | 95% flexi   |   VIC/SA/QLD % |
|:--------------|:---------------------------------------|-------:|--------:|-------------:|-----------------:|:------------|--------------:|:------------|---------------:|
| Win           | Combo top                              |   1648 |    30.9 |          1.0 |             -8.1 | -16 to +0   |          -8.1 | -16 to +0   |           -4.3 |
| Win           | SP fav (control)                       |   1648 |    35.0 |          1.0 |             -6.1 | -13 to +0   |          -6.1 | -12 to +0   |           -4.7 |
| Quinella      | box SP, same count as A (control)      |   1198 |    35.6 |          3.9 |             -8.9 | -18 to +1   |          -4.7 | -14 to +5   |           -5.8 |
| Exacta        | box SP, same count as A (control)      |   1198 |    35.6 |          7.8 |             -9.0 | -18 to +1   |          -6.4 | -15 to +3   |           -6.1 |
| Exacta        | SP fav / SP same count as B (control)  |   1543 |    20.5 |          3.2 |             -4.8 | -15 to +6   |          -4.5 | -15 to +5   |           -4.0 |
| Trifecta      | box SP, same count as A (control)      |    673 |    23.0 |         31.4 |            -19.3 | -34 to -3   |         -10.7 | -26 to +6   |          -18.3 |
| Trifecta      | SA / SA / SB (control)                 |   1082 |    24.8 |         31.6 |            -10.4 | -23 to +3   |          -1.5 | -16 to +14  |           -8.5 |
| Trifecta      | SP fav / SA / SB (control)             |   1082 |     9.9 |          7.3 |              7.7 | -16 to +34  |           1.2 | -19 to +22  |            8.2 |
| FirstFour     | SA / SA / SB / SB (control)            |    843 |    17.0 |        142.8 |            -22.8 | -39 to -3   |           1.1 | -23 to +29  |          -19.8 |
| Quinella      | box A                                  |   1198 |    33.7 |          3.9 |              1.0 | -10 to +13  |           3.7 | -7 to +14   |            2.3 |
| Quinella      | box Combo top 3                        |   1645 |    32.6 |          3.0 |             -8.6 | -17 to -0   |          -8.6 | -17 to -0   |          -10.7 |
| Quinella      | box SP top 3 (control)                 |   1645 |    37.6 |          3.0 |             -4.7 | -12 to +3   |          -4.7 | -12 to +3   |           -3.4 |
| Exacta        | box A                                  |   1198 |    33.7 |          7.8 |              2.6 | -9 to +16   |           2.1 | -8 to +13   |            3.6 |
| Exacta        | T / B                                  |   1543 |    16.5 |          3.2 |            -10.0 | -22 to +4   |          -6.0 | -19 to +8   |           -2.8 |
| Exacta        | box Combo top 3                        |   1645 |    32.6 |          6.0 |             -9.2 | -18 to -0   |          -9.2 | -18 to -0   |          -11.5 |
| Exacta        | box SP top 3 (control)                 |   1645 |    37.6 |          6.0 |             -5.9 | -13 to +2   |          -5.9 | -14 to +2   |           -4.8 |
| Trifecta      | box A                                  |    673 |    21.8 |         31.4 |             -3.4 | -25 to +22  |          12.3 | -15 to +44  |           -0.0 |
| Trifecta      | T / A / B                              |   1082 |     6.4 |          7.3 |            -12.8 | -41 to +20  |          11.5 | -21 to +48  |            9.6 |
| Trifecta      | A / A / B                              |   1082 |    21.5 |         31.6 |              3.8 | -14 to +23  |          13.4 | -6 to +37   |            6.2 |
| Trifecta      | box Combo top 4                        |   1640 |    26.7 |         24.0 |            -14.8 | -25 to -3   |         -14.8 | -26 to -4   |          -12.8 |
| Trifecta      | box SP top 4 (control)                 |   1640 |    29.8 |         24.0 |            -14.1 | -22 to -6   |         -14.1 | -22 to -6   |          -16.4 |
| FirstFour     | A / A / B / B                          |    843 |    12.8 |        142.8 |            -21.3 | -48 to +16  |          -3.0 | -34 to +33  |           -2.9 |
| FirstFour     | T / A / B / B                          |    843 |     3.2 |         29.3 |            -55.3 | -76 to -29  |         -41.2 | -66 to -11  |          -46.6 |
| FirstFour     | box Combo top 5                        |   1615 |    26.3 |        120.0 |            -20.3 | -32 to -8   |         -20.3 | -32 to -8   |          -21.8 |
| FirstFour     | box SP top 5 (control)                 |   1615 |    29.0 |        120.0 |            -12.2 | -24 to -0   |         -12.2 | -23 to +0   |           -9.9 |
| RunningDouble | A x A ...                              |   1293 |    34.8 |          6.4 |              2.7 | -9 to +16   |           8.3 | -5 to +22   |            1.2 |
| RunningDouble | B x B ... (dashboard quaddie rule)     |   1293 |    54.8 |         16.2 |             -0.7 | -14 to +15  |           2.1 | -9 to +14   |          -16.0 |
| RunningDouble | Combo top only                         |   1293 |    10.1 |          1.0 |              5.2 | -20 to +33  |           5.2 | -20 to +33  |            3.1 |
| RunningDouble | SP, same count as A each leg (control) |   1293 |    36.8 |          6.4 |             -3.2 | -13 to +9   |           1.3 | -10 to +13  |           -5.5 |
| RunningDouble | SP, same count as B each leg (control) |   1293 |    59.6 |         16.2 |             -7.2 | -16 to +2   |          -2.1 | -11 to +8   |          -13.2 |
| RunningDouble | SP top 2 each leg (control)            |   1293 |    31.9 |          4.0 |              2.3 | -9 to +15   |           2.3 | -10 to +15  |            1.4 |
| RunningDouble | SP top 3 each leg (control)            |   1293 |    48.0 |          9.0 |             -9.5 | -18 to -1   |          -9.5 | -17 to -1   |           -7.7 |
| DailyDouble   | A x A ...                              |    228 |    30.3 |          7.6 |              5.4 | -20 to +31  |          15.1 | -14 to +45  |            7.7 |
| DailyDouble   | B x B ... (dashboard quaddie rule)     |    228 |    52.6 |         19.1 |              2.1 | -17 to +23  |          10.6 | -10 to +33  |          -10.6 |
| DailyDouble   | Combo top only                         |    228 |     8.8 |          1.0 |             23.3 | -35 to +92  |          23.3 | -34 to +92  |           65.9 |
| DailyDouble   | SP, same count as A each leg (control) |    228 |    36.4 |          7.6 |             29.7 | +2 to +60   |          34.5 | +5 to +65   |           25.9 |
| DailyDouble   | SP, same count as B each leg (control) |    228 |    61.8 |         19.1 |             16.1 | -2 to +37   |          23.9 | +5 to +45   |           13.8 |
| DailyDouble   | SP top 2 each leg (control)            |    228 |    27.2 |          4.0 |             29.7 | -2 to +64   |          29.7 | -3 to +64   |           53.5 |
| DailyDouble   | SP top 3 each leg (control)            |    228 |    43.4 |          9.0 |             13.7 | -8 to +36   |          13.7 | -8 to +36   |           25.2 |
| Treble        | A x A ...                              |    217 |    19.4 |         20.2 |             -0.2 | -37 to +48  |          28.1 | -19 to +85  |            0.9 |
| Treble        | B x B ... (dashboard quaddie rule)     |    217 |    38.7 |         82.7 |            -15.8 | -39 to +9   |           6.7 | -21 to +37  |          -27.8 |
| Treble        | Combo top only                         |    217 |     3.7 |          1.0 |             57.5 | -55 to +198 |          57.5 | -58 to +207 |           69.9 |
| Treble        | SP, same count as A each leg (control) |    217 |    23.0 |         20.2 |             12.1 | -26 to +54  |          34.8 | -8 to +81   |            6.0 |
| Treble        | SP, same count as B each leg (control) |    217 |    47.9 |         82.7 |              1.5 | -20 to +24  |           5.6 | -16 to +29  |            2.3 |
| Treble        | SP top 2 each leg (control)            |    217 |    17.1 |          8.0 |             20.8 | -21 to +66  |          20.8 | -21 to +67  |           30.7 |
| Treble        | SP top 3 each leg (control)            |    217 |    29.0 |         27.0 |             -4.9 | -32 to +27  |          -4.9 | -34 to +25  |            2.2 |
| EarlyQuaddie  | A x A ...                              |    127 |    15.0 |         28.9 |              3.0 | -57 to +76  |           2.5 | -47 to +65  |          -29.6 |
| EarlyQuaddie  | B x B ... (dashboard quaddie rule)     |    123 |    32.5 |        147.7 |             73.6 | -48 to +296 |          27.5 | -38 to +131 |          -34.7 |
| EarlyQuaddie  | Combo top only                         |    127 |     2.4 |          1.0 |            -20.8 | -100 to +86 |         -20.8 | -100 to +85 |           13.5 |
| EarlyQuaddie  | SP, same count as A each leg (control) |    127 |    17.3 |         28.9 |             22.4 | -34 to +94  |          31.6 | -31 to +107 |           -3.8 |
| EarlyQuaddie  | SP, same count as B each leg (control) |    123 |    36.6 |        147.7 |             18.3 | -28 to +68  |          60.3 | -17 to +165 |          -23.6 |
| EarlyQuaddie  | SP top 2 each leg (control)            |    127 |    16.5 |         16.0 |             91.3 | -12 to +232 |          91.3 | -14 to +215 |           89.4 |
| EarlyQuaddie  | SP top 3 each leg (control)            |    127 |    32.3 |         81.0 |             17.4 | -24 to +64  |          17.4 | -25 to +66  |            9.6 |
| Quaddie       | A x A ...                              |    196 |    10.7 |         52.1 |             -0.6 | -56 to +65  |          19.8 | -37 to +89  |          -38.1 |
| Quaddie       | B x B ... (dashboard quaddie rule)     |    160 |    25.0 |        211.9 |             10.0 | -42 to +72  |          29.2 | -24 to +91  |           -4.5 |
| Quaddie       | Combo top only                         |    196 |     2.0 |          1.0 |            305.7 | -84 to +935 |         305.7 | -84 to +954 |           27.5 |
| Quaddie       | SP, same count as A each leg (control) |    196 |    12.2 |         52.1 |             14.5 | -56 to +130 |          72.8 | -13 to +175 |          -44.4 |
| Quaddie       | SP, same count as B each leg (control) |    160 |    30.0 |        211.9 |            -12.3 | -46 to +29  |           6.0 | -29 to +48  |          -16.9 |
| Quaddie       | SP top 2 each leg (control)            |    196 |     8.2 |         16.0 |             14.1 | -46 to +91  |          14.1 | -48 to +90  |           39.4 |
| Quaddie       | SP top 3 each leg (control)            |    196 |    19.4 |         81.0 |              2.3 | -39 to +50  |           2.3 | -40 to +54  |           -2.0 |

## Rule vs matched SP control (same bets, flexi; the calibration level cancels out)

- Control = the same number of runners per position, picked by SP instead of Combo / speed map. A gap here is what the dashboard adds beyond the market; it does not depend on the calibration level (only on its slope b, about 1 for every pool).

| pool          | rule                               |   bets |   rule hit % |   control hit % |   rule ROI flexi % |   control ROI flexi % |   rule - control (pts) | 95%             |
|:--------------|:-----------------------------------|-------:|-------------:|----------------:|-------------------:|----------------------:|-----------------------:|:----------------|
| Win           | Combo top                          |   1648 |         30.9 |            35.0 |               -8.1 |                  -6.1 |                   -2.1 | -10.8 to +6.9   |
| Quinella      | box A                              |   1198 |         33.7 |            35.6 |                3.7 |                  -4.7 |                    8.4 | -1.3 to +18.0   |
| Exacta        | box A                              |   1198 |         33.7 |            35.6 |                2.1 |                  -6.4 |                    8.5 | -1.1 to +18.5   |
| Exacta        | T / B                              |   1543 |         16.5 |            20.5 |               -6.0 |                  -4.5 |                   -1.5 | -16.1 to +14.5  |
| Trifecta      | box A                              |    673 |         21.8 |            23.0 |               12.3 |                 -10.7 |                   23.1 | -5.4 to +55.5   |
| Trifecta      | A / A / B                          |   1082 |         21.5 |            24.8 |               13.4 |                  -1.5 |                   14.9 | -7.1 to +36.8   |
| Trifecta      | T / A / B                          |   1082 |          6.4 |             9.9 |               11.5 |                   1.2 |                   10.2 | -24.4 to +48.2  |
| FirstFour     | A / A / B / B                      |    843 |         12.8 |            17.0 |               -3.0 |                   1.1 |                   -4.2 | -33.9 to +27.8  |
| RunningDouble | A x A ...                          |   1293 |         34.8 |            36.8 |                8.3 |                   1.3 |                    7.0 | -6.6 to +20.1   |
| DailyDouble   | A x A ...                          |    228 |         30.3 |            36.4 |               15.1 |                  34.5 |                  -19.4 | -50.7 to +13.3  |
| Treble        | A x A ...                          |    217 |         19.4 |            23.0 |               28.1 |                  34.8 |                   -6.7 | -62.2 to +55.5  |
| Quaddie       | A x A ...                          |    196 |         10.7 |            12.2 |               19.8 |                  72.8 |                  -53.0 | -135.2 to +15.8 |
| EarlyQuaddie  | A x A ...                          |    127 |         15.0 |            17.3 |                2.5 |                  31.6 |                  -29.1 | -90.3 to +27.5  |
| RunningDouble | B x B ... (dashboard quaddie rule) |   1293 |         54.8 |            59.6 |                2.1 |                  -2.1 |                    4.2 | -8.3 to +17.0   |
| DailyDouble   | B x B ... (dashboard quaddie rule) |    228 |         52.6 |            61.8 |               10.6 |                  23.9 |                  -13.4 | -39.0 to +12.8  |
| Treble        | B x B ... (dashboard quaddie rule) |    217 |         38.7 |            47.9 |                6.7 |                   5.6 |                    1.1 | -28.9 to +32.8  |
| Quaddie       | B x B ... (dashboard quaddie rule) |    160 |         25.0 |            30.0 |               29.2 |                   6.0 |                   23.2 | -39.0 to +93.6  |
| EarlyQuaddie  | B x B ... (dashboard quaddie rule) |    123 |         32.5 |            36.6 |               27.5 |                  60.3 |                  -32.9 | -172.8 to +98.7 |

## Calibration days with REAL dividends (2026-10-02; few bets, in-sample for the calibration)

- Hits without a matching TAB dividend dropped: 52.

| pool          | rule                                   |   bets |   hit % |   avg combos |   ROI $1/combo % |   ROI flexi % |   VIC/SA/QLD % |
|:--------------|:---------------------------------------|-------:|--------:|-------------:|-----------------:|--------------:|---------------:|
| Win           | Combo top                              |     50 |    36.0 |          1.0 |            -17.0 |         -17.0 |          -49.6 |
| Win           | SP fav (control)                       |     49 |    42.9 |          1.0 |             -5.9 |          -5.9 |          -13.5 |
| Quinella      | box SP, same count as A (control)      |     32 |    37.5 |          3.1 |            -19.0 |         -31.3 |          -38.7 |
| Exacta        | box SP, same count as A (control)      |     32 |    37.5 |          6.2 |            -18.3 |         -27.9 |          -35.9 |
| Exacta        | SP fav / SP same count as B (control)  |     41 |    26.8 |          2.7 |            -20.2 |           9.5 |          -52.8 |
| Trifecta      | box SP, same count as A (control)      |     18 |    38.9 |         20.3 |            -16.7 |           6.6 |           25.3 |
| Trifecta      | SA / SA / SB (control)                 |     28 |    28.6 |         21.6 |            -45.0 |          -5.7 |          -38.5 |
| Trifecta      | SP fav / SA / SB (control)             |     29 |    10.3 |          5.5 |            -59.2 |         -56.5 |          -91.0 |
| FirstFour     | SA / SA / SB / SB (control)            |     19 |    10.5 |         93.1 |            -75.9 |         -59.6 |          -64.9 |
| Quinella      | box A                                  |     33 |    27.3 |          3.1 |            -45.7 |         -50.0 |          -92.1 |
| Quinella      | box Combo top 3                        |     47 |    31.9 |          3.0 |            -33.9 |         -33.9 |          -47.1 |
| Quinella      | box SP top 3 (control)                 |     46 |    43.5 |          3.0 |             -4.9 |          -4.9 |          -29.7 |
| Exacta        | box A                                  |     33 |    27.3 |          6.2 |            -46.0 |         -48.1 |          -91.4 |
| Exacta        | T / B                                  |     42 |    11.9 |          2.7 |            -65.9 |         -65.5 |         -100.0 |
| Exacta        | box Combo top 3                        |     47 |    31.9 |          6.0 |            -36.2 |         -36.2 |          -50.4 |
| Exacta        | box SP top 3 (control)                 |     46 |    43.5 |          6.0 |            -12.2 |         -12.2 |          -31.0 |
| Trifecta      | box A                                  |     19 |    15.8 |         19.6 |            -81.5 |         -77.0 |         -100.0 |
| Trifecta      | T / A / B                              |     29 |    13.8 |          5.5 |            -22.2 |         -28.8 |         -100.0 |
| Trifecta      | A / A / B                              |     29 |    13.8 |         21.2 |            -79.8 |         -80.5 |         -100.0 |
| Trifecta      | box Combo top 4                        |     46 |    37.0 |         24.0 |            -23.8 |         -23.8 |          -14.3 |
| Trifecta      | box SP top 4 (control)                 |     45 |    48.9 |         24.0 |             12.4 |          12.4 |           38.3 |
| FirstFour     | A / A / B / B                          |     19 |     0.0 |         93.1 |           -100.0 |        -100.0 |         -100.0 |
| FirstFour     | T / A / B / B                          |     19 |     0.0 |         22.0 |           -100.0 |        -100.0 |         -100.0 |
| FirstFour     | box Combo top 5                        |     43 |    27.9 |        120.0 |            -44.3 |         -44.3 |           -8.4 |
| FirstFour     | box SP top 5 (control)                 |     43 |    32.6 |        120.0 |            -49.6 |         -49.6 |          -28.5 |
| RunningDouble | A x A ...                              |     43 |    39.5 |          5.2 |            -28.3 |           8.5 |          -37.8 |
| RunningDouble | B x B ... (dashboard quaddie rule)     |     42 |    50.0 |         11.6 |            -49.0 |         -37.5 |          -49.9 |
| RunningDouble | Combo top only                         |     43 |    14.0 |          1.0 |            -32.3 |         -32.3 |         -100.0 |
| RunningDouble | SP, same count as A each leg (control) |     43 |    58.1 |          5.2 |             82.8 |         119.8 |          133.3 |
| RunningDouble | SP, same count as B each leg (control) |     43 |    67.4 |         11.5 |             19.3 |          20.2 |           45.3 |
| RunningDouble | SP top 2 each leg (control)            |     43 |    37.2 |          4.0 |            -14.0 |         -14.0 |            0.2 |
| RunningDouble | SP top 3 each leg (control)            |     41 |    53.7 |          9.0 |            -28.6 |         -28.6 |           -8.2 |
| DailyDouble   | A x A ...                              |      7 |    42.9 |          4.3 |             51.3 |          78.1 |           40.6 |
| DailyDouble   | B x B ... (dashboard quaddie rule)     |      7 |    42.9 |         13.0 |            -50.1 |         -16.6 |          -64.3 |
| DailyDouble   | Combo top only                         |      7 |     0.0 |          1.0 |           -100.0 |        -100.0 |         -100.0 |
| DailyDouble   | SP, same count as A each leg (control) |      6 |    50.0 |          4.0 |             89.2 |         107.8 |           40.6 |
| DailyDouble   | SP, same count as B each leg (control) |      6 |    83.3 |         13.8 |             73.1 |          71.8 |           82.4 |
| DailyDouble   | SP top 2 each leg (control)            |      7 |    28.6 |          4.0 |             13.6 |          13.6 |           99.2 |
| DailyDouble   | SP top 3 each leg (control)            |      6 |    50.0 |          9.0 |            -15.9 |         -15.9 |          -11.5 |
| Treble        | A x A ...                              |      7 |    42.9 |         11.7 |             37.3 |         243.0 |           27.3 |
| Treble        | B x B ... (dashboard quaddie rule)     |      7 |    42.9 |         64.3 |            -75.0 |         -19.6 |          -80.5 |
| Treble        | Combo top only                         |      7 |     0.0 |          1.0 |           -100.0 |        -100.0 |         -100.0 |
| Treble        | SP, same count as A each leg (control) |      7 |    42.9 |         11.7 |             37.3 |         243.0 |           27.3 |
| Treble        | SP, same count as B each leg (control) |      7 |    71.4 |         64.3 |             54.5 |          39.6 |           70.4 |
| Treble        | SP top 2 each leg (control)            |      7 |    28.6 |          8.0 |             55.7 |          55.7 |          212.9 |
| Treble        | SP top 3 each leg (control)            |      6 |    50.0 |         27.0 |            -30.5 |         -30.5 |           -7.3 |
| Quaddie       | A x A ...                              |      7 |    42.9 |         25.7 |            103.2 |         607.6 |           10.8 |
| Quaddie       | B x B ... (dashboard quaddie rule)     |      7 |    42.9 |        184.9 |            -71.7 |          35.8 |          -87.2 |
| Quaddie       | Combo top only                         |      7 |     0.0 |          1.0 |           -100.0 |        -100.0 |         -100.0 |
| Quaddie       | SP, same count as A each leg (control) |      7 |    42.9 |         25.7 |            103.2 |         607.6 |           10.8 |
| Quaddie       | SP, same count as B each leg (control) |      7 |    71.4 |        184.9 |             89.1 |          95.0 |          112.6 |
| Quaddie       | SP top 2 each leg (control)            |      7 |    28.6 |         16.0 |             61.4 |          61.4 |          177.1 |
| Quaddie       | SP top 3 each leg (control)            |      7 |    42.9 |         81.0 |            -35.5 |         -35.5 |          -45.3 |
| EarlyQuaddie  | A x A ...                              |      6 |     0.0 |         22.0 |           -100.0 |        -100.0 |         -100.0 |
| EarlyQuaddie  | B x B ... (dashboard quaddie rule)     |      6 |    16.7 |         74.7 |            -83.3 |         -68.9 |         -100.0 |
| EarlyQuaddie  | Combo top only                         |      6 |     0.0 |          1.0 |           -100.0 |        -100.0 |         -100.0 |
| EarlyQuaddie  | SP, same count as A each leg (control) |      6 |    33.3 |         22.0 |            742.0 |         407.9 |          673.2 |
| EarlyQuaddie  | SP, same count as B each leg (control) |      6 |    50.0 |         74.7 |            164.8 |          51.4 |           56.2 |
| EarlyQuaddie  | SP top 2 each leg (control)            |      6 |     0.0 |         16.0 |           -100.0 |        -100.0 |         -100.0 |
| EarlyQuaddie  | SP top 3 each leg (control)            |      6 |    16.7 |         81.0 |             19.9 |          19.9 |          139.7 |

