# Leader value by projected pace and track

- 37,986 VIC/SA/QLD races, 2023 to 23 Sep 2026, walk-forward projection v3 (fitted on 2019 to Y-1, tested on Y). Races with >= 4 runners, one winner, SP for all.
- Slope = within-race WPR per unit projected settle share (0 = leader, 1 = last). Negative = forward runners better. Actual = WPR minus pre-race ability (runners with form). Model = proj_adj + bias_adj.
- Projected vs actual early shape: corr 0.32 (R2 0.11).
- Cost coefficients by fold (WPR): 2023: settle -2.58, pace -0.36, 2024: settle -2.56, pace -0.34, 2025: settle -2.59, pace -0.36, 2026: settle -2.57, pace -0.37

## 1. Leader value by PROJECTED pace (what the model can use)

| pband     |   races |   mean proj shape |   mean actual shape | actual slope (95% CI)   |   model slope |   actual - model |
|:----------|--------:|------------------:|--------------------:|:------------------------|--------------:|-----------------:|
| 1 slowest |    7598 |             -2.65 |               -2.12 | -1.61 (-2.12 to -1.14)  |         -3.72 |             2.10 |
| 2         |    7597 |             -0.60 |               -0.51 | -1.38 (-1.81 to -0.93)  |         -3.14 |             1.77 |
| 3         |    7597 |              0.10 |               -0.16 | -1.20 (-1.66 to -0.77)  |         -2.94 |             1.74 |
| 4         |    7597 |              0.74 |                0.40 | -0.65 (-1.06 to -0.30)  |         -2.60 |             1.95 |
| 5 fastest |    7597 |              2.32 |                1.65 | +0.36 (-0.01 to +0.73)  |         -1.83 |             2.19 |
| all       |   37986 |             -0.02 |               -0.11 | -0.76 (-0.94 to -0.57)  |         -2.72 |             1.96 |

## 1b. Leader value by ACTUAL early shape (hindsight: a perfect pace forecast)

| aband     |   races |   mean proj shape |   mean actual shape | actual slope (95% CI)   |   model slope |   actual - model |
|:----------|--------:|------------------:|--------------------:|:------------------------|--------------:|-----------------:|
| 1 slowest |    6731 |             -0.90 |               -5.53 | -3.14 (-3.54 to -2.74)  |         -2.80 |            -0.34 |
| 2         |    6495 |             -0.14 |               -1.50 | -1.78 (-2.16 to -1.35)  |         -2.72 |             0.95 |
| 3         |    6731 |              0.11 |                0.00 | -0.72 (-1.13 to -0.30)  |         -2.62 |             1.89 |
| 4         |    6286 |              0.32 |                1.47 | +0.14 (-0.29 to +0.58)  |         -2.54 |             2.69 |
| 5 fastest |    6496 |              0.88 |                5.26 | +2.62 (+2.15 to +3.11)  |         -2.26 |             4.89 |
| all       |   37986 |             -0.02 |               -0.11 | -0.76 (-0.95 to -0.58)  |         -2.72 |             1.96 |

## 1c. Leader value by distance

| dband     |   races |   mean proj shape |   mean actual shape | actual slope (95% CI)   |   model slope |   actual - model |
|:----------|--------:|------------------:|--------------------:|:------------------------|--------------:|-----------------:|
| <=1100    |    9691 |              0.11 |               -0.11 | -1.66 (-2.07 to -1.27)  |         -2.87 |             1.22 |
| 1101-1300 |   10402 |             -0.09 |               -0.11 | -0.79 (-1.12 to -0.44)  |         -2.84 |             2.05 |
| 1301-1700 |   12353 |             -0.14 |               -0.27 | -0.73 (-1.03 to -0.43)  |         -2.69 |             1.96 |
| 1701+     |    5540 |              0.18 |                0.26 | +0.69 (+0.15 to +1.25)  |         -2.29 |             2.98 |
| all       |   37986 |             -0.02 |               -0.11 | -0.76 (-0.94 to -0.57)  |         -2.72 |             1.96 |

## 1d. Actual slope by distance x projected pace (model slope in brackets)

| dist      | 1 slowest     | 2             | 3             | 4             | 5 fastest     |
|:----------|:--------------|:--------------|:--------------|:--------------|:--------------|
| 1101-1300 | -2.25 (-3.47) | -1.11 (-3.16) | -0.67 (-3.04) | -0.48 (-2.59) | +0.04 (-2.09) |
| 1301-1700 | -2.08 (-3.87) | -0.40 (-3.16) | -1.03 (-2.83) | -0.65 (-2.54) | -0.04 (-1.84) |
| 1701+     | -0.07 (-3.85) | -0.04 (-2.93) | +1.46 (-2.43) | -0.07 (-2.23) | +1.22 (-1.44) |
| <=1100    | -1.56 (-3.28) | -3.17 (-3.17) | -2.20 (-3.00) | -0.94 (-2.73) | +0.33 (-2.26) |

## 2. At SP: A/E (actual / expected wins at normalised SP) by projected pace

| projected pace   | proj leader A/E   | front third A/E   | back third A/E    |   leader win % |
|:-----------------|:------------------|:------------------|:------------------|---------------:|
| 1 slowest        | 1.099 (1.06-1.14) | 1.051 (1.03-1.07) | 0.921 (0.89-0.95) |           20.5 |
| 2                | 1.043 (1.00-1.09) | 1.038 (1.02-1.06) | 0.964 (0.93-1.00) |           18.1 |
| 3                | 1.103 (1.05-1.16) | 1.042 (1.02-1.06) | 0.952 (0.92-0.99) |           17.6 |
| 4                | 1.070 (1.02-1.12) | 1.031 (1.01-1.05) | 0.956 (0.92-0.99) |           16   |
| 5 fastest        | 1.003 (0.95-1.06) | 1.000 (0.98-1.02) | 1.026 (0.99-1.06) |           13.2 |
| all              | 1.066 (1.04-1.09) | 1.033 (1.02-1.04) | 0.963 (0.95-0.98) |           17.1 |

## 2b. Conditional logit at SP, leave one year out

sd = projected settle share minus race mean; sd x pace = sd times standardised projected shape (a positive beta = forward runners lose value in races projected fast).

| variant                                 |   log loss | betas (all years)                                        | vs previous row                 |
|:----------------------------------------|-----------:|:---------------------------------------------------------|:--------------------------------|
| SP                                      |    1.78779 | log_p_sp +1.129                                          | nan                             |
| SP + model adj                          |    1.78718 | log_p_sp +1.119, adj +0.053                              | -0.00061 (-0.00094 to -0.00025) |
| SP + model adj + settle                 |    1.78714 | log_p_sp +1.121, adj +0.065, sd +0.079                   | -0.00004 (-0.00014 to +0.00006) |
| SP + model adj + settle + settle x pace |    1.78705 | log_p_sp +1.121, adj +0.057, sd +0.050, sd_x_pace +0.101 | -0.00009 (-0.00025 to +0.00006) |

## 3. By track (>= 150 races)

- 70 tracks. Corr actual vs model slope across tracks 0.84; split-half reliability of the actual track slopes 0.53.
- Tracks where forward runners are significantly better (CI below 0): 22 of 70. Tracks with any CI above 0 (back-markers better): 7.
- Tracks where the model slope is outside the actual 95% CI: 38 (Balaklava, Gatton, Gold Coast Poly, Ballarat Synthetic, Yarra Glen, Thangool, Bordertown, Kilmore, Sandown-Lakeside, Rockhampton, Ipswich, Doomben, Emerald, Townsville, Sale, Wangaratta, Ararat, Morphettville Parks, Toowoomba, Bendigo, Mackay, Moonee Valley, Warrnambool, Cranbourne, Strathalbyn, Ballarat, Eagle Farm, Pakenham, Gold Coast, Sunshine Coast, Cairns, Pakenham Synthetic, Mt Gambier, Morphettville, Murray Bridge GH, Longreach, Caulfield Heath, Barcaldine)

| track               | state   |   races | actual (95% CI)         |   model |   actual slow pace |   actual fast pace |   model fast pace |
|:--------------------|:--------|--------:|:------------------------|--------:|-------------------:|-------------------:|------------------:|
| Casterton           | VIC     |     152 | -5.92 (-10.16 to -1.68) |   -8.34 |              -7.57 |              +0.91 |             -7.97 |
| Port Augusta        | SA      |     232 | -5.82 (-8.30 to -3.31)  |   -7.95 |              -9.10 |              -4.20 |             -7.72 |
| Mt Isa              | QLD     |     332 | -5.70 (-9.61 to -1.89)  |   -8.91 |              -6.15 |              -4.92 |             -9.12 |
| Hamilton            | VIC     |     210 | -5.63 (-9.12 to -2.38)  |   -7.29 |              -2.51 |             -11.38 |             -6.43 |
| Balaklava           | SA      |     403 | -5.52 (-7.43 to -3.71)  |   -7.58 |              -5.92 |              -5.37 |             -7.25 |
| Kilcoy              | QLD     |     322 | -5.03 (-7.01 to -2.84)  |   -6.15 |              -4.91 |              -4.36 |             -5.60 |
| Donald              | VIC     |     179 | -4.99 (-7.79 to -2.40)  |   -3.82 |              -3.71 |              -7.03 |             -3.31 |
| Terang              | VIC     |     174 | -4.54 (-8.39 to -0.74)  |   -4.57 |              -7.96 |              -5.45 |             -4.18 |
| Gatton              | QLD     |     484 | -4.00 (-5.41 to -2.63)  |   -5.85 |              -4.05 |              -2.69 |             -5.53 |
| Gold Coast Poly     | QLD     |     637 | -3.55 (-5.05 to -2.10)  |   -5.26 |              -5.98 |              -0.81 |             -4.80 |
| Beaudesert          | QLD     |     294 | -3.50 (-5.78 to -1.49)  |   -4.77 |              -4.67 |              -5.07 |             -3.95 |
| Bairnsdale          | VIC     |     204 | -3.15 (-5.63 to -0.73)  |   -4.11 |              -4.77 |              -3.18 |             -3.32 |
| Horsham             | VIC     |     162 | -3.06 (-5.83 to -0.40)  |   -5.76 |              -2.16 |              -3.40 |             -5.26 |
| Port Lincoln        | SA      |     349 | -3.04 (-4.77 to -1.54)  |   -4.42 |              -2.12 |              -1.74 |             -4.06 |
| Swan Hill           | VIC     |     301 | -2.80 (-4.72 to -0.65)  |   -2.77 |              -2.65 |              -0.22 |             -2.22 |
| Home Hill           | QLD     |     169 | -2.78 (-6.18 to +0.54)  |   -5.15 |              -0.47 |              -5.28 |             -3.85 |
| Gympie              | QLD     |     152 | -2.53 (-7.72 to +3.07)  |   -6.76 |              -8.31 |              +3.93 |             -6.02 |
| Gawler              | SA      |     412 | -2.50 (-4.13 to -0.81)  |   -2.96 |              -0.52 |              -3.84 |             -2.50 |
| Roma                | QLD     |     182 | -2.50 (-7.09 to +1.83)  |   -5.96 |              -1.66 |              -1.72 |             -5.75 |
| Dalby               | QLD     |     294 | -2.28 (-4.70 to -0.27)  |   -2.72 |              -3.10 |              +0.15 |             -2.57 |
| Geelong             | VIC     |     782 | -2.12 (-3.24 to -0.91)  |   -3.09 |              -4.27 |              -0.94 |             -2.62 |
| Warwick             | QLD     |     321 | -2.10 (-3.88 to -0.34)  |   -2.77 |              -1.57 |              -1.45 |             -2.37 |
| Oakbank             | SA      |     170 | -1.93 (-4.31 to +0.37)  |   -2.20 |              -0.91 |              -1.72 |             -1.64 |
| Warracknabeal       | VIC     |     160 | -1.92 (-4.37 to +0.68)  |   -4.15 |              -2.21 |              -2.12 |             -3.63 |
| Ballarat Synthetic  | VIC     |     545 | -1.86 (-3.65 to -0.16)  |   -4.26 |              -3.78 |              -2.13 |             -3.71 |
| Yarra Glen          | VIC     |     223 | -1.84 (-4.24 to +0.64)  |   -4.71 |              -3.09 |              -2.16 |             -4.17 |
| Thangool            | QLD     |     176 | -1.67 (-5.41 to +2.05)  |   -6.58 |              -0.74 |              -2.23 |             -6.14 |
| Bordertown          | SA      |     165 | -1.67 (-4.22 to +0.63)  |   -5.31 |              +0.17 |              -2.53 |             -5.00 |
| Kilmore             | VIC     |     289 | -1.52 (-3.63 to +0.70)  |   -4.50 |              -1.48 |              -2.16 |             -3.99 |
| Wodonga             | VIC     |     267 | -1.28 (-3.45 to +0.94)  |   -3.29 |              -1.29 |              -0.30 |             -2.88 |
| Sandown-Lakeside    | VIC     |     463 | -1.03 (-2.59 to +0.68)  |   -3.97 |              -1.12 |              -1.06 |             -3.59 |
| Echuca              | VIC     |     354 | -1.01 (-2.77 to +0.76)  |   -2.22 |              -2.57 |              -0.88 |             -1.88 |
| Rockhampton         | QLD     |     868 | -0.94 (-2.19 to +0.27)  |   -3.98 |              -1.12 |              -1.01 |             -3.69 |
| Ipswich             | QLD     |    1294 | -0.93 (-1.75 to -0.10)  |   -2.68 |              -1.77 |              -0.36 |             -2.32 |
| Doomben             | QLD     |    1338 | -0.89 (-1.65 to -0.15)  |   -2.89 |              -1.81 |              -0.36 |             -2.34 |
| Emerald             | QLD     |     174 | -0.86 (-4.43 to +2.68)  |   -4.49 |              -1.25 |              -1.29 |             -3.92 |
| Moe                 | VIC     |     407 | -0.77 (-2.91 to +1.11)  |   -1.24 |              -2.91 |              -0.11 |             -0.85 |
| Sandown-Hillside    | VIC     |     610 | -0.61 (-1.88 to +0.63)  |   -1.74 |              -0.74 |              -0.48 |             -1.36 |
| Townsville          | QLD     |     886 | -0.41 (-1.44 to +0.61)  |   -4.42 |              -0.29 |              +0.03 |             -4.09 |
| Benalla             | VIC     |     222 | -0.35 (-2.52 to +1.90)  |   -1.47 |              -0.59 |              +0.20 |             -1.09 |
| Sale                | VIC     |     521 | -0.14 (-1.99 to +1.62)  |   -2.35 |              -0.40 |              -0.92 |             -1.80 |
| Wangaratta          | VIC     |     297 | -0.11 (-2.05 to +1.80)  |   -3.00 |              +3.26 |              +0.29 |             -2.73 |
| Ararat              | VIC     |     180 | -0.03 (-2.92 to +2.76)  |   -3.00 |              -2.59 |              +0.70 |             -2.66 |
| Morphettville Parks | SA      |     688 | -0.02 (-1.08 to +1.04)  |   -2.58 |              -1.21 |              +0.52 |             -2.18 |
| Toowoomba           | QLD     |    1113 | +0.00 (-1.11 to +1.19)  |   -2.10 |              -0.83 |              +0.13 |             -1.85 |
| Caulfield           | VIC     |     665 | +0.05 (-1.11 to +1.22)  |   -0.64 |              -1.26 |              +0.21 |             -0.23 |
| Bendigo             | VIC     |     640 | +0.06 (-1.26 to +1.42)  |   -3.07 |              -0.93 |              -0.32 |             -2.77 |
| Kyneton             | VIC     |     320 | +0.36 (-1.54 to +2.41)  |   -1.16 |              -6.25 |              +2.02 |             -0.88 |
| Mackay              | QLD     |     648 | +0.38 (-0.93 to +1.59)  |   -3.48 |              +0.78 |              +1.11 |             -3.10 |
| Moonee Valley       | VIC     |     540 | +0.40 (-0.90 to +1.73)  |   -2.35 |              +0.93 |              +0.83 |             -1.96 |
| Warrnambool         | VIC     |     542 | +0.44 (-2.03 to +2.82)  |   -3.05 |              -0.92 |              +0.55 |             -2.40 |
| Cranbourne          | VIC     |     686 | +0.48 (-0.93 to +1.91)  |   -2.30 |              -0.52 |              +0.93 |             -1.78 |
| Strathalbyn         | SA      |     386 | +0.76 (-0.91 to +2.53)  |   -1.52 |              -0.57 |              +1.83 |             -1.18 |
| Ballarat            | VIC     |     527 | +0.87 (-1.02 to +2.78)  |   -2.07 |              +0.67 |              +1.91 |             -1.56 |
| Eagle Farm          | QLD     |    1252 | +0.91 (+0.09 to +1.73)  |   -0.68 |              -0.06 |              +2.87 |             -0.08 |
| Pakenham            | VIC     |     796 | +0.94 (-0.50 to +2.39)  |   -1.43 |              -0.45 |              +1.63 |             -1.05 |
| Gold Coast          | QLD     |     585 | +1.00 (-0.12 to +2.13)  |   -2.41 |              -1.50 |              +1.65 |             -2.18 |
| Sunshine Coast      | QLD     |    1494 | +1.16 (+0.34 to +2.08)  |   -1.45 |              +1.03 |              +1.28 |             -0.93 |
| Seymour             | VIC     |     399 | +1.23 (-0.67 to +3.29)  |   +0.27 |              -0.00 |              +1.61 |             +0.57 |
| Werribee            | VIC     |     237 | +1.29 (-1.74 to +4.10)  |   -1.49 |              +4.48 |              +0.13 |             -1.24 |
| Cairns              | QLD     |     536 | +1.37 (-0.41 to +3.07)  |   -2.17 |              +0.08 |              +2.76 |             -1.67 |
| Pakenham Synthetic  | VIC     |     419 | +1.59 (-0.01 to +3.32)  |   -0.55 |              +0.83 |              +2.81 |             -0.17 |
| Mt Gambier          | SA      |     324 | +1.70 (-0.80 to +4.52)  |   -1.00 |              +2.29 |              +0.78 |             -0.73 |
| Morphettville       | SA      |     801 | +1.71 (+0.77 to +2.65)  |   +0.07 |              -0.56 |              +2.39 |             +0.46 |
| Murray Bridge GH    | SA      |     702 | +1.85 (+0.81 to +2.93)  |   +0.40 |              +1.33 |              +2.03 |             +0.98 |
| Longreach           | QLD     |     189 | +1.87 (-1.59 to +5.32)  |   -4.30 |              -0.66 |              +1.24 |             -3.79 |
| Mornington          | VIC     |     529 | +2.04 (+0.57 to +3.48)  |   +0.62 |              +0.81 |              +2.98 |             +0.92 |
| Flemington          | VIC     |     722 | +2.20 (+0.96 to +3.47)  |   +1.20 |              +0.23 |              +3.01 |             +1.52 |
| Caulfield Heath     | VIC     |     204 | +2.39 (+0.16 to +4.60)  |   -0.23 |              +1.77 |              +4.74 |             +0.48 |
| Barcaldine          | QLD     |     152 | +3.10 (-0.28 to +7.02)  |   -1.72 |              +1.28 |              +2.72 |             -1.19 |

