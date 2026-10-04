# WPR projection v2: the WPR each horse runs (walk-forward 2023 to 2026, VIC/SA/QLD)

- 38,310 races, 364,722 runs with a WPR (345,926 with prior form).

## WPR forecast error (runners with prior form)

| forecast | MAE | RMSE |
|---|---|---|
| WPR model | 6.59 | 9.79 |
| prior average WPR (h_wpr) | 6.92 | 10.37 |

- Spread: actual within +/- 1 predicted sd for 60% of runs (68% if calibrated); median sd 6.1 WPR.

## Picking winners

| model                    |   top pick win % |   log loss |
|:-------------------------|-----------------:|-----------:|
| Racing Model (win logit) |            29.32 |     1.9227 |
| WPR model, simulated     |            28.02 |     1.9883 |
| WPR model, fitted scale  |            28.16 |     1.9413 |

|   fold |   races |   RM top % |   WPR top % |   RM ll |   WPR sim ll |
|-------:|--------:|-----------:|------------:|--------:|-------------:|
|   2023 |   10245 |     29.468 |      27.233 |   1.924 |        2.019 |
|   2024 |   10374 |     29.564 |      28.061 |   1.92  |        1.999 |
|   2025 |   10218 |     29.546 |      29.164 |   1.927 |        1.967 |
|   2026 |    7473 |     28.449 |      28.181 |   1.919 |        1.96  |

## Top inputs (gain, mean over folds)

|             |     0 |
|:------------|------:|
| mu_abs      | 0.533 |
| h_wpr       | 0.11  |
| dm          | 0.071 |
| f_mean_hwpr | 0.033 |
| mean3       | 0.012 |
| fig_last    | 0.01  |
| dist        | 0.01  |
| cm_last_tag | 0.01  |
| best3       | 0.009 |
| f_max_hwpr  | 0.009 |
| t_sr        | 0.008 |
| h_s_l600    | 0.008 |
| r_mu        | 0.007 |
| f_mean_mu   | 0.006 |
| log_days    | 0.006 |


## Against TopRate's projection (pre-race values, 873 VIC/SA/QLD races 22 Aug to Sep 2026, 7,980 runs with form)

| forecast | MAE | RMSE | bias | top pick win % |
|---|---|---|---|---|
| WPR model | 6.00 | 8.56 | -0.27 | 27.5 |
| TopRate projection (raw, 08:00 file) | 6.50 | 9.43 | +1.91 | 27.5 |
| TopRate projection (dashboard adjusted) | 6.56 | 9.50 | +1.92 | 27.0 |
| Racing Model (win logit) | | | | 28.4 |
