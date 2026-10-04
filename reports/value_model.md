# Value models fitted on the market's errors (walk-forward, VIC/SA/QLD, test 2024 to Sep 2026, SP)

- 26,092 test races (fits on all earlier years; 2023 is training only).

## Accuracy against SP (log loss per race; negative = better than calibrated SP)

| model | log loss | vs SP only (95%) | QLD | VIC / SA |
|---|---|---|---|---|
| SP only | 1.7800 |  | +0.0000 | +0.0000 |
| RM blend (production style) | 1.7795 | -0.0005 (-0.0011 to +0.0001) | -0.0014 | +0.0002 |
| RM value | 1.7793 | -0.0007 (-0.0018 to +0.0003) | -0.0019 | +0.0001 |
| Proj value | 1.7794 | -0.0007 (-0.0016 to +0.0003) | -0.0012 | -0.0002 |

## Betting on value (model chance x SP above the cut, SP <= $21, flat at SP)

| model                       |   value cut | pool            |   bets |   per week |   median SP |   A/E pm |   ROI % | 95%         |   ROI 2024 % |   ROI 2025 % |   ROI 2026 % |
|:----------------------------|------------:|:----------------|-------:|-----------:|------------:|---------:|--------:|:------------|-------------:|-------------:|-------------:|
| RM blend (production style) |        1    | all             |    195 |        1.4 |         3.1 |    1.296 |    12.5 | -10 to +34  |         33.2 |         12   |        -24.2 |
| RM blend (production style) |        1    | within 4, no FS |    119 |        0.8 |         3.1 |    1.279 |     4.1 | -22 to +33  |         43.5 |         -9.2 |        -28.9 |
| RM value                    |        1    | all             |   2404 |       16.9 |         4   |    1.148 |    -3.4 | -11 to +5   |         -3.6 |          3.1 |        -19.7 |
| RM value                    |        1    | within 4, no FS |   1474 |       10.4 |         4   |    1.148 |    -1.2 | -11 to +8   |          2.7 |         -2.4 |        -22.8 |
| RM value                    |        1.05 | all             |    643 |        4.5 |         4.6 |    1.174 |     8.2 | -10 to +27  |          1.9 |         42   |        -55.2 |
| RM value                    |        1.05 | within 4, no FS |    386 |        2.7 |         4.4 |    1.2   |    16.6 | -7 to +43   |         11.1 |         49.5 |        -84.6 |
| RM value                    |        1.1  | all             |    180 |        1.3 |         4.8 |    1.27  |    25.6 | -11 to +65  |         23.9 |         45.2 |        -38.3 |
| RM value                    |        1.1  | within 4, no FS |    111 |        0.8 |         4.8 |    1.188 |    23.1 | -22 to +74  |         17.3 |         59   |       -100   |
| Proj value                  |        1    | all             |   1892 |       13.3 |         4   |    1.171 |     2.4 | -7 to +12   |         -2.8 |         13.3 |          8.7 |
| Proj value                  |        1    | within 4, no FS |   1073 |        7.5 |         3.7 |    1.156 |     3.8 | -7 to +15   |         -1.3 |         14.2 |          3.4 |
| Proj value                  |        1.05 | all             |    471 |        3.3 |         4.4 |    1.308 |    20.4 | -1 to +43   |         10.6 |         79.4 |        -50   |
| Proj value                  |        1.05 | within 4, no FS |    271 |        1.9 |         4   |    1.156 |    16.5 | -12 to +48  |          8.2 |         69.1 |        -75   |
| Proj value                  |        1.1  | all             |    117 |        0.8 |         5   |    1.446 |    30.6 | -12 to +78  |         43.5 |        -14.2 |        -73.6 |
| Proj value                  |        1.1  | within 4, no FS |     65 |        0.5 |         5   |    1.383 |    36.9 | -20 to +102 |         62.9 |        -34.4 |       -100   |

## Fitted weights (2026 fit: all of 2023-2025)

**RM value**: lsp +1.038, lrm +0.089, f_barrier10 +0.040, f_dist_down +0.004, f_dist_up +0.025, f_back14 +0.011, f_4thup +0.045, f_age6 +0.027, f_weak_jockey +0.021, f_sm +0.039, f_bias +0.013, f_wide +0.066, f_gps_ground +0.080, f_heldup -0.004, f_laid +0.016, f_vet +0.093, f_l600_worst +0.027, f_wet_poor_sire -0.089, n_top_jockey -0.040, n_apprentice -0.078, n_every_chance -0.089, n_stay_poor_sire -0.022, lsp_x_field13 +0.023, lsp_x_wet -0.022, lsp_x_qld +0.007, lsp_x_fs_race +0.027, lsp_x_sprint +0.055

**Proj value**: lsp +1.074, wpr_r +0.005, adj_r +0.021, bias_r +0.039, debut +0.277, f_barrier10 +0.043, f_dist_down -0.006, f_dist_up +0.021, f_back14 +0.016, f_4thup +0.047, f_age6 +0.012, f_weak_jockey +0.005, f_sm +0.029, f_bias -0.032, f_wide +0.069, f_gps_ground +0.083, f_heldup -0.003, f_laid +0.021, f_vet +0.104, f_l600_worst +0.016, f_wet_poor_sire -0.088, n_top_jockey -0.011, n_apprentice -0.079, n_every_chance -0.097, n_stay_poor_sire -0.021, lsp_x_field13 +0.020, lsp_x_wet -0.022, lsp_x_qld +0.010, lsp_x_fs_race +0.028, lsp_x_sprint +0.058


## Live pipeline check (model/value_live.py, apprentice = claimed in the last 120 days)

- Walk-forward log loss vs SP only: -0.0006 (-0.0016 to +0.0003).

| value cut | bets | A/E pm | ROI % | 95% | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 1.0 | 1916 | 1.195 | +5.7 | -4 to +16 | +0.6 | +12.7 | +20.9 |
| 1.05 | 477 | 1.362 | +27.0 | +5 to +52 | +19.3 | +75.3 | -50.0 |

Final fit (all races): lsp +1.080, wpr_r +0.004, adj_r +0.024, bias_r +0.049, debut +0.249, f_barrier10 +0.051, f_dist_down +0.006, f_dist_up +0.033, f_back14 +0.015, f_4thup +0.045, f_age6 +0.024, f_weak_jockey +0.015, f_sm +0.019, f_bias -0.043, f_wide +0.069, f_gps_ground +0.080, f_heldup +0.003, f_laid +0.021, f_vet +0.104, f_l600_worst +0.010, f_wet_poor_sire -0.001, n_top_jockey -0.021, n_apprentice +0.010, n_every_chance -0.093, n_stay_poor_sire -0.067, lsp_x_field13 +0.024, lsp_x_wet -0.035, lsp_x_qld +0.008, lsp_x_fs_race +0.029, lsp_x_sprint +0.068

Thresholds: sm 0.525, bias 0.297, gps 2.700, l600 -2.391


## Volume: value cut and price cap (live pipeline, walk-forward 2024 to Sep 2026, SP)

|   value cut |   max SP |   bets |   per week |   win % |   median SP |   ROI % | 95%        |   2024 |   2025 |   2026 |
|------------:|---------:|-------:|-----------:|--------:|------------:|--------:|:-----------|-------:|-------:|-------:|
|        1    |       21 |   1916 |       13.5 |    27.6 |         4   |     5.7 | -4 to +16  |    0.6 |   12.7 |   20.9 |
|        1    |       51 |   1930 |       13.6 |    27.5 |         4   |     6.3 | -3 to +16  |    1.6 |   12.7 |   20.9 |
|        0.97 |       21 |   4203 |       29.5 |    27.6 |         3.7 |    -4.1 | -10 to +2  |   -3.3 |   -7   |   -1.4 |
|        0.97 |       51 |   4252 |       29.9 |    27.4 |         3.7 |    -2.3 | -9 to +4   |   -0.1 |   -7.1 |   -1.5 |
|        0.95 |       21 |   6926 |       48.7 |    27.7 |         3.6 |    -7   | -11 to -3  |   -7.2 |   -8.6 |   -3.3 |
|        0.95 |       51 |   7003 |       49.2 |    27.4 |         3.6 |    -6.2 | -11 to -1  |   -5.6 |   -8.8 |   -3.4 |
|        0.92 |       21 |  13744 |       96.6 |    27.9 |         3.6 |    -8.2 | -11 to -5  |   -7.8 |  -10.3 |   -5.7 |
|        0.92 |       51 |  13902 |       97.7 |    27.6 |         3.6 |    -8.2 | -11 to -5  |   -7.5 |  -10.6 |   -5.8 |
|        0.9  |       21 |  20619 |      144.9 |    27.3 |         3.7 |    -9.9 | -12 to -7  |   -9.5 |  -12.2 |   -7   |
|        0.9  |       51 |  20870 |      146.7 |    27   |         3.7 |   -10.1 | -13 to -7  |   -9.7 |  -12.6 |   -7.1 |
|        0.85 |       21 |  46576 |      327.3 |    24   |         4.2 |   -12.4 | -14 to -11 |  -11.9 |  -13.3 |  -11.9 |
|        0.85 |       51 |  47341 |      332.7 |    23.7 |         4.2 |   -12.3 | -14 to -11 |  -11.9 |  -13.4 |  -11.6 |
