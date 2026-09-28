# Production logit in WPR points

- Model: conditional logit on 89 inputs (figure, ability, jockey/trainer, race-day projection, run comments); saved to data/models/logit_2026-01-01.pkl
- Training states: VIC, SA, QLD + NSW, WA, TAS, NT, ACT
- Trained on races before 2026-01-01. One WPR point of ability = 0.1687 utility
- Blend with the market: a = 0.089 (model), b = 1.065 (market); calibrated market c = 1.129; fitted on 04 Jan 2025 to 31 Dec 2025
- 'WPR points per unit': the bonus / penalty for +1 on that input, holding the others; a horse's contribution is that times (its value minus the field average)
- 'fit to YYYY' columns: the same weights fitted on races before that year (stability)

|                   |   beta |   WPR points per unit | group                   |   fit to 2023 |   fit to 2024 |   fit to 2025 |   fit to 2026 |
|:------------------|-------:|----------------------:|:------------------------|--------------:|--------------:|--------------:|--------------:|
| log_n             | -0.207 |                -1.225 | ability                 |        -0.889 |        -1.129 |        -1.205 |        -1.225 |
| mean3             | -0.018 |                -0.106 | ability                 |        -0.134 |        -0.126 |        -0.126 |        -0.106 |
| h_class           | -0.013 |                -0.078 | ability                 |        -0.044 |        -0.078 |        -0.075 |        -0.078 |
| fig_last          |  0.010 |                 0.062 | ability                 |         0.069 |         0.068 |         0.067 |         0.062 |
| h_wpr             |  0.012 |                 0.072 | ability                 |         0.076 |         0.078 |         0.077 |         0.072 |
| dm                |  0.013 |                 0.076 | ability                 |         0.081 |         0.082 |         0.082 |         0.076 |
| best10            |  0.016 |                 0.092 | ability                 |         0.051 |         0.076 |         0.086 |         0.092 |
| r_sigma           |  0.021 |                 0.125 | ability                 |         0.292 |         0.145 |         0.139 |         0.125 |
| best3             |  0.024 |                 0.142 | ability                 |         0.115 |         0.137 |         0.139 |         0.142 |
| r_mu              |  0.111 |                 0.660 | ability                 |         0.742 |         0.685 |         0.675 |         0.660 |
| h_none            |  1.365 |                 8.094 | ability                 |         6.533 |         7.632 |         7.899 |         8.094 |
| age2              | -1.189 |                -7.047 | age / sex / weight      |        -6.751 |        -6.503 |        -6.880 |        -7.047 |
| age3              | -0.377 |                -2.235 | age / sex / weight      |        -2.290 |        -2.197 |        -2.162 |        -2.235 |
| female            | -0.329 |                -1.951 | age / sex / weight      |        -1.937 |        -1.906 |        -1.936 |        -1.951 |
| age7              | -0.133 |                -0.788 | age / sex / weight      |        -1.073 |        -0.966 |        -0.907 |        -0.788 |
| wt_rel_today      | -0.083 |                -0.494 | age / sex / weight      |        -0.496 |        -0.526 |        -0.524 |        -0.494 |
| cm_last_has       | -1.383 |                -8.200 | comments                |        -6.540 |        -7.651 |        -8.024 |        -8.200 |
| cm_last_vwide     | -0.057 |                -0.335 | comments                |        -0.274 |        -0.314 |        -0.336 |        -0.335 |
| cm_last_slow      | -0.048 |                -0.287 | comments                |        -0.178 |        -0.319 |        -0.381 |        -0.287 |
| cm_last_health    | -0.036 |                -0.214 | comments                |        -0.203 |        -0.192 |        -0.147 |        -0.214 |
| cm_last_wide      | -0.036 |                -0.211 | comments                |        -0.617 |        -0.428 |        -0.241 |        -0.211 |
| cm_last_over      | -0.030 |                -0.178 | comments                |         0.036 |        -0.221 |        -0.179 |        -0.178 |
| cm_last_checked   | -0.022 |                -0.130 | comments                |        -0.047 |         0.089 |        -0.042 |        -0.130 |
| cm_last_vblocked  |  0.009 |                 0.055 | comments                |         0.518 |         0.098 |        -0.088 |         0.055 |
| cm_last_tag       |  0.017 |                 0.098 | comments                |         0.061 |         0.116 |         0.117 |         0.098 |
| cm_dm_vblocked    |  0.054 |                 0.321 | comments                |         0.310 |         0.597 |         0.556 |         0.321 |
| cm_dm_tag         |  0.071 |                 0.424 | comments                |         0.337 |         0.414 |         0.404 |         0.424 |
| cm_dm_checked     |  0.075 |                 0.444 | comments                |        -0.147 |         0.006 |         0.332 |         0.444 |
| cm_dm_slow        |  0.109 |                 0.647 | comments                |         0.780 |         0.685 |         0.767 |         0.647 |
| cm_dm_over        |  0.132 |                 0.783 | comments                |         0.710 |         0.926 |         0.870 |         0.783 |
| cm_dm_health      |  0.138 |                 0.818 | comments                |         1.633 |         1.038 |         0.770 |         0.818 |
| cm_dm_wide        |  0.180 |                 1.068 | comments                |         1.575 |         1.332 |         1.127 |         1.068 |
| cm_dm_vwide       |  0.205 |                 1.215 | comments                |         0.746 |         1.028 |         1.198 |         1.215 |
| dist_abs          | -0.062 |                -0.366 | distance / going        |         0.837 |        -0.141 |        -0.361 |        -0.366 |
| surface_fit       | -0.007 |                -0.042 | distance / going        |        -0.077 |        -0.053 |        -0.044 |        -0.042 |
| dist_fit          |  0.003 |                 0.021 | distance / going        |         0.007 |         0.024 |         0.022 |         0.021 |
| going_fit         |  0.004 |                 0.024 | distance / going        |         0.041 |         0.028 |         0.018 |         0.024 |
| dist_ratio        |  0.133 |                 0.788 | distance / going        |         0.714 |        -0.109 |        -0.030 |         0.788 |
| h_wt_rel          | -0.081 |                -0.482 | form shape              |        -0.438 |        -0.439 |        -0.460 |        -0.482 |
| h_shape           | -0.015 |                -0.087 | form shape              |        -0.047 |        -0.117 |        -0.112 |        -0.087 |
| trend             | -0.003 |                -0.015 | form shape              |        -0.012 |        -0.011 |        -0.013 |        -0.015 |
| h_s_early_miss    | -0.000 |                -0.002 | form shape              |        -0.157 |        -0.128 |         0.157 |        -0.002 |
| h_s_early         |  0.001 |                 0.004 | form shape              |        -0.005 |         0.036 |         0.024 |         0.004 |
| h_pace            |  0.028 |                 0.167 | form shape              |         0.196 |         0.149 |         0.152 |         0.167 |
| h_s_l600          |  0.043 |                 0.255 | form shape              |         0.270 |         0.266 |         0.275 |         0.255 |
| h_settle_miss     |  0.070 |                 0.413 | form shape              |        -0.241 |         0.361 |         0.344 |         0.413 |
| h_settle          |  0.250 |                 1.481 | form shape              |         0.416 |         2.225 |         1.829 |         1.481 |
| h_rail            | -0.030 |                -0.178 | ground loss (past runs) |        -0.278 |        -0.342 |        -0.363 |        -0.178 |
| h_gl_miss         | -0.011 |                -0.066 | ground loss (past runs) |         0.586 |        -0.026 |         0.062 |        -0.066 |
| h_gl              |  0.030 |                 0.177 | ground loss (past runs) |        -0.009 |         0.166 |         0.227 |         0.177 |
| j_ae              | -0.277 |                -1.641 | jockey / trainer        |        -1.128 |        -1.575 |        -1.730 |        -1.641 |
| h_ae              | -0.121 |                -0.715 | jockey / trainer        |        -0.222 |        -0.604 |        -0.737 |        -0.715 |
| t_ae              | -0.072 |                -0.428 | jockey / trainer        |        -0.635 |        -0.424 |        -0.318 |        -0.428 |
| j_change          |  0.018 |                 0.109 | jockey / trainer        |         0.213 |         0.223 |         0.154 |         0.109 |
| c_ae              |  0.058 |                 0.344 | jockey / trainer        |         0.362 |         0.325 |         0.282 |         0.344 |
| tfu_ae            |  0.073 |                 0.432 | jockey / trainer        |        -0.112 |         0.200 |         0.350 |         0.432 |
| j90_ae            |  0.077 |                 0.459 | jockey / trainer        |         0.152 |         0.296 |         0.308 |         0.459 |
| j_upgrade         |  0.266 |                 1.578 | jockey / trainer        |         2.493 |         2.434 |         2.538 |         1.578 |
| t_sr              |  0.964 |                 5.715 | jockey / trainer        |         6.229 |         5.107 |         4.659 |         5.715 |
| j_sr              |  2.565 |                15.205 | jockey / trainer        |        13.609 |        13.675 |        14.737 |        15.205 |
| trial_pos         | -0.468 |                -2.773 | prep                    |        -2.689 |        -3.069 |        -3.070 |        -2.773 |
| trial_since       | -0.089 |                -0.525 | prep                    |        -0.244 |        -0.540 |        -0.614 |        -0.525 |
| trial_pos_debut   | -0.068 |                -0.401 | prep                    |         0.939 |         0.390 |         0.321 |        -0.401 |
| log_days          | -0.040 |                -0.238 | prep                    |        -0.442 |        -0.260 |        -0.249 |        -0.238 |
| trial_marg_debut  | -0.019 |                -0.112 | prep                    |        -0.167 |        -0.100 |        -0.089 |        -0.112 |
| su                | -0.016 |                -0.097 | prep                    |         0.079 |        -0.078 |        -0.050 |        -0.097 |
| fu_apt            | -0.001 |                -0.008 | prep                    |        -0.017 |        -0.022 |         0.004 |        -0.008 |
| up3               | -0.001 |                -0.004 | prep                    |        -0.028 |        -0.029 |        -0.067 |        -0.004 |
| su_apt            |  0.003 |                 0.017 | prep                    |         0.011 |         0.023 |         0.030 |         0.017 |
| trial_marg        |  0.008 |                 0.050 | prep                    |         0.187 |         0.082 |         0.057 |         0.050 |
| first_up          |  0.034 |                 0.200 | prep                    |         0.371 |         0.248 |         0.204 |         0.200 |
| fu                |  0.034 |                 0.200 | prep                    |         0.371 |         0.248 |         0.204 |         0.200 |
| proj_settle       | -0.608 |                -3.603 | race-day projection     |        -3.591 |        -4.265 |        -4.010 |        -3.603 |
| tdx_settle        | -0.527 |                -3.123 | race-day projection     |        -3.202 |        -1.265 |        -2.488 |        -3.123 |
| early_rank2       | -0.023 |                -0.135 | race-day projection     |        -0.279 |        -0.336 |        -0.387 |        -0.135 |
| proj_gl           | -0.002 |                -0.014 | race-day projection     |        -0.021 |         0.079 |         0.029 |        -0.014 |
| nb_diff_out       | -0.001 |                -0.005 | race-day projection     |        -0.006 |        -0.012 |        -0.003 |        -0.005 |
| proj_shape        |  0.000 |                 0.000 | race-day projection     |        -0.000 |         0.000 |        -0.000 |         0.000 |
| nb_diff_in        |  0.002 |                 0.009 | race-day projection     |         0.016 |         0.006 |         0.008 |         0.009 |
| proj_pace         |  0.006 |                 0.034 | race-day projection     |         0.203 |         0.093 |         0.015 |         0.034 |
| tdx_perf          |  0.015 |                 0.090 | race-day projection     |         0.171 |         0.132 |         0.095 |         0.090 |
| wide_x_slow       |  0.020 |                 0.116 | race-day projection     |         0.383 |         0.219 |         0.288 |         0.116 |
| lv_x              |  0.079 |                 0.468 | race-day projection     |         0.352 |         0.388 |         0.450 |         0.468 |
| barrier_pct       |  0.127 |                 0.753 | race-day projection     |         0.200 |         0.494 |         0.606 |         0.753 |
| proj_settle_rank  |  0.158 |                 0.937 | race-day projection     |         0.971 |         0.958 |         1.071 |         0.937 |
| proj_adj          |  0.181 |                 1.070 | race-day projection     |         1.116 |         1.252 |         1.167 |         1.070 |
| tbx_settle_long   | -0.059 |                -0.348 | track bias              |        -0.045 |        -0.267 |        -0.272 |        -0.348 |
| bias_adj          | -0.008 |                -0.047 | track bias              |        -0.020 |        -0.009 |        -0.026 |        -0.047 |
| tbx_bar_long      |  0.018 |                 0.105 | track bias              |        -0.009 |         0.115 |         0.096 |         0.105 |
| tbx_settle_recent |  0.038 |                 0.222 | track bias              |         0.374 |         0.402 |         0.342 |         0.222 |
| tbx_bar_recent    |  0.063 |                 0.374 | track bias              |         0.406 |         0.386 |         0.340 |         0.374 |
