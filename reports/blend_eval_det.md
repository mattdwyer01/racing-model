# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                             | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                     |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)         |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit             |     1.9338 |     1.9308 |     1.9352 |    1.9328 |     1.9331 |
| baseline: blend logit             |     1.7906 |     1.7872 |     1.7845 |    1.7752 |     1.7852 |
| baseline: blend logit (per state) |     1.7910 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| baseline: model gbm               |     1.9179 |     1.9108 |     1.9039 |    1.8994 |     1.9087 |
| baseline: blend gbm               |     1.7914 |     1.7878 |     1.7845 |    1.7752 |     1.7856 |
| baseline: blend gbm (per state)   |     1.7910 |     1.7877 |     1.7841 |    1.7749 |     1.7853 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5949 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.6007 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5902 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5237 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5331 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0004 |  -0.0004 |   0.0011 |                  0.5160 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0032 |                  0.5957 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0063 |  -0.0078 |  -0.0046 |                  0.6020 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0044 |  -0.0013 |                  0.5906 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5201 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0023 |  -0.0029 |  -0.0016 |                  0.5362 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0006 |   0.0000 |   0.0011 |                  0.5070 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0048 to -0.0008   |        -0.0019 | -0.0031 to -0.0006 |
| 2023 H2  |    5233 |           0.0000 | -0.0020 to +0.0019   |         0.0007 | -0.0006 to +0.0019 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0002   |        -0.0010 | -0.0018 to -0.0002 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0002   |        -0.0003 | -0.0011 to +0.0004 |
| 2025 H1  |    5065 |          -0.0010 | -0.0026 to +0.0005   |        -0.0008 | -0.0019 to +0.0003 |
| 2025 H2  |    5153 |          -0.0011 | -0.0026 to +0.0004   |        -0.0013 | -0.0024 to -0.0002 |
| 2026 H1  |    4992 |          -0.0002 | -0.0016 to +0.0013   |        -0.0004 | -0.0018 to +0.0009 |
| 2026 H2  |    1992 |          -0.0014 | -0.0035 to +0.0009   |        -0.0009 | -0.0034 to +0.0015 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5236 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0027 |  -0.0042 |  -0.0012 |                  0.5204 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5262 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5058 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0025 |  -0.0038 |  -0.0012 |                  0.5269 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0002 |                  0.4886 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5010 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4707 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5050 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0001 |  -0.0006 |   0.0009 |                  0.5400 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0006 |  -0.0012 |  -0.0001 |                  0.4764 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0006                                                 |                                                      -0.0028 | -0.0050 to -0.0007                                               |
| 2023 H2  |    5233 |                                                         0.0004 | -0.0020 to +0.0030                                                 |                                                       0.0006 | -0.0016 to +0.0028                                               |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0002                                                 |                                                      -0.0000 | -0.0012 to +0.0012                                               |
| 2024 H2  |    5229 |                                                        -0.0018 | -0.0033 to -0.0002                                                 |                                                      -0.0016 | -0.0028 to -0.0002                                               |
| 2025 H1  |    5065 |                                                        -0.0012 | -0.0029 to +0.0006                                                 |                                                      -0.0012 | -0.0026 to +0.0004                                               |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0038 to -0.0004                                                 |                                                      -0.0019 | -0.0034 to -0.0003                                               |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0021 to +0.0012                                                 |                                                      -0.0009 | -0.0026 to +0.0008                                               |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0041 to +0.0010                                                 |                                                      -0.0006 | -0.0033 to +0.0021                                               |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.261 |                   1.049 |                      0.051 |                      1.132 |            0.103 |            1.118 |                 0.246 |                 1.059 |                   -0.002 |                    1.168 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.159 |                   1.031 |                      0.023 |                      1.066 |            0.066 |            1.063 |                 0.147 |                 1.038 |                   -0.030 |                    1.102 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.117 |              1.076 |                   0.181 |                   1.037 |                      0.045 |                      1.116 |            0.090 |            1.089 |                 0.183 |                 1.030 |                   -0.007 |                    1.151 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.109 |              1.045 |                   0.172 |                   0.987 |                      0.052 |                      1.091 |            0.123 |            1.028 |                 0.202 |                 0.957 |                    0.052 |                    1.087 |
