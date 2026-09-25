# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prodmu (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples
- Dropped 1 races with a missing model output (19 Sep 2026 to 19 Sep 2026; inputs such as carried weight not yet in TopRate)

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                             | 10245.0000 | 10374.0000 | 10218.0000 | 7237.0000 | 38074.0000 |
| SP raw                            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7899 |
| SP calibrated                     |     1.7920 |     1.7885 |     1.7856 |    1.7758 |     1.7862 |
| SP calibrated (per state)         |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7863 |
| baseline: model logit             |     1.9372 |     1.9334 |     1.9368 |    1.9345 |     1.9355 |
| baseline: blend logit             |     1.7910 |     1.7873 |     1.7845 |    1.7751 |     1.7852 |
| baseline: blend logit (per state) |     1.7914 |     1.7872 |     1.7841 |    1.7749 |     1.7851 |
| prodmu: model logit               |     1.9279 |     1.9237 |     1.9298 |    1.9254 |     1.9268 |
| prodmu: blend logit               |     1.7908 |     1.7869 |     1.7847 |    1.7750 |     1.7851 |
| prodmu: blend logit (per state)   |     1.7911 |     1.7867 |     1.7842 |    1.7748 |     1.7850 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 38074 | -0.0047 |  -0.0058 |  -0.0035 |                  0.5968 |
| baseline blend logit - SP raw        | QLD     | 17105 | -0.0066 |  -0.0083 |  -0.0048 |                  0.6014 |
| baseline blend logit - SP raw        | VIC/SA  | 20969 | -0.0031 |  -0.0046 |  -0.0016 |                  0.5931 |
| baseline blend logit - SP calibrated | all     | 38074 | -0.0010 |  -0.0015 |  -0.0005 |                  0.5222 |
| baseline blend logit - SP calibrated | QLD     | 17105 | -0.0026 |  -0.0034 |  -0.0017 |                  0.5304 |
| baseline blend logit - SP calibrated | VIC/SA  | 20969 |  0.0003 |  -0.0004 |   0.0011 |                  0.5156 |
| prodmu blend logit - SP raw          | all     | 38074 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5897 |
| prodmu blend logit - SP raw          | QLD     | 17105 | -0.0071 |  -0.0090 |  -0.0052 |                  0.5957 |
| prodmu blend logit - SP raw          | VIC/SA  | 20969 | -0.0030 |  -0.0046 |  -0.0014 |                  0.5848 |
| prodmu blend logit - SP calibrated   | all     | 38074 | -0.0011 |  -0.0018 |  -0.0004 |                  0.5226 |
| prodmu blend logit - SP calibrated   | QLD     | 17105 | -0.0031 |  -0.0042 |  -0.0020 |                  0.5333 |
| prodmu blend logit - SP calibrated   | VIC/SA  | 20969 |  0.0005 |  -0.0004 |   0.0014 |                  0.5139 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   prodmu logit | prodmu logit 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0023 | -0.0041 to -0.0004   |        -0.0026 | -0.0048 to -0.0005 |
| 2023 H2  |    5233 |           0.0003 | -0.0015 to +0.0020   |         0.0001 | -0.0021 to +0.0023 |
| 2024 H1  |    5145 |          -0.0013 | -0.0025 to -0.0001   |        -0.0017 | -0.0033 to -0.0000 |
| 2024 H2  |    5229 |          -0.0010 | -0.0022 to +0.0002   |        -0.0015 | -0.0031 to +0.0003 |
| 2025 H1  |    5065 |          -0.0009 | -0.0025 to +0.0006   |        -0.0012 | -0.0031 to +0.0009 |
| 2025 H2  |    5153 |          -0.0012 | -0.0028 to +0.0003   |        -0.0006 | -0.0025 to +0.0013 |
| 2026 H1  |    4992 |          -0.0001 | -0.0016 to +0.0013   |        -0.0001 | -0.0017 to +0.0014 |
| 2026 H2  |    2245 |          -0.0018 | -0.0039 to +0.0002   |        -0.0020 | -0.0043 to +0.0004 |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 38074 | -0.0012 |  -0.0018 |  -0.0005 |                  0.5224 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 17105 | -0.0024 |  -0.0038 |  -0.0010 |                  0.5163 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20969 | -0.0002 |  -0.0004 |   0.0001 |                  0.5273 |
| prodmu blend logit (per state) - SP calibrated (per state)               | all     | 38074 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5231 |
| prodmu blend logit (per state) - SP calibrated (per state)               | QLD     | 17105 | -0.0027 |  -0.0043 |  -0.0010 |                  0.5232 |
| prodmu blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20969 | -0.0002 |  -0.0007 |   0.0002 |                  0.5230 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 38074 | -0.0001 |  -0.0005 |   0.0003 |                  0.5001 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 17105 |  0.0006 |  -0.0000 |   0.0012 |                  0.5367 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20969 | -0.0006 |  -0.0012 |  -0.0002 |                  0.4703 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | all     | 38074 | -0.0001 |  -0.0005 |   0.0002 |                  0.4999 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | QLD     | 17105 |  0.0008 |   0.0002 |   0.0013 |                  0.5343 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | VIC/SA  | 20969 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4719 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 38074 |  0.0001 |  -0.0001 |   0.0002 |                  0.4947 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 17105 |  0.0004 |   0.0001 |   0.0007 |                  0.5537 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20969 | -0.0002 |  -0.0004 |   0.0000 |                  0.4465 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   prodmu blend logit (per state) - SP calibrated (per state) | prodmu blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0022 | -0.0043 to -0.0001                                                 |                                                      -0.0025 | -0.0051 to -0.0000                                               |
| 2023 H2  |    5233 |                                                         0.0007 | -0.0017 to +0.0030                                                 |                                                       0.0004 | -0.0024 to +0.0031                                               |
| 2024 H1  |    5145 |                                                        -0.0010 | -0.0022 to +0.0003                                                 |                                                      -0.0014 | -0.0031 to +0.0003                                               |
| 2024 H2  |    5229 |                                                        -0.0016 | -0.0029 to -0.0003                                                 |                                                      -0.0021 | -0.0037 to -0.0003                                               |
| 2025 H1  |    5065 |                                                        -0.0012 | -0.0027 to +0.0004                                                 |                                                      -0.0015 | -0.0035 to +0.0005                                               |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0036 to -0.0004                                                 |                                                      -0.0014 | -0.0034 to +0.0006                                               |
| 2026 H1  |    4992 |                                                        -0.0004 | -0.0019 to +0.0013                                                 |                                                      -0.0004 | -0.0021 to +0.0013                                               |
| 2026 H2  |    2245 |                                                        -0.0022 | -0.0046 to +0.0003                                                 |                                                      -0.0024 | -0.0049 to +0.0002                                               |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prodmu blend logit - baseline blend logit | all     | 38074 | -0.0002 |  -0.0004 |   0.0001 |                  0.5059 |
| prodmu blend logit - baseline blend logit | QLD     | 17105 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5195 |
| prodmu blend logit - baseline blend logit | VIC/SA  | 20969 |  0.0002 |  -0.0002 |   0.0005 |                  0.4949 |
| prodmu model logit - baseline model logit | all     | 38074 | -0.0087 |  -0.0104 |  -0.0071 |                  0.5207 |
| prodmu model logit - baseline model logit | QLD     | 17105 | -0.0097 |  -0.0122 |  -0.0072 |                  0.5265 |
| prodmu model logit - baseline model logit | VIC/SA  | 20969 | -0.0079 |  -0.0102 |  -0.0055 |                  0.5160 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prodmu blend logit - baseline blend logit | prodmu blend logit - baseline blend logit 95%   |
|:---------|--------:|--------------------------------------------:|:------------------------------------------------|
| 2023 H1  |    5012 |                                     -0.0004 | -0.0012 to +0.0004                              |
| 2023 H2  |    5233 |                                     -0.0002 | -0.0010 to +0.0006                              |
| 2024 H1  |    5145 |                                     -0.0004 | -0.0011 to +0.0003                              |
| 2024 H2  |    5229 |                                     -0.0005 | -0.0011 to +0.0002                              |
| 2025 H1  |    5065 |                                     -0.0002 | -0.0010 to +0.0005                              |
| 2025 H2  |    5153 |                                      0.0006 | -0.0001 to +0.0014                              |
| 2026 H1  |    4992 |                                     -0.0000 | -0.0005 to +0.0005                              |
| 2026 H2  |    2245 |                                     -0.0002 | -0.0009 to +0.0006                              |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   prodmu logit a |   prodmu logit b |   prodmu logit a, QLD |   prodmu logit b, QLD |   prodmu logit a, VIC/SA |   prodmu logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.140 |              1.097 |                   0.245 |                   1.059 |                      0.042 |                      1.138 |            0.172 |            1.072 |                 0.266 |                 1.037 |                    0.086 |                    1.109 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.092 |              1.049 |                   0.142 |                   1.044 |                      0.022 |                      1.067 |            0.129 |            1.020 |                 0.176 |                 1.013 |                    0.063 |                    1.039 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.114 |              1.079 |                   0.171 |                   1.045 |                      0.048 |                      1.114 |            0.144 |            1.054 |                 0.195 |                 1.022 |                    0.086 |                    1.086 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.106 |              1.047 |                   0.170 |                   0.989 |                      0.048 |                      1.093 |            0.117 |            1.036 |                 0.184 |                 0.973 |                    0.057 |                    1.086 |
