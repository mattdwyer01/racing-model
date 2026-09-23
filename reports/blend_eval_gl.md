# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, gl (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                       |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                 | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated         |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| baseline: model logit |     1.9338 |     1.9308 |     1.9352 |    1.9328 |     1.9332 |
| baseline: blend logit |     1.7907 |     1.7872 |     1.7845 |    1.7752 |     1.7852 |
| baseline: model gbm   |     1.9186 |     1.9104 |     1.9045 |    1.8981 |     1.9087 |
| baseline: blend gbm   |     1.7916 |     1.7878 |     1.7846 |    1.7750 |     1.7856 |
| gl: model logit       |     1.9349 |     1.9298 |     1.9346 |    1.9313 |     1.9327 |
| gl: blend logit       |     1.7905 |     1.7871 |     1.7845 |    1.7751 |     1.7851 |
| gl: model gbm         |     1.9193 |     1.9093 |     1.9049 |    1.8942 |     1.9080 |
| gl: blend gbm         |     1.7914 |     1.7877 |     1.7847 |    1.7747 |     1.7855 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5948 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.6004 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5903 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5238 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5329 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0004 |  -0.0004 |   0.0011 |                  0.5165 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0032 |                  0.5940 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0064 |  -0.0080 |  -0.0047 |                  0.6000 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0027 |  -0.0043 |  -0.0011 |                  0.5890 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0007 |  -0.0011 |  -0.0002 |                  0.5203 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0024 |  -0.0031 |  -0.0017 |                  0.5350 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0007 |   0.0001 |   0.0013 |                  0.5083 |
| gl blend logit - SP raw              | all     | 37821 | -0.0049 |  -0.0061 |  -0.0037 |                  0.5964 |
| gl blend logit - SP raw              | QLD     | 16991 | -0.0070 |  -0.0087 |  -0.0051 |                  0.6030 |
| gl blend logit - SP raw              | VIC/SA  | 20830 | -0.0031 |  -0.0047 |  -0.0016 |                  0.5910 |
| gl blend logit - SP calibrated       | all     | 37821 | -0.0012 |  -0.0018 |  -0.0006 |                  0.5254 |
| gl blend logit - SP calibrated       | QLD     | 16991 | -0.0030 |  -0.0039 |  -0.0022 |                  0.5373 |
| gl blend logit - SP calibrated       | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0010 |                  0.5157 |
| gl blend gbm - SP raw                | all     | 37821 | -0.0045 |  -0.0055 |  -0.0033 |                  0.5954 |
| gl blend gbm - SP raw                | QLD     | 16991 | -0.0064 |  -0.0080 |  -0.0048 |                  0.6023 |
| gl blend gbm - SP raw                | VIC/SA  | 20830 | -0.0029 |  -0.0044 |  -0.0013 |                  0.5899 |
| gl blend gbm - SP calibrated         | all     | 37821 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5203 |
| gl blend gbm - SP calibrated         | QLD     | 16991 | -0.0024 |  -0.0031 |  -0.0017 |                  0.5360 |
| gl blend gbm - SP calibrated         | VIC/SA  | 20830 |  0.0005 |  -0.0001 |   0.0010 |                  0.5076 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   gl logit | gl logit 95%       |   gl gbm | gl gbm 95%         |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-----------:|:-------------------|---------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0008   |        -0.0019 | -0.0034 to -0.0004 |    -0.0027 | -0.0042 to -0.0011 |  -0.0018 | -0.0031 to -0.0006 |
| 2023 H2  |    5233 |           0.0000 | -0.0020 to +0.0019   |         0.0010 | -0.0006 to +0.0025 |    -0.0004 | -0.0020 to +0.0012 |   0.0006 | -0.0007 to +0.0019 |
| 2024 H1  |    5145 |          -0.0016 | -0.0028 to -0.0003   |        -0.0010 | -0.0018 to -0.0002 |    -0.0016 | -0.0029 to -0.0002 |  -0.0010 | -0.0019 to -0.0002 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |        -0.0003 | -0.0011 to +0.0004 |    -0.0011 | -0.0024 to +0.0002 |  -0.0004 | -0.0012 to +0.0004 |
| 2025 H1  |    5065 |          -0.0010 | -0.0026 to +0.0006   |        -0.0007 | -0.0019 to +0.0005 |    -0.0009 | -0.0025 to +0.0006 |  -0.0006 | -0.0018 to +0.0005 |
| 2025 H2  |    5153 |          -0.0011 | -0.0027 to +0.0005   |        -0.0012 | -0.0024 to -0.0001 |    -0.0012 | -0.0028 to +0.0005 |  -0.0011 | -0.0023 to -0.0000 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0006 | -0.0021 to +0.0008 |    -0.0003 | -0.0018 to +0.0011 |  -0.0009 | -0.0024 to +0.0005 |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0009   |        -0.0009 | -0.0032 to +0.0014 |    -0.0014 | -0.0037 to +0.0009 |  -0.0014 | -0.0036 to +0.0011 |

## Variants vs baseline (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| gl blend logit - baseline blend logit | all     | 37821 | -0.0001 |  -0.0002 |   0.0000 |                  0.4623 |
| gl blend logit - baseline blend logit | QLD     | 16991 | -0.0001 |  -0.0003 |   0.0001 |                  0.4678 |
| gl blend logit - baseline blend logit | VIC/SA  | 20830 | -0.0001 |  -0.0001 |   0.0000 |                  0.4578 |
| gl blend gbm - baseline blend gbm     | all     | 37821 | -0.0001 |  -0.0002 |  -0.0000 |                  0.4975 |
| gl blend gbm - baseline blend gbm     | QLD     | 16991 | -0.0000 |  -0.0002 |   0.0002 |                  0.4910 |
| gl blend gbm - baseline blend gbm     | VIC/SA  | 20830 | -0.0002 |  -0.0003 |  -0.0001 |                  0.5028 |
| gl model logit - baseline model logit | all     | 37821 | -0.0004 |  -0.0010 |   0.0002 |                  0.4449 |
| gl model logit - baseline model logit | QLD     | 16991 | -0.0013 |  -0.0026 |   0.0000 |                  0.4576 |
| gl model logit - baseline model logit | VIC/SA  | 20830 |  0.0002 |   0.0001 |   0.0004 |                  0.4346 |
| gl model gbm - baseline model gbm     | all     | 37821 | -0.0007 |  -0.0016 |   0.0002 |                  0.4972 |
| gl model gbm - baseline model gbm     | QLD     | 16991 | -0.0014 |  -0.0029 |   0.0002 |                  0.4918 |
| gl model gbm - baseline model gbm     | VIC/SA  | 20830 | -0.0001 |  -0.0012 |   0.0010 |                  0.5017 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   gl blend logit - baseline blend logit | gl blend logit - baseline blend logit 95%   |   gl blend gbm - baseline blend gbm | gl blend gbm - baseline blend gbm 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|------------------------------------:|:----------------------------------------|
| 2023 H1  |    5012 |                                  0.0001 | -0.0003 to +0.0005                          |                              0.0001 | -0.0003 to +0.0005                      |
| 2023 H2  |    5233 |                                 -0.0004 | -0.0008 to +0.0001                          |                             -0.0004 | -0.0009 to -0.0000                      |
| 2024 H1  |    5145 |                                  0.0000 | -0.0001 to +0.0002                          |                             -0.0001 | -0.0003 to +0.0001                      |
| 2024 H2  |    5229 |                                 -0.0001 | -0.0003 to +0.0000                          |                             -0.0001 | -0.0003 to +0.0001                      |
| 2025 H1  |    5065 |                                  0.0001 | -0.0001 to +0.0003                          |                              0.0001 | -0.0001 to +0.0003                      |
| 2025 H2  |    5153 |                                 -0.0001 | -0.0003 to +0.0001                          |                              0.0001 | -0.0002 to +0.0003                      |
| 2026 H1  |    4992 |                                 -0.0001 | -0.0003 to +0.0000                          |                             -0.0003 | -0.0006 to -0.0000                      |
| 2026 H2  |    1992 |                                 -0.0000 | -0.0002 to +0.0002                          |                             -0.0004 | -0.0009 to +0.0000                      |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   baseline logit a |   baseline logit b |   baseline gbm a |   baseline gbm b |   gl logit a |   gl logit b |   gl gbm a |   gl gbm b |
|-----:|-------------------:|:---------------------------|-------------------:|-------------------:|-----------------:|-----------------:|-------------:|-------------:|-----------:|-----------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |              0.150 |              1.090 |            0.128 |            1.098 |        0.124 |        1.107 |      0.105 |      1.114 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |              0.101 |              1.042 |            0.063 |            1.066 |        0.101 |        1.042 |      0.071 |      1.059 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |              0.117 |              1.076 |            0.099 |            1.083 |        0.120 |        1.073 |      0.096 |      1.086 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |              0.109 |              1.045 |            0.121 |            1.029 |        0.110 |        1.044 |      0.120 |      1.029 |
