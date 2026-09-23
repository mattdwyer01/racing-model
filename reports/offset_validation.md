# Market-offset models: walk-forward on SP

- Eval set and folds as validate_figure.py (VIC/SA/QLD, test 2023 to 2026 YTD, trained 2022 to Y-1)
- gbm offset: LightGBM, per-race softmax objective, score = calibrated SP + trees

## Log loss by fold

|                          |       2023 |       2024 |       2025 |      2026 |     pooled |
|:-------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                    | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP (calibrated)          |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| logit: SP + ability      |     1.7896 |     1.7869 |     1.7843 |    1.7743 |     1.7846 |
| logit: SP + ability + jt |     1.7899 |     1.7867 |     1.7843 |    1.7743 |     1.7846 |
| gbm offset               |     1.7904 |     1.7874 |     1.7838 |    1.7738 |     1.7847 |

## vs SP (calibrated), pooled (negative = better)

| model | diff | se |
|---|---|---|
| SP (calibrated) | +0.0000 | 0.0000 |
| logit: SP + ability | -0.0011 | 0.0004 |
| logit: SP + ability + jt | -0.0012 | 0.0004 |
| gbm offset | -0.0010 | 0.0002 |

GBM rounds by fold: 2023: 20, 2024: 33, 2025: 143, 2026: 165

## GBM feature importance (share of gain, mean over folds, top 20)

|              |   gain share |
|:-------------|-------------:|
| wt_rel_today |        0.054 |
| log_p_sp     |        0.052 |
| best10       |        0.040 |
| j_upgrade    |        0.034 |
| log_days     |        0.030 |
| j_ae_gap     |        0.029 |
| j_ae         |        0.029 |
| c_ae         |        0.026 |
| j_ae_rel     |        0.026 |
| j_sr_rel     |        0.024 |
| fig_last     |        0.024 |
| h_ae         |        0.024 |
| h_ae_gap     |        0.024 |
| h_class_rel  |        0.023 |
| t_sr         |        0.022 |
| t_sr_gap     |        0.022 |
| t_sr_rel     |        0.022 |
| dist_abs     |        0.021 |
| best3_gap    |        0.021 |
| j_sr_gap     |        0.021 |
