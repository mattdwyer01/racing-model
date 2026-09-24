# Production logit in WPR points

- Model: conditional logit on 88 inputs (figure, ability, jockey/trainer, race-day projection, run comments); saved to data/models/logit_2026-01-01.pkl
- Training states: VIC, SA, QLD + NSW, WA
- Trained on races before 2026-01-01. One WPR point of ability = 0.1681 utility
- Blend with the market: a = 0.094 (model), b = 1.060 (market); calibrated market c = 1.128; fitted on 05 Jan 2025 to 31 Dec 2025
- 'WPR points per unit': the bonus / penalty for +1 on that input, holding the others; a horse's contribution is that times (its value minus the field average)
- 'fit to YYYY' columns: the same weights fitted on races before that year (stability)

|                   |   beta |   WPR points per unit | group                   |   fit to 2023 |   fit to 2024 |   fit to 2025 |   fit to 2026 |
|:------------------|-------:|----------------------:|:------------------------|--------------:|--------------:|--------------:|--------------:|
| log_n             | -0.202 |                -1.202 | ability                 |        -0.794 |        -1.095 |        -1.182 |        -1.202 |
| mean3             | -0.019 |                -0.111 | ability                 |        -0.139 |        -0.131 |        -0.131 |        -0.111 |
| h_class           | -0.013 |                -0.077 | ability                 |        -0.045 |        -0.077 |        -0.075 |        -0.077 |
| fig_last          |  0.011 |                 0.065 | ability                 |         0.077 |         0.074 |         0.071 |         0.065 |
| h_wpr             |  0.013 |                 0.075 | ability                 |         0.086 |         0.085 |         0.083 |         0.075 |
| dm                |  0.013 |                 0.080 | ability                 |         0.091 |         0.089 |         0.087 |         0.080 |
| best10            |  0.014 |                 0.085 | ability                 |         0.044 |         0.069 |         0.078 |         0.085 |
| r_sigma           |  0.023 |                 0.135 | ability                 |         0.339 |         0.166 |         0.148 |         0.135 |
| best3             |  0.024 |                 0.143 | ability                 |         0.111 |         0.134 |         0.138 |         0.143 |
| r_mu              |  0.111 |                 0.663 | ability                 |         0.729 |         0.679 |         0.673 |         0.663 |
| h_none            |  1.347 |                 8.010 | ability                 |         6.847 |         7.767 |         7.912 |         8.010 |
| age2              | -1.214 |                -7.220 | age / sex / weight      |        -6.856 |        -6.848 |        -7.165 |        -7.220 |
| age3              | -0.380 |                -2.263 | age / sex / weight      |        -2.313 |        -2.222 |        -2.187 |        -2.263 |
| female            | -0.331 |                -1.969 | age / sex / weight      |        -1.972 |        -1.973 |        -1.969 |        -1.969 |
| age7              | -0.134 |                -0.799 | age / sex / weight      |        -1.103 |        -0.997 |        -0.917 |        -0.799 |
| wt_rel_today      | -0.084 |                -0.499 | age / sex / weight      |        -0.503 |        -0.526 |        -0.528 |        -0.499 |
| cm_last_has       | -1.363 |                -8.106 | comments                |        -6.854 |        -7.789 |        -8.043 |        -8.106 |
| cm_last_vwide     | -0.051 |                -0.305 | comments                |        -0.238 |        -0.277 |        -0.303 |        -0.305 |
| cm_last_slow      | -0.050 |                -0.296 | comments                |        -0.071 |        -0.286 |        -0.373 |        -0.296 |
| cm_last_health    | -0.043 |                -0.256 | comments                |        -0.199 |        -0.187 |        -0.183 |        -0.256 |
| cm_last_over      | -0.029 |                -0.173 | comments                |         0.037 |        -0.265 |        -0.177 |        -0.173 |
| cm_last_wide      | -0.027 |                -0.161 | comments                |        -0.569 |        -0.383 |        -0.174 |        -0.161 |
| cm_last_checked   | -0.026 |                -0.156 | comments                |         0.031 |         0.066 |        -0.069 |        -0.156 |
| cm_last_tag       |  0.015 |                 0.091 | comments                |         0.031 |         0.093 |         0.105 |         0.091 |
| cm_last_vblocked  |  0.022 |                 0.132 | comments                |         0.588 |         0.142 |         0.004 |         0.132 |
| cm_dm_vblocked    |  0.029 |                 0.172 | comments                |         0.172 |         0.543 |         0.425 |         0.172 |
| cm_dm_checked     |  0.072 |                 0.429 | comments                |        -0.246 |        -0.035 |         0.281 |         0.429 |
| cm_dm_tag         |  0.076 |                 0.451 | comments                |         0.405 |         0.463 |         0.444 |         0.451 |
| cm_dm_slow        |  0.113 |                 0.671 | comments                |         0.573 |         0.640 |         0.772 |         0.671 |
| cm_dm_over        |  0.127 |                 0.755 | comments                |         0.663 |         0.955 |         0.842 |         0.755 |
| cm_dm_health      |  0.143 |                 0.852 | comments                |         1.662 |         0.945 |         0.792 |         0.852 |
| cm_dm_wide        |  0.168 |                 1.002 | comments                |         1.612 |         1.327 |         1.048 |         1.002 |
| cm_dm_vwide       |  0.189 |                 1.122 | comments                |         0.634 |         0.907 |         1.101 |         1.122 |
| dist_abs          | -0.048 |                -0.283 | distance / going        |         0.937 |        -0.188 |        -0.272 |        -0.283 |
| surface_fit       | -0.008 |                -0.050 | distance / going        |        -0.080 |        -0.060 |        -0.052 |        -0.050 |
| dist_fit          |  0.004 |                 0.026 | distance / going        |         0.005 |         0.030 |         0.027 |         0.026 |
| going_fit         |  0.005 |                 0.030 | distance / going        |         0.050 |         0.031 |         0.023 |         0.030 |
| dist_ratio        |  0.141 |                 0.839 | distance / going        |         0.898 |         0.005 |         0.075 |         0.839 |
| h_wt_rel          | -0.082 |                -0.488 | form shape              |        -0.443 |        -0.460 |        -0.467 |        -0.488 |
| h_shape           | -0.014 |                -0.083 | form shape              |        -0.027 |        -0.108 |        -0.107 |        -0.083 |
| trend             | -0.003 |                -0.020 | form shape              |        -0.020 |        -0.020 |        -0.020 |        -0.020 |
| h_s_early         | -0.001 |                -0.006 | form shape              |        -0.032 |         0.027 |         0.014 |        -0.006 |
| h_s_early_miss    | -0.000 |                -0.000 | form shape              |        -0.182 |        -0.017 |         0.212 |        -0.000 |
| h_pace            |  0.030 |                 0.180 | form shape              |         0.200 |         0.156 |         0.166 |         0.180 |
| h_s_l600          |  0.045 |                 0.265 | form shape              |         0.265 |         0.269 |         0.284 |         0.265 |
| h_settle_miss     |  0.073 |                 0.434 | form shape              |        -0.185 |         0.418 |         0.350 |         0.434 |
| h_settle          |  0.254 |                 1.513 | form shape              |         0.308 |         2.182 |         1.865 |         1.513 |
| h_rail            | -0.029 |                -0.175 | ground loss (past runs) |        -0.287 |        -0.333 |        -0.356 |        -0.175 |
| h_gl_miss         | -0.007 |                -0.039 | ground loss (past runs) |         0.546 |        -0.022 |         0.080 |        -0.039 |
| h_gl              |  0.032 |                 0.188 | ground loss (past runs) |         0.003 |         0.171 |         0.239 |         0.188 |
| j_ae              | -0.266 |                -1.584 | jockey / trainer        |        -0.993 |        -1.395 |        -1.632 |        -1.584 |
| h_ae              | -0.117 |                -0.693 | jockey / trainer        |        -0.126 |        -0.576 |        -0.691 |        -0.693 |
| t_ae              | -0.078 |                -0.466 | jockey / trainer        |        -0.698 |        -0.492 |        -0.366 |        -0.466 |
| j_change          |  0.015 |                 0.088 | jockey / trainer        |         0.176 |         0.205 |         0.127 |         0.088 |
| c_ae              |  0.065 |                 0.384 | jockey / trainer        |         0.420 |         0.359 |         0.321 |         0.384 |
| j90_ae            |  0.075 |                 0.449 | jockey / trainer        |         0.088 |         0.219 |         0.306 |         0.449 |
| tfu_ae            |  0.091 |                 0.540 | jockey / trainer        |         0.013 |         0.265 |         0.422 |         0.540 |
| j_upgrade         |  0.268 |                 1.594 | jockey / trainer        |         2.828 |         2.252 |         2.473 |         1.594 |
| t_sr              |  0.992 |                 5.899 | jockey / trainer        |         7.319 |         5.691 |         5.006 |         5.899 |
| j_sr              |  2.609 |                15.515 | jockey / trainer        |        13.839 |        13.865 |        15.015 |        15.515 |
| trial_pos         | -0.483 |                -2.875 | prep                    |        -2.933 |        -3.205 |        -3.186 |        -2.875 |
| trial_since       | -0.086 |                -0.514 | prep                    |        -0.205 |        -0.501 |        -0.571 |        -0.514 |
| log_days          | -0.044 |                -0.260 | prep                    |        -0.479 |        -0.294 |        -0.289 |        -0.260 |
| trial_marg_debut  | -0.024 |                -0.144 | prep                    |        -0.207 |        -0.123 |        -0.132 |        -0.144 |
| su                | -0.020 |                -0.122 | prep                    |         0.002 |        -0.091 |        -0.068 |        -0.122 |
| fu_apt            | -0.003 |                -0.021 | prep                    |        -0.012 |        -0.032 |        -0.003 |        -0.021 |
| up3               |  0.001 |                 0.003 | prep                    |        -0.026 |        -0.021 |        -0.059 |         0.003 |
| su_apt            |  0.003 |                 0.017 | prep                    |         0.018 |         0.027 |         0.032 |         0.017 |
| trial_pos_debut   |  0.005 |                 0.029 | prep                    |         1.234 |         0.713 |         0.740 |         0.029 |
| trial_marg        |  0.009 |                 0.054 | prep                    |         0.193 |         0.088 |         0.063 |         0.054 |
| first_up          |  0.036 |                 0.214 | prep                    |         0.352 |         0.242 |         0.220 |         0.214 |
| fu                |  0.036 |                 0.214 | prep                    |         0.352 |         0.242 |         0.220 |         0.214 |
| tdx_settle        | -0.733 |                -4.361 | race-day projection     |        -4.518 |        -2.557 |        -3.604 |        -4.361 |
| proj_settle       | -0.644 |                -3.829 | race-day projection     |        -3.382 |        -4.243 |        -4.219 |        -3.829 |
| early_rank2       | -0.028 |                -0.169 | race-day projection     |        -0.318 |        -0.358 |        -0.416 |        -0.169 |
| proj_pace         | -0.008 |                -0.050 | race-day projection     |         0.091 |         0.008 |        -0.075 |        -0.050 |
| nb_diff_out       | -0.001 |                -0.004 | race-day projection     |        -0.003 |        -0.012 |        -0.002 |        -0.004 |
| proj_shape        | -0.000 |                -0.000 | race-day projection     |         0.000 |        -0.000 |        -0.000 |        -0.000 |
| nb_diff_in        |  0.001 |                 0.007 | race-day projection     |         0.020 |         0.005 |         0.005 |         0.007 |
| proj_gl           |  0.002 |                 0.014 | race-day projection     |        -0.013 |         0.090 |         0.051 |         0.014 |
| wide_x_slow       |  0.013 |                 0.076 | race-day projection     |         0.438 |         0.214 |         0.262 |         0.076 |
| tdx_perf          |  0.017 |                 0.104 | race-day projection     |         0.194 |         0.162 |         0.118 |         0.104 |
| barrier_pct       |  0.130 |                 0.775 | race-day projection     |         0.202 |         0.509 |         0.625 |         0.775 |
| proj_settle_rank  |  0.162 |                 0.963 | race-day projection     |         0.875 |         0.881 |         1.089 |         0.963 |
| proj_adj          |  0.204 |                 1.214 | race-day projection     |         1.249 |         1.347 |         1.311 |         1.214 |
| tbx_settle_long   | -0.010 |                -0.059 | track bias              |         0.213 |         0.006 |         0.025 |        -0.059 |
| bias_adj          |  0.001 |                 0.004 | track bias              |         0.011 |         0.024 |         0.024 |         0.004 |
| tbx_bar_long      |  0.007 |                 0.039 | track bias              |        -0.092 |         0.036 |         0.025 |         0.039 |
| tbx_settle_recent |  0.034 |                 0.203 | track bias              |         0.389 |         0.378 |         0.335 |         0.203 |
| tbx_bar_recent    |  0.060 |                 0.359 | track bias              |         0.403 |         0.361 |         0.319 |         0.359 |
