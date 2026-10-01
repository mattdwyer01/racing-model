# Production logit in WPR points

- Model: conditional logit on 95 inputs (figure, ability, jockey/trainer, race-day projection, run comments); saved to data/models/logit_2026-01-01.pkl
- Training states: VIC, SA, QLD + NSW, WA, TAS, NT, ACT
- Trained on races before 2026-01-01. One WPR point of ability = 0.1688 utility
- Blend with the market: a = 0.090 (model), b = 1.064 (market); calibrated market c = 1.129; fitted on 04 Jan 2025 to 31 Dec 2025
- 'WPR points per unit': the bonus / penalty for +1 on that input, holding the others; a horse's contribution is that times (its value minus the field average)
- 'fit to YYYY' columns: the same weights fitted on races before that year (stability)

|                   |   beta |   WPR points per unit | group                   |   fit to 2023 |   fit to 2024 |   fit to 2025 |   fit to 2026 |
|:------------------|-------:|----------------------:|:------------------------|--------------:|--------------:|--------------:|--------------:|
| log_n             | -0.207 |                -1.225 | ability                 |        -0.886 |        -1.125 |        -1.204 |        -1.225 |
| mean3             | -0.018 |                -0.105 | ability                 |        -0.134 |        -0.124 |        -0.126 |        -0.105 |
| h_class           | -0.013 |                -0.077 | ability                 |        -0.042 |        -0.077 |        -0.074 |        -0.077 |
| fig_last          |  0.010 |                 0.062 | ability                 |         0.069 |         0.068 |         0.067 |         0.062 |
| h_wpr             |  0.012 |                 0.072 | ability                 |         0.076 |         0.078 |         0.077 |         0.072 |
| dm                |  0.013 |                 0.076 | ability                 |         0.081 |         0.082 |         0.082 |         0.076 |
| best10            |  0.016 |                 0.092 | ability                 |         0.050 |         0.076 |         0.085 |         0.092 |
| r_sigma           |  0.022 |                 0.130 | ability                 |         0.294 |         0.153 |         0.143 |         0.130 |
| best3             |  0.024 |                 0.142 | ability                 |         0.116 |         0.136 |         0.139 |         0.142 |
| r_mu              |  0.112 |                 0.662 | ability                 |         0.742 |         0.685 |         0.675 |         0.662 |
| h_none            |  1.360 |                 8.058 | ability                 |         6.551 |         7.619 |         7.915 |         8.058 |
| age2              | -1.191 |                -7.055 | age / sex / weight      |        -6.678 |        -6.472 |        -6.864 |        -7.055 |
| age3              | -0.375 |                -2.224 | age / sex / weight      |        -2.267 |        -2.174 |        -2.148 |        -2.224 |
| female            | -0.329 |                -1.950 | age / sex / weight      |        -1.935 |        -1.906 |        -1.935 |        -1.950 |
| age7              | -0.135 |                -0.798 | age / sex / weight      |        -1.091 |        -0.983 |        -0.919 |        -0.798 |
| wt_rel_today      | -0.083 |                -0.494 | age / sex / weight      |        -0.495 |        -0.526 |        -0.524 |        -0.494 |
| cm_last_has       | -1.375 |                -8.146 | comments                |        -6.557 |        -7.639 |        -8.038 |        -8.146 |
| cm_last_vwide     | -0.057 |                -0.335 | comments                |        -0.270 |        -0.312 |        -0.335 |        -0.335 |
| cm_last_slow      | -0.049 |                -0.289 | comments                |        -0.181 |        -0.323 |        -0.385 |        -0.289 |
| cm_last_health    | -0.037 |                -0.219 | comments                |        -0.209 |        -0.197 |        -0.151 |        -0.219 |
| cm_last_wide      | -0.035 |                -0.210 | comments                |        -0.613 |        -0.425 |        -0.241 |        -0.210 |
| cm_last_over      | -0.030 |                -0.180 | comments                |         0.032 |        -0.223 |        -0.181 |        -0.180 |
| cm_last_checked   | -0.022 |                -0.129 | comments                |        -0.039 |         0.092 |        -0.041 |        -0.129 |
| cm_last_vblocked  |  0.009 |                 0.055 | comments                |         0.523 |         0.100 |        -0.085 |         0.055 |
| cm_last_tag       |  0.016 |                 0.097 | comments                |         0.058 |         0.115 |         0.117 |         0.097 |
| cm_dm_vblocked    |  0.053 |                 0.317 | comments                |         0.299 |         0.588 |         0.551 |         0.317 |
| cm_dm_tag         |  0.072 |                 0.424 | comments                |         0.339 |         0.416 |         0.405 |         0.424 |
| cm_dm_checked     |  0.075 |                 0.443 | comments                |        -0.160 |         0.005 |         0.333 |         0.443 |
| cm_dm_slow        |  0.111 |                 0.657 | comments                |         0.790 |         0.695 |         0.778 |         0.657 |
| cm_dm_over        |  0.132 |                 0.781 | comments                |         0.707 |         0.924 |         0.869 |         0.781 |
| cm_dm_health      |  0.139 |                 0.825 | comments                |         1.647 |         1.047 |         0.778 |         0.825 |
| cm_dm_wide        |  0.181 |                 1.070 | comments                |         1.578 |         1.338 |         1.132 |         1.070 |
| cm_dm_vwide       |  0.204 |                 1.208 | comments                |         0.736 |         1.021 |         1.193 |         1.208 |
| dist_abs          | -0.061 |                -0.362 | distance / going        |         0.837 |        -0.156 |        -0.366 |        -0.362 |
| untried_heavy     | -0.059 |                -0.348 | distance / going        |         0.314 |        -0.133 |        -0.241 |        -0.348 |
| untried_wet       | -0.054 |                -0.322 | distance / going        |        -0.378 |        -0.359 |        -0.342 |        -0.322 |
| surface_fit       | -0.006 |                -0.038 | distance / going        |        -0.073 |        -0.049 |        -0.040 |        -0.038 |
| heavy_x           | -0.003 |                -0.019 | distance / going        |        -0.064 |        -0.037 |        -0.039 |        -0.019 |
| going_fit         |  0.003 |                 0.016 | distance / going        |         0.027 |         0.019 |         0.009 |         0.016 |
| dist_fit          |  0.004 |                 0.021 | distance / going        |         0.009 |         0.025 |         0.023 |         0.021 |
| soft_x            |  0.006 |                 0.033 | distance / going        |         0.092 |         0.037 |         0.057 |         0.033 |
| sire_heavy_x      |  0.025 |                 0.147 | distance / going        |         0.082 |         0.066 |         0.154 |         0.147 |
| sire_wet_x        |  0.058 |                 0.344 | distance / going        |         0.382 |         0.406 |         0.329 |         0.344 |
| dist_ratio        |  0.134 |                 0.792 | distance / going        |         0.754 |        -0.088 |        -0.015 |         0.792 |
| h_wt_rel          | -0.081 |                -0.481 | form shape              |        -0.436 |        -0.437 |        -0.458 |        -0.481 |
| h_shape           | -0.015 |                -0.086 | form shape              |        -0.046 |        -0.115 |        -0.111 |        -0.086 |
| trend             | -0.002 |                -0.015 | form shape              |        -0.012 |        -0.011 |        -0.013 |        -0.015 |
| h_s_early_miss    |  0.001 |                 0.004 | form shape              |        -0.138 |        -0.126 |         0.163 |         0.004 |
| h_s_early         |  0.001 |                 0.004 | form shape              |        -0.005 |         0.036 |         0.024 |         0.004 |
| h_pace            |  0.028 |                 0.167 | form shape              |         0.197 |         0.148 |         0.152 |         0.167 |
| h_s_l600          |  0.043 |                 0.256 | form shape              |         0.269 |         0.266 |         0.275 |         0.256 |
| h_settle_miss     |  0.070 |                 0.417 | form shape              |        -0.259 |         0.358 |         0.344 |         0.417 |
| h_settle          |  0.245 |                 1.451 | form shape              |         0.384 |         2.190 |         1.812 |         1.451 |
| h_rail            | -0.030 |                -0.177 | ground loss (past runs) |        -0.280 |        -0.343 |        -0.363 |        -0.177 |
| h_gl_miss         | -0.011 |                -0.063 | ground loss (past runs) |         0.586 |        -0.027 |         0.062 |        -0.063 |
| h_gl              |  0.030 |                 0.177 | ground loss (past runs) |        -0.006 |         0.167 |         0.227 |         0.177 |
| j_ae              | -0.277 |                -1.641 | jockey / trainer        |        -1.131 |        -1.573 |        -1.732 |        -1.641 |
| h_ae              | -0.122 |                -0.724 | jockey / trainer        |        -0.238 |        -0.617 |        -0.750 |        -0.724 |
| t_ae              | -0.073 |                -0.435 | jockey / trainer        |        -0.652 |        -0.442 |        -0.329 |        -0.435 |
| j_change          |  0.019 |                 0.112 | jockey / trainer        |         0.214 |         0.224 |         0.156 |         0.112 |
| c_ae              |  0.059 |                 0.347 | jockey / trainer        |         0.365 |         0.330 |         0.285 |         0.347 |
| tfu_ae            |  0.073 |                 0.434 | jockey / trainer        |        -0.096 |         0.209 |         0.357 |         0.434 |
| j90_ae            |  0.077 |                 0.456 | jockey / trainer        |         0.146 |         0.291 |         0.304 |         0.456 |
| j_upgrade         |  0.266 |                 1.576 | jockey / trainer        |         2.499 |         2.445 |         2.535 |         1.576 |
| t_sr              |  0.969 |                 5.742 | jockey / trainer        |         6.279 |         5.215 |         4.741 |         5.742 |
| j_sr              |  2.563 |                15.183 | jockey / trainer        |        13.636 |        13.709 |        14.768 |        15.183 |
| trial_pos         | -0.468 |                -2.775 | prep                    |        -2.685 |        -3.073 |        -3.076 |        -2.775 |
| trial_since       | -0.089 |                -0.525 | prep                    |        -0.244 |        -0.538 |        -0.613 |        -0.525 |
| trial_pos_debut   | -0.065 |                -0.386 | prep                    |         0.943 |         0.383 |         0.313 |        -0.386 |
| log_days          | -0.040 |                -0.237 | prep                    |        -0.441 |        -0.264 |        -0.250 |        -0.237 |
| trial_marg_debut  | -0.019 |                -0.113 | prep                    |        -0.170 |        -0.102 |        -0.089 |        -0.113 |
| su                | -0.016 |                -0.097 | prep                    |         0.080 |        -0.079 |        -0.051 |        -0.097 |
| fu_apt            | -0.001 |                -0.008 | prep                    |        -0.016 |        -0.022 |         0.004 |        -0.008 |
| up3               |  0.000 |                 0.001 | prep                    |        -0.026 |        -0.024 |        -0.063 |         0.001 |
| su_apt            |  0.003 |                 0.017 | prep                    |         0.012 |         0.023 |         0.030 |         0.017 |
| trial_marg        |  0.009 |                 0.051 | prep                    |         0.187 |         0.082 |         0.057 |         0.051 |
| first_up          |  0.034 |                 0.202 | prep                    |         0.373 |         0.254 |         0.206 |         0.202 |
| fu                |  0.034 |                 0.202 | prep                    |         0.373 |         0.254 |         0.206 |         0.202 |
| proj_settle       | -0.606 |                -3.587 | race-day projection     |        -3.572 |        -4.246 |        -4.002 |        -3.587 |
| tdx_settle        | -0.531 |                -3.146 | race-day projection     |        -3.243 |        -1.288 |        -2.492 |        -3.146 |
| early_rank2       | -0.023 |                -0.136 | race-day projection     |        -0.288 |        -0.337 |        -0.390 |        -0.136 |
| proj_gl           | -0.002 |                -0.014 | race-day projection     |        -0.021 |         0.078 |         0.028 |        -0.014 |
| nb_diff_out       | -0.001 |                -0.005 | race-day projection     |        -0.006 |        -0.012 |        -0.003 |        -0.005 |
| proj_shape        |  0.000 |                 0.000 | race-day projection     |        -0.000 |        -0.000 |         0.000 |         0.000 |
| nb_diff_in        |  0.002 |                 0.009 | race-day projection     |         0.015 |         0.006 |         0.007 |         0.009 |
| proj_pace         |  0.005 |                 0.032 | race-day projection     |         0.197 |         0.089 |         0.013 |         0.032 |
| tdx_perf          |  0.015 |                 0.091 | race-day projection     |         0.172 |         0.134 |         0.097 |         0.091 |
| wide_x_slow       |  0.019 |                 0.114 | race-day projection     |         0.382 |         0.216 |         0.287 |         0.114 |
| lv_x              |  0.079 |                 0.467 | race-day projection     |         0.348 |         0.389 |         0.449 |         0.467 |
| barrier_pct       |  0.127 |                 0.754 | race-day projection     |         0.200 |         0.496 |         0.608 |         0.754 |
| proj_settle_rank  |  0.158 |                 0.935 | race-day projection     |         0.971 |         0.960 |         1.073 |         0.935 |
| proj_adj          |  0.180 |                 1.067 | race-day projection     |         1.119 |         1.252 |         1.167 |         1.067 |
| tbx_settle_long   | -0.059 |                -0.347 | track bias              |        -0.045 |        -0.267 |        -0.271 |        -0.347 |
| bias_adj          | -0.008 |                -0.048 | track bias              |        -0.018 |        -0.008 |        -0.026 |        -0.048 |
| tbx_bar_long      |  0.017 |                 0.104 | track bias              |        -0.007 |         0.116 |         0.095 |         0.104 |
| tbx_settle_recent |  0.037 |                 0.219 | track bias              |         0.365 |         0.397 |         0.337 |         0.219 |
| tbx_bar_recent    |  0.063 |                 0.374 | track bias              |         0.407 |         0.387 |         0.341 |         0.374 |
