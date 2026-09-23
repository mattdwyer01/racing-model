# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                    |       2023 |       2024 |       2025 |      2026 |     pooled |
|:-----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                              | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                             |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                      |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)          |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit              |     1.9339 |     1.9307 |     1.9348 |    1.9328 |     1.9331 |
| baseline: blend logit              |     1.7907 |     1.7872 |     1.7844 |    1.7752 |     1.7852 |
| baseline: blend logit (per state)  |     1.7910 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| baseline: model gbm                |     1.9195 |     1.9094 |     1.9021 |    1.8972 |     1.9079 |
| baseline: blend gbm                |     1.7915 |     1.7877 |     1.7844 |    1.7750 |     1.7855 |
| baseline: blend gbm (per state)    |     1.7914 |     1.7875 |     1.7841 |    1.7748 |     1.7853 |
| baseline: model rating             |     1.9714 |     1.9710 |     1.9709 |    1.9711 |     1.9711 |
| baseline: blend rating             |     1.7922 |     1.7879 |     1.7852 |    1.7758 |     1.7861 |
| baseline: blend rating (per state) |     1.7932 |     1.7880 |     1.7849 |    1.7755 |     1.7863 |

## Differences vs SP, pooled

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw         | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5946 |
| baseline blend logit - SP raw         | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5998 |
| baseline blend logit - SP raw         | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5904 |
| baseline blend logit - SP calibrated  | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5237 |
| baseline blend logit - SP calibrated  | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5339 |
| baseline blend logit - SP calibrated  | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5153 |
| baseline blend gbm - SP raw           | all     | 37821 | -0.0045 |  -0.0056 |  -0.0033 |                  0.5963 |
| baseline blend gbm - SP raw           | QLD     | 16991 | -0.0063 |  -0.0078 |  -0.0046 |                  0.6036 |
| baseline blend gbm - SP raw           | VIC/SA  | 20830 | -0.0030 |  -0.0046 |  -0.0014 |                  0.5903 |
| baseline blend gbm - SP calibrated    | all     | 37821 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5214 |
| baseline blend gbm - SP calibrated    | QLD     | 16991 | -0.0023 |  -0.0029 |  -0.0017 |                  0.5379 |
| baseline blend gbm - SP calibrated    | VIC/SA  | 20830 |  0.0004 |  -0.0001 |   0.0010 |                  0.5079 |
| baseline blend rating - SP raw        | all     | 37821 | -0.0039 |  -0.0050 |  -0.0027 |                  0.6063 |
| baseline blend rating - SP raw        | QLD     | 16991 | -0.0050 |  -0.0067 |  -0.0032 |                  0.6077 |
| baseline blend rating - SP raw        | VIC/SA  | 20830 | -0.0029 |  -0.0044 |  -0.0015 |                  0.6051 |
| baseline blend rating - SP calibrated | all     | 37821 | -0.0002 |  -0.0006 |   0.0002 |                  0.5200 |
| baseline blend rating - SP calibrated | QLD     | 16991 | -0.0010 |  -0.0016 |  -0.0004 |                  0.5331 |
| baseline blend rating - SP calibrated | VIC/SA  | 20830 |  0.0005 |   0.0000 |   0.0010 |                  0.5093 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   baseline rating | baseline rating 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|------------------:|:----------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0008   |        -0.0017 | -0.0030 to -0.0004 |           -0.0007 | -0.0022 to +0.0007    |
| 2023 H2  |    5233 |           0.0001 | -0.0018 to +0.0020   |         0.0006 | -0.0006 to +0.0018 |            0.0010 | -0.0004 to +0.0024    |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0002   |        -0.0011 | -0.0020 to -0.0002 |           -0.0006 | -0.0013 to +0.0000    |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |        -0.0004 | -0.0013 to +0.0005 |           -0.0004 | -0.0011 to +0.0002    |
| 2025 H1  |    5065 |          -0.0011 | -0.0027 to +0.0006   |        -0.0008 | -0.0019 to +0.0003 |           -0.0001 | -0.0012 to +0.0011    |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0003   |        -0.0014 | -0.0024 to -0.0003 |           -0.0007 | -0.0018 to +0.0004    |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0007 | -0.0019 to +0.0007 |            0.0000 | -0.0009 to +0.0009    |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0009   |        -0.0009 | -0.0031 to +0.0012 |            0.0001 | -0.0015 to +0.0016    |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                                 | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:---------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5236 |
| baseline blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0027 |  -0.0041 |  -0.0012 |                  0.5213 |
| baseline blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5255 |
| baseline blend gbm (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0011 |  -0.0017 |  -0.0004 |                  0.5144 |
| baseline blend gbm (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0024 |  -0.0038 |  -0.0010 |                  0.5288 |
| baseline blend gbm (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0000 |  -0.0001 |   0.0001 |                  0.5027 |
| baseline blend rating (per state) - SP calibrated (per state)              | all     | 37821 | -0.0001 |  -0.0006 |   0.0005 |                  0.5201 |
| baseline blend rating (per state) - SP calibrated (per state)              | QLD     | 16991 | -0.0003 |  -0.0014 |   0.0008 |                  0.5207 |
| baseline blend rating (per state) - SP calibrated (per state)              | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0003 |                  0.5196 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)   | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5002 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)   | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5375 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)   | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4698 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)       | all     | 37821 | -0.0002 |  -0.0008 |   0.0003 |                  0.5033 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)       | QLD     | 16991 |  0.0002 |  -0.0006 |   0.0010 |                  0.5373 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)       | VIC/SA  | 20830 | -0.0006 |  -0.0012 |  -0.0000 |                  0.4755 |
| baseline blend rating (per state) - baseline blend rating (pooled weights) | all     | 37821 |  0.0002 |  -0.0002 |   0.0005 |                  0.4959 |
| baseline blend rating (per state) - baseline blend rating (pooled weights) | QLD     | 16991 |  0.0011 |   0.0005 |   0.0017 |                  0.5562 |
| baseline blend rating (per state) - baseline blend rating (pooled weights) | VIC/SA  | 20830 | -0.0006 |  -0.0010 |  -0.0002 |                  0.4468 |
| SP calibrated (per state) - SP calibrated (pooled)                         | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                         | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                         | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   baseline blend rating (per state) - SP calibrated (per state) | baseline blend rating (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|----------------------------------------------------------------:|:--------------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0050 to -0.0003                                                 |                                                      -0.0024 | -0.0045 to -0.0003                                               |                                                         -0.0001 | -0.0022 to +0.0019                                                  |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0021 to +0.0030                                                 |                                                       0.0009 | -0.0013 to +0.0030                                               |                                                          0.0023 | +0.0002 to +0.0044                                                  |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0027 to +0.0002                                                 |                                                      -0.0003 | -0.0016 to +0.0011                                               |                                                         -0.0004 | -0.0011 to +0.0003                                                  |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0033 to -0.0002                                                 |                                                      -0.0017 | -0.0030 to -0.0004                                               |                                                         -0.0006 | -0.0013 to +0.0001                                                  |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0005                                                 |                                                      -0.0011 | -0.0025 to +0.0003                                               |                                                         -0.0004 | -0.0015 to +0.0007                                                  |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0004                                                 |                                                      -0.0021 | -0.0035 to -0.0007                                               |                                                         -0.0010 | -0.0021 to +0.0002                                                  |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0023 to +0.0011                                                 |                                                      -0.0010 | -0.0026 to +0.0007                                               |                                                         -0.0002 | -0.0015 to +0.0010                                                  |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0040 to +0.0010                                                 |                                                      -0.0009 | -0.0035 to +0.0017                                               |                                                         -0.0002 | -0.0023 to +0.0018                                                  |

## Rating model vs the baseline models (paired by race)

| comparison                          | races   |     n |   mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------|:--------|------:|-------:|---------:|---------:|------------------------:|
| rating blend - baseline logit blend | all     | 37821 | 0.0009 |   0.0005 |   0.0014 |                  0.4788 |
| rating blend - baseline logit blend | QLD     | 16991 | 0.0019 |   0.0013 |   0.0026 |                  0.4686 |
| rating blend - baseline logit blend | VIC/SA  | 20830 | 0.0002 |  -0.0004 |   0.0007 |                  0.4871 |
| rating blend - baseline gbm blend   | all     | 37821 | 0.0006 |   0.0002 |   0.0010 |                  0.4860 |
| rating blend - baseline gbm blend   | QLD     | 16991 | 0.0012 |   0.0007 |   0.0018 |                  0.4827 |
| rating blend - baseline gbm blend   | VIC/SA  | 20830 | 0.0001 |  -0.0004 |   0.0006 |                  0.4887 |
| rating model - baseline logit model | all     | 37821 | 0.0380 |   0.0339 |   0.0421 |                  0.4508 |
| rating model - baseline logit model | QLD     | 16991 | 0.0341 |   0.0281 |   0.0398 |                  0.4542 |
| rating model - baseline logit model | VIC/SA  | 20830 | 0.0412 |   0.0360 |   0.0465 |                  0.4481 |

## Rating model: bonus / penalty per unit of each input (WPR points), fit on each fold's training rows

|                  |   2023 |   2024 |   2025 |   2026 |
|:-----------------|-------:|-------:|-------:|-------:|
| dm_v2            |  0.356 |  0.354 |  0.358 |  0.369 |
| fig_last_v2      |  0.301 |  0.293 |  0.295 |  0.302 |
| best3_v2         |  0.031 |  0.045 |  0.059 |  0.059 |
| best10_v2        | -0.003 | -0.002 | -0.007 | -0.010 |
| trend_v2         | -0.223 | -0.226 | -0.233 | -0.237 |
| h_class          | -0.212 | -0.212 | -0.217 | -0.222 |
| log_n            |  0.758 |  0.750 |  0.719 |  0.671 |
| h_none           | 25.156 | 25.151 | 25.418 | 25.840 |
| trial_pos_debut  | -9.260 | -8.157 | -7.802 | -6.534 |
| trial_marg_debut |  0.021 | -0.110 | -0.195 | -0.297 |
| age2             |  6.594 |  6.352 |  6.359 |  6.393 |
| age3             |  2.681 |  2.557 |  2.355 |  2.299 |
| age7             | -0.705 | -0.652 | -0.672 | -0.689 |
| female           |  0.685 |  0.723 |  0.775 |  0.753 |
| proj_adj         |  0.101 |  0.162 |  0.164 |  0.139 |
| bias_adj         |  0.691 |  0.831 |  0.842 |  0.824 |
| tdx_perf         |  0.308 |  0.240 |  0.203 |  0.220 |
| proj_settle      | -0.686 | -0.215 | -0.212 | -0.197 |
| proj_pace        | -0.683 | -0.619 | -0.514 | -0.446 |
| proj_gl          |  0.095 | -0.035 | -0.046 | -0.036 |
| barrier_pct      | -1.482 | -1.085 | -1.061 | -1.109 |
| dist_ratio       |  3.128 |  2.980 |  2.931 |  2.958 |
| dist_abs         | -5.951 | -5.271 | -5.421 | -5.692 |
| dist_fit_v2      |  0.006 | -0.004 | -0.013 | -0.000 |
| going_fit_v2     |  0.060 |  0.038 |  0.010 | -0.001 |
| surface_fit_v2   | -0.094 | -0.051 | -0.006 | -0.003 |
| fu               |  0.330 |  0.339 |  0.452 |  0.412 |
| su               | -0.952 | -0.934 | -0.897 | -0.956 |
| up3              | -0.332 | -0.472 | -0.464 | -0.506 |
| fu_apt_v2        |  0.017 |  0.058 |  0.097 |  0.090 |
| su_apt_v2        | -0.010 |  0.000 |  0.005 | -0.016 |
| log_days         | -0.946 | -1.045 | -1.126 | -1.137 |
| trial_since      |  0.492 |  0.511 |  0.526 |  0.569 |
| trial_pos        | -2.220 | -1.993 | -1.951 | -1.879 |
| trial_marg       | -0.303 | -0.297 | -0.286 | -0.309 |
| wt_rel_today     |  0.425 |  0.423 |  0.415 |  0.406 |
| j_ae             | -0.685 | -0.418 | -0.531 | -0.716 |
| j_sr             | 19.733 | 18.184 | 18.550 | 18.869 |
| t_ae             | -3.301 | -3.202 | -3.187 | -3.026 |
| t_sr             | 30.134 | 30.981 | 31.725 | 31.011 |
| c_ae             |  0.352 |  0.413 |  0.423 |  0.462 |
| tfu_ae           |  0.713 |  0.842 |  1.019 |  1.222 |
| j_upgrade        |  1.255 |  1.138 |  1.156 |  1.401 |
| j_change         | -0.567 | -0.659 | -0.621 | -0.590 |
| h_ae             | -1.206 | -1.104 | -1.015 | -0.895 |
| cm_last_tag      |  0.403 |  0.348 |  0.314 |  0.281 |
| cm_dm_tag        |  0.111 |  0.121 |  0.098 |  0.108 |
| cm_last_checked  | -0.266 | -0.239 | -0.151 | -0.107 |
| cm_last_vblocked |  0.260 |  0.426 |  0.318 |  0.264 |
| cm_last_slow     | -0.010 | -0.147 | -0.120 | -0.041 |
| cm_last_wide     |  0.282 |  0.271 |  0.328 |  0.307 |
| cm_last_vwide    |  0.439 |  0.563 |  0.542 |  0.553 |
| cm_last_health   |  0.065 | -0.039 | -0.026 |  0.017 |
| cm_last_over     |  0.164 |  0.232 |  0.221 |  0.247 |
| cm_dm_checked    |  1.386 |  1.414 |  1.250 |  1.156 |
| cm_dm_vblocked   |  0.772 |  0.421 |  0.754 |  0.838 |

Uncertainty (sigma) model, WPR points: 2023: scale 1.18, intercept 7.03; 2024: scale 1.18, intercept 6.94; 2025: scale 1.20, intercept 6.94; 2026: scale 1.24, intercept 6.82

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   baseline rating a |   baseline rating b |   baseline rating a, QLD |   baseline rating b, QLD |   baseline rating a, VIC/SA |   baseline rating b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|--------------------:|--------------------:|-------------------------:|-------------------------:|----------------------------:|----------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.262 |                   1.048 |                      0.049 |                      1.134 |            0.098 |            1.120 |                 0.253 |                 1.049 |                   -0.016 |                    1.177 |               0.106 |               1.124 |                    0.217 |                    1.088 |                       0.018 |                       1.155 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.102 |              1.041 |                   0.160 |                   1.030 |                      0.023 |                      1.066 |            0.076 |            1.056 |                 0.155 |                 1.033 |                   -0.019 |                    1.094 |               0.047 |               1.081 |                    0.065 |                    1.104 |                       0.018 |                       1.070 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.180 |                   1.038 |                      0.047 |                      1.114 |            0.090 |            1.090 |                 0.172 |                 1.039 |                    0.004 |                    1.143 |               0.084 |               1.103 |                    0.105 |                    1.099 |                       0.060 |                       1.110 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.987 |                      0.051 |                      1.092 |            0.112 |            1.036 |                 0.188 |                 0.968 |                    0.045 |                    1.092 |               0.070 |               1.075 |                    0.134 |                    1.020 |                       0.011 |                       1.118 |
