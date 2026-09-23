# Per-run figure: walk-forward validation

- Eval set: VIC/SA/QLD races 2022 on, SP for every runner, one winner (46,860 races, 446,324 runners)
- Folds: test year Y (2023 to 2026 YTD), trained on 2022 to Y-1
- Metric: mean -log p(winner) per race (lower is better)

## Log loss by fold

| fold   |      races |   SP (raw) |   SP (calibrated) |    wpr |   +weight |   +sectionals |   +pace (figure) |   SP + figure |   SP + wpr |
|:-------|-----------:|-----------:|------------------:|-------:|----------:|--------------:|-----------------:|--------------:|-----------:|
| 2023   | 10245.0000 |     1.7934 |            1.7907 | 2.0010 |    2.0012 |        2.0011 |           1.9966 |        1.7894 |     1.7902 |
| 2024   | 10374.0000 |     1.7933 |            1.7882 | 2.0041 |    2.0040 |        2.0027 |           1.9992 |        1.7874 |     1.7879 |
| 2025   | 10218.0000 |     1.7891 |            1.7853 | 2.0014 |    2.0015 |        2.0003 |           1.9971 |        1.7844 |     1.7844 |
| 2026   |  6984.0000 |     1.7811 |            1.7756 | 1.9995 |    1.9996 |        1.9976 |           1.9958 |        1.7747 |     1.7749 |
| pooled | 37821.0000 |     1.7899 |            1.7857 | 2.0017 |    2.0018 |        2.0007 |           1.9973 |        1.7848 |     1.7852 |

## Paired differences (pooled over test races, negative = first is better)

| model | vs | diff | se |
|---|---|---|---|
| +weight | wpr | +0.0001 | 0.0001 |
| +sectionals | +weight | -0.0011 | 0.0002 |
| +pace (figure) | +sectionals | -0.0034 | 0.0005 |
| +pace (figure) | wpr | -0.0044 | 0.0006 |
| SP + wpr | SP (calibrated) | -0.0006 | 0.0002 |
| SP + figure | SP + wpr | -0.0004 | 0.0003 |
| SP + figure | SP (calibrated) | -0.0010 | 0.0003 |

## Figure weights (fit on all 2022 on)

fig = wpr + sum(c_j * x_j), per unit of each component:

| component | c_j |
|---|---|
| wpr | +1.000 |
| s_early | +0.017 |
| s_l600 | +0.293 |
| wt_rel | +0.006 |
| settle | -5.387 |
| shape | -0.109 |
| pace | +0.673 |

Full logit coefficients (raw units):

| feature | beta |
|---|---|
| h_none | +6.1843 |
| log_n | -0.2183 |
| log_days | -0.1637 |
| first_up | +0.0354 |
| h_wpr | +0.1128 |
| wt_rel_today | +0.0012 |
| h_wt_rel | +0.0007 |
| h_s_early | +0.0019 |
| h_s_l600 | +0.0330 |
| h_s_early_miss | -0.2129 |
| h_settle | -0.6075 |
| h_shape | -0.0123 |
| h_pace | +0.0759 |
| h_settle_miss | +0.2958 |
