# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prodmu, shape, shape-pace, shape-dist (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples
- Dropped 254 races with a missing model output (12 Sep 2026 to 23 Sep 2026; inputs such as carried weight not yet in TopRate)

## Log loss by fold

|                                     |       2023 |       2024 |       2025 |      2026 |     pooled |
|:------------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                               | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw                              |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated                       |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| SP calibrated (per state)           |     1.7921 |     1.7885 |     1.7857 |    1.7758 |     1.7864 |
| baseline: model logit               |     1.9340 |     1.9306 |     1.9348 |    1.9327 |     1.9331 |
| baseline: blend logit               |     1.7907 |     1.7872 |     1.7844 |    1.7752 |     1.7852 |
| baseline: blend logit (per state)   |     1.7911 |     1.7870 |     1.7841 |    1.7750 |     1.7851 |
| prodmu: model logit                 |     1.9245 |     1.9210 |     1.9278 |    1.9229 |     1.9242 |
| prodmu: blend logit                 |     1.7903 |     1.7867 |     1.7847 |    1.7751 |     1.7850 |
| prodmu: blend logit (per state)     |     1.7906 |     1.7865 |     1.7842 |    1.7748 |     1.7848 |
| shape: model logit                  |     1.9246 |     1.9209 |     1.9278 |    1.9227 |     1.9241 |
| shape: blend logit                  |     1.7903 |     1.7866 |     1.7847 |    1.7750 |     1.7850 |
| shape: blend logit (per state)      |     1.7906 |     1.7865 |     1.7842 |    1.7748 |     1.7848 |
| shape-pace: model logit             |     1.9246 |     1.9209 |     1.9278 |    1.9227 |     1.9241 |
| shape-pace: blend logit             |     1.7903 |     1.7866 |     1.7847 |    1.7750 |     1.7850 |
| shape-pace: blend logit (per state) |     1.7906 |     1.7865 |     1.7842 |    1.7748 |     1.7848 |
| shape-dist: model logit             |     1.9245 |     1.9210 |     1.9278 |    1.9229 |     1.9242 |
| shape-dist: blend logit             |     1.7903 |     1.7867 |     1.7847 |    1.7751 |     1.7850 |
| shape-dist: blend logit (per state) |     1.7906 |     1.7865 |     1.7842 |    1.7748 |     1.7848 |

## Differences vs SP, pooled

| comparison                             | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:---------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw          | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5939 |
| baseline blend logit - SP raw          | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5995 |
| baseline blend logit - SP raw          | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5894 |
| baseline blend logit - SP calibrated   | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5239 |
| baseline blend logit - SP calibrated   | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5335 |
| baseline blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5160 |
| prodmu blend logit - SP raw            | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5879 |
| prodmu blend logit - SP raw            | QLD     | 16991 | -0.0076 |  -0.0095 |  -0.0055 |                  0.5951 |
| prodmu blend logit - SP raw            | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0012 |                  0.5820 |
| prodmu blend logit - SP calibrated     | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5234 |
| prodmu blend logit - SP calibrated     | QLD     | 16991 | -0.0036 |  -0.0047 |  -0.0025 |                  0.5353 |
| prodmu blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0015 |                  0.5136 |
| shape blend logit - SP raw             | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5872 |
| shape blend logit - SP raw             | QLD     | 16991 | -0.0076 |  -0.0095 |  -0.0055 |                  0.5951 |
| shape blend logit - SP raw             | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0012 |                  0.5807 |
| shape blend logit - SP calibrated      | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5229 |
| shape blend logit - SP calibrated      | QLD     | 16991 | -0.0036 |  -0.0048 |  -0.0024 |                  0.5343 |
| shape blend logit - SP calibrated      | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0015 |                  0.5135 |
| shape-pace blend logit - SP raw        | all     | 37821 | -0.0050 |  -0.0062 |  -0.0037 |                  0.5873 |
| shape-pace blend logit - SP raw        | QLD     | 16991 | -0.0076 |  -0.0094 |  -0.0057 |                  0.5951 |
| shape-pace blend logit - SP raw        | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0012 |                  0.5808 |
| shape-pace blend logit - SP calibrated | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5229 |
| shape-pace blend logit - SP calibrated | QLD     | 16991 | -0.0036 |  -0.0048 |  -0.0024 |                  0.5343 |
| shape-pace blend logit - SP calibrated | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0015 |                  0.5136 |
| shape-dist blend logit - SP raw        | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5879 |
| shape-dist blend logit - SP raw        | QLD     | 16991 | -0.0076 |  -0.0095 |  -0.0055 |                  0.5951 |
| shape-dist blend logit - SP raw        | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0012 |                  0.5820 |
| shape-dist blend logit - SP calibrated | all     | 37821 | -0.0013 |  -0.0021 |  -0.0005 |                  0.5234 |
| shape-dist blend logit - SP calibrated | QLD     | 16991 | -0.0036 |  -0.0047 |  -0.0023 |                  0.5353 |
| shape-dist blend logit - SP calibrated | VIC/SA  | 20830 |  0.0005 |  -0.0005 |   0.0015 |                  0.5136 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   prodmu logit | prodmu logit 95%   |   shape logit | shape logit 95%    |   shape-pace logit | shape-pace logit 95%   |   shape-dist logit | shape-dist logit 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|--------------:|:-------------------|-------------------:|:-----------------------|-------------------:|:-----------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0048 to -0.0009   |        -0.0033 | -0.0058 to -0.0008 |       -0.0032 | -0.0057 to -0.0008 |            -0.0032 | -0.0057 to -0.0008     |            -0.0033 | -0.0058 to -0.0009     |
| 2023 H2  |    5233 |           0.0001 | -0.0019 to +0.0020   |        -0.0002 | -0.0027 to +0.0022 |       -0.0002 | -0.0027 to +0.0024 |            -0.0003 | -0.0028 to +0.0021     |            -0.0002 | -0.0025 to +0.0024     |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |        -0.0021 | -0.0038 to -0.0003 |       -0.0021 | -0.0040 to -0.0003 |            -0.0021 | -0.0040 to -0.0003     |            -0.0021 | -0.0039 to -0.0003     |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0002   |        -0.0015 | -0.0034 to +0.0003 |       -0.0015 | -0.0034 to +0.0004 |            -0.0015 | -0.0034 to +0.0002     |            -0.0015 | -0.0033 to +0.0002     |
| 2025 H1  |    5065 |          -0.0011 | -0.0025 to +0.0006   |        -0.0013 | -0.0034 to +0.0008 |       -0.0013 | -0.0035 to +0.0008 |            -0.0013 | -0.0032 to +0.0007     |            -0.0013 | -0.0032 to +0.0007     |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |        -0.0005 | -0.0024 to +0.0015 |       -0.0005 | -0.0024 to +0.0015 |            -0.0005 | -0.0024 to +0.0015     |            -0.0005 | -0.0024 to +0.0015     |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0002 | -0.0019 to +0.0014 |       -0.0003 | -0.0020 to +0.0014 |            -0.0003 | -0.0020 to +0.0013     |            -0.0002 | -0.0019 to +0.0015     |
| 2026 H2  |    1992 |          -0.0014 | -0.0037 to +0.0009   |        -0.0017 | -0.0044 to +0.0009 |       -0.0017 | -0.0042 to +0.0009 |            -0.0017 | -0.0042 to +0.0009     |            -0.0017 | -0.0043 to +0.0008     |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                                   | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-----------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5239 |
| baseline blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0026 |  -0.0042 |  -0.0010 |                  0.5211 |
| baseline blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5262 |
| prodmu blend logit (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0015 |  -0.0024 |  -0.0007 |                  0.5225 |
| prodmu blend logit (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5232 |
| prodmu blend logit (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5218 |
| shape blend logit (per state) - SP calibrated (per state)                    | all     | 37821 | -0.0016 |  -0.0024 |  -0.0007 |                  0.5230 |
| shape blend logit (per state) - SP calibrated (per state)                    | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5239 |
| shape blend logit (per state) - SP calibrated (per state)                    | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5223 |
| shape-pace blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0016 |  -0.0024 |  -0.0008 |                  0.5230 |
| shape-pace blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5238 |
| shape-pace blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5223 |
| shape-dist blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5225 |
| shape-dist blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5232 |
| shape-dist blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5218 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5008 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4703 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)         | all     | 37821 | -0.0002 |  -0.0006 |   0.0002 |                  0.4998 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)         | QLD     | 16991 |  0.0009 |   0.0002 |   0.0015 |                  0.5325 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4731 |
| shape blend logit (per state) - shape blend logit (pooled weights)           | all     | 37821 | -0.0002 |  -0.0006 |   0.0002 |                  0.4993 |
| shape blend logit (per state) - shape blend logit (pooled weights)           | QLD     | 16991 |  0.0009 |   0.0003 |   0.0014 |                  0.5318 |
| shape blend logit (per state) - shape blend logit (pooled weights)           | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4728 |
| shape-pace blend logit (per state) - shape-pace blend logit (pooled weights) | all     | 37821 | -0.0002 |  -0.0006 |   0.0002 |                  0.4995 |
| shape-pace blend logit (per state) - shape-pace blend logit (pooled weights) | QLD     | 16991 |  0.0008 |   0.0003 |   0.0015 |                  0.5321 |
| shape-pace blend logit (per state) - shape-pace blend logit (pooled weights) | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4729 |
| shape-dist blend logit (per state) - shape-dist blend logit (pooled weights) | all     | 37821 | -0.0002 |  -0.0005 |   0.0002 |                  0.4998 |
| shape-dist blend logit (per state) - shape-dist blend logit (pooled weights) | QLD     | 16991 |  0.0009 |   0.0002 |   0.0015 |                  0.5325 |
| shape-dist blend logit (per state) - shape-dist blend logit (pooled weights) | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4731 |
| SP calibrated (per state) - SP calibrated (pooled)                           | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                           | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                           | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   prodmu blend logit (per state) - SP calibrated (per state) | prodmu blend logit (per state) - SP calibrated (per state) 95%   |   shape blend logit (per state) - SP calibrated (per state) | shape blend logit (per state) - SP calibrated (per state) 95%   |   shape-pace blend logit (per state) - SP calibrated (per state) | shape-pace blend logit (per state) - SP calibrated (per state) 95%   |   shape-dist blend logit (per state) - SP calibrated (per state) | shape-dist blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|------------------------------------------------------------:|:----------------------------------------------------------------|-----------------------------------------------------------------:|:---------------------------------------------------------------------|-----------------------------------------------------------------:|:---------------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0053 to -0.0004                                                 |                                                      -0.0033 | -0.0060 to -0.0005                                               |                                                     -0.0032 | -0.0061 to -0.0005                                              |                                                          -0.0032 | -0.0060 to -0.0006                                                   |                                                          -0.0033 | -0.0061 to -0.0006                                                   |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0031                                                 |                                                       0.0002 | -0.0027 to +0.0031                                               |                                                      0.0001 | -0.0027 to +0.0029                                              |                                                           0.0001 | -0.0028 to +0.0029                                                   |                                                           0.0002 | -0.0028 to +0.0030                                                   |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0001                                                 |                                                      -0.0018 | -0.0037 to +0.0001                                               |                                                     -0.0019 | -0.0038 to -0.0001                                              |                                                          -0.0019 | -0.0037 to -0.0000                                                   |                                                          -0.0018 | -0.0037 to +0.0001                                                   |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0032 to -0.0002                                                 |                                                      -0.0022 | -0.0041 to -0.0002                                               |                                                     -0.0022 | -0.0041 to -0.0003                                              |                                                          -0.0022 | -0.0042 to -0.0003                                                   |                                                          -0.0022 | -0.0042 to -0.0002                                                   |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0005                                                 |                                                      -0.0015 | -0.0036 to +0.0004                                               |                                                     -0.0015 | -0.0035 to +0.0007                                              |                                                          -0.0015 | -0.0036 to +0.0005                                                   |                                                          -0.0015 | -0.0036 to +0.0006                                                   |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0036 to -0.0003                                                 |                                                      -0.0014 | -0.0035 to +0.0006                                               |                                                     -0.0014 | -0.0035 to +0.0006                                              |                                                          -0.0014 | -0.0035 to +0.0006                                                   |                                                          -0.0014 | -0.0035 to +0.0007                                                   |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0012                                                 |                                                      -0.0006 | -0.0023 to +0.0012                                               |                                                     -0.0006 | -0.0024 to +0.0010                                              |                                                          -0.0006 | -0.0024 to +0.0013                                                   |                                                          -0.0006 | -0.0024 to +0.0012                                                   |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0040 to +0.0009                                                 |                                                      -0.0019 | -0.0047 to +0.0009                                               |                                                     -0.0019 | -0.0048 to +0.0009                                              |                                                          -0.0019 | -0.0048 to +0.0010                                                   |                                                          -0.0019 | -0.0049 to +0.0008                                                   |

## Settle x race shape vs prodmu (paired by race)

| comparison                                  | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| shape model logit - prodmu model logit      | all     | 37821 | -0.0001 |  -0.0002 |   0.0001 |                  0.4951 |
| shape model logit - prodmu model logit      | QLD     | 16991 | -0.0002 |  -0.0004 |   0.0001 |                  0.5072 |
| shape model logit - prodmu model logit      | VIC/SA  | 20830 |  0.0000 |  -0.0002 |   0.0003 |                  0.4853 |
| shape blend logit - prodmu blend logit      | all     | 37821 | -0.0000 |  -0.0000 |   0.0000 |                  0.4995 |
| shape blend logit - prodmu blend logit      | QLD     | 16991 | -0.0000 |  -0.0001 |  -0.0000 |                  0.5110 |
| shape blend logit - prodmu blend logit      | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0001 |                  0.4902 |
| shape-pace model logit - prodmu model logit | all     | 37821 | -0.0001 |  -0.0002 |   0.0001 |                  0.4958 |
| shape-pace model logit - prodmu model logit | QLD     | 16991 | -0.0002 |  -0.0004 |   0.0001 |                  0.5077 |
| shape-pace model logit - prodmu model logit | VIC/SA  | 20830 |  0.0000 |  -0.0002 |   0.0003 |                  0.4861 |
| shape-pace blend logit - prodmu blend logit | all     | 37821 | -0.0000 |  -0.0000 |   0.0000 |                  0.4997 |
| shape-pace blend logit - prodmu blend logit | QLD     | 16991 | -0.0000 |  -0.0001 |  -0.0000 |                  0.5116 |
| shape-pace blend logit - prodmu blend logit | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0001 |                  0.4900 |
| shape-dist model logit - prodmu model logit | all     | 37821 |  0.0000 |  -0.0000 |   0.0000 |                  0.5050 |
| shape-dist model logit - prodmu model logit | QLD     | 16991 | -0.0000 |  -0.0000 |   0.0000 |                  0.5034 |
| shape-dist model logit - prodmu model logit | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0000 |                  0.5062 |
| shape-dist blend logit - prodmu blend logit | all     | 37821 |  0.0000 |  -0.0000 |   0.0000 |                  0.5072 |
| shape-dist blend logit - prodmu blend logit | QLD     | 16991 | -0.0000 |  -0.0000 |   0.0000 |                  0.5102 |
| shape-dist blend logit - prodmu blend logit | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0000 |                  0.5047 |
| shape model logit - shape-pace model logit  | all     | 37821 |  0.0000 |   0.0000 |   0.0000 |                  0.5010 |
| shape model logit - shape-pace model logit  | QLD     | 16991 |  0.0000 |   0.0000 |   0.0000 |                  0.5024 |
| shape model logit - shape-pace model logit  | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0000 |                  0.5000 |
| shape blend logit - shape-pace blend logit  | all     | 37821 |  0.0000 |  -0.0000 |   0.0000 |                  0.5004 |
| shape blend logit - shape-pace blend logit  | QLD     | 16991 |  0.0000 |  -0.0000 |   0.0000 |                  0.5007 |
| shape blend logit - shape-pace blend logit  | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0000 |                  0.5001 |
| shape model logit - shape-dist model logit  | all     | 37821 | -0.0001 |  -0.0002 |   0.0001 |                  0.4954 |
| shape model logit - shape-dist model logit  | QLD     | 16991 | -0.0002 |  -0.0004 |   0.0001 |                  0.5072 |
| shape model logit - shape-dist model logit  | VIC/SA  | 20830 |  0.0000 |  -0.0002 |   0.0003 |                  0.4858 |
| shape blend logit - shape-dist blend logit  | all     | 37821 | -0.0000 |  -0.0000 |   0.0000 |                  0.4998 |
| shape blend logit - shape-dist blend logit  | QLD     | 16991 | -0.0000 |  -0.0001 |  -0.0000 |                  0.5110 |
| shape blend logit - shape-dist blend logit  | VIC/SA  | 20830 |  0.0000 |  -0.0000 |   0.0001 |                  0.4907 |

| period   |   races |   shape blend logit - prodmu blend logit | shape blend logit - prodmu blend logit 95%   |
|:---------|--------:|-----------------------------------------:|:---------------------------------------------|
| 2023 H1  |    5012 |                                   0.0001 | -0.0000 to +0.0001                           |
| 2023 H2  |    5233 |                                  -0.0001 | -0.0002 to +0.0000                           |
| 2024 H1  |    5145 |                                  -0.0000 | -0.0001 to +0.0000                           |
| 2024 H2  |    5229 |                                  -0.0000 | -0.0001 to +0.0000                           |
| 2025 H1  |    5065 |                                   0.0000 | -0.0001 to +0.0001                           |
| 2025 H2  |    5153 |                                  -0.0000 | -0.0001 to +0.0001                           |
| 2026 H1  |    4992 |                                  -0.0000 | -0.0001 to +0.0000                           |
| 2026 H2  |    1992 |                                   0.0000 | -0.0001 to +0.0001                           |

## Variants vs baseline (paired by race)

| comparison                                    | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:----------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prodmu blend logit - baseline blend logit     | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5099 |
| prodmu blend logit - baseline blend logit     | QLD     | 16991 | -0.0007 |  -0.0010 |  -0.0002 |                  0.5236 |
| prodmu blend logit - baseline blend logit     | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4988 |
| shape blend logit - baseline blend logit      | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5098 |
| shape blend logit - baseline blend logit      | QLD     | 16991 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5247 |
| shape blend logit - baseline blend logit      | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0006 |                  0.4977 |
| shape-pace blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5097 |
| shape-pace blend logit - baseline blend logit | QLD     | 16991 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5245 |
| shape-pace blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0006 |                  0.4976 |
| shape-dist blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5099 |
| shape-dist blend logit - baseline blend logit | QLD     | 16991 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5233 |
| shape-dist blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0006 |                  0.4989 |
| prodmu model logit - baseline model logit     | all     | 37821 | -0.0089 |  -0.0106 |  -0.0071 |                  0.5211 |
| prodmu model logit - baseline model logit     | QLD     | 16991 | -0.0103 |  -0.0129 |  -0.0078 |                  0.5261 |
| prodmu model logit - baseline model logit     | VIC/SA  | 20830 | -0.0077 |  -0.0100 |  -0.0053 |                  0.5170 |
| shape model logit - baseline model logit      | all     | 37821 | -0.0090 |  -0.0107 |  -0.0073 |                  0.5218 |
| shape model logit - baseline model logit      | QLD     | 16991 | -0.0105 |  -0.0131 |  -0.0078 |                  0.5292 |
| shape model logit - baseline model logit      | VIC/SA  | 20830 | -0.0077 |  -0.0101 |  -0.0055 |                  0.5157 |
| shape-pace model logit - baseline model logit | all     | 37821 | -0.0090 |  -0.0107 |  -0.0073 |                  0.5218 |
| shape-pace model logit - baseline model logit | QLD     | 16991 | -0.0105 |  -0.0131 |  -0.0079 |                  0.5293 |
| shape-pace model logit - baseline model logit | VIC/SA  | 20830 | -0.0077 |  -0.0101 |  -0.0056 |                  0.5157 |
| shape-dist model logit - baseline model logit | all     | 37821 | -0.0089 |  -0.0107 |  -0.0072 |                  0.5210 |
| shape-dist model logit - baseline model logit | QLD     | 16991 | -0.0103 |  -0.0129 |  -0.0078 |                  0.5259 |
| shape-dist model logit - baseline model logit | VIC/SA  | 20830 | -0.0077 |  -0.0101 |  -0.0055 |                  0.5170 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prodmu blend logit - baseline blend logit | prodmu blend logit - baseline blend logit 95%   |   shape blend logit - baseline blend logit | shape blend logit - baseline blend logit 95%   |   shape-pace blend logit - baseline blend logit | shape-pace blend logit - baseline blend logit 95%   |   shape-dist blend logit - baseline blend logit | shape-dist blend logit - baseline blend logit 95%   |
|:---------|--------:|--------------------------------------------:|:------------------------------------------------|-------------------------------------------:|:-----------------------------------------------|------------------------------------------------:|:----------------------------------------------------|------------------------------------------------:|:----------------------------------------------------|
| 2023 H1  |    5012 |                                     -0.0005 | -0.0014 to +0.0004                              |                                    -0.0004 | -0.0013 to +0.0005                             |                                         -0.0004 | -0.0014 to +0.0004                                  |                                         -0.0005 | -0.0014 to +0.0004                                  |
| 2023 H2  |    5233 |                                     -0.0003 | -0.0012 to +0.0006                              |                                    -0.0004 | -0.0012 to +0.0006                             |                                         -0.0004 | -0.0013 to +0.0006                                  |                                         -0.0003 | -0.0012 to +0.0006                                  |
| 2024 H1  |    5145 |                                     -0.0005 | -0.0013 to +0.0002                              |                                    -0.0005 | -0.0013 to +0.0002                             |                                         -0.0005 | -0.0013 to +0.0002                                  |                                         -0.0005 | -0.0012 to +0.0002                                  |
| 2024 H2  |    5229 |                                     -0.0005 | -0.0013 to +0.0003                              |                                    -0.0005 | -0.0013 to +0.0002                             |                                         -0.0005 | -0.0013 to +0.0002                                  |                                         -0.0005 | -0.0013 to +0.0002                                  |
| 2025 H1  |    5065 |                                     -0.0002 | -0.0009 to +0.0005                              |                                    -0.0002 | -0.0010 to +0.0005                             |                                         -0.0002 | -0.0010 to +0.0005                                  |                                         -0.0002 | -0.0010 to +0.0005                                  |
| 2025 H2  |    5153 |                                      0.0007 | -0.0000 to +0.0015                              |                                     0.0007 | -0.0000 to +0.0015                             |                                          0.0007 | -0.0000 to +0.0015                                  |                                          0.0007 | +0.0000 to +0.0015                                  |
| 2026 H1  |    4992 |                                     -0.0000 | -0.0005 to +0.0005                              |                                    -0.0001 | -0.0006 to +0.0005                             |                                         -0.0001 | -0.0006 to +0.0005                                  |                                         -0.0000 | -0.0005 to +0.0005                                  |
| 2026 H2  |    1992 |                                     -0.0003 | -0.0012 to +0.0005                              |                                    -0.0003 | -0.0012 to +0.0006                             |                                         -0.0003 | -0.0012 to +0.0005                                  |                                         -0.0003 | -0.0012 to +0.0005                                  |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   prodmu logit a |   prodmu logit b |   prodmu logit a, QLD |   prodmu logit b, QLD |   prodmu logit a, VIC/SA |   prodmu logit b, VIC/SA |   shape logit a |   shape logit b |   shape logit a, QLD |   shape logit b, QLD |   shape logit a, VIC/SA |   shape logit b, VIC/SA |   shape-pace logit a |   shape-pace logit b |   shape-pace logit a, QLD |   shape-pace logit b, QLD |   shape-pace logit a, VIC/SA |   shape-pace logit b, VIC/SA |   shape-dist logit a |   shape-dist logit b |   shape-dist logit a, QLD |   shape-dist logit b, QLD |   shape-dist logit a, VIC/SA |   shape-dist logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|----------------:|----------------:|---------------------:|---------------------:|------------------------:|------------------------:|---------------------:|---------------------:|--------------------------:|--------------------------:|-----------------------------:|-----------------------------:|---------------------:|---------------------:|--------------------------:|--------------------------:|-----------------------------:|-----------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |            0.186 |            1.061 |                 0.288 |                 1.021 |                    0.093 |                    1.103 |           0.185 |           1.061 |                0.287 |                1.022 |                   0.093 |                   1.103 |                0.185 |                1.061 |                     0.287 |                     1.022 |                        0.093 |                        1.103 |                0.186 |                1.061 |                     0.288 |                     1.021 |                        0.093 |                        1.103 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |            0.140 |            1.011 |                 0.195 |                 0.998 |                    0.066 |                    1.037 |           0.140 |           1.011 |                0.196 |                0.997 |                   0.067 |                   1.036 |                0.141 |                1.011 |                     0.196 |                     0.997 |                        0.067 |                        1.036 |                0.140 |                1.011 |                     0.195 |                     0.998 |                        0.066 |                        1.037 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |            0.150 |            1.048 |                 0.206 |                 1.013 |                    0.088 |                    1.085 |           0.151 |           1.047 |                0.208 |                1.011 |                   0.087 |                   1.085 |                0.151 |                1.047 |                     0.208 |                     1.011 |                        0.087 |                        1.085 |                0.150 |                1.048 |                     0.206 |                     1.013 |                        0.088 |                        1.085 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |            0.120 |            1.033 |                 0.186 |                 0.971 |                    0.060 |                    1.083 |           0.120 |           1.033 |                0.187 |                0.969 |                   0.059 |                   1.084 |                0.120 |                1.033 |                     0.187 |                     0.969 |                        0.059 |                        1.084 |                0.120 |                1.033 |                     0.186 |                     0.971 |                        0.060 |                        1.083 |
