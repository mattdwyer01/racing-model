# Current-ability model: walk-forward validation

- Eval set and folds as validate_figure.py (VIC/SA/QLD races, test 2023 to 2026 YTD, trained 2022 to Y-1)
- Figure weights refitted on each fold's training races only

## Log loss by fold (lower is better)

|                                  |       2023 |       2024 |       2025 |      2026 |     pooled |
|:---------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                            | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| figure (baseline)                |     1.9966 |     1.9992 |     1.9971 |    1.9958 |     1.9973 |
| ability                          |     1.9714 |     1.9674 |     1.9654 |    1.9662 |     1.9677 |
| ability - form                   |     2.1182 |     2.1187 |     2.1090 |    2.1024 |     2.1129 |
| ability - class                  |     1.9717 |     1.9677 |     1.9660 |    1.9660 |     1.9680 |
| ability - distance/going/surface |     1.9750 |     1.9713 |     1.9701 |    1.9702 |     1.9718 |
| ability - prep                   |     1.9715 |     1.9677 |     1.9662 |    1.9663 |     1.9681 |
| ability - trials                 |     1.9792 |     1.9764 |     1.9734 |    1.9751 |     1.9761 |
| ability - age/sex/weight         |     1.9748 |     1.9704 |     1.9678 |    1.9698 |     1.9708 |
| SP (calibrated)                  |     1.7907 |     1.7882 |     1.7853 |    1.7756 |     1.7857 |
| SP + figure                      |     1.7894 |     1.7874 |     1.7844 |    1.7747 |     1.7848 |
| SP + ability                     |     1.7896 |     1.7869 |     1.7843 |    1.7743 |     1.7846 |

## Paired differences (pooled; negative = first is better)

| model | vs | diff | se |
|---|---|---|---|
| ability | figure (baseline) | -0.0296 | 0.0013 |
| ability - form | ability | +0.1452 | 0.0027 |
| ability - class | ability | +0.0003 | 0.0002 |
| ability - distance/going/surface | ability | +0.0041 | 0.0004 |
| ability - prep | ability | +0.0003 | 0.0002 |
| ability - trials | ability | +0.0084 | 0.0007 |
| ability - age/sex/weight | ability | +0.0031 | 0.0005 |
| SP + figure | SP (calibrated) | -0.0010 | 0.0003 |
| SP + ability | SP (calibrated) | -0.0011 | 0.0004 |
| SP + ability | SP + figure | -0.0002 | 0.0003 |

## Coefficients (fit on all 2022 on, raw units)

| feature | beta |
|---|---|
| h_none | +7.1630 |
| log_n | -0.2374 |
| log_days | -0.1423 |
| first_up | +0.0254 |
| dm | +0.0565 |
| fig_last | +0.0432 |
| best3 | +0.0371 |
| best10 | +0.0174 |
| mean3 | -0.0195 |
| trend | -0.0335 |
| h_class | -0.0094 |
| dist_ratio | +0.7817 |
| dist_abs | -0.8742 |
| dist_fit | +0.0002 |
| going_fit | +0.0029 |
| surface_fit | -0.0096 |
| fu | +0.0254 |
| su | -0.1078 |
| up3 | -0.0305 |
| fu_apt | +0.0020 |
| su_apt | +0.0004 |
| trial_since | -0.0077 |
| trial_pos | -0.9320 |
| trial_marg | -0.0070 |
| trial_pos_debut | -0.7907 |
| trial_marg_debut | -0.0459 |
| age2 | -0.4517 |
| age3 | -0.0867 |
| age7 | -0.2311 |
| female | -0.1654 |
| wt_rel_today | -0.0258 |

## Figure weights by fold

|         |   2023 |   2024 |   2025 |   2026 |
|:--------|-------:|-------:|-------:|-------:|
| wpr     |  1.000 |  1.000 |  1.000 |  1.000 |
| s_early | -0.126 | -0.084 | -0.046 | -0.026 |
| s_l600  |  0.236 |  0.218 |  0.241 |  0.269 |
| wt_rel  |  0.133 |  0.047 |  0.049 |  0.026 |
| settle  | -6.538 | -5.673 | -5.597 | -5.565 |
| shape   |  0.081 | -0.044 | -0.054 | -0.065 |
| pace    |  0.599 |  0.588 |  0.592 |  0.651 |
