# Staged model: ability -> conditions -> race shape -> win probability

- S1 ability and S2 conditions: one ridge regression of today's WPR (within race) on history and today's conditions; S3 race shape: projected lengths behind the leader, width, early / mid / late pace, valued by track bias maps (track, distance, going, rail) plus a track-specific cost per extra metre
- Final: conditional logit on S1, S2, S3 and a debut flag; walk-forward 2023 to 2026, VIC/SA/QLD

## Log loss by fold

|                          |   2023 |   2024 |   2025 |   2026 |   pooled |
|:-------------------------|-------:|-------:|-------:|-------:|---------:|
| SP calibrated            | 1.7920 | 1.7885 | 1.7856 | 1.7757 |   1.7863 |
| model staged             | 1.9635 | 1.9626 | 1.9598 | 1.9643 |   1.9624 |
| blend staged             | 1.7918 | 1.7882 | 1.7848 | 1.7761 |   1.7860 |
| model S1 + S2            | 1.9701 | 1.9707 | 1.9666 | 1.9708 |   1.9694 |
| blend S1 + S2            | 1.7917 | 1.7882 | 1.7849 | 1.7759 |   1.7860 |
| model S1                 | 2.0068 | 2.0117 | 2.0055 | 2.0038 |   2.0073 |
| blend S1                 | 1.7909 | 1.7882 | 1.7850 | 1.7758 |   1.7858 |
| model prod               | 1.9278 | 1.9242 | 1.9310 | 1.9268 |   1.9275 |
| blend prod               | 1.7903 | 1.7867 | 1.7846 | 1.7751 |   1.7849 |
| model prod mu            | 1.9245 | 1.9210 | 1.9278 | 1.9229 |   1.9242 |
| blend prod mu            | 1.7903 | 1.7867 | 1.7847 | 1.7751 |   1.7850 |
| model prod mu + S3       | 1.9255 | 1.9216 | 1.9267 | 1.9232 |   1.9243 |
| blend prod mu + S3       | 1.7905 | 1.7867 | 1.7847 | 1.7752 |   1.7851 |
| model prod mu + S3 parts | 1.9253 | 1.9222 | 1.9269 | 1.9232 |   1.9245 |
| blend prod mu + S3 parts | 1.7903 | 1.7868 | 1.7847 | 1.7753 |   1.7851 |
| model prod2 (no fig2)    | 1.9247 | 1.9206 | 1.9278 | 1.9228 |   1.9241 |
| blend prod2 (no fig2)    | 1.7903 | 1.7866 | 1.7847 | 1.7751 |   1.7850 |

## Paired differences (negative = first is better; 95% race bootstrap)

| first                    | minus                 |   races | all                          | QLD                          | VIC/SA                       |
|:-------------------------|:----------------------|--------:|:-----------------------------|:-----------------------------|:-----------------------------|
| model prod mu + S3       | model prod mu         |   37821 | +0.0002 (-0.0005 to +0.0009) | -0.0002 (-0.0012 to +0.0009) | +0.0005 (-0.0004 to +0.0013) |
| blend prod mu + S3       | blend prod mu         |   37821 | +0.0001 (-0.0000 to +0.0002) | -0.0001 (-0.0002 to +0.0001) | +0.0002 (+0.0001 to +0.0004) |
| model prod mu + S3 parts | model prod mu         |   37821 | +0.0003 (-0.0004 to +0.0010) | -0.0000 (-0.0011 to +0.0011) | +0.0006 (-0.0004 to +0.0015) |
| blend prod mu + S3 parts | blend prod mu         |   37821 | +0.0001 (-0.0000 to +0.0002) | -0.0001 (-0.0003 to +0.0001) | +0.0002 (+0.0000 to +0.0004) |
| blend prod mu + S3       | SP calibrated         |   37821 | -0.0012 (-0.0020 to -0.0004) | -0.0036 (-0.0049 to -0.0022) | +0.0008 (-0.0003 to +0.0018) |
| model staged             | model prod            |   37821 | +0.0349 (+0.0319 to +0.0378) | +0.0321 (+0.0278 to +0.0369) | +0.0372 (+0.0335 to +0.0409) |
| blend staged             | blend prod            |   37821 | +0.0010 (+0.0006 to +0.0015) | +0.0019 (+0.0013 to +0.0026) | +0.0003 (-0.0003 to +0.0009) |
| blend staged             | SP calibrated         |   37821 | -0.0003 (-0.0009 to +0.0002) | -0.0015 (-0.0024 to -0.0007) | +0.0007 (-0.0001 to +0.0014) |
| model S1 + S2            | model S1              |   37821 | -0.0378 (-0.0406 to -0.0349) | -0.0399 (-0.0446 to -0.0350) | -0.0361 (-0.0397 to -0.0328) |
| model staged             | model S1 + S2         |   37821 | -0.0070 (-0.0087 to -0.0054) | -0.0093 (-0.0120 to -0.0067) | -0.0052 (-0.0073 to -0.0031) |
| blend staged             | blend S1 + S2         |   37821 | -0.0000 (-0.0003 to +0.0002) | -0.0005 (-0.0009 to -0.0001) | +0.0004 (+0.0000 to +0.0007) |
| model staged             | model prod2 (no fig2) |   37821 | +0.0383 (+0.0351 to +0.0415) | +0.0379 (+0.0330 to +0.0427) | +0.0386 (+0.0347 to +0.0427) |
| blend staged             | blend prod2 (no fig2) |   37821 | +0.0010 (+0.0006 to +0.0015) | +0.0021 (+0.0014 to +0.0028) | +0.0002 (-0.0004 to +0.0007) |

## Stage fits and accuracy by fold

|                                     | 2023                                                                                                | 2024                                                                                                | 2025                                                                                                 | 2026                                                                                                 |
|:------------------------------------|:----------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------|
| S1+S2 WPR R2 (train)                | 0.21454605884073785                                                                                 | 0.21852203340114074                                                                                 | 0.22299480206280642                                                                                  | 0.22627675985792461                                                                                  |
| lengths R2                          | 0.34600589959701755                                                                                 | 0.3457081812553887                                                                                  | 0.3262669017821308                                                                                   | 0.3004232228648065                                                                                   |
| pace early R2                       | 0.061342770189933504                                                                                | 0.0920325796159066                                                                                  | 0.11149975149151581                                                                                  | 0.11262160843017643                                                                                  |
| pace mid R2                         | -0.0007611890606087357                                                                              | 0.0418677722520433                                                                                  | 0.061613557654676576                                                                                 | 0.08678845729521412                                                                                  |
| pace late R2                        | 0.02779570627749084                                                                                 | 0.05941101732329446                                                                                 | 0.0741955407692817                                                                                   | 0.06604441925614513                                                                                  |
| ground cost global (WPR / m)        | -0.025062317540796256                                                                               | -0.07331591852297219                                                                                | -0.08555023293949286                                                                                 | -0.08777497652899914                                                                                 |
| stage weights (S1, S2, S3, debut)   | (np.float64(0.1706), np.float64(0.1553), np.float64(0.3001), np.float64(0.6653))                    | (np.float64(0.1813), np.float64(0.1408), np.float64(0.2861), np.float64(0.7395))                    | (np.float64(0.1822), np.float64(0.1394), np.float64(0.2634), np.float64(0.7631))                     | (np.float64(0.1805), np.float64(0.1394), np.float64(0.258), np.float64(0.7345))                      |
| blend a/b staged                    | (np.float64(0.133), np.float64(1.112))                                                              | (np.float64(0.111), np.float64(1.044))                                                              | (np.float64(0.097), np.float64(1.097))                                                               | (np.float64(0.111), np.float64(1.051))                                                               |
| blend a/b prod                      | (np.float64(0.181), np.float64(1.067))                                                              | (np.float64(0.135), np.float64(1.016))                                                              | (np.float64(0.149), np.float64(1.049))                                                               | (np.float64(0.124), np.float64(1.032))                                                               |
| S3 weight in prod mu + S3 (per WPR) | 0.22337047543722327                                                                                 | 0.18723243497128386                                                                                 | 0.16096885471207817                                                                                  | 0.1703416606647476                                                                                   |
| S3 part weights                     | (np.float64(0.2306), np.float64(0.1998), np.float64(0.355), np.float64(0.0167), np.float64(0.1329)) | (np.float64(0.168), np.float64(0.1066), np.float64(0.4297), np.float64(0.4172), np.float64(0.0947)) | (np.float64(0.1724), np.float64(0.1297), np.float64(0.2533), np.float64(0.1807), np.float64(0.0486)) | (np.float64(0.1875), np.float64(0.0886), np.float64(0.1872), np.float64(0.3644), np.float64(0.0305)) |

## S1 / S2 weights: WPR points per unit of each input (fit on all training rows)

| input            | stage         |   2023 |   2024 |   2025 |   2026 |
|:-----------------|:--------------|-------:|-------:|-------:|-------:|
| age2             | S1 ability    |  7.334 |  6.910 |  6.964 |  7.034 |
| age3             | S1 ability    |  2.824 |  2.616 |  2.433 |  2.366 |
| age7             | S1 ability    | -0.801 | -0.695 | -0.684 | -0.676 |
| best10           | S1 ability    | -0.012 | -0.016 | -0.018 | -0.020 |
| best3            | S1 ability    |  0.091 |  0.110 |  0.121 |  0.120 |
| cm_dm_checked    | S1 ability    |  1.202 |  1.205 |  1.070 |  0.972 |
| cm_dm_health     | S1 ability    |  0.619 |  0.869 |  0.830 |  0.802 |
| cm_dm_over       | S1 ability    |  0.618 |  0.733 |  0.505 |  0.471 |
| cm_dm_slow       | S1 ability    |  0.241 |  0.175 |  0.204 |  0.351 |
| cm_dm_tag        | S1 ability    |  0.329 |  0.349 |  0.333 |  0.342 |
| cm_dm_vblocked   | S1 ability    |  0.595 |  0.206 |  0.602 |  0.678 |
| cm_dm_vwide      | S1 ability    |  0.646 |  0.767 |  0.933 |  1.020 |
| cm_dm_wide       | S1 ability    |  1.140 |  0.836 |  0.940 |  0.958 |
| cm_last_checked  | S1 ability    | -0.241 | -0.202 | -0.134 | -0.083 |
| cm_last_has      | S1 ability    | 24.665 |  8.538 |  9.157 |  9.156 |
| cm_last_health   | S1 ability    |  0.025 | -0.145 | -0.081 | -0.020 |
| cm_last_over     | S1 ability    | -0.136 | -0.110 | -0.011 |  0.022 |
| cm_last_slow     | S1 ability    | -0.091 | -0.201 | -0.179 | -0.177 |
| cm_last_tag      | S1 ability    |  0.429 |  0.366 |  0.331 |  0.297 |
| cm_last_vblocked | S1 ability    |  0.212 |  0.411 |  0.313 |  0.264 |
| cm_last_vwide    | S1 ability    |  0.130 |  0.189 |  0.097 |  0.075 |
| cm_last_wide     | S1 ability    | -0.136 | -0.029 | -0.016 | -0.040 |
| dm               | S1 ability    |  0.225 |  0.227 |  0.219 |  0.218 |
| female           | S1 ability    |  0.408 |  0.394 |  0.439 |  0.410 |
| fig_last         | S1 ability    |  0.162 |  0.161 |  0.150 |  0.143 |
| h_class          | S1 ability    | -0.108 | -0.113 | -0.113 | -0.117 |
| h_gl             | S1 ability    | -0.006 |  0.099 |  0.120 |  0.102 |
| h_gl_miss        | S1 ability    | -0.698 | -0.870 | -0.881 | -0.955 |
| h_last_wpr       | S1 ability    | -0.019 | -0.032 | -0.012 |  0.016 |
| h_none           | S1 ability    | 49.763 | 33.703 | 33.759 | 34.206 |
| h_pace           | S1 ability    |  0.001 | -0.032 | -0.004 | -0.012 |
| h_rail           | S1 ability    |  0.055 | -0.010 | -0.072 | -0.036 |
| h_s_early        | S1 ability    | -0.003 | -0.032 | -0.054 | -0.069 |
| h_s_early_miss   | S1 ability    | -0.401 | -0.257 |  0.107 | -0.048 |
| h_s_l600         | S1 ability    | -0.107 | -0.090 | -0.063 | -0.075 |
| h_settle         | S1 ability    |  2.846 |  2.421 |  2.005 |  1.882 |
| h_settle_miss    | S1 ability    |  0.825 |  0.320 |  0.132 |  0.087 |
| h_shape          | S1 ability    | -0.054 |  0.014 |  0.038 |  0.047 |
| h_wpr            | S1 ability    |  0.221 |  0.222 |  0.213 |  0.213 |
| h_wt_rel         | S1 ability    | -0.226 | -0.213 | -0.213 | -0.200 |
| log_n            | S1 ability    |  0.392 |  0.394 |  0.323 |  0.274 |
| mean3            | S1 ability    | -0.085 | -0.084 | -0.082 | -0.086 |
| trend            | S1 ability    | -0.096 | -0.091 | -0.101 | -0.117 |
| trial_marg_debut | S1 ability    | -0.022 | -0.147 | -0.240 | -0.341 |
| trial_pos_debut  | S1 ability    | -8.983 | -7.900 | -7.529 | -6.296 |
| c_ae             | S2 conditions |  0.330 |  0.347 |  0.360 |  0.396 |
| dist_abs         | S2 conditions | -5.887 | -5.125 | -5.274 | -5.580 |
| dist_fit         | S2 conditions |  0.013 |  0.008 |  0.001 |  0.009 |
| dist_ratio       | S2 conditions |  0.905 |  0.940 |  0.818 |  0.964 |
| first_up         | S2 conditions |  0.225 |  0.203 |  0.233 |  0.215 |
| fu               | S2 conditions |  0.225 |  0.203 |  0.233 |  0.215 |
| fu_apt           | S2 conditions | -0.012 |  0.012 |  0.040 |  0.034 |
| going_fit        | S2 conditions |  0.042 |  0.030 |  0.006 |  0.001 |
| h_ae             | S2 conditions | -0.930 | -0.835 | -0.721 | -0.609 |
| j90_ae           | S2 conditions | -0.265 |  0.019 | -0.024 | -0.044 |
| j_ae             | S2 conditions | -0.562 | -0.468 | -0.521 | -0.694 |
| j_change         | S2 conditions | -0.472 | -0.554 | -0.511 | -0.481 |
| j_sr             | S2 conditions | 20.457 | 18.640 | 18.807 | 18.988 |
| j_upgrade        | S2 conditions |  0.178 |  0.433 |  0.633 |  0.954 |
| log_days         | S2 conditions | -0.964 | -1.013 | -1.084 | -1.089 |
| su               | S2 conditions | -0.945 | -0.891 | -0.853 | -0.919 |
| su_apt           | S2 conditions | -0.021 | -0.008 | -0.002 | -0.017 |
| surface_fit      | S2 conditions | -0.068 | -0.038 | -0.009 | -0.007 |
| t_ae             | S2 conditions | -3.194 | -3.094 | -3.061 | -2.907 |
| t_sr             | S2 conditions | 28.895 | 29.748 | 30.170 | 29.636 |
| tfu_ae           | S2 conditions |  0.761 |  0.889 |  1.119 |  1.310 |
| trial_marg       | S2 conditions | -0.282 | -0.277 | -0.260 | -0.285 |
| trial_pos        | S2 conditions | -2.333 | -2.098 | -2.108 | -2.003 |
| trial_since      | S2 conditions |  0.583 |  0.612 |  0.651 |  0.691 |
| up3              | S2 conditions | -0.350 | -0.466 | -0.452 | -0.497 |
| wt_rel_today     | S2 conditions |  0.552 |  0.548 |  0.542 |  0.534 |
