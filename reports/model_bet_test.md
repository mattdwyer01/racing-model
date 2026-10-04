# Betting on the Racing Model's probabilities

- 67,391 races, 2023-01-01 00:00:00 to 2026-09-23 00:00:00, every state, out of sample (yearly retrain). See the module docstring for the method.
- Blend weights recovered per year (a on the model, b on SP): 2023 a 0.12 b 1.07, 2024 a 0.15 b 1.01, 2025 a 0.10 b 1.08, 2026 a 0.09 b 1.07

## Win overlays at SP (blend chance x SP > 1 + margin)

|   margin |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|---------:|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
|     0    |   1459 |       2   |    34.4 |         2.8 |    1.104 |         -4.1 | -12.6 to +4.3  |              -8.2 |
|     0.03 |    446 |       1.3 |    31.4 |         3.1 |    1.104 |         -1   | -17.2 to +16.7 |              -8.3 |
|     0.05 |    211 |       1.2 |    27   |         3.7 |    1.092 |          0.9 | -27.0 to +36.6 |             -10.8 |
|     0.1  |     41 |       1.2 |    17.1 |         5   |    1.008 |        -13.9 | -69.0 to +31.8 |             -21.8 |
|     0.2  |      7 |       1   |    28.6 |         7   |    2.454 |         95.7 |                |              16.4 |

Model alone (model chance x SP > 1 + margin):

|   margin |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|---------:|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
|     0    | 282104 |     207.6 |     5.5 |          21 |    1.011 |        -33.7 | -35.2 to -32.2 |             -25.1 |
|     0.03 | 269149 |     198   |     5.3 |          21 |    1.014 |        -34   | -35.6 to -32.3 |             -25.1 |
|     0.05 | 260752 |     191.9 |     5.1 |          21 |    1.014 |        -34.3 | -35.9 to -32.7 |             -25.2 |
|     0.1  | 241042 |     177.4 |     4.8 |          26 |    1.012 |        -35.3 | -37.1 to -33.5 |             -25.4 |
|     0.2  | 206592 |     152   |     4.2 |          26 |    1.013 |        -36.6 | -38.5 to -34.7 |             -25.9 |

Blend, margin 0.05, by state:

| state    |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%             |   ROI 1/4 Kelly % |
|:---------|-------:|----------:|--------:|------------:|---------:|-------------:|:----------------|------------------:|
| NSW      |     79 |       1.2 |    21.5 |         3.8 |    0.927 |        -29.1 | -54.7 to -0.7   |             -17.2 |
| QLD      |     38 |       1   |    23.7 |         3.9 |    0.988 |         39.2 | -62.8 to +192.2 |             -24.2 |
| VIC/SA   |     79 |       1.1 |    36.7 |         3.7 |    1.438 |         22.8 | -14.9 to +60.4  |              12.5 |
| WA/other |     15 |       1   |    13.3 |         2.9 |    0.437 |        -54   | -100.0 to +21.3 |             -66.9 |

Blend, margin 0.05, by day:

| day        |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|:-----------|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
| Saturday   |     60 |       1.4 |    21.7 |         3.8 |    0.944 |        -25.3 | -58.2 to +9.9  |              -6.3 |
| other days |    151 |       1.1 |    29.1 |         3.6 |    1.145 |         11.3 | -22.9 to +57.9 |             -12.4 |

Blend, margin 0.05, by meeting tier:

| meeting tier   |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%             |   ROI 1/4 Kelly % |
|:---------------|-------:|----------:|--------:|------------:|---------:|-------------:|:----------------|------------------:|
| country        |     89 |       1.1 |    25.8 |         3.4 |    0.999 |        -13.6 | -44.5 to +20.8  |             -17.5 |
| metro          |     54 |       1.3 |    22.2 |         4   |    1.025 |        -19.2 | -60.0 to +33.1  |             -22.7 |
| provincial     |     68 |       1   |    32.4 |         3.6 |    1.26  |         35.7 | -26.2 to +125.7 |               6.8 |

Blend, margin 0.05, by year:

|   year |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|-------:|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
|   2023 |     74 |       1.1 |    27   |         3   |    0.953 |          6.5 | -50.1 to +87.8 |             -30.2 |
|   2024 |    106 |       1.3 |    24.5 |         4   |    1.146 |         -5.6 | -32.0 to +25.1 |               2.2 |
|   2025 |     25 |       1.1 |    36   |         3.4 |    1.316 |         16   | -46.6 to +85.2 |              12.7 |
|   2026 |      6 |       1   |    33.3 |         3.1 |    1.198 |        -18.3 |                |              19.1 |

Blend, margin 0.05, Saturdays by meeting tier:

| tier       |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%             |   ROI 1/4 Kelly % |
|:-----------|-------:|----------:|--------:|------------:|---------:|-------------:|:----------------|------------------:|
| country    |     18 |       1.1 |    16.7 |         3.7 |    0.698 |         -3.3 | -100.0 to +86.0 |             -12.7 |
| metro      |     30 |       1.5 |    13.3 |         4.3 |    0.666 |        -63.2 | -94.2 to -12.1  |             -41.7 |
| provincial |     12 |       1   |    50   |         3.2 |    1.731 |         36.2 | -44.6 to +119.2 |              70.6 |

## Win overlays at the dashboard's fixed price (1369 races, 2026-08-22 00:00:00 to 2026-09-23 00:00:00; blend re-formed on the fixed price)

|   margin |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|---------:|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
|     0    |     80 |       5.7 |    22.5 |         6.5 |    1.092 |         11.8 | -8.3 to +24.1  |               8.1 |
|     0.03 |     65 |       5.9 |    20   |         6.5 |    1.032 |          7.9 | -28.3 to +34.6 |               6.9 |
|     0.05 |     55 |       5   |    21.8 |         7   |    1.081 |         17.5 | -18.8 to +53.8 |               8.5 |
|     0.1  |     43 |       5.4 |    20.9 |         7   |    1.041 |         30   |                |               4.9 |
|     0.2  |     23 |       3.8 |    17.4 |         7   |    0.814 |        -13   |                |               2.3 |

Same bets settled at SP instead (price taken vs SP):

|   margin |   bets |   per day |   win % |   avg price |   A/E pm |   ROI flat % | 95%            |   ROI 1/4 Kelly % |
|---------:|-------:|----------:|--------:|------------:|---------:|-------------:|:---------------|------------------:|
|     0    |     80 |       5.7 |    22.5 |         4.4 |    1.092 |        -28.4 | -40.7 to -17.3 |             -25.8 |
|     0.03 |     65 |       5.9 |    20   |         5   |    1.032 |        -33   | -54.4 to -10.4 |             -26.9 |
|     0.05 |     55 |       5   |    21.8 |         4.8 |    1.081 |        -27.2 | -47.0 to +2.0  |             -25.7 |
|     0.1  |     43 |       5.4 |    20.9 |         4.8 |    1.041 |        -22.6 |                |             -30.2 |
|     0.2  |     23 |       3.8 |    17.4 |         4.2 |    0.814 |        -40.9 |                |             -31.3 |

## Exotic overlays vs the same number of combinations picked by SP (estimated dividends), 2025-2026

- est ROI uses k / SP chance as the dividend; the gap to the SP control is the firmer number.

| pool     |   margin | picks      |   combos |   races |   hits |   hits / SP-expected |   est ROI % | 95%            |
|:---------|---------:|:-----------|---------:|--------:|-------:|---------------------:|------------:|:---------------|
| Exacta   |     0    | SP control |    15195 |    9451 |   1574 |                1.255 |         4.7 | -0.4 to +9.6   |
| Exacta   |     0    | model      |    15195 |    9451 |   1474 |                1.25  |         3.2 | -2.4 to +8.3   |
| Exacta   |     0.05 | SP control |     2863 |    2182 |    348 |                1.397 |        14.3 | +3.0 to +26.7  |
| Exacta   |     0.05 | model      |     2863 |    2182 |    338 |                1.463 |        22.1 | +8.4 to +35.7  |
| Exacta   |     0.1  | SP control |      442 |     342 |     56 |                1.48  |        23.7 | -4.6 to +57.2  |
| Exacta   |     0.1  | model      |      442 |     342 |     61 |                1.837 |        50.6 | +12.2 to +94.9 |
| Quinella |     0    | SP control |     8467 |    7294 |   1461 |                1.212 |         2.1 | -3.2 to +7.1   |
| Quinella |     0    | model      |     8467 |    7294 |   1369 |                1.208 |         1.1 | -4.0 to +6.1   |
| Quinella |     0.05 | SP control |     1381 |    1271 |    252 |                1.274 |         9.3 | -3.5 to +22.8  |
| Quinella |     0.05 | model      |     1381 |    1271 |    240 |                1.309 |        13.9 | -1.1 to +28.1  |
| Quinella |     0.1  | SP control |      179 |     158 |     40 |                1.557 |        27.5 | -5.7 to +59.9  |
| Quinella |     0.1  | model      |      179 |     158 |     34 |                1.571 |        31.9 | -11.6 to +85.1 |
| Trifecta |     0    | SP control |    71023 |   14886 |   1535 |                1.34  |         6.5 | +0.2 to +12.7  |
| Trifecta |     0    | model      |    71023 |   14886 |   1461 |                1.397 |        14   | +6.9 to +20.7  |
| Trifecta |     0.05 | SP control |    19442 |    6263 |    505 |                1.452 |        20.9 | +8.8 to +34.3  |
| Trifecta |     0.05 | model      |    19442 |    6263 |    469 |                1.496 |        21.8 | +8.7 to +35.3  |
| Trifecta |     0.1  | SP control |     4604 |    1877 |    139 |                1.584 |        22.8 | +1.0 to +46.6  |
| Trifecta |     0.1  | model      |     4604 |    1877 |    146 |                1.905 |        52.3 | +22.5 to +86.1 |

Exotics, margin 0.05, by state:

| pool     | state    | picks      |   combos |   races |   hits |   hits / SP-expected |   est ROI % | 95%            |
|:---------|:---------|:-----------|---------:|--------:|-------:|---------------------:|------------:|:---------------|
| Exacta   | NSW      | SP control |      700 |     535 |     74 |                1.236 |         1.3 | -21.7 to +25.9 |
| Exacta   | NSW      | model      |      700 |     535 |     72 |                1.307 |         5.3 | -19.9 to +32.5 |
| Exacta   | QLD      | SP control |      683 |     533 |     98 |                1.6   |        31.6 | +7.0 to +53.7  |
| Exacta   | QLD      | model      |      683 |     533 |     91 |                1.601 |        29.7 | +2.9 to +58.7  |
| Exacta   | VIC/SA   | SP control |     1027 |     742 |    121 |                1.398 |        10.8 | -7.4 to +31.6  |
| Exacta   | VIC/SA   | model      |     1027 |     742 |    119 |                1.493 |        24.9 | +1.3 to +50.4  |
| Exacta   | WA/other | SP control |      453 |     372 |     55 |                1.327 |        16.4 | -10.6 to +45.2 |
| Exacta   | WA/other | model      |      453 |     372 |     56 |                1.419 |        30   | -5.2 to +67.1  |
| Quinella | NSW      | SP control |      317 |     295 |     49 |                1.129 |        -7.6 | -32.4 to +17.6 |
| Quinella | NSW      | model      |      317 |     295 |     44 |                1.1   |       -14.9 | -40.2 to +11.2 |
| Quinella | QLD      | SP control |      342 |     321 |     67 |                1.354 |        21   | -6.6 to +49.0  |
| Quinella | QLD      | model      |      342 |     321 |     62 |                1.349 |        22.1 | -10.1 to +54.5 |
| Quinella | VIC/SA   | SP control |      512 |     457 |     99 |                1.349 |        14.4 | -6.0 to +36.2  |
| Quinella | VIC/SA   | model      |      512 |     457 |     95 |                1.413 |        22.8 | -2.5 to +49.1  |
| Quinella | WA/other | SP control |      210 |     198 |     37 |                1.175 |         3.4 | -30.4 to +37.9 |
| Quinella | WA/other | model      |      210 |     198 |     39 |                1.295 |        22.2 | -15.3 to +64.2 |
| Trifecta | NSW      | SP control |     4674 |    1575 |    109 |                1.278 |        -8.3 | -26.6 to +10.1 |
| Trifecta | NSW      | model      |     4674 |    1575 |     99 |                1.296 |         4.6 | -18.2 to +30.4 |
| Trifecta | QLD      | SP control |     4417 |    1435 |    139 |                1.643 |        55.3 | +21.1 to +90.8 |
| Trifecta | QLD      | model      |     4417 |    1435 |    125 |                1.636 |        39.4 | +10.7 to +74.4 |
| Trifecta | VIC/SA   | SP control |     7010 |    2118 |    176 |                1.455 |        12.2 | -6.8 to +34.5  |
| Trifecta | VIC/SA   | model      |     7010 |    2118 |    173 |                1.603 |        24.8 | +3.5 to +48.1  |
| Trifecta | WA/other | SP control |     3341 |    1135 |     81 |                1.421 |        34.4 | +2.8 to +70.0  |
| Trifecta | WA/other | model      |     3341 |    1135 |     72 |                1.365 |        16.4 | -12.5 to +49.3 |

Exotics, margin 0.05, by day:

| pool     | day        | picks      |   combos |   races |   hits |   hits / SP-expected |   est ROI % | 95%            |
|:---------|:-----------|:-----------|---------:|--------:|-------:|---------------------:|------------:|:---------------|
| Exacta   | Saturday   | SP control |      845 |     644 |    108 |                1.591 |        31.5 | +6.1 to +56.1  |
| Exacta   | Saturday   | model      |      845 |     644 |     98 |                1.558 |        28.9 | +0.0 to +53.7  |
| Exacta   | other days | SP control |     2018 |    1538 |    240 |                1.324 |         7.1 | -6.1 to +21.0  |
| Exacta   | other days | model      |     2018 |    1538 |    240 |                1.427 |        19.2 | +1.9 to +37.0  |
| Quinella | Saturday   | SP control |      424 |     394 |     76 |                1.353 |        13.8 | -10.6 to +37.4 |
| Quinella | Saturday   | model      |      424 |     394 |     73 |                1.394 |        16.5 | -7.9 to +43.5  |
| Quinella | other days | SP control |      957 |     877 |    176 |                1.243 |         7.3 | -7.1 to +22.1  |
| Quinella | other days | model      |      957 |     877 |    167 |                1.275 |        12.7 | -5.5 to +32.0  |
| Trifecta | Saturday   | SP control |     5637 |    1797 |    135 |                1.487 |        21.2 | -3.6 to +48.6  |
| Trifecta | Saturday   | model      |     5637 |    1797 |    124 |                1.532 |        29.1 | -0.7 to +61.4  |
| Trifecta | other days | SP control |    13805 |    4466 |    370 |                1.44  |        20.7 | +6.4 to +35.8  |
| Trifecta | other days | model      |    13805 |    4466 |    345 |                1.484 |        18.8 | +5.1 to +34.2  |

Exotics, margin 0.05, by meeting tier:

| pool     | meeting tier   | picks      |   combos |   races |   hits |   hits / SP-expected |   est ROI % | 95%            |
|:---------|:---------------|:-----------|---------:|--------:|-------:|---------------------:|------------:|:---------------|
| Exacta   | country        | SP control |     1387 |    1059 |    156 |                1.295 |         2.1 | -12.6 to +16.9 |
| Exacta   | country        | model      |     1387 |    1059 |    152 |                1.364 |         8.6 | -10.4 to +27.1 |
| Exacta   | metro          | SP control |      379 |     282 |     36 |                1.182 |        -4.1 | -35.9 to +31.1 |
| Exacta   | metro          | model      |      379 |     282 |     37 |                1.329 |         5.8 | -31.1 to +47.3 |
| Exacta   | provincial     | SP control |     1097 |     841 |    156 |                1.588 |        36.1 | +15.2 to +58.6 |
| Exacta   | provincial     | model      |     1097 |     841 |    149 |                1.624 |        44.7 | +19.5 to +69.3 |
| Quinella | country        | SP control |      667 |     615 |    119 |                1.25  |         1.3 | -16.4 to +21.2 |
| Quinella | country        | model      |      667 |     615 |    112 |                1.271 |         4.2 | -17.3 to +27.0 |
| Quinella | metro          | SP control |      199 |     184 |     23 |                0.877 |       -28.2 | -54.9 to +3.0  |
| Quinella | metro          | model      |      199 |     184 |     23 |                0.941 |       -24.8 | -56.9 to +10.8 |
| Quinella | provincial     | SP control |      515 |     472 |    110 |                1.441 |        34.1 | +13.5 to +57.0 |
| Quinella | provincial     | model      |      515 |     472 |    105 |                1.484 |        41.3 | +16.3 to +68.3 |
| Trifecta | country        | SP control |     8799 |    2807 |    242 |                1.491 |        20.6 | +3.5 to +37.3  |
| Trifecta | country        | model      |     8799 |    2807 |    211 |                1.442 |        16.9 | -1.8 to +35.6  |
| Trifecta | metro          | SP control |     2936 |     922 |     46 |                1.047 |        -8.8 | -39.8 to +27.7 |
| Trifecta | metro          | model      |     2936 |     922 |     50 |                1.285 |        11.7 | -24.1 to +52.7 |
| Trifecta | provincial     | SP control |     7707 |    2534 |    217 |                1.533 |        32.5 | +12.7 to +56.1 |
| Trifecta | provincial     | model      |     7707 |    2534 |    208 |                1.623 |        31.3 | +9.9 to +53.7  |
