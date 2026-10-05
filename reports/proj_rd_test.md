# Proj: age / sex / weight out, race-day projection as an explicit adjustment (walk-forward 2023 to Sep 2026)

- 38,310 VIC/SA/QLD races; lines set per variant to hold 3.03 / 4.62 runners a race (the 3 / 5
  lines). 'vs form' = winners per 100 races vs the form-only model (no race-day group, no age / sex / weight), 95% race
  bootstrap: positive = the race-day part adds winners.

| variant    |   inside 3 % |   inside 5 % | vs form, inside 3      | vs form, inside 5      |   top pick % |   MAE |
|:-----------|-------------:|-------------:|:-----------------------|:-----------------------|-------------:|------:|
| live       |        60.53 |        77.15 | +0.08 (-0.20 to +0.37) | -0.10 (-0.35 to +0.12) |        28.24 | 6.481 |
| no_asw     |        60.82 |        77.17 | +0.37 (+0.09 to +0.65) | -0.09 (-0.31 to +0.17) |        28.82 | 6.488 |
| form       |        60.45 |        77.26 | +0.00 (+0.00 to +0.00) | +0.00 (+0.00 to +0.00) |        28.48 | 6.487 |
| form+rd    |        61.09 |        77.3  | +0.64 (+0.45 to +0.82) | +0.04 (-0.13 to +0.20) |        28.73 | 6.492 |
| form+rd1   |        61.04 |        77.26 | +0.60 (+0.41 to +0.78) | +0.01 (-0.16 to +0.16) |        28.77 | 6.492 |
| form+rdraw |        60.84 |        77.38 | +0.39 (+0.17 to +0.63) | +0.13 (-0.08 to +0.32) |        28.7  | 6.501 |

## Inside 3 by year (%)

|            |   2023 |   2024 |   2025 |   2026 |
|:-----------|-------:|-------:|-------:|-------:|
| live       |   60.3 |   60.3 |   60.7 |   60.9 |
| no_asw     |   60.4 |   60.6 |   61   |   61   |
| form       |   60.6 |   60.6 |   60.6 |   61.1 |
| form+rd    |   60.6 |   61   |   60.7 |   61.5 |
| form+rd1   |   60.6 |   60.8 |   60.7 |   61.5 |
| form+rdraw |   61   |   61   |   61   |   61.4 |

## Fitted race-day coefficients (WPR per unit, vs race mean)

|   fold |   b_proj_adj |   b_lv_x |   b_sx_wet |   b1_proj_adj |
|-------:|-------------:|---------:|-----------:|--------------:|
|   2023 |        0.626 |    0.116 |      0.402 |         0.553 |
|   2024 |        0.628 |    0.079 |      0.454 |         0.574 |
|   2025 |        0.627 |    0.384 |     -0.136 |         0.733 |
|   2026 |        0.476 |    0.28  |      0.116 |         0.519 |

