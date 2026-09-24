# Market-offset models: walk-forward on SP

- Eval set and folds as validate_figure.py (VIC/SA/QLD, test 2023 to 2026 YTD, trained 2022 to Y-1)
- gbm offset: LightGBM, per-race softmax objective, score = calibrated SP + trees; features include the race-day projection (model/projection.py); params tuned per fold on inner validation

## Log loss by fold

|                                       |       2023 |       2024 |       2025 |      2026 |     pooled |
|:--------------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                                 | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP (calibrated)                       |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| logit: SP + ability                   |     1.7896 |     1.7869 |     1.7843 |    1.7743 |     1.7846 |
| logit: SP + ability + jt              |     1.7899 |     1.7867 |     1.7843 |    1.7743 |     1.7846 |
| logit: SP + ability + jt + projection |     1.7900 |     1.7868 |     1.7846 |    1.7743 |     1.7848 |
| gbm offset, no projection             |     1.7903 |     1.7876 |     1.7842 |    1.7741 |     1.7849 |
| gbm offset                            |     1.7907 |     1.7877 |     1.7845 |    1.7732 |     1.7850 |

## vs SP (calibrated), pooled (negative = better)

| model | diff | se |
|---|---|---|
| SP (calibrated) | +0.0000 | 0.0000 |
| logit: SP + ability | -0.0011 | 0.0004 |
| logit: SP + ability + jt | -0.0012 | 0.0004 |
| logit: SP + ability + jt + projection | -0.0010 | 0.0005 |
| gbm offset, no projection | -0.0008 | 0.0002 |
| gbm offset | -0.0008 | 0.0002 |

## GBM tuning (chosen on the inner validation window of each fold)

- 2023: chose {'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}, rounds 23; inner-val loss by grid point {"{'num_leaves': 15, 'min_data_in_leaf': 1000, 'learning_rate': 0.03}": np.float64(1.72718), "{'num_leaves': 31, 'min_data_in_leaf': 300, 'learning_rate': 0.03}": np.float64(1.72827), "{'num_leaves': 63, 'min_data_in_leaf': 300, 'learning_rate': 0.02}": np.float64(1.72801), "{'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}": np.float64(1.72706)}
- 2024: chose {'num_leaves': 31, 'min_data_in_leaf': 300, 'learning_rate': 0.03}, rounds 20; inner-val loss by grid point {"{'num_leaves': 15, 'min_data_in_leaf': 1000, 'learning_rate': 0.03}": np.float64(1.78386), "{'num_leaves': 31, 'min_data_in_leaf': 300, 'learning_rate': 0.03}": np.float64(1.78354), "{'num_leaves': 63, 'min_data_in_leaf': 300, 'learning_rate': 0.02}": np.float64(1.7838), "{'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}": np.float64(1.78428)}
- 2025: chose {'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}, rounds 36; inner-val loss by grid point {"{'num_leaves': 15, 'min_data_in_leaf': 1000, 'learning_rate': 0.03}": np.float64(1.79537), "{'num_leaves': 31, 'min_data_in_leaf': 300, 'learning_rate': 0.03}": np.float64(1.7956), "{'num_leaves': 63, 'min_data_in_leaf': 300, 'learning_rate': 0.02}": np.float64(1.79559), "{'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}": np.float64(1.79504)}
- 2026: chose {'num_leaves': 15, 'min_data_in_leaf': 1000, 'learning_rate': 0.03}, rounds 127; inner-val loss by grid point {"{'num_leaves': 15, 'min_data_in_leaf': 1000, 'learning_rate': 0.03}": np.float64(1.79967), "{'num_leaves': 31, 'min_data_in_leaf': 300, 'learning_rate': 0.03}": np.float64(1.80019), "{'num_leaves': 63, 'min_data_in_leaf': 300, 'learning_rate': 0.02}": np.float64(1.79993), "{'num_leaves': 15, 'min_data_in_leaf': 300, 'learning_rate': 0.05, 'lambda_l2': 30.0}": np.float64(1.79996)}

## GBM feature importance (share of gain, mean over folds, top 20)

|                  |   gain share |
|:-----------------|-------------:|
| log_p_sp         |        0.051 |
| wt_rel_today     |        0.044 |
| proj_gl          |        0.031 |
| proj_pace_rel    |        0.029 |
| best10           |        0.028 |
| proj_settle_rank |        0.027 |
| h_class_gap      |        0.027 |
| j_ae_gap         |        0.025 |
| j_sr_rel         |        0.024 |
| proj_settle      |        0.024 |
| t_ae_rel         |        0.023 |
| c_ae             |        0.023 |
| t_sr_rel         |        0.022 |
| proj_pace_gap    |        0.021 |
| best3_gap        |        0.021 |
| best3_rel        |        0.021 |
| dm_rel           |        0.020 |
| j_sr_gap         |        0.020 |
| j90_ae           |        0.019 |
| log_n            |        0.018 |
