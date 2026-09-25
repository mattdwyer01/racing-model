# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prodmu (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples
- Dropped 254 races with a missing model output (12 Sep 2026 to 23 Sep 2026; inputs such as carried weight not yet in TopRate)

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                             | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                     |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)         |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit             |     1.9339 |     1.9307 |     1.9348 |    1.9328 |     1.9331 |
| baseline: blend logit             |     1.7907 |     1.7872 |     1.7844 |    1.7752 |     1.7852 |
| baseline: blend logit (per state) |     1.7910 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| prodmu: model logit               |     1.9247 |     1.9215 |     1.9275 |    1.9228 |     1.9242 |
| prodmu: blend logit               |     1.7904 |     1.7868 |     1.7846 |    1.7751 |     1.7850 |
| prodmu: blend logit (per state)   |     1.7908 |     1.7866 |     1.7841 |    1.7748 |     1.7849 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5946 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5998 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5904 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5237 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5339 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5153 |
| prodmu blend logit - SP raw          | all     | 37821 | -0.0050 |  -0.0062 |  -0.0037 |                  0.5882 |
| prodmu blend logit - SP raw          | QLD     | 16991 | -0.0075 |  -0.0095 |  -0.0055 |                  0.5958 |
| prodmu blend logit - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0012 |                  0.5821 |
| prodmu blend logit - SP calibrated   | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5220 |
| prodmu blend logit - SP calibrated   | QLD     | 16991 | -0.0036 |  -0.0047 |  -0.0025 |                  0.5331 |
| prodmu blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0006 |  -0.0004 |   0.0016 |                  0.5130 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   prodmu logit | prodmu logit 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0048 to -0.0008   |        -0.0034 | -0.0058 to -0.0011 |
| 2023 H2  |    5233 |           0.0001 | -0.0019 to +0.0019   |        -0.0001 | -0.0025 to +0.0025 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0002   |        -0.0020 | -0.0037 to -0.0002 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |        -0.0015 | -0.0032 to +0.0003 |
| 2025 H1  |    5065 |          -0.0011 | -0.0026 to +0.0005   |        -0.0012 | -0.0032 to +0.0008 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |        -0.0006 | -0.0026 to +0.0014 |
| 2026 H1  |    4992 |          -0.0002 | -0.0016 to +0.0013   |        -0.0002 | -0.0019 to +0.0014 |
| 2026 H2  |    1992 |          -0.0014 | -0.0035 to +0.0010   |        -0.0017 | -0.0043 to +0.0007 |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5236 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0027 |  -0.0042 |  -0.0011 |                  0.5213 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5255 |
| prodmu blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5215 |
| prodmu blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0030 |  -0.0047 |  -0.0013 |                  0.5226 |
| prodmu blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0002 |                  0.5205 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5002 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5375 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4698 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5003 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | QLD     | 16991 |  0.0009 |   0.0003 |   0.0016 |                  0.5322 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4743 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   prodmu blend logit (per state) - SP calibrated (per state) | prodmu blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0005                                                 |                                                      -0.0033 | -0.0060 to -0.0004                                               |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0031                                                 |                                                       0.0005 | -0.0025 to +0.0032                                               |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0001                                                 |                                                      -0.0017 | -0.0034 to +0.0002                                               |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0033 to -0.0001                                                 |                                                      -0.0022 | -0.0040 to -0.0003                                               |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0029 to +0.0006                                                 |                                                      -0.0015 | -0.0035 to +0.0005                                               |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0038 to -0.0004                                                 |                                                      -0.0015 | -0.0036 to +0.0005                                               |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0012                                                 |                                                      -0.0006 | -0.0025 to +0.0012                                               |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0040 to +0.0011                                                 |                                                      -0.0019 | -0.0047 to +0.0009                                               |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prodmu blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0004 |   0.0001 |                  0.5066 |
| prodmu blend logit - baseline blend logit | QLD     | 16991 | -0.0006 |  -0.0011 |  -0.0002 |                  0.5197 |
| prodmu blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0001 |   0.0006 |                  0.4960 |
| prodmu model logit - baseline model logit | all     | 37821 | -0.0088 |  -0.0106 |  -0.0070 |                  0.5211 |
| prodmu model logit - baseline model logit | QLD     | 16991 | -0.0102 |  -0.0131 |  -0.0076 |                  0.5239 |
| prodmu model logit - baseline model logit | VIC/SA  | 20830 | -0.0077 |  -0.0101 |  -0.0054 |                  0.5189 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prodmu blend logit - baseline blend logit | prodmu blend logit - baseline blend logit 95%   |
|:---------|--------:|--------------------------------------------:|:------------------------------------------------|
| 2023 H1  |    5012 |                                     -0.0006 | -0.0014 to +0.0004                              |
| 2023 H2  |    5233 |                                     -0.0001 | -0.0010 to +0.0009                              |
| 2024 H1  |    5145 |                                     -0.0003 | -0.0011 to +0.0003                              |
| 2024 H2  |    5229 |                                     -0.0005 | -0.0012 to +0.0002                              |
| 2025 H1  |    5065 |                                     -0.0002 | -0.0009 to +0.0005                              |
| 2025 H2  |    5153 |                                      0.0006 | -0.0001 to +0.0013                              |
| 2026 H1  |    4992 |                                     -0.0000 | -0.0005 to +0.0006                              |
| 2026 H2  |    1992 |                                     -0.0004 | -0.0013 to +0.0005                              |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   prodmu logit a |   prodmu logit b |   prodmu logit a, QLD |   prodmu logit b, QLD |   prodmu logit a, VIC/SA |   prodmu logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.262 |                   1.048 |                      0.049 |                      1.134 |            0.184 |            1.063 |                 0.291 |                 1.020 |                    0.087 |                    1.107 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.102 |              1.041 |                   0.160 |                   1.030 |                      0.023 |                      1.066 |            0.137 |            1.013 |                 0.194 |                 0.998 |                    0.060 |                    1.041 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.180 |                   1.038 |                      0.047 |                      1.114 |            0.148 |            1.049 |                 0.206 |                 1.013 |                    0.083 |                    1.088 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.987 |                      0.051 |                      1.092 |            0.120 |            1.033 |                 0.187 |                 0.969 |                    0.059 |                    1.085 |
