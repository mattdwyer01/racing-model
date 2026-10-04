# Strategy search: win rules chosen on 2023-2024, scored on 2025 to Sep 2026 (walk-forward RM, SP)

- 35,722 VIC/SA/QLD races (19,390 train / 16,332 test), 9,282 rules with >= 150 train bets. Model top pick: train -10.1%, test -13.4%. All bets at SP; every runner loses ~-20% at SP on average here.

## Do good training rules stay good? Rules grouped by training ROI decile

|   train decile |   rules |   train_roi |   test_roi |   test_ae |
|---------------:|--------:|------------:|-----------:|----------:|
|              0 |     929 |      -46.13 |     -32.45 |      1.04 |
|              1 |     928 |      -27.34 |     -24.81 |      1.03 |
|              2 |     928 |      -20.33 |     -18.77 |      1.02 |
|              3 |     928 |      -16.52 |     -17.7  |      1.01 |
|              4 |     928 |      -13.73 |     -16.01 |      1.01 |
|              5 |     928 |      -11.52 |     -14.48 |      1.02 |
|              6 |     928 |       -9.33 |     -14.53 |      1.01 |
|              7 |     928 |       -6.79 |     -13.51 |      1.03 |
|              8 |     928 |       -2.97 |     -14.5  |      1.02 |
|              9 |     929 |        9.25 |     -12.74 |      1.06 |

## Best 30 rules on 2023-2024 and what they did on 2025-2026

| selection             | price   | state   | sm        | field   | extra        |   train bets |   train ROI % |   train A/E |   test bets |   test ROI % |   test A/E | test 95%     |
|:----------------------|:--------|:--------|:----------|:--------|:-------------|-------------:|--------------:|------------:|------------:|-------------:|-----------:|:-------------|
| model overlay 1.5+    | $15+    | SA      | sm >= 0.5 | 13+     | good 1-6     |          187 |        150.27 |        3.15 |         111 |       -12.61 |       1.09 | -100 to +156 |
| model overlay 1.5+    | $15+    | SA      | sm >= 0.5 | 13+     | none         |          191 |        145.03 |        3.02 |         154 |       -37.01 |       0.82 | -100 to +72  |
| model overlay 1.5+    | any     | SA      | sm >= 0.5 | 13+     | not first-up |          159 |        143.71 |        2.74 |         157 |       -22.93 |       1.13 | -92 to +97   |
| model overlay 1.5+    | any     | SA      | sm >= 0.5 | 13+     | good 1-6     |          204 |        139.95 |        2.69 |         124 |        -2.42 |       1.43 | -90 to +135  |
| model overlay 1.5+    | any     | SA      | sm >= 0.5 | 13+     | none         |          208 |        135.34 |        2.62 |         174 |       -30.46 |       0.96 | -93 to +70   |
| model overlay 1.2+    | $15+    | SA      | sm >= 0.5 | 13+     | good 1-6     |          238 |        118.07 |        2.44 |         144 |         2.78 |       1.07 | -100 to +137 |
| model overlay 1.2+    | $15+    | SA      | sm >= 0.5 | 13+     | none         |          247 |        110.12 |        2.28 |         202 |       -26.73 |       0.78 | -100 to +72  |
| model overlay 1.2+    | any     | SA      | sm >= 0.5 | 13+     | good 1-6     |          281 |         97.86 |        1.82 |         186 |        15.32 |       1.35 | -70 to +123  |
| any runner            | any     | SA      | sm >= 0.5 | 13+     | 1600+        |          185 |         93.65 |        1.35 |         247 |       -31.68 |       1.27 | -61 to +3    |
| model overlay 1.2+    | any     | SA      | sm >= 0.5 | 13+     | none         |          292 |         92.47 |        1.82 |         261 |       -17.82 |       0.95 | -78 to +65   |
| model overlay 1.2+    | $15+    | SA      | sm >= 0.5 | 13+     | not first-up |          192 |         90.62 |        2.05 |         183 |       -19.13 |       0.85 | -100 to +86  |
| model overlay 1.2+    | $15+    | all     | sm >= 0.5 | 13+     | first-up     |          178 |         86.52 |        2.6  |         116 |      -100    |       0    | -100 to -100 |
| any runner            | $15+    | SA      | sm >= 0.5 | any     | 1600+        |          358 |         79.33 |        1.84 |         360 |       -13.33 |       1.23 | -61 to +45   |
| any runner            | $15+    | SA      | sm >= 0.5 | 13+     | good 1-6     |          388 |         76.03 |        1.85 |         229 |       -24.02 |       0.73 | -89 to +60   |
| model overlay 1.2+    | any     | SA      | sm >= 0.5 | 13+     | not first-up |          230 |         75.22 |        1.69 |         234 |        -8.33 |       1.13 | -75 to +77   |
| model overlay 1.2+    | any     | all     | sm >= 0.5 | 13+     | first-up     |          215 |         74.42 |        1.77 |         146 |       -82.88 |       0.73 | -98 to -63   |
| any runner            | $15+    | SA      | sm >= 0.5 | 13+     | none         |          404 |         69.06 |        1.74 |         333 |       -47.75 |       0.52 | -92 to +18   |
| model overlay 1.5+    | any     | all     | sm >= 0.5 | 13+     | first-up     |          153 |         66.01 |        1.8  |         100 |       -78.3  |       1.09 | -100 to -50  |
| any runner            | $15+    | SA      | sm >= 0.5 | 13+     | not first-up |          323 |         64.09 |        1.7  |         289 |       -39.79 |       0.59 | -91 to +31   |
| model overlay 1.5+    | $15+    | SA      | sm >= 0.5 | any     | 1600+        |          183 |         62.3  |        1.64 |         188 |         2.13 |       1.59 | -74 to +95   |
| model overlay 1.2+    | any     | SA      | sm >= 0.5 | 13+     | 1200-1599    |          176 |         60.23 |        2.04 |         141 |        27.3  |       1.18 | -82 to +173  |
| model overlay 1.2+    | $15+    | SA      | sm >= 0.5 | 13+     | 1200-1599    |          150 |         59.33 |        1.93 |         109 |        35.78 |       1.48 | -100 to +217 |
| model top             | $8-15   | all     | any       | <= 8    | none         |          181 |         53.31 |        1.68 |         132 |        15.15 |       1.46 | -34 to +72   |
| model top, not SP fav | $8-15   | all     | any       | <= 8    | none         |          181 |         53.31 |        1.68 |         132 |        15.15 |       1.46 | -36 to +73   |
| model top 2           | $15+    | all     | any       | 9-12    | 1600+        |          158 |         51.9  |        2.22 |         110 |       -23.64 |       1.16 | -85 to +48   |
| model top, not SP fav | $8-15   | all     | any       | <= 8    | good 1-6     |          164 |         49.09 |        1.63 |         121 |         4.96 |       1.31 | -46 to +61   |
| model top             | $8-15   | all     | any       | <= 8    | good 1-6     |          164 |         49.09 |        1.63 |         121 |         4.96 |       1.31 | -45 to +65   |
| model overlay 1.2+    | $8-15   | VIC     | sm >= 1   | 9-12    | not first-up |          180 |         46.67 |        1.96 |         188 |       -11.44 |       1.12 | -51 to +33   |
| model overlay 1.5+    | $15+    | all     | sm >= 1   | any     | first-up     |          173 |         44.51 |        1.51 |         142 |       120.42 |       3.06 | -20 to +304  |
| model overlay 1.5+    | $8-15   | VIC     | any       | <= 8    | 1600+        |          212 |         44.1  |        1.76 |         131 |        30.92 |       1.79 | -23 to +93   |

- Mean test ROI of these 30: -11.8% (train +82.7%).

## Rules profitable in both periods (>= 100 test bets), most consistent first

| selection          | price   | state   | sm        | field   | extra         |   train bets |   train ROI % |   train A/E |   test bets |   test ROI % |   test A/E |   2023 |   2024 |   2025 |   2026 |   years + | all 95%     |
|:-------------------|:--------|:--------|:----------|:--------|:--------------|-------------:|--------------:|------------:|------------:|-------------:|-----------:|-------:|-------:|-------:|-------:|----------:|:------------|
| model overlay 1.5+ | $15+    | all     | sm >= 1   | any     | first-up      |          173 |          44.5 |         1.5 |         142 |        120.4 |        3.1 |   38   |   51.9 |   54.7 |  221.4 |         4 | -17 to +193 |
| model overlay 1.2+ | $15+    | all     | sm >= 1   | any     | first-up      |          222 |          30.6 |         1.5 |         188 |         75.5 |        2.3 |    8.5 |   55.2 |   29.3 |  150   |         4 | -24 to +141 |
| model overlay 1.5+ | any     | all     | sm >= 1   | any     | first-up      |          278 |          16.4 |         1   |         234 |         54.2 |        1.1 |    3.9 |   29.7 |   15.7 |  107.7 |         4 | -26 to +106 |
| model overlay 1.2+ | $8-15   | all     | sm >= 0.5 | <= 8    | 1200-1599     |          319 |           6.9 |         1.3 |         286 |         46.9 |        1.9 |    8.3 |    5.6 |   38.7 |   57.8 |         4 | +0 to +54   |
| model overlay 1.2+ | $8-15   | all     | sm >= 1   | <= 8    | good 1-6      |          254 |           8.7 |         1.3 |         230 |         41.1 |        1.9 |    7.4 |   10   |   45.1 |   34.3 |         4 | -6 to +55   |
| model overlay 1.2+ | $8-15   | all     | sm >= 0.5 | <= 8    | 1600+         |          228 |           9.4 |         1.4 |         138 |         40.2 |        1.8 |    7.4 |   11.3 |   34.1 |   52.1 |         4 | -13 to +57  |
| any runner         | any     | SA      | sm >= 1   | 9-12    | 1600+         |          279 |          23.6 |         1   |         355 |         33.1 |        1.4 |   37.9 |   13.9 |   30.2 |   37.1 |         4 | -6 to +71   |
| model overlay 1.2+ | $8-15   | all     | sm >= 1   | any     | 1600+         |          226 |          13.5 |         1.4 |         223 |         24   |        1.6 |   19.6 |    8.9 |   28.1 |   17.4 |         4 | -12 to +50  |
| model overlay 1.2+ | $2-3    | all     | sm >= 0.5 | any     | not first-up  |          193 |           7.9 |         1.2 |         154 |         20.8 |        1.4 |    7.5 |    8.2 |   19.5 |   23   |         4 | +0 to +28   |
| model top 2        | $8-15   | VIC     | any       | any     | wet 7+        |          258 |          20.2 |         1.5 |         316 |         20.3 |        1.5 |    2.8 |   41.4 |   19.5 |   20.8 |         4 | -5 to +48   |
| model top 2        | $8-15   | VIC     | any       | <= 8    | not first-up  |          245 |          36.5 |         1.6 |         263 |         19   |        1.5 |   34.6 |   38.7 |    9.4 |   32.6 |         4 | -1 to +58   |
| model overlay 1.5+ | $8-15   | VIC     | any       | <= 8    | not first-up  |          430 |          21.2 |         1.5 |         411 |         18.4 |        1.6 |   20.7 |   21.7 |   23.7 |   10.7 |         4 | -2 to +43   |
| model top 2        | $8-15   | VIC     | any       | <= 8    | none          |          334 |          27.2 |         1.5 |         332 |         17.5 |        1.5 |   35.6 |   17.8 |   11.8 |   25.2 |         4 | -3 to +48   |
| model overlay 1.5+ | $8-15   | VIC     | any       | <= 8    | none          |          568 |          19.1 |         1.5 |         512 |         15.5 |        1.5 |   18.8 |   19.4 |   25.1 |    3.1 |         4 | -3 to +39   |
| model top 2        | $2-5    | all     | sm >= 1   | 13+     | none          |          178 |          10.7 |         1.3 |         162 |         14.2 |        1.3 |    7.8 |   12.9 |   16.4 |   11.2 |         4 | -5 to +30   |
| model top 4+ clear | $2-3    | all     | sm >= 1   | <= 8    | not first-up  |          187 |           4.8 |         1.2 |         184 |         14   |        1.3 |    0.2 |    9.5 |   17.2 |    8.9 |         4 | -2 to +21   |
| model top 4+ clear | $2-3    | QLD     | sm >= 1   | any     | not first-up  |          211 |          11   |         1.3 |         214 |         13.6 |        1.3 |    5.8 |   14.5 |    9   |   21.7 |         4 | +2 to +24   |
| model top 4+ clear | $2-3    | QLD     | sm >= 0.5 | any     | sprint < 1200 |          164 |           8.7 |         1.2 |         150 |         12.9 |        1.3 |   15.3 |    3.7 |   19.8 |    4.3 |         4 | -3 to +23   |
| model overlay 1.2+ | $2-3    | all     | any       | <= 8    | not first-up  |          200 |           4.3 |         1.2 |         180 |         12.7 |        1.3 |    0.2 |    8.5 |   15.9 |    8.2 |         4 | -4 to +21   |
| model top 2        | $2-5    | all     | sm >= 1   | 13+     | good 1-6      |          159 |           6.5 |         1.2 |         129 |         12.6 |        1.3 |    5.3 |    7.5 |   18.8 |    3.4 |         4 | -9 to +29   |
| model top 4+ clear | $2-3    | QLD     | sm >= 1   | any     | none          |          235 |          10.9 |         1.3 |         233 |         12.6 |        1.3 |   10.7 |   11   |   12.2 |   13.3 |         4 | +1 to +23   |
| model overlay 1.2+ | $2-3    | all     | sm >= 0.5 | <= 8    | none          |          158 |           6.2 |         1.2 |         136 |         11.4 |        1.3 |    9.5 |    3.1 |   13.3 |    8.9 |         4 | -6 to +22   |
| any runner         | $8-15   | VIC     | sm >= 1   | <= 8    | none          |          165 |          27.9 |         1.6 |         154 |         11   |        1.4 |   26.2 |   29.7 |   15.6 |    3.4 |         4 | -16 to +58  |
| model top 4+ clear | $2-3    | QLD     | sm >= 1   | any     | good 1-6      |          216 |          12.2 |         1.3 |         216 |         10.6 |        1.3 |   10.5 |   13.4 |   10   |   11.7 |         4 | +1 to +24   |
| any runner         | $2-5    | all     | sm >= 1   | 13+     | none          |          214 |           7.1 |         1.2 |         200 |          8.3 |        1.3 |    2.3 |   10.7 |    8.8 |    7.6 |         4 | -7 to +23   |


## Neighbour check on the survivors (all years, SP)
- QLD, model top pick clear, race-day adj vs field >= 1 (top ~7% of runners), SP $2-3: clear 3+ +6.3% (604 bets), 4+ +11.7%
  (468, +1 to +22; years +11 +11 +12 +13), 5+ +17.9% (351, +5 to +31), 6+ +21.1% (241, +6 to +36). Widening the price band
  weakens it ($1.5-3 +3.5%, $2-4 +4.5%); adj >= 0.5 +4.1%; no adj filter -2.8%. Same rule VIC -1.6%, SA -25.7%.
  Smooth in clear and adj, QLD only (where the blend edge is): the one credible lead. Not out of sample (all years used).
- VIC model top 2, $8-15, field <= 8 (+22%): neighbours lose (field <= 10 -4%, $6-10 -19%): noise.
