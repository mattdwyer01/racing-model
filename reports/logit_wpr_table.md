# Production logit in WPR points

- Model: conditional logit on 88 inputs (figure, ability, jockey/trainer, race-day projection, run comments); saved to data/models/logit_2026-01-01.pkl
- Trained on races before 2026-01-01. One WPR point of ability = 0.1293 utility
- Blend with the market: a = 0.124 (model), b = 1.032 (market); calibrated market c = 1.119; fitted on 09 Jan 2025 to 31 Dec 2025
- 'WPR points per unit': the bonus / penalty for +1 on that input, holding the others; a horse's contribution is that times (its value minus the field average)
- 'fit to YYYY' columns: the same weights fitted on races before that year (stability)

|                   |   beta |   WPR points per unit | group                   |   fit to 2023 |   fit to 2024 |   fit to 2025 |   fit to 2026 |
|:------------------|-------:|----------------------:|:------------------------|--------------:|--------------:|--------------:|--------------:|
| log_n             | -0.150 |                -1.160 | ability                 |        -0.920 |        -0.972 |        -1.112 |        -1.160 |
| h_class           | -0.021 |                -0.164 | ability                 |        -0.116 |        -0.156 |        -0.152 |        -0.164 |
| mean3             | -0.016 |                -0.128 | ability                 |        -0.126 |        -0.148 |        -0.143 |        -0.128 |
| best10            |  0.016 |                 0.124 | ability                 |         0.068 |         0.097 |         0.120 |         0.124 |
| fig_last          |  0.027 |                 0.211 | ability                 |         0.239 |         0.231 |         0.219 |         0.211 |
| best3             |  0.033 |                 0.254 | ability                 |         0.236 |         0.245 |         0.252 |         0.254 |
| dm                |  0.035 |                 0.269 | ability                 |         0.294 |         0.289 |         0.276 |         0.269 |
| h_wpr             |  0.035 |                 0.270 | ability                 |         0.289 |         0.287 |         0.275 |         0.270 |
| h_none            |  3.307 |                25.581 | ability                 |        26.155 |        26.080 |        25.960 |        25.581 |
| age2              | -0.670 |                -5.184 | age / sex / weight      |        -8.231 |        -6.767 |        -5.431 |        -5.184 |
| female            | -0.226 |                -1.744 | age / sex / weight      |        -1.810 |        -1.945 |        -1.774 |        -1.744 |
| age7              | -0.171 |                -1.326 | age / sex / weight      |        -1.701 |        -1.531 |        -1.486 |        -1.326 |
| age3              | -0.153 |                -1.186 | age / sex / weight      |        -0.657 |        -0.926 |        -1.034 |        -1.186 |
| wt_rel_today      | -0.041 |                -0.314 | age / sex / weight      |        -0.388 |        -0.386 |        -0.363 |        -0.314 |
| cm_last_has       | -3.309 |               -25.597 | comments                |       -26.164 |       -26.094 |       -25.982 |       -25.597 |
| cm_last_health    | -0.070 |                -0.540 | comments                |        -0.799 |        -0.726 |        -0.611 |        -0.540 |
| cm_last_slow      | -0.049 |                -0.377 | comments                |        -0.738 |        -0.576 |        -0.639 |        -0.377 |
| cm_last_checked   | -0.015 |                -0.115 | comments                |        -0.115 |         0.052 |        -0.047 |        -0.115 |
| cm_last_vwide     | -0.009 |                -0.071 | comments                |        -0.140 |        -0.182 |        -0.221 |        -0.071 |
| cm_last_wide      |  0.001 |                 0.011 | comments                |        -0.320 |        -0.205 |         0.113 |         0.011 |
| cm_last_vblocked  |  0.026 |                 0.202 | comments                |         1.117 |         0.415 |         0.135 |         0.202 |
| cm_last_over      |  0.043 |                 0.336 | comments                |         0.665 |         0.232 |         0.250 |         0.336 |
| cm_last_tag       |  0.047 |                 0.365 | comments                |         0.329 |         0.383 |         0.403 |         0.365 |
| cm_dm_over        |  0.049 |                 0.378 | comments                |        -0.215 |         0.548 |         0.582 |         0.378 |
| cm_dm_tag         |  0.097 |                 0.750 | comments                |         0.984 |         0.914 |         0.802 |         0.750 |
| cm_dm_slow        |  0.107 |                 0.828 | comments                |         2.047 |         1.088 |         1.151 |         0.828 |
| cm_dm_checked     |  0.145 |                 1.119 | comments                |         0.796 |         0.982 |         1.108 |         1.119 |
| cm_dm_vblocked    |  0.167 |                 1.289 | comments                |         0.816 |         0.834 |         1.287 |         1.289 |
| cm_dm_vwide       |  0.177 |                 1.368 | comments                |         0.880 |         1.383 |         1.529 |         1.368 |
| cm_dm_wide        |  0.182 |                 1.407 | comments                |         2.106 |         1.735 |         1.206 |         1.407 |
| cm_dm_health      |  0.201 |                 1.553 | comments                |         3.434 |         1.777 |         1.564 |         1.553 |
| dist_abs          | -0.699 |                -5.408 | distance / going        |        -5.215 |        -5.034 |        -5.533 |        -5.408 |
| surface_fit       | -0.008 |                -0.059 | distance / going        |        -0.132 |        -0.094 |        -0.056 |        -0.059 |
| dist_fit          |  0.003 |                 0.021 | distance / going        |        -0.004 |         0.019 |         0.013 |         0.021 |
| going_fit         |  0.004 |                 0.028 | distance / going        |         0.064 |         0.054 |         0.021 |         0.028 |
| dist_ratio        |  0.421 |                 3.256 | distance / going        |         2.539 |         1.873 |         2.226 |         3.256 |
| h_s_early_miss    | -0.130 |                -1.005 | form shape              |        -2.070 |        -1.402 |        -0.310 |        -1.005 |
| h_wt_rel          | -0.047 |                -0.360 | form shape              |        -0.285 |        -0.352 |        -0.343 |        -0.360 |
| trend             | -0.016 |                -0.125 | form shape              |        -0.144 |        -0.138 |        -0.124 |        -0.125 |
| h_s_early         | -0.016 |                -0.120 | form shape              |        -0.092 |        -0.070 |        -0.096 |        -0.120 |
| h_shape           | -0.011 |                -0.084 | form shape              |        -0.040 |        -0.110 |        -0.101 |        -0.084 |
| h_s_l600          |  0.001 |                 0.005 | form shape              |         0.093 |         0.054 |         0.051 |         0.005 |
| h_pace            |  0.007 |                 0.051 | form shape              |         0.011 |         0.049 |         0.048 |         0.051 |
| h_settle_miss     |  0.155 |                 1.201 | form shape              |         1.842 |         1.771 |         1.090 |         1.201 |
| h_settle          |  0.603 |                 4.664 | form shape              |         3.028 |         5.373 |         4.799 |         4.664 |
| h_gl_miss         | -0.194 |                -1.501 | ground loss (past runs) |        -0.743 |        -1.429 |        -1.421 |        -1.501 |
| h_rail            | -0.029 |                -0.228 | ground loss (past runs) |        -0.400 |        -0.500 |        -0.474 |        -0.228 |
| h_gl              |  0.034 |                 0.261 | ground loss (past runs) |         0.088 |         0.288 |         0.367 |         0.261 |
| t_ae              | -0.441 |                -3.411 | jockey / trainer        |        -5.108 |        -3.842 |        -3.649 |        -3.411 |
| j_ae              | -0.354 |                -2.735 | jockey / trainer        |        -2.655 |        -2.835 |        -2.806 |        -2.735 |
| h_ae              | -0.173 |                -1.335 | jockey / trainer        |        -0.925 |        -1.120 |        -1.335 |        -1.335 |
| j_change          | -0.048 |                -0.374 | jockey / trainer        |        -0.395 |        -0.365 |        -0.377 |        -0.374 |
| j90_ae            |  0.032 |                 0.247 | jockey / trainer        |         0.170 |         0.306 |         0.217 |         0.247 |
| c_ae              |  0.115 |                 0.891 | jockey / trainer        |         1.094 |         0.776 |         0.780 |         0.891 |
| tfu_ae            |  0.194 |                 1.497 | jockey / trainer        |         0.469 |         0.502 |         0.996 |         1.497 |
| j_upgrade         |  0.358 |                 2.768 | jockey / trainer        |         4.102 |         2.690 |         3.746 |         2.768 |
| t_sr              |  4.516 |                34.931 | jockey / trainer        |        46.578 |        37.417 |        36.485 |        34.931 |
| j_sr              |  4.738 |                36.650 | jockey / trainer        |        44.429 |        38.190 |        37.112 |        36.650 |
| trial_pos         | -0.814 |                -6.298 | prep                    |        -8.357 |        -7.792 |        -7.249 |        -6.298 |
| trial_pos_debut   | -0.350 |                -2.711 | prep                    |        -4.898 |        -2.867 |        -2.043 |        -2.711 |
| log_days          | -0.160 |                -1.235 | prep                    |        -1.781 |        -1.340 |        -1.300 |        -1.235 |
| su                | -0.141 |                -1.088 | prep                    |        -1.149 |        -1.045 |        -0.979 |        -1.088 |
| trial_marg_debut  | -0.067 |                -0.519 | prep                    |        -0.498 |        -0.487 |        -0.558 |        -0.519 |
| up3               | -0.057 |                -0.438 | prep                    |        -0.514 |        -0.574 |        -0.467 |        -0.438 |
| trial_since       | -0.023 |                -0.180 | prep                    |         0.100 |        -0.202 |        -0.261 |        -0.180 |
| trial_marg        | -0.008 |                -0.062 | prep                    |         0.153 |         0.103 |         0.015 |        -0.062 |
| su_apt            |  0.000 |                 0.004 | prep                    |        -0.012 |         0.047 |         0.039 |         0.004 |
| fu_apt            |  0.002 |                 0.018 | prep                    |         0.118 |         0.003 |         0.051 |         0.018 |
| first_up          |  0.057 |                 0.442 | prep                    |         0.706 |         0.430 |         0.478 |         0.442 |
| fu                |  0.057 |                 0.442 | prep                    |         0.706 |         0.430 |         0.478 |         0.442 |
| tdx_settle        | -0.760 |                -5.876 | race-day projection     |       -14.135 |        -4.705 |        -6.280 |        -5.876 |
| proj_settle       | -0.465 |                -3.594 | race-day projection     |        -2.968 |        -4.026 |        -4.081 |        -3.594 |
| early_rank2       | -0.092 |                -0.714 | race-day projection     |        -1.629 |        -0.950 |        -1.096 |        -0.714 |
| proj_pace         | -0.068 |                -0.525 | race-day projection     |        -0.417 |        -0.539 |        -0.637 |        -0.525 |
| proj_gl           | -0.010 |                -0.074 | race-day projection     |        -0.153 |         0.021 |        -0.013 |        -0.074 |
| nb_diff_out       | -0.000 |                -0.001 | race-day projection     |         0.010 |         0.005 |         0.003 |        -0.001 |
| nb_diff_in        | -0.000 |                -0.001 | race-day projection     |        -0.041 |        -0.025 |        -0.006 |        -0.001 |
| proj_shape        | -0.000 |                -0.000 | race-day projection     |         0.000 |         0.000 |        -0.000 |        -0.000 |
| barrier_pct       |  0.009 |                 0.067 | race-day projection     |        -1.004 |        -0.291 |        -0.264 |         0.067 |
| wide_x_slow       |  0.034 |                 0.259 | race-day projection     |         0.780 |         0.184 |         0.480 |         0.259 |
| tdx_perf          |  0.043 |                 0.335 | race-day projection     |         0.700 |         0.494 |         0.379 |         0.335 |
| proj_settle_rank  |  0.132 |                 1.019 | race-day projection     |         1.281 |         0.786 |         1.337 |         1.019 |
| proj_adj          |  0.237 |                 1.834 | race-day projection     |         2.189 |         2.126 |         2.058 |         1.834 |
| tbx_settle_long   |  0.031 |                 0.240 | track bias              |         0.648 |         0.537 |         0.387 |         0.240 |
| bias_adj          |  0.044 |                 0.340 | track bias              |         0.475 |         0.442 |         0.391 |         0.340 |
| tbx_settle_recent |  0.054 |                 0.417 | track bias              |         0.598 |         0.349 |         0.515 |         0.417 |
| tbx_bar_long      |  0.057 |                 0.437 | track bias              |         0.433 |         0.443 |         0.438 |         0.437 |
| tbx_bar_recent    |  0.061 |                 0.473 | track bias              |         0.505 |         0.462 |         0.417 |         0.473 |
