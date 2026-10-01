# Dashboard review (pre-race values)

- 1,614 races, 2026-08-22 to 2026-09-30, all states on the dashboard (847 VIC/SA/QLD). Races with >= 4 runners, one winner, SP and a pre-race projection for every runner.
- Racing Model part from the dashboard file for 18% of runners, out-of-sample scores 81%, none (TopRate speed map kept) 1%.
- Fixed price at the snapshot for 92% of runners. See the module docstring for definitions.

## 1. Top picks (flat 1 unit)

| pick                         |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n | ROI SP 95%   |
|:-----------------------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|:-------------|
| Combo top                    |   1614 |    491 |    30.4 |      3.6 |      -14.9 |                 1.0 |         -14.2 |      1452 | -22 to -8    |
| Proj (adjusted) top          |   1614 |    427 |    26.5 |      4.9 |      -17.9 |                 1.0 |         -16.8 |      1452 | -26 to -10   |
| TopRate rating top           |   1438 |    490 |    34.1 |      3.1 |       -8.4 |                 1.1 |         -10.5 |      1438 | -16 to -1    |
| SP favourite                 |   1614 |    558 |    34.6 |      2.7 |      -12.8 |                 1.0 |          -6.5 |      1452 | -19 to -7    |
| Racing Model top (24 Sep on) |    285 |     96 |    33.7 |      3.8 |       -1.5 |                 1.2 |          -5.5 |       256 | -19 to +17   |

By state group:

| Combo top    |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n | ROI SP 95%   |
|:-------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|:-------------|
| NSW/WA/other |    767 |    230 |    30.0 |      3.5 |      -18.7 |                 1.0 |         -17.5 |       709 | -28 to -9    |
| QLD          |    420 |    125 |    29.8 |      3.5 |      -22.5 |                 1.0 |         -19.4 |       318 | -34 to -9    |
| VIC/SA       |    427 |    136 |    31.9 |      3.8 |       -0.6 |                 1.2 |          -4.7 |       425 | -16 to +14   |

## 2. Combo gap band x speed map tag

A/E price-matched > 1 = wins more than runners at the same SP.

| gap from top   | speed map   |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n |
|:---------------|:------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|
| top            | favoured    |    890 |    284 |    31.9 |      3.6 |      -11.5 |                 1.1 |         -11.0 |       799 |
| top            | neutral     |    516 |    144 |    27.9 |      3.6 |      -22.1 |                 0.9 |         -21.0 |       466 |
| top            | unfavoured  |    208 |     63 |    30.3 |      3.7 |      -11.6 |                 1.1 |         -10.7 |       187 |
| 0-2            | favoured    |    451 |    109 |    24.2 |      5.5 |        2.0 |                 1.2 |           4.2 |       414 |
| 0-2            | neutral     |    379 |     66 |    17.4 |      5.2 |      -32.5 |                 0.9 |         -33.3 |       329 |
| 0-2            | unfavoured  |    199 |     42 |    21.1 |      5.0 |      -10.9 |                 1.0 |          -9.7 |       177 |
| 2-4            | favoured    |    566 |     90 |    15.9 |      6.9 |      -15.3 |                 1.0 |         -22.5 |       517 |
| 2-4            | neutral     |    525 |     79 |    15.0 |      6.7 |      -21.0 |                 1.0 |         -28.1 |       461 |
| 2-4            | unfavoured  |    311 |     55 |    17.7 |      6.2 |      -10.6 |                 1.1 |         -13.6 |       286 |
| 4-6            | favoured    |    615 |     70 |    11.4 |      8.8 |      -32.1 |                 0.9 |         -30.2 |       575 |
| 4-6            | neutral     |    584 |     66 |    11.3 |      9.0 |      -29.6 |                 0.9 |         -35.4 |       511 |
| 4-6            | unfavoured  |    485 |     55 |    11.3 |      8.9 |      -32.3 |                 0.9 |         -32.8 |       447 |
| 6-10           | favoured    |    938 |     76 |     8.1 |     14.6 |      -16.9 |                 1.0 |         -26.8 |       884 |
| 6-10           | neutral     |   1293 |    118 |     9.1 |     13.6 |      -22.5 |                 1.1 |         -23.2 |      1185 |
| 6-10           | unfavoured  |   1150 |    102 |     8.9 |     13.6 |      -16.9 |                 1.1 |         -23.9 |      1071 |
| 10+            | favoured    |   1143 |     37 |     3.2 |     44.4 |      -56.2 |                 0.8 |         -51.6 |      1095 |
| 10+            | neutral     |   2209 |     76 |     3.4 |     46.5 |      -25.9 |                 0.9 |         -19.8 |      2056 |
| 10+            | unfavoured  |   2659 |     82 |     3.1 |     50.9 |      -43.4 |                 0.9 |         -42.2 |      2500 |

| speed map (all runners)   |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n |
|:--------------------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|
| favoured                  |   4603 |    666 |    14.5 |     17.3 |      -25.6 |                 1.1 |         -27.1 |      4284 |
| neutral                   |   5506 |    549 |    10.0 |     24.1 |      -25.1 |                 0.9 |         -23.9 |      5008 |
| unfavoured                |   5012 |    399 |     8.0 |     31.7 |      -31.6 |                 1.0 |         -32.9 |      4668 |

## 3. Your rule: Combo top pick 4+ clear, speed map not unfavoured, no first starter

Main rule:

| rule                      |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n | ROI SP 95%   |
|:--------------------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|:-------------|
| 4 clear, not unfav, no FS |    307 |    126 |    41.0 |      2.6 |       -5.1 |                 1.1 |          -4.4 |       274 | -19 to +9    |

By state group:

| group        |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n | ROI SP 95%   |
|:-------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|:-------------|
| NSW/WA/other |    140 |     56 |    40.0 |      2.7 |      -11.7 |                 1.0 |         -14.3 |       131 | -31 to +9    |
| QLD          |     92 |     38 |    41.3 |      2.4 |      -12.9 |                 1.0 |          -2.6 |        69 | -36 to +10   |
| VIC/SA       |     75 |     32 |    42.7 |      2.7 |       16.7 |                 1.2 |          11.6 |        74 | -17 to +54   |

By SP band:

| SP      |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n |
|:--------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|
| (1, 2]  |    104 |     58 |    55.8 |      1.7 |      -10.2 |                 1.0 |          -6.9 |        91 |
| (2, 3]  |    136 |     50 |    36.8 |      2.5 |       -8.3 |                 1.1 |          -7.7 |       123 |
| (3, 5]  |     57 |     15 |    26.3 |      3.8 |       -2.5 |                 1.2 |          -4.0 |        52 |
| (5, 10] |     10 |      3 |    30.0 |      6.8 |       75.0 |                 2.4 |          75.0 |         8 |

By week:

| week from   |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n |
|:------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|
| 2026-08-17  |     29 |     10 |    34.5 |      2.9 |      -16.0 |                 1.1 |          -7.5 |        20 |
| 2026-08-24  |     34 |     10 |    29.4 |      2.6 |      -16.2 |                 0.8 |          -7.3 |        28 |
| 2026-08-31  |     54 |     22 |    40.7 |      2.8 |       -8.4 |                 1.1 |          -5.4 |        48 |
| 2026-09-07  |     64 |     25 |    39.1 |      2.5 |      -15.9 |                 0.9 |         -13.4 |        61 |
| 2026-09-14  |     51 |     21 |    41.2 |      2.4 |      -10.2 |                 1.0 |         -12.9 |        46 |
| 2026-09-21  |     63 |     34 |    54.0 |      2.5 |       24.7 |                 1.3 |          17.3 |        59 |
| 2026-09-28  |     12 |      4 |    33.3 |      2.7 |      -10.8 |                 0.9 |         -15.4 |        12 |

Variants:

|   clear by | speed map      | first starters   |   bets |   wins |   win % |   avg SP |   ROI SP % |   A/E price-matched |   ROI fixed % |   fixed n | ROI SP 95%   |
|-----------:|:---------------|:-----------------|-------:|-------:|--------:|---------:|-----------:|--------------------:|--------------:|----------:|:-------------|
|          2 | any            | no FS in race    |    726 |    251 |    34.6 |      3.2 |      -10.4 |                 1.1 |          -7.9 |       638 | nan          |
|          2 | any            | FS allowed       |    888 |    317 |    35.7 |      3.1 |       -9.5 |                 1.1 |          -8.6 |       796 | nan          |
|          2 | not unfavoured | no FS in race    |    643 |    225 |    35.0 |      3.1 |       -9.8 |                 1.1 |          -5.9 |       564 | nan          |
|          2 | not unfavoured | FS allowed       |    791 |    285 |    36.0 |      3.1 |       -8.6 |                 1.1 |          -6.6 |       708 | nan          |
|          2 | favoured       | no FS in race    |    435 |    170 |    39.1 |      3.1 |        1.0 |                 1.2 |           4.2 |       383 | nan          |
|          2 | favoured       | FS allowed       |    516 |    201 |    39.0 |      3.1 |        0.4 |                 1.2 |           0.8 |       462 | nan          |
|          3 | any            | no FS in race    |    488 |    181 |    37.1 |      2.8 |      -10.8 |                 1.0 |          -9.2 |       428 | nan          |
|          3 | any            | FS allowed       |    609 |    232 |    38.1 |      2.7 |      -10.8 |                 1.0 |         -10.5 |       546 | nan          |
|          3 | not unfavoured | no FS in race    |    439 |    164 |    37.4 |      2.8 |       -9.8 |                 1.0 |          -7.2 |       383 | nan          |
|          3 | not unfavoured | FS allowed       |    548 |    209 |    38.1 |      2.8 |       -9.9 |                 1.0 |          -9.0 |       489 | nan          |
|          3 | favoured       | no FS in race    |    304 |    128 |    42.1 |      2.7 |        2.5 |                 1.2 |           2.9 |       267 | nan          |
|          3 | favoured       | FS allowed       |    359 |    150 |    41.8 |      2.7 |        1.0 |                 1.1 |          -0.9 |       321 | nan          |
|          4 | any            | no FS in race    |    340 |    140 |    41.2 |      2.6 |       -5.2 |                 1.1 |          -5.0 |       303 | -19 to +8    |
|          4 | any            | FS allowed       |    435 |    183 |    42.1 |      2.5 |       -5.3 |                 1.1 |          -6.4 |       395 | -17 to +7    |
|          4 | not unfavoured | no FS in race    |    307 |    126 |    41.0 |      2.6 |       -5.1 |                 1.1 |          -4.4 |       274 | -19 to +10   |
|          4 | not unfavoured | FS allowed       |    391 |    163 |    41.7 |      2.6 |       -5.2 |                 1.0 |          -6.0 |       355 | -18 to +8    |
|          4 | favoured       | no FS in race    |    223 |    102 |    45.7 |      2.6 |        6.7 |                 1.2 |           5.5 |       200 | -10 to +24   |
|          4 | favoured       | FS allowed       |    266 |    121 |    45.5 |      2.6 |        6.1 |                 1.2 |           2.6 |       242 | -9 to +22    |
|          5 | any            | no FS in race    |    226 |     92 |    40.7 |      2.4 |      -12.9 |                 1.0 |         -14.5 |       200 | nan          |
|          5 | any            | FS allowed       |    297 |    127 |    42.8 |      2.4 |      -11.6 |                 1.0 |         -13.6 |       268 | nan          |
|          5 | not unfavoured | no FS in race    |    209 |     85 |    40.7 |      2.4 |      -13.0 |                 1.0 |         -14.6 |       185 | nan          |
|          5 | not unfavoured | FS allowed       |    271 |    115 |    42.4 |      2.4 |      -11.7 |                 1.0 |         -14.0 |       244 | nan          |
|          5 | favoured       | no FS in race    |    156 |     72 |    46.2 |      2.4 |       -0.5 |                 1.1 |          -3.1 |       138 | nan          |
|          5 | favoured       | FS allowed       |    192 |     89 |    46.4 |      2.4 |       -0.5 |                 1.1 |          -5.0 |       173 | nan          |
|          6 | any            | no FS in race    |    138 |     69 |    50.0 |      2.2 |        5.6 |                 1.1 |          -0.0 |       125 | nan          |
|          6 | any            | FS allowed       |    185 |     96 |    51.9 |      2.2 |        4.9 |                 1.1 |          -1.0 |       170 | nan          |
|          6 | not unfavoured | no FS in race    |    130 |     65 |    50.0 |      2.2 |        5.5 |                 1.1 |           0.1 |       118 | nan          |
|          6 | not unfavoured | FS allowed       |    171 |     88 |    51.5 |      2.2 |        4.9 |                 1.1 |          -1.4 |       157 | nan          |
|          6 | favoured       | no FS in race    |     97 |     55 |    56.7 |      2.3 |       22.5 |                 1.3 |          15.3 |        88 | nan          |
|          6 | favoured       | FS allowed       |    121 |     67 |    55.4 |      2.3 |       18.4 |                 1.2 |           8.8 |       111 | nan          |
|          8 | any            | no FS in race    |     52 |     30 |    57.7 |      1.8 |       -8.9 |                 1.1 |         -16.7 |        47 | nan          |
|          8 | any            | FS allowed       |     72 |     40 |    55.6 |      1.8 |      -11.7 |                 1.0 |         -17.0 |        66 | nan          |
|          8 | not unfavoured | no FS in race    |     51 |     29 |    56.9 |      1.8 |      -10.3 |                 1.0 |         -18.2 |        46 | nan          |
|          8 | not unfavoured | FS allowed       |     70 |     38 |    54.3 |      1.8 |      -13.9 |                 1.0 |         -19.6 |        64 | nan          |
|          8 | favoured       | no FS in race    |     42 |     25 |    59.5 |      1.8 |       -3.9 |                 1.1 |         -13.6 |        38 | nan          |
|          8 | favoured       | FS allowed       |     53 |     30 |    56.6 |      1.8 |       -8.5 |                 1.0 |         -17.6 |        49 | nan          |

## 4. Quaddies

- 304 quaddies with complete pre-race data (234 main, 70 early). Cost = combinations x 1 unit; return = estimated dividend when all four legs are covered.

| quaddie   | selection                       | cap   |   quaddies |   share played % |   hits |   hit % |   avg combos |   median est div (hits) |   est ROI % | est ROI 95%   |
|:----------|:--------------------------------|:------|-----------:|-----------------:|-------:|--------:|-------------:|------------------------:|------------:|:--------------|
| main      | your rule                       | 500   |        118 |             50.4 |     39 |    33.1 |        252.3 |                   298.4 |       -37.3 | -63 to -6     |
| main      | your rule                       | 600   |        138 |             59.0 |     48 |    34.8 |        296.2 |                   304.9 |       -38.1 | -63 to -9     |
| main      | your rule                       | 1000  |        179 |             76.5 |     61 |    34.1 |        409.4 |                   331.3 |       -37.3 | -62 to -9     |
| main      | your rule                       | none  |        234 |            100.0 |     87 |    37.2 |        678.4 |                   472.9 |       -39.3 | -58 to -16    |
| main      | your rule, no first-starter add | 500   |        124 |             53.0 |     41 |    33.1 |        242.4 |                   298.4 |       -35.2 | -61 to -1     |
| main      | your rule, no first-starter add | 600   |        140 |             59.8 |     49 |    35.0 |        279.1 |                   298.4 |       -34.5 | -60 to -2     |
| main      | your rule, no first-starter add | 1000  |        183 |             78.2 |     64 |    35.0 |        399.3 |                   339.2 |       -33.0 | -58 to -4     |
| main      | your rule, no first-starter add | none  |        234 |            100.0 |     87 |    37.2 |        657.9 |                   472.9 |       -37.4 | -56 to -14    |
| main      | within 4 only                   | 500   |        233 |             99.6 |     25 |    10.7 |         49.6 |                   260.1 |       -12.4 | -55 to +38    |
| main      | within 4 only                   | 600   |        234 |            100.0 |     25 |    10.7 |         51.8 |                   260.1 |       -16.6 | -58 to +31    |
| main      | within 4 only                   | 1000  |        234 |            100.0 |     25 |    10.7 |         51.8 |                   260.1 |       -16.6 | -59 to +34    |
| main      | within 4 only                   | none  |        234 |            100.0 |     25 |    10.7 |         51.8 |                   260.1 |       -16.6 | -57 to +33    |
| main      | within 10 all                   | 500   |         54 |             23.1 |     30 |    55.6 |        270.1 |                   183.1 |        -5.5 | -50 to +42    |
| main      | within 10 all                   | 600   |         80 |             34.2 |     40 |    50.0 |        365.6 |                   241.1 |       -31.3 | -61 to +4     |
| main      | within 10 all                   | 1000  |        108 |             46.2 |     54 |    50.0 |        481.2 |                   336.0 |       -34.4 | -59 to -9     |
| main      | within 10 all                   | none  |        234 |            100.0 |    144 |    61.5 |       1588.9 |                   781.6 |       -38.4 | -53 to -22    |
| early     | your rule                       | 500   |         37 |             52.9 |     12 |    32.4 |        261.3 |                   127.3 |       -77.7 | -90 to -61    |
| early     | your rule                       | 600   |         47 |             67.1 |     16 |    34.0 |        322.6 |                   211.3 |       -72.9 | -87 to -57    |
| early     | your rule                       | 1000  |         59 |             84.3 |     20 |    33.9 |        421.3 |                   227.9 |       -56.8 | -86 to -14    |
| early     | your rule                       | none  |         70 |            100.0 |     27 |    38.6 |        582.9 |                   269.8 |       -56.7 | -80 to -25    |
| early     | your rule, no first-starter add | 500   |         47 |             67.1 |     13 |    27.7 |        206.0 |                   188.9 |       -70.7 | -87 to -52    |
| early     | your rule, no first-starter add | 600   |         56 |             80.0 |     17 |    30.4 |        260.5 |                   229.4 |       -52.5 | -81 to -10    |
| early     | your rule, no first-starter add | 1000  |         64 |             91.4 |     21 |    32.8 |        325.7 |                   269.8 |       -32.2 | -76 to +25    |
| early     | your rule, no first-starter add | none  |         70 |            100.0 |     25 |    35.7 |        416.4 |                   272.8 |       -40.2 | -72 to +3     |
| early     | within 4 only                   | 500   |         69 |             98.6 |      8 |    11.6 |         33.4 |                    79.6 |       -56.5 | -88 to -7     |
| early     | within 4 only                   | 600   |         70 |            100.0 |      8 |    11.4 |         41.5 |                    79.6 |       -65.5 | -91 to -20    |
| early     | within 4 only                   | 1000  |         70 |            100.0 |      8 |    11.4 |         41.5 |                    79.6 |       -65.5 | -92 to -20    |
| early     | within 4 only                   | none  |         70 |            100.0 |      8 |    11.4 |         41.5 |                    79.6 |       -65.5 | -91 to -23    |
| early     | within 10 all                   | 500   |         31 |             44.3 |     13 |    41.9 |        251.6 |                   132.8 |       -62.9 | -88 to -21    |
| early     | within 10 all                   | 600   |         33 |             47.1 |     15 |    45.5 |        269.8 |                   174.3 |       -42.2 | -81 to +5     |
| early     | within 10 all                   | 1000  |         53 |             75.7 |     26 |    49.1 |        478.1 |                   254.1 |       -30.2 | -65 to +11    |
| early     | within 10 all                   | none  |         70 |            100.0 |     40 |    57.1 |        874.0 |                   404.3 |       -16.1 | -53 to +26    |
| both      | your rule                       | 500   |        155 |             51.0 |     51 |    32.9 |        254.5 |                   214.2 |       -47.2 | -68 to -22    |
| both      | your rule                       | 600   |        185 |             60.9 |     64 |    34.6 |        302.9 |                   268.9 |       -47.5 | -66 to -25    |
| both      | your rule                       | 1000  |        238 |             78.3 |     81 |    34.0 |        412.4 |                   311.5 |       -42.2 | -63 to -19    |
| both      | your rule                       | none  |        304 |            100.0 |    114 |    37.5 |        656.4 |                   424.4 |       -42.9 | -59 to -24    |
| both      | your rule, no first-starter add | 500   |        171 |             56.2 |     54 |    31.6 |        232.4 |                   248.7 |       -43.8 | -64 to -18    |
| both      | your rule, no first-starter add | 600   |        196 |             64.5 |     66 |    33.7 |        273.8 |                   270.1 |       -39.4 | -61 to -13    |
| both      | your rule, no first-starter add | 1000  |        247 |             81.2 |     85 |    34.4 |        380.3 |                   325.6 |       -32.8 | -55 to -7     |
| both      | your rule, no first-starter add | none  |        304 |            100.0 |    112 |    36.8 |        602.3 |                   425.6 |       -37.9 | -55 to -18    |
| both      | within 4 only                   | 500   |        302 |             99.3 |     33 |    10.9 |         45.9 |                   217.0 |       -19.8 | -57 to +24    |
| both      | within 4 only                   | 600   |        304 |            100.0 |     33 |    10.9 |         49.5 |                   217.0 |       -26.1 | -59 to +17    |
| both      | within 4 only                   | 1000  |        304 |            100.0 |     33 |    10.9 |         49.5 |                   217.0 |       -26.1 | -62 to +16    |
| both      | within 4 only                   | none  |        304 |            100.0 |     33 |    10.9 |         49.5 |                   217.0 |       -26.1 | -60 to +16    |
| both      | within 10 all                   | 500   |         85 |             28.0 |     43 |    50.6 |        263.4 |                   172.1 |       -25.5 | -55 to +9     |
| both      | within 10 all                   | 600   |        113 |             37.2 |     55 |    48.7 |        337.6 |                   194.1 |       -33.8 | -59 to -5     |
| both      | within 10 all                   | 1000  |        161 |             53.0 |     80 |    49.7 |        480.2 |                   312.0 |       -33.1 | -53 to -11    |
| both      | within 10 all                   | none  |        304 |            100.0 |    184 |    60.5 |       1424.3 |                   708.8 |       -35.3 | -49 to -20    |

Your rule at the 600 cap, by state group and leg-miss reasons:

| group   |   quaddies |   share played % |   hits |   hit % |   avg combos |   median est div (hits) |   est ROI % | est ROI 95%   |
|:--------|-----------:|-----------------:|-------:|--------:|-------------:|------------------------:|------------:|:--------------|
| QLD     |         57 |            100.0 |     17 |    29.8 |        289.0 |                   174.3 |       -63.2 | -85 to -34    |
| SA      |          4 |            100.0 |      2 |    50.0 |        333.0 |                   922.4 |        38.5 | -100 to +220  |
| VIC     |         40 |            100.0 |     14 |    35.0 |        333.2 |                   329.3 |       -45.9 | -83 to +13    |
| other   |         84 |            100.0 |     31 |    36.9 |        296.5 |                   260.1 |       -42.6 | -69 to -6     |

Where race winners sit (all races):

| winner was                 |   share of winners % |
|:---------------------------|---------------------:|
| within 4                   |                 57.7 |
| 4-10, speed map ok         |                 20.4 |
| outside 10                 |                 11.6 |
| 4-10, unfavoured           |                  9.5 |
| first starter (outside 10) |                  0.7 |

