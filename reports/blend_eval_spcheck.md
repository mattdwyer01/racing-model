# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, lv (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                        |       2023 |       2024 |       2025 |      2026 |     pooled |
|:---------------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                                  | 10245.0000 | 10374.0000 | 10218.0000 | 7473.0000 | 38310.0000 |
| SP raw                                 |     1.7934 |     1.7934 |     1.7891 |    1.7789 |     1.7894 |
| SP calibrated                          |     1.7920 |     1.7885 |     1.7856 |    1.7735 |     1.7857 |
| SP calibrated (SP-checked fit)         |     1.7920 |     1.7885 |     1.7856 |    1.7735 |     1.7857 |
| sp_ok                                  |     0.9926 |     0.9943 |     0.9940 |    0.9950 |     0.9939 |
| SP calibrated (per state)              |     1.7921 |     1.7885 |     1.7857 |    1.7735 |     1.7858 |
| baseline: model logit                  |     1.9340 |     1.9306 |     1.9348 |    1.9300 |     1.9325 |
| baseline: blend logit                  |     1.7907 |     1.7872 |     1.7844 |    1.7727 |     1.7846 |
| baseline: blend logit (SP-checked fit) |     1.7906 |     1.7872 |     1.7845 |    1.7727 |     1.7845 |
| baseline: blend logit (per state)      |     1.7911 |     1.7870 |     1.7841 |    1.7724 |     1.7844 |
| lv: model logit                        |     1.9242 |     1.9204 |     1.9271 |    1.9196 |     1.9230 |
| lv: blend logit                        |     1.7903 |     1.7866 |     1.7846 |    1.7726 |     1.7843 |
| lv: blend logit (SP-checked fit)       |     1.7902 |     1.7866 |     1.7847 |    1.7725 |     1.7843 |
| lv: blend logit (per state)            |     1.7906 |     1.7864 |     1.7841 |    1.7721 |     1.7841 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 38310 | -0.0049 |  -0.0061 |  -0.0036 |                  0.5942 |
| baseline blend logit - SP raw        | QLD     | 17228 | -0.0070 |  -0.0088 |  -0.0052 |                  0.6001 |
| baseline blend logit - SP raw        | VIC/SA  | 21082 | -0.0031 |  -0.0046 |  -0.0014 |                  0.5894 |
| baseline blend logit - SP calibrated | all     | 38310 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5241 |
| baseline blend logit - SP calibrated | QLD     | 17228 | -0.0030 |  -0.0040 |  -0.0021 |                  0.5343 |
| baseline blend logit - SP calibrated | VIC/SA  | 21082 |  0.0004 |  -0.0004 |   0.0011 |                  0.5157 |
| lv blend logit - SP raw              | all     | 38310 | -0.0051 |  -0.0064 |  -0.0038 |                  0.5878 |
| lv blend logit - SP raw              | QLD     | 17228 | -0.0078 |  -0.0098 |  -0.0058 |                  0.5955 |
| lv blend logit - SP raw              | VIC/SA  | 21082 | -0.0029 |  -0.0047 |  -0.0012 |                  0.5815 |
| lv blend logit - SP calibrated       | all     | 38310 | -0.0014 |  -0.0022 |  -0.0006 |                  0.5234 |
| lv blend logit - SP calibrated       | QLD     | 17228 | -0.0037 |  -0.0049 |  -0.0026 |                  0.5369 |
| lv blend logit - SP calibrated       | VIC/SA  | 21082 |  0.0005 |  -0.0004 |   0.0014 |                  0.5124 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   lv logit | lv logit 95%       |
|:---------|--------:|-----------------:|:---------------------|-----------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0010   |    -0.0034 | -0.0057 to -0.0010 |
| 2023 H2  |    5233 |           0.0001 | -0.0019 to +0.0021   |    -0.0002 | -0.0025 to +0.0022 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |    -0.0022 | -0.0039 to -0.0003 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |    -0.0016 | -0.0035 to +0.0002 |
| 2025 H1  |    5065 |          -0.0011 | -0.0026 to +0.0005   |    -0.0013 | -0.0034 to +0.0009 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |    -0.0005 | -0.0026 to +0.0015 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |    -0.0003 | -0.0019 to +0.0014 |
| 2026 H2  |    2481 |          -0.0018 | -0.0038 to +0.0003   |    -0.0021 | -0.0044 to +0.0002 |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 38310 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5241 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 17228 | -0.0027 |  -0.0043 |  -0.0013 |                  0.5221 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 21082 | -0.0002 |  -0.0005 |   0.0001 |                  0.5258 |
| lv blend logit (per state) - SP calibrated (per state)                   | all     | 38310 | -0.0017 |  -0.0025 |  -0.0008 |                  0.5229 |
| lv blend logit (per state) - SP calibrated (per state)                   | QLD     | 17228 | -0.0033 |  -0.0050 |  -0.0015 |                  0.5255 |
| lv blend logit (per state) - SP calibrated (per state)                   | VIC/SA  | 21082 | -0.0003 |  -0.0008 |   0.0002 |                  0.5209 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 38310 | -0.0001 |  -0.0005 |   0.0003 |                  0.5012 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 17228 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 21082 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4710 |
| lv blend logit (per state) - lv blend logit (pooled weights)             | all     | 38310 | -0.0002 |  -0.0006 |   0.0002 |                  0.5005 |
| lv blend logit (per state) - lv blend logit (pooled weights)             | QLD     | 17228 |  0.0008 |   0.0002 |   0.0015 |                  0.5333 |
| lv blend logit (per state) - lv blend logit (pooled weights)             | VIC/SA  | 21082 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4737 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 38310 |  0.0001 |  -0.0001 |   0.0002 |                  0.4946 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 17228 |  0.0004 |   0.0001 |   0.0006 |                  0.5523 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 21082 | -0.0002 |  -0.0004 |   0.0000 |                  0.4474 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   lv blend logit (per state) - SP calibrated (per state) | lv blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0003                                                 |                                                  -0.0033 | -0.0061 to -0.0006                                           |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0019 to +0.0030                                                 |                                                   0.0002 | -0.0027 to +0.0028                                           |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0002                                                 |                                                  -0.0019 | -0.0037 to +0.0000                                           |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0032 to -0.0001                                                 |                                                  -0.0023 | -0.0042 to -0.0003                                           |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0005                                                 |                                                  -0.0016 | -0.0037 to +0.0006                                           |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0004                                                 |                                                  -0.0015 | -0.0036 to +0.0006                                           |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0021 to +0.0011                                                 |                                                  -0.0007 | -0.0026 to +0.0012                                           |
| 2026 H2  |    2481 |                                                        -0.0022 | -0.0045 to +0.0000                                                 |                                                  -0.0027 | -0.0052 to -0.0001                                           |

## Variants vs baseline (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| lv blend logit - baseline blend logit | all     | 38310 | -0.0002 |  -0.0005 |   0.0000 |                  0.5099 |
| lv blend logit - baseline blend logit | QLD     | 17228 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5232 |
| lv blend logit - baseline blend logit | VIC/SA  | 21082 |  0.0002 |  -0.0002 |   0.0005 |                  0.4991 |
| lv model logit - baseline model logit | all     | 38310 | -0.0095 |  -0.0112 |  -0.0079 |                  0.5222 |
| lv model logit - baseline model logit | QLD     | 17228 | -0.0113 |  -0.0138 |  -0.0089 |                  0.5294 |
| lv model logit - baseline model logit | VIC/SA  | 21082 | -0.0080 |  -0.0103 |  -0.0057 |                  0.5164 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   lv blend logit - baseline blend logit | lv blend logit - baseline blend logit 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|
| 2023 H1  |    5012 |                                 -0.0006 | -0.0014 to +0.0003                          |
| 2023 H2  |    5233 |                                 -0.0003 | -0.0012 to +0.0006                          |
| 2024 H1  |    5145 |                                 -0.0006 | -0.0013 to +0.0002                          |
| 2024 H2  |    5229 |                                 -0.0006 | -0.0013 to +0.0001                          |
| 2025 H1  |    5065 |                                 -0.0003 | -0.0010 to +0.0005                          |
| 2025 H2  |    5153 |                                  0.0006 | -0.0001 to +0.0014                          |
| 2026 H1  |    4992 |                                 -0.0001 | -0.0006 to +0.0004                          |
| 2026 H2  |    2481 |                                 -0.0003 | -0.0011 to +0.0005                          |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, SP-checked |   baseline logit b, SP-checked |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   lv logit a |   lv logit b |   lv logit a, SP-checked |   lv logit b, SP-checked |   lv logit a, QLD |   lv logit b, QLD |   lv logit a, VIC/SA |   lv logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|-------------------------------:|-------------------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-------------:|-------------:|-------------------------:|-------------------------:|------------------:|------------------:|---------------------:|---------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                          0.148 |                          1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |        0.185 |        1.062 |                    0.184 |                    1.060 |             0.292 |             1.018 |                0.088 |                1.107 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                          0.099 |                          1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |        0.139 |        1.012 |                    0.137 |                    1.013 |             0.195 |             0.998 |                0.064 |                1.038 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                          0.120 |                          1.074 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |        0.153 |        1.046 |                    0.153 |                    1.047 |             0.212 |             1.009 |                0.087 |                1.085 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                          0.104 |                          1.049 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |        0.122 |        1.032 |                    0.117 |                    1.036 |             0.191 |             0.967 |                0.060 |                1.084 |
