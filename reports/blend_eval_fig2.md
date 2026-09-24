# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, fig2 (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                             | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                     |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)         |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit             |     1.9338 |     1.9309 |     1.9352 |    1.9328 |     1.9332 |
| baseline: blend logit             |     1.7907 |     1.7872 |     1.7845 |    1.7752 |     1.7852 |
| baseline: blend logit (per state) |     1.7910 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| baseline: model gbm               |     1.9183 |     1.9113 |     1.9040 |    1.8974 |     1.9087 |
| baseline: blend gbm               |     1.7915 |     1.7878 |     1.7845 |    1.7749 |     1.7856 |
| baseline: blend gbm (per state)   |     1.7912 |     1.7876 |     1.7841 |    1.7747 |     1.7853 |
| fig2: model logit                 |     1.9290 |     1.9280 |     1.9329 |    1.9295 |     1.9299 |
| fig2: blend logit                 |     1.7906 |     1.7873 |     1.7847 |    1.7753 |     1.7853 |
| fig2: blend logit (per state)     |     1.7910 |     1.7871 |     1.7842 |    1.7751 |     1.7851 |
| fig2: model gbm                   |     1.9167 |     1.9115 |     1.9056 |    1.9007 |     1.9093 |
| fig2: blend gbm                   |     1.7915 |     1.7878 |     1.7847 |    1.7754 |     1.7857 |
| fig2: blend gbm (per state)       |     1.7912 |     1.7877 |     1.7844 |    1.7751 |     1.7854 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5948 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.6006 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5901 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5235 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5332 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0004 |  -0.0004 |   0.0011 |                  0.5157 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0032 |                  0.5946 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0064 |  -0.0080 |  -0.0047 |                  0.6000 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0028 |  -0.0044 |  -0.0012 |                  0.5902 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0007 |  -0.0012 |  -0.0003 |                  0.5206 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0024 |  -0.0031 |  -0.0017 |                  0.5355 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0006 |   0.0001 |   0.0012 |                  0.5084 |
| fig2 blend logit - SP raw            | all     | 37821 | -0.0047 |  -0.0059 |  -0.0035 |                  0.5947 |
| fig2 blend logit - SP raw            | QLD     | 16991 | -0.0068 |  -0.0085 |  -0.0049 |                  0.5999 |
| fig2 blend logit - SP raw            | VIC/SA  | 20830 | -0.0030 |  -0.0045 |  -0.0014 |                  0.5905 |
| fig2 blend logit - SP calibrated     | all     | 37821 | -0.0010 |  -0.0016 |  -0.0004 |                  0.5227 |
| fig2 blend logit - SP calibrated     | QLD     | 16991 | -0.0028 |  -0.0037 |  -0.0020 |                  0.5320 |
| fig2 blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0005 |  -0.0003 |   0.0012 |                  0.5151 |
| fig2 blend gbm - SP raw              | all     | 37821 | -0.0043 |  -0.0054 |  -0.0031 |                  0.5942 |
| fig2 blend gbm - SP raw              | QLD     | 16991 | -0.0064 |  -0.0080 |  -0.0048 |                  0.5993 |
| fig2 blend gbm - SP raw              | VIC/SA  | 20830 | -0.0026 |  -0.0041 |  -0.0010 |                  0.5901 |
| fig2 blend gbm - SP calibrated       | all     | 37821 | -0.0006 |  -0.0011 |  -0.0001 |                  0.5194 |
| fig2 blend gbm - SP calibrated       | QLD     | 16991 | -0.0024 |  -0.0031 |  -0.0016 |                  0.5332 |
| fig2 blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0008 |   0.0002 |   0.0014 |                  0.5082 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   fig2 logit | fig2 logit 95%     |   fig2 gbm | fig2 gbm 95%       |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0008   |        -0.0018 | -0.0033 to -0.0004 |      -0.0030 | -0.0049 to -0.0012 |    -0.0021 | -0.0038 to -0.0005 |
| 2023 H2  |    5233 |           0.0000 | -0.0020 to +0.0020   |         0.0008 | -0.0007 to +0.0022 |       0.0001 | -0.0019 to +0.0021 |     0.0010 | -0.0006 to +0.0026 |
| 2024 H1  |    5145 |          -0.0016 | -0.0028 to -0.0002   |        -0.0010 | -0.0018 to -0.0001 |      -0.0014 | -0.0028 to -0.0001 |    -0.0012 | -0.0022 to -0.0002 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |        -0.0003 | -0.0011 to +0.0005 |      -0.0009 | -0.0022 to +0.0003 |    -0.0002 | -0.0012 to +0.0007 |
| 2025 H1  |    5065 |          -0.0010 | -0.0026 to +0.0006   |        -0.0008 | -0.0019 to +0.0004 |      -0.0009 | -0.0023 to +0.0006 |    -0.0005 | -0.0017 to +0.0006 |
| 2025 H2  |    5153 |          -0.0011 | -0.0027 to +0.0005   |        -0.0013 | -0.0024 to -0.0002 |      -0.0007 | -0.0023 to +0.0008 |    -0.0011 | -0.0023 to +0.0000 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0007 | -0.0022 to +0.0007 |      -0.0001 | -0.0014 to +0.0013 |    -0.0002 | -0.0015 to +0.0012 |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0009   |        -0.0009 | -0.0031 to +0.0013 |      -0.0014 | -0.0035 to +0.0008 |    -0.0009 | -0.0030 to +0.0014 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5239 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0027 |  -0.0042 |  -0.0011 |                  0.5212 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5261 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5091 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0026 |  -0.0040 |  -0.0011 |                  0.5282 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0002 |                  0.4935 |
| fig2 blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0012 |  -0.0019 |  -0.0005 |                  0.5230 |
| fig2 blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0026 |  -0.0041 |  -0.0010 |                  0.5216 |
| fig2 blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0001 |  -0.0004 |   0.0001 |                  0.5241 |
| fig2 blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0009 |  -0.0016 |  -0.0003 |                  0.5145 |
| fig2 blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0022 |  -0.0037 |  -0.0008 |                  0.5249 |
| fig2 blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0002 |                  0.5060 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5008 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5379 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0013 |  -0.0002 |                  0.4706 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5049 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0002 |  -0.0006 |   0.0010 |                  0.5387 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0007 |  -0.0013 |  -0.0001 |                  0.4772 |
| fig2 blend logit (per state) - fig2 blend logit (pooled weights)         | all     | 37821 | -0.0001 |  -0.0006 |   0.0003 |                  0.4997 |
| fig2 blend logit (per state) - fig2 blend logit (pooled weights)         | QLD     | 16991 |  0.0006 |  -0.0001 |   0.0013 |                  0.5337 |
| fig2 blend logit (per state) - fig2 blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0008 |  -0.0013 |  -0.0002 |                  0.4719 |
| fig2 blend gbm (per state) - fig2 blend gbm (pooled weights)             | all     | 37821 | -0.0002 |  -0.0007 |   0.0002 |                  0.5042 |
| fig2 blend gbm (per state) - fig2 blend gbm (pooled weights)             | QLD     | 16991 |  0.0005 |  -0.0003 |   0.0014 |                  0.5339 |
| fig2 blend gbm (per state) - fig2 blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0009 |  -0.0014 |  -0.0003 |                  0.4799 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0006 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   fig2 blend logit (per state) - SP calibrated (per state) | fig2 blend logit (per state) - SP calibrated (per state) 95%   |   fig2 blend gbm (per state) - SP calibrated (per state) | fig2 blend gbm (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0053 to -0.0005                                                 |                                                      -0.0027 | -0.0047 to -0.0004                                               |                                                    -0.0029 | -0.0052 to -0.0006                                             |                                                  -0.0026 | -0.0050 to -0.0002                                           |
| 2023 H2  |    5233 |                                                         0.0004 | -0.0022 to +0.0029                                                 |                                                       0.0008 | -0.0014 to +0.0031                                               |                                                     0.0006 | -0.0020 to +0.0032                                             |                                                   0.0006 | -0.0019 to +0.0030                                           |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0027 to +0.0002                                                 |                                                      -0.0001 | -0.0014 to +0.0012                                               |                                                    -0.0011 | -0.0026 to +0.0003                                             |                                                  -0.0001 | -0.0017 to +0.0014                                           |
| 2024 H2  |    5229 |                                                        -0.0018 | -0.0034 to -0.0002                                                 |                                                      -0.0016 | -0.0030 to -0.0003                                               |                                                    -0.0017 | -0.0031 to -0.0003                                             |                                                  -0.0015 | -0.0031 to -0.0000                                           |
| 2025 H1  |    5065 |                                                        -0.0012 | -0.0029 to +0.0005                                                 |                                                      -0.0012 | -0.0027 to +0.0003                                               |                                                    -0.0013 | -0.0030 to +0.0004                                             |                                                  -0.0008 | -0.0024 to +0.0007                                           |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0003                                                 |                                                      -0.0019 | -0.0034 to -0.0005                                               |                                                    -0.0017 | -0.0033 to +0.0000                                             |                                                  -0.0017 | -0.0033 to -0.0002                                           |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0011                                                 |                                                      -0.0012 | -0.0029 to +0.0006                                               |                                                    -0.0003 | -0.0019 to +0.0013                                             |                                                  -0.0006 | -0.0022 to +0.0010                                           |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0043 to +0.0011                                                 |                                                      -0.0009 | -0.0035 to +0.0020                                               |                                                    -0.0016 | -0.0042 to +0.0009                                             |                                                  -0.0009 | -0.0034 to +0.0016                                           |

## Variants vs baseline (paired by race)

| comparison                              | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:----------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| fig2 blend logit - baseline blend logit | all     | 37821 |  0.0001 |  -0.0001 |   0.0003 |                  0.4858 |
| fig2 blend logit - baseline blend logit | QLD     | 16991 |  0.0001 |  -0.0001 |   0.0004 |                  0.4781 |
| fig2 blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0003 |                  0.4920 |
| fig2 blend gbm - baseline blend gbm     | all     | 37821 |  0.0001 |  -0.0001 |   0.0003 |                  0.4972 |
| fig2 blend gbm - baseline blend gbm     | QLD     | 16991 |  0.0000 |  -0.0003 |   0.0003 |                  0.5011 |
| fig2 blend gbm - baseline blend gbm     | VIC/SA  | 20830 |  0.0002 |  -0.0001 |   0.0004 |                  0.4940 |
| fig2 model logit - baseline model logit | all     | 37821 | -0.0033 |  -0.0047 |  -0.0020 |                  0.5010 |
| fig2 model logit - baseline model logit | QLD     | 16991 | -0.0055 |  -0.0075 |  -0.0034 |                  0.5014 |
| fig2 model logit - baseline model logit | VIC/SA  | 20830 | -0.0016 |  -0.0034 |   0.0004 |                  0.5007 |
| fig2 model gbm - baseline model gbm     | all     | 37821 |  0.0007 |  -0.0014 |   0.0026 |                  0.4986 |
| fig2 model gbm - baseline model gbm     | QLD     | 16991 |  0.0000 |  -0.0029 |   0.0030 |                  0.5010 |
| fig2 model gbm - baseline model gbm     | VIC/SA  | 20830 |  0.0012 |  -0.0016 |   0.0039 |                  0.4966 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   fig2 blend logit - baseline blend logit | fig2 blend logit - baseline blend logit 95%   |   fig2 blend gbm - baseline blend gbm | fig2 blend gbm - baseline blend gbm 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|
| 2023 H1  |    5012 |                                   -0.0002 | -0.0007 to +0.0003                            |                               -0.0003 | -0.0010 to +0.0004                        |
| 2023 H2  |    5233 |                                    0.0001 | -0.0004 to +0.0006                            |                                0.0002 | -0.0005 to +0.0009                        |
| 2024 H1  |    5145 |                                    0.0002 | -0.0002 to +0.0005                            |                               -0.0002 | -0.0006 to +0.0002                        |
| 2024 H2  |    5229 |                                    0.0001 | -0.0003 to +0.0004                            |                                0.0001 | -0.0004 to +0.0005                        |
| 2025 H1  |    5065 |                                    0.0001 | -0.0003 to +0.0006                            |                                0.0003 | -0.0002 to +0.0008                        |
| 2025 H2  |    5153 |                                    0.0004 | -0.0000 to +0.0008                            |                                0.0001 | -0.0004 to +0.0007                        |
| 2026 H1  |    4992 |                                    0.0001 | -0.0003 to +0.0006                            |                                0.0005 | -0.0000 to +0.0012                        |
| 2026 H2  |    1992 |                                   -0.0000 | -0.0007 to +0.0006                            |                                0.0001 | -0.0009 to +0.0011                        |

## Figure v2 weights by training cut-off (WPR points per unit)

|              |   2023-01-01 |   2024-01-01 |   2025-01-01 |   2026-01-01 |
|:-------------|-------------:|-------------:|-------------:|-------------:|
| wpr          |        1.000 |        1.000 |        1.000 |        1.000 |
| s_early      |       -0.190 |       -0.190 |       -0.187 |       -0.175 |
| s_l600       |       -0.146 |       -0.147 |       -0.151 |       -0.165 |
| wt_rel       |        0.379 |        0.396 |        0.387 |        0.377 |
| settle       |        0.281 |        0.130 |        0.172 |        0.312 |
| shape        |        0.064 |        0.062 |        0.064 |        0.043 |
| pace         |        0.181 |        0.194 |        0.190 |        0.188 |
| s_early_miss |       -1.485 |       -1.961 |       -1.938 |       -1.969 |
| prelim       |       -0.000 |       -0.003 |       -0.154 |       -0.492 |
| far_beaten   |        0.824 |        0.819 |        0.817 |        0.794 |
| heavy        |        0.444 |        0.551 |        0.688 |        0.728 |
| loc_p        |       -4.261 |       -4.403 |       -4.320 |       -4.335 |
| loc_c        |       -6.239 |       -6.414 |       -6.376 |       -6.426 |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   fig2 logit a |   fig2 logit b |   fig2 logit a, QLD |   fig2 logit b, QLD |   fig2 logit a, VIC/SA |   fig2 logit b, VIC/SA |   fig2 gbm a |   fig2 gbm b |   fig2 gbm a, QLD |   fig2 gbm b, QLD |   fig2 gbm a, VIC/SA |   fig2 gbm b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.261 |                   1.049 |                      0.051 |                      1.132 |            0.120 |            1.106 |                 0.260 |                 1.046 |                    0.016 |                    1.155 |          0.147 |          1.089 |               0.267 |               1.040 |                  0.041 |                  1.138 |        0.131 |        1.097 |             0.277 |             1.033 |                0.023 |                1.150 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.102 |              1.042 |                   0.160 |                   1.031 |                      0.023 |                      1.066 |            0.068 |            1.062 |                 0.155 |                 1.034 |                   -0.034 |                    1.104 |          0.100 |          1.041 |               0.161 |               1.028 |                  0.020 |                  1.068 |        0.084 |        1.049 |             0.184 |             1.007 |               -0.032 |                1.103 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.117 |              1.076 |                   0.181 |                   1.037 |                      0.045 |                      1.116 |            0.094 |            1.086 |                 0.185 |                 1.028 |                   -0.001 |                    1.147 |          0.114 |          1.077 |               0.178 |               1.038 |                  0.043 |                  1.116 |        0.097 |        1.083 |             0.185 |             1.028 |                0.008 |                1.140 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.109 |              1.045 |                   0.171 |                   0.987 |                      0.052 |                      1.091 |            0.117 |            1.032 |                 0.195 |                 0.961 |                    0.048 |                    1.090 |          0.099 |          1.050 |               0.176 |               0.982 |                  0.031 |                  1.104 |        0.110 |        1.037 |             0.188 |             0.966 |                0.042 |                1.094 |
