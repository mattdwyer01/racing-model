# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prod, prodmu (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                             | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                     |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)         |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit             |     1.9340 |     1.9306 |     1.9348 |    1.9327 |     1.9331 |
| baseline: blend logit             |     1.7907 |     1.7872 |     1.7844 |    1.7752 |     1.7852 |
| baseline: blend logit (per state) |     1.7911 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| baseline: model gbm               |     1.9185 |     1.9102 |     1.9048 |    1.8972 |     1.9086 |
| baseline: blend gbm               |     1.7914 |     1.7878 |     1.7846 |    1.7750 |     1.7855 |
| baseline: blend gbm (per state)   |     1.7911 |     1.7875 |     1.7842 |    1.7748 |     1.7852 |
| prod: model logit                 |     1.9278 |     1.9242 |     1.9310 |    1.9268 |     1.9275 |
| prod: blend logit                 |     1.7903 |     1.7867 |     1.7846 |    1.7751 |     1.7849 |
| prod: blend logit (per state)     |     1.7906 |     1.7866 |     1.7841 |    1.7748 |     1.7848 |
| prod: model gbm                   |     1.9167 |     1.9135 |     1.9049 |    1.8968 |     1.9090 |
| prod: blend gbm                   |     1.7912 |     1.7886 |     1.7849 |    1.7753 |     1.7859 |
| prod: blend gbm (per state)       |     1.7911 |     1.7882 |     1.7843 |    1.7750 |     1.7855 |
| prodmu: model logit               |     1.9245 |     1.9210 |     1.9278 |    1.9229 |     1.9242 |
| prodmu: blend logit               |     1.7903 |     1.7867 |     1.7847 |    1.7751 |     1.7850 |
| prodmu: blend logit (per state)   |     1.7906 |     1.7865 |     1.7842 |    1.7748 |     1.7848 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5939 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5995 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5894 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5238 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5335 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5160 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0033 |                  0.5953 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0063 |  -0.0078 |  -0.0046 |                  0.6020 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0013 |                  0.5899 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5205 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0023 |  -0.0029 |  -0.0016 |                  0.5363 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0005 |  -0.0000 |   0.0011 |                  0.5076 |
| prod blend logit - SP raw            | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5891 |
| prod blend logit - SP raw            | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0053 |                  0.5956 |
| prod blend logit - SP raw            | VIC/SA  | 20830 | -0.0031 |  -0.0047 |  -0.0014 |                  0.5838 |
| prod blend logit - SP calibrated     | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5225 |
| prod blend logit - SP calibrated     | QLD     | 16991 | -0.0034 |  -0.0046 |  -0.0023 |                  0.5323 |
| prod blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0003 |  -0.0006 |   0.0013 |                  0.5145 |
| prod blend gbm - SP raw              | all     | 37821 | -0.0041 |  -0.0054 |  -0.0028 |                  0.5764 |
| prod blend gbm - SP raw              | QLD     | 16991 | -0.0072 |  -0.0091 |  -0.0054 |                  0.5858 |
| prod blend gbm - SP raw              | VIC/SA  | 20830 | -0.0016 |  -0.0033 |   0.0002 |                  0.5688 |
| prod blend gbm - SP calibrated       | all     | 37821 | -0.0004 |  -0.0012 |   0.0004 |                  0.5158 |
| prod blend gbm - SP calibrated       | QLD     | 16991 | -0.0032 |  -0.0044 |  -0.0020 |                  0.5323 |
| prod blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0018 |   0.0008 |   0.0028 |                  0.5023 |
| prodmu blend logit - SP raw          | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5879 |
| prodmu blend logit - SP raw          | QLD     | 16991 | -0.0076 |  -0.0095 |  -0.0055 |                  0.5951 |
| prodmu blend logit - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0012 |                  0.5820 |
| prodmu blend logit - SP calibrated   | all     | 37821 | -0.0013 |  -0.0021 |  -0.0005 |                  0.5233 |
| prodmu blend logit - SP calibrated   | QLD     | 16991 | -0.0036 |  -0.0047 |  -0.0023 |                  0.5353 |
| prodmu blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0005 |  -0.0005 |   0.0015 |                  0.5136 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   prod logit | prod logit 95%     |   prod gbm | prod gbm 95%       |   prodmu logit | prodmu logit 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|---------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0048 to -0.0009   |        -0.0019 | -0.0031 to -0.0007 |      -0.0032 | -0.0056 to -0.0010 |    -0.0025 | -0.0045 to -0.0005 |        -0.0033 | -0.0058 to -0.0009 |
| 2023 H2  |    5233 |           0.0001 | -0.0019 to +0.0020   |         0.0006 | -0.0005 to +0.0018 |      -0.0002 | -0.0025 to +0.0023 |     0.0007 | -0.0012 to +0.0026 |        -0.0002 | -0.0025 to +0.0024 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |        -0.0009 | -0.0017 to -0.0001 |      -0.0020 | -0.0039 to -0.0003 |    -0.0001 | -0.0022 to +0.0020 |        -0.0021 | -0.0039 to -0.0003 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0002   |        -0.0004 | -0.0012 to +0.0005 |      -0.0016 | -0.0034 to +0.0002 |     0.0003 | -0.0019 to +0.0025 |        -0.0015 | -0.0033 to +0.0002 |
| 2025 H1  |    5065 |          -0.0011 | -0.0025 to +0.0006   |        -0.0006 | -0.0018 to +0.0005 |      -0.0013 | -0.0034 to +0.0009 |    -0.0009 | -0.0029 to +0.0012 |        -0.0013 | -0.0032 to +0.0007 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |        -0.0013 | -0.0023 to -0.0002 |      -0.0007 | -0.0027 to +0.0013 |    -0.0003 | -0.0024 to +0.0018 |        -0.0005 | -0.0024 to +0.0015 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0006 | -0.0020 to +0.0007 |      -0.0003 | -0.0021 to +0.0014 |    -0.0003 | -0.0025 to +0.0018 |        -0.0002 | -0.0019 to +0.0015 |
| 2026 H2  |    1992 |          -0.0014 | -0.0037 to +0.0009   |        -0.0011 | -0.0034 to +0.0011 |      -0.0017 | -0.0043 to +0.0010 |    -0.0006 | -0.0042 to +0.0031 |        -0.0017 | -0.0043 to +0.0008 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5239 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0026 |  -0.0042 |  -0.0010 |                  0.5211 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5261 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5129 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0025 |  -0.0038 |  -0.0012 |                  0.5262 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0002 |                  0.5020 |
| prod blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5226 |
| prod blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0030 |  -0.0046 |  -0.0013 |                  0.5217 |
| prod blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0004 |  -0.0009 |   0.0002 |                  0.5233 |
| prod blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0009 |  -0.0018 |  -0.0000 |                  0.5164 |
| prod blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0025 |  -0.0043 |  -0.0007 |                  0.5259 |
| prod blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 |  0.0004 |  -0.0002 |   0.0010 |                  0.5085 |
| prodmu blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5225 |
| prodmu blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5232 |
| prodmu blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5218 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5008 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4703 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5027 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0001 |  -0.0007 |   0.0009 |                  0.5363 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0006 |  -0.0012 |  -0.0001 |                  0.4752 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | all     | 37821 | -0.0001 |  -0.0005 |   0.0002 |                  0.5020 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | QLD     | 16991 |  0.0008 |   0.0003 |   0.0014 |                  0.5370 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4735 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | all     | 37821 | -0.0004 |  -0.0008 |   0.0000 |                  0.5074 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | QLD     | 16991 |  0.0011 |   0.0004 |   0.0017 |                  0.5360 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0016 |  -0.0020 |  -0.0011 |                  0.4840 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | all     | 37821 | -0.0002 |  -0.0005 |   0.0002 |                  0.4998 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | QLD     | 16991 |  0.0009 |   0.0002 |   0.0015 |                  0.5325 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4731 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   prod blend logit (per state) - SP calibrated (per state) | prod blend logit (per state) - SP calibrated (per state) 95%   |   prod blend gbm (per state) - SP calibrated (per state) | prod blend gbm (per state) - SP calibrated (per state) 95%   |   prodmu blend logit (per state) - SP calibrated (per state) | prodmu blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0053 to -0.0004                                                 |                                                      -0.0026 | -0.0046 to -0.0005                                               |                                                    -0.0033 | -0.0060 to -0.0007                                             |                                                  -0.0029 | -0.0054 to -0.0005                                           |                                                      -0.0033 | -0.0061 to -0.0006                                               |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0031                                                 |                                                       0.0006 | -0.0017 to +0.0029                                               |                                                     0.0002 | -0.0025 to +0.0029                                             |                                                   0.0006 | -0.0019 to +0.0031                                           |                                                       0.0002 | -0.0028 to +0.0030                                               |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0001                                                 |                                                      -0.0002 | -0.0014 to +0.0011                                               |                                                    -0.0017 | -0.0036 to +0.0000                                             |                                                  -0.0001 | -0.0022 to +0.0021                                           |                                                      -0.0018 | -0.0037 to +0.0001                                               |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0032 to -0.0002                                                 |                                                      -0.0018 | -0.0031 to -0.0005                                               |                                                    -0.0021 | -0.0040 to -0.0003                                             |                                                  -0.0006 | -0.0028 to +0.0016                                           |                                                      -0.0022 | -0.0042 to -0.0002                                               |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0005                                                 |                                                      -0.0010 | -0.0024 to +0.0005                                               |                                                    -0.0014 | -0.0034 to +0.0008                                             |                                                  -0.0015 | -0.0038 to +0.0008                                           |                                                      -0.0015 | -0.0036 to +0.0006                                               |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0036 to -0.0003                                                 |                                                      -0.0020 | -0.0035 to -0.0005                                               |                                                    -0.0016 | -0.0036 to +0.0004                                             |                                                  -0.0012 | -0.0035 to +0.0010                                           |                                                      -0.0014 | -0.0035 to +0.0007                                               |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0012                                                 |                                                      -0.0010 | -0.0026 to +0.0007                                               |                                                    -0.0006 | -0.0024 to +0.0012                                             |                                                  -0.0008 | -0.0030 to +0.0015                                           |                                                      -0.0006 | -0.0024 to +0.0012                                               |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0040 to +0.0009                                                 |                                                      -0.0009 | -0.0033 to +0.0018                                               |                                                    -0.0018 | -0.0047 to +0.0010                                             |                                                  -0.0007 | -0.0044 to +0.0030                                           |                                                      -0.0019 | -0.0049 to +0.0008                                               |

## Rating mu as a logit input vs production inputs (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prodmu blend logit - prod blend logit | all     | 37821 |  0.0000 |  -0.0001 |   0.0002 |                  0.4956 |
| prodmu blend logit - prod blend logit | QLD     | 16991 | -0.0001 |  -0.0004 |   0.0001 |                  0.4966 |
| prodmu blend logit - prod blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0000 |   0.0004 |                  0.4948 |
| prodmu model logit - prod model logit | all     | 37821 | -0.0033 |  -0.0043 |  -0.0024 |                  0.5135 |
| prodmu model logit - prod model logit | QLD     | 16991 | -0.0053 |  -0.0068 |  -0.0039 |                  0.5186 |
| prodmu model logit - prod model logit | VIC/SA  | 20830 | -0.0017 |  -0.0030 |  -0.0004 |                  0.5094 |

| period   |   races |   prodmu blend logit - prod blend logit | prodmu blend logit - prod blend logit 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|
| 2023 H1  |    5012 |                                 -0.0000 | -0.0006 to +0.0005                          |
| 2023 H2  |    5233 |                                  0.0000 | -0.0005 to +0.0006                          |
| 2024 H1  |    5145 |                                 -0.0001 | -0.0004 to +0.0003                          |
| 2024 H2  |    5229 |                                  0.0000 | -0.0003 to +0.0004                          |
| 2025 H1  |    5065 |                                 -0.0000 | -0.0003 to +0.0003                          |
| 2025 H2  |    5153 |                                  0.0003 | -0.0001 to +0.0006                          |
| 2026 H1  |    4992 |                                  0.0000 | -0.0002 to +0.0003                          |
| 2026 H2  |    1992 |                                 -0.0000 | -0.0005 to +0.0004                          |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod blend logit - baseline blend logit   | all     | 37821 | -0.0002 |  -0.0005 |   0.0000 |                  0.5095 |
| prod blend logit - baseline blend logit   | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0002 |                  0.5244 |
| prod blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0000 |  -0.0003 |   0.0003 |                  0.4974 |
| prod blend gbm - baseline blend gbm       | all     | 37821 |  0.0003 |  -0.0001 |   0.0008 |                  0.5008 |
| prod blend gbm - baseline blend gbm       | QLD     | 16991 | -0.0009 |  -0.0016 |  -0.0003 |                  0.5150 |
| prod blend gbm - baseline blend gbm       | VIC/SA  | 20830 |  0.0013 |   0.0007 |   0.0019 |                  0.4892 |
| prodmu blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5099 |
| prodmu blend logit - baseline blend logit | QLD     | 16991 | -0.0007 |  -0.0010 |  -0.0002 |                  0.5236 |
| prodmu blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4988 |
| prod model logit - baseline model logit   | all     | 37821 | -0.0056 |  -0.0071 |  -0.0041 |                  0.5127 |
| prod model logit - baseline model logit   | QLD     | 16991 | -0.0050 |  -0.0070 |  -0.0030 |                  0.5208 |
| prod model logit - baseline model logit   | VIC/SA  | 20830 | -0.0060 |  -0.0081 |  -0.0039 |                  0.5060 |
| prod model gbm - baseline model gbm       | all     | 37821 |  0.0004 |  -0.0015 |   0.0024 |                  0.4853 |
| prod model gbm - baseline model gbm       | QLD     | 16991 | -0.0012 |  -0.0040 |   0.0016 |                  0.4804 |
| prod model gbm - baseline model gbm       | VIC/SA  | 20830 |  0.0018 |  -0.0010 |   0.0045 |                  0.4893 |
| prodmu model logit - baseline model logit | all     | 37821 | -0.0089 |  -0.0106 |  -0.0072 |                  0.5211 |
| prodmu model logit - baseline model logit | QLD     | 16991 | -0.0103 |  -0.0129 |  -0.0078 |                  0.5261 |
| prodmu model logit - baseline model logit | VIC/SA  | 20830 | -0.0077 |  -0.0101 |  -0.0055 |                  0.5170 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prod blend logit - baseline blend logit | prod blend logit - baseline blend logit 95%   |   prod blend gbm - baseline blend gbm | prod blend gbm - baseline blend gbm 95%   |   prodmu blend logit - baseline blend logit | prodmu blend logit - baseline blend logit 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|--------------------------------------------:|:------------------------------------------------|
| 2023 H1  |    5012 |                                   -0.0004 | -0.0011 to +0.0003                            |                               -0.0006 | -0.0015 to +0.0004                        |                                     -0.0005 | -0.0013 to +0.0004                              |
| 2023 H2  |    5233 |                                   -0.0003 | -0.0010 to +0.0004                            |                                0.0001 | -0.0008 to +0.0011                        |                                     -0.0003 | -0.0012 to +0.0007                              |
| 2024 H1  |    5145 |                                   -0.0004 | -0.0011 to +0.0002                            |                                0.0009 | -0.0006 to +0.0022                        |                                     -0.0005 | -0.0012 to +0.0003                              |
| 2024 H2  |    5229 |                                   -0.0005 | -0.0012 to +0.0001                            |                                0.0007 | -0.0007 to +0.0021                        |                                     -0.0005 | -0.0012 to +0.0002                              |
| 2025 H1  |    5065 |                                   -0.0002 | -0.0010 to +0.0004                            |                               -0.0003 | -0.0015 to +0.0009                        |                                     -0.0002 | -0.0010 to +0.0005                              |
| 2025 H2  |    5153 |                                    0.0005 | -0.0002 to +0.0011                            |                                0.0009 | -0.0003 to +0.0022                        |                                      0.0007 | -0.0000 to +0.0015                              |
| 2026 H1  |    4992 |                                   -0.0001 | -0.0006 to +0.0004                            |                                0.0003 | -0.0008 to +0.0014                        |                                     -0.0000 | -0.0006 to +0.0005                              |
| 2026 H2  |    1992 |                                   -0.0003 | -0.0011 to +0.0005                            |                                0.0005 | -0.0012 to +0.0023                        |                                     -0.0003 | -0.0012 to +0.0005                              |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   prod logit a |   prod logit b |   prod logit a, QLD |   prod logit b, QLD |   prod logit a, VIC/SA |   prod logit b, VIC/SA |   prod gbm a |   prod gbm b |   prod gbm a, QLD |   prod gbm b, QLD |   prod gbm a, VIC/SA |   prod gbm b, VIC/SA |   prodmu logit a |   prodmu logit b |   prodmu logit a, QLD |   prodmu logit b, QLD |   prodmu logit a, VIC/SA |   prodmu logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |            0.097 |            1.120 |                 0.251 |                 1.051 |                   -0.015 |                    1.176 |          0.181 |          1.067 |               0.274 |               1.037 |                  0.096 |                  1.102 |        0.155 |        1.078 |             0.283 |             1.026 |                0.064 |                1.119 |            0.186 |            1.061 |                 0.288 |                 1.021 |                    0.093 |                    1.103 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |            0.071 |            1.060 |                 0.153 |                 1.035 |                   -0.027 |                    1.099 |          0.135 |          1.016 |               0.183 |               1.009 |                  0.070 |                  1.035 |        0.175 |        0.979 |             0.231 |             0.971 |                0.114 |                0.997 |            0.140 |            1.011 |                 0.195 |                 0.998 |                    0.066 |                    1.037 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |            0.093 |            1.087 |                 0.182 |                 1.031 |                    0.000 |                    1.146 |          0.149 |          1.049 |               0.201 |               1.018 |                  0.091 |                  1.083 |        0.176 |        1.023 |             0.246 |             0.982 |                0.107 |                1.064 |            0.150 |            1.048 |                 0.206 |                 1.013 |                    0.088 |                    1.085 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |            0.115 |            1.033 |                 0.189 |                 0.966 |                    0.049 |                    1.089 |          0.124 |          1.032 |               0.182 |               0.976 |                  0.072 |                  1.076 |        0.178 |        0.982 |             0.238 |             0.924 |                0.127 |                1.029 |            0.120 |            1.033 |                 0.186 |                 0.971 |                    0.060 |                    1.083 |
