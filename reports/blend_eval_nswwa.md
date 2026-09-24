# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prod, prodmu (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples
- Dropped 413 races with a missing model output (12 Sep 2026 to 22 Sep 2026; inputs such as carried weight not yet in TopRate)

## Log loss by fold

|                                   |       2023 |       2024 |       2025 |       2026 |     pooled |
|:----------------------------------|-----------:|-----------:|-----------:|-----------:|-----------:|
| races                             | 17964.0000 | 17820.0000 | 17687.0000 | 12163.0000 | 65634.0000 |
| SP raw                            |     1.7853 |     1.7848 |     1.7706 |     1.7692 |     1.7782 |
| SP calibrated                     |     1.7819 |     1.7796 |     1.7664 |     1.7638 |     1.7737 |
| SP calibrated (per state)         |     1.7824 |     1.7796 |     1.7665 |     1.7639 |     1.7739 |
| baseline: model logit             |     1.9273 |     1.9289 |     1.9192 |     1.9280 |     1.9257 |
| baseline: blend logit             |     1.7811 |     1.7792 |     1.7658 |     1.7640 |     1.7733 |
| baseline: blend logit (per state) |     1.7822 |     1.7794 |     1.7655 |     1.7636 |     1.7735 |
| prod: model logit                 |     1.9211 |     1.9233 |     1.9150 |     1.9219 |     1.9202 |
| prod: blend logit                 |     1.7806 |     1.7791 |     1.7658 |     1.7639 |     1.7731 |
| prod: blend logit (per state)     |     1.7821 |     1.7794 |     1.7655 |     1.7635 |     1.7734 |
| prodmu: model logit               |     1.9176 |     1.9196 |     1.9115 |     1.9177 |     1.9165 |
| prodmu: blend logit               |     1.7806 |     1.7791 |     1.7659 |     1.7639 |     1.7731 |
| prodmu: blend logit (per state)   |     1.7822 |     1.7793 |     1.7655 |     1.7634 |     1.7734 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 65634 | -0.0050 |  -0.0058 |  -0.0042 |                  0.5978 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0085 |  -0.0052 |                  0.6018 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0036 |  -0.0051 |  -0.0022 |                  0.5937 |
| baseline blend logit - SP raw        | NSW     | 20018 | -0.0056 |  -0.0070 |  -0.0041 |                  0.6020 |
| baseline blend logit - SP raw        | WA      |  7795 | -0.0029 |  -0.0054 |  -0.0005 |                  0.5891 |
| baseline blend logit - SP calibrated | all     | 65634 | -0.0005 |  -0.0008 |  -0.0001 |                  0.5179 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0026 |  -0.0034 |  -0.0019 |                  0.5338 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0001 |  -0.0005 |   0.0007 |                  0.5187 |
| baseline blend logit - SP calibrated | NSW     | 20018 | -0.0000 |  -0.0007 |   0.0006 |                  0.5121 |
| baseline blend logit - SP calibrated | WA      |  7795 |  0.0017 |   0.0007 |   0.0026 |                  0.4957 |
| prod blend logit - SP raw            | all     | 65634 | -0.0051 |  -0.0060 |  -0.0042 |                  0.5925 |
| prod blend logit - SP raw            | QLD     | 16991 | -0.0075 |  -0.0093 |  -0.0057 |                  0.5982 |
| prod blend logit - SP raw            | VIC/SA  | 20830 | -0.0036 |  -0.0051 |  -0.0021 |                  0.5880 |
| prod blend logit - SP raw            | NSW     | 20018 | -0.0057 |  -0.0073 |  -0.0041 |                  0.5963 |
| prod blend logit - SP raw            | WA      |  7795 | -0.0022 |  -0.0048 |   0.0003 |                  0.5819 |
| prod blend logit - SP calibrated     | all     | 65634 | -0.0006 |  -0.0011 |  -0.0001 |                  0.5181 |
| prod blend logit - SP calibrated     | QLD     | 16991 | -0.0033 |  -0.0043 |  -0.0022 |                  0.5360 |
| prod blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0001 |  -0.0007 |   0.0009 |                  0.5174 |
| prod blend logit - SP calibrated     | NSW     | 20018 | -0.0002 |  -0.0010 |   0.0006 |                  0.5134 |
| prod blend logit - SP calibrated     | WA      |  7795 |  0.0023 |   0.0011 |   0.0035 |                  0.4933 |
| prodmu blend logit - SP raw          | all     | 65634 | -0.0051 |  -0.0060 |  -0.0042 |                  0.5911 |
| prodmu blend logit - SP raw          | QLD     | 16991 | -0.0076 |  -0.0093 |  -0.0059 |                  0.5976 |
| prodmu blend logit - SP raw          | VIC/SA  | 20830 | -0.0035 |  -0.0050 |  -0.0020 |                  0.5870 |
| prodmu blend logit - SP raw          | NSW     | 20018 | -0.0057 |  -0.0073 |  -0.0041 |                  0.5942 |
| prodmu blend logit - SP raw          | WA      |  7795 | -0.0022 |  -0.0047 |   0.0003 |                  0.5802 |
| prodmu blend logit - SP calibrated   | all     | 65634 | -0.0006 |  -0.0011 |  -0.0001 |                  0.5169 |
| prodmu blend logit - SP calibrated   | QLD     | 16991 | -0.0034 |  -0.0043 |  -0.0023 |                  0.5354 |
| prodmu blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0002 |  -0.0007 |   0.0010 |                  0.5152 |
| prodmu blend logit - SP calibrated   | NSW     | 20018 | -0.0002 |  -0.0011 |   0.0006 |                  0.5131 |
| prodmu blend logit - SP calibrated   | WA      |  7795 |  0.0024 |   0.0011 |   0.0036 |                  0.4908 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   prod logit | prod logit 95%     |   prodmu logit | prodmu logit 95%   |
|:---------|--------:|-----------------:|:---------------------|-------------:|:-------------------|---------------:|:-------------------|
| 2023 H1  |    8777 |          -0.0011 | -0.0022 to -0.0000   |      -0.0015 | -0.0029 to -0.0001 |        -0.0015 | -0.0029 to -0.0001 |
| 2023 H2  |    9187 |          -0.0007 | -0.0017 to +0.0004   |      -0.0011 | -0.0025 to +0.0003 |        -0.0012 | -0.0025 to +0.0002 |
| 2024 H1  |    8782 |          -0.0004 | -0.0015 to +0.0007   |      -0.0005 | -0.0019 to +0.0010 |        -0.0004 | -0.0019 to +0.0010 |
| 2024 H2  |    9038 |          -0.0004 | -0.0015 to +0.0007   |      -0.0003 | -0.0019 to +0.0011 |        -0.0005 | -0.0019 to +0.0010 |
| 2025 H1  |    8786 |          -0.0006 | -0.0014 to +0.0002   |      -0.0007 | -0.0018 to +0.0004 |        -0.0006 | -0.0017 to +0.0005 |
| 2025 H2  |    8901 |          -0.0006 | -0.0014 to +0.0003   |      -0.0004 | -0.0015 to +0.0007 |        -0.0003 | -0.0014 to +0.0008 |
| 2026 H1  |    8690 |           0.0001 | -0.0007 to +0.0009   |       0.0001 | -0.0009 to +0.0010 |         0.0001 | -0.0008 to +0.0011 |
| 2026 H2  |    3473 |           0.0003 | -0.0009 to +0.0016   |       0.0003 | -0.0013 to +0.0019 |         0.0001 | -0.0014 to +0.0016 |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 65634 | -0.0004 |  -0.0009 |   0.0001 |                  0.5174 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0026 |  -0.0040 |  -0.0011 |                  0.5202 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5270 |
| baseline blend logit (per state) - SP calibrated (per state)             | NSW     | 20018 |  0.0005 |  -0.0004 |   0.0014 |                  0.5118 |
| baseline blend logit (per state) - SP calibrated (per state)             | WA      |  7795 |  0.0014 |  -0.0001 |   0.0027 |                  0.5001 |
| prod blend logit (per state) - SP calibrated (per state)                 | all     | 65634 | -0.0005 |  -0.0011 |   0.0001 |                  0.5177 |
| prod blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0029 |  -0.0045 |  -0.0013 |                  0.5245 |
| prod blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0004 |  -0.0009 |   0.0002 |                  0.5241 |
| prod blend logit (per state) - SP calibrated (per state)                 | NSW     | 20018 |  0.0006 |  -0.0005 |   0.0018 |                  0.5120 |
| prod blend logit (per state) - SP calibrated (per state)                 | WA      |  7795 |  0.0019 |   0.0004 |   0.0033 |                  0.5006 |
| prodmu blend logit (per state) - SP calibrated (per state)               | all     | 65634 | -0.0005 |  -0.0011 |   0.0001 |                  0.5162 |
| prodmu blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0031 |  -0.0046 |  -0.0014 |                  0.5229 |
| prodmu blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5241 |
| prodmu blend logit (per state) - SP calibrated (per state)               | NSW     | 20018 |  0.0005 |  -0.0006 |   0.0016 |                  0.5117 |
| prodmu blend logit (per state) - SP calibrated (per state)               | WA      |  7795 |  0.0020 |   0.0006 |   0.0036 |                  0.4919 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 65634 |  0.0002 |  -0.0002 |   0.0006 |                  0.5017 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0007 |  -0.0002 |   0.0015 |                  0.5422 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0001 |  -0.0005 |   0.0003 |                  0.4681 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | NSW     | 20018 |  0.0004 |  -0.0000 |   0.0009 |                  0.4996 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | WA      |  7795 | -0.0003 |  -0.0025 |   0.0019 |                  0.5087 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | all     | 65634 |  0.0003 |  -0.0001 |   0.0007 |                  0.5051 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | QLD     | 16991 |  0.0009 |   0.0002 |   0.0017 |                  0.5433 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0001 |                  0.4730 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | NSW     | 20018 |  0.0007 |   0.0002 |   0.0012 |                  0.5046 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | WA      |  7795 | -0.0004 |  -0.0028 |   0.0020 |                  0.5084 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | all     | 65634 |  0.0003 |  -0.0001 |   0.0007 |                  0.5034 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | QLD     | 16991 |  0.0009 |   0.0001 |   0.0017 |                  0.5390 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0004 |  -0.0008 |   0.0000 |                  0.4731 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | NSW     | 20018 |  0.0006 |   0.0002 |   0.0011 |                  0.5016 |
| prodmu blend logit (per state) - prodmu blend logit (pooled weights)     | WA      |  7795 | -0.0003 |  -0.0026 |   0.0020 |                  0.5119 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 65634 |  0.0002 |   0.0000 |   0.0003 |                  0.4942 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0006 |   0.0002 |   0.0010 |                  0.5558 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 |  0.0002 |  -0.0000 |   0.0004 |                  0.4464 |
| SP calibrated (per state) - SP calibrated (pooled)                       | NSW     | 20018 | -0.0001 |  -0.0003 |   0.0001 |                  0.4942 |
| SP calibrated (per state) - SP calibrated (pooled)                       | WA      |  7795 |  0.0000 |  -0.0005 |   0.0006 |                  0.4875 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   prod blend logit (per state) - SP calibrated (per state) | prod blend logit (per state) - SP calibrated (per state) 95%   |   prodmu blend logit (per state) - SP calibrated (per state) | prodmu blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    8777 |                                                        -0.0009 | -0.0029 to +0.0010                                                 |                                                    -0.0008 | -0.0030 to +0.0014                                             |                                                      -0.0009 | -0.0030 to +0.0013                                               |
| 2023 H2  |    9187 |                                                         0.0005 | -0.0013 to +0.0024                                                 |                                                     0.0003 | -0.0020 to +0.0026                                             |                                                       0.0004 | -0.0018 to +0.0027                                               |
| 2024 H1  |    8782 |                                                        -0.0001 | -0.0013 to +0.0012                                                 |                                                    -0.0003 | -0.0018 to +0.0013                                             |                                                      -0.0002 | -0.0018 to +0.0014                                               |
| 2024 H2  |    9038 |                                                        -0.0003 | -0.0016 to +0.0009                                                 |                                                    -0.0002 | -0.0017 to +0.0014                                             |                                                      -0.0005 | -0.0021 to +0.0011                                               |
| 2025 H1  |    8786 |                                                        -0.0006 | -0.0017 to +0.0004                                                 |                                                    -0.0008 | -0.0021 to +0.0004                                             |                                                      -0.0009 | -0.0021 to +0.0003                                               |
| 2025 H2  |    8901 |                                                        -0.0012 | -0.0022 to -0.0002                                                 |                                                    -0.0011 | -0.0024 to +0.0002                                             |                                                      -0.0010 | -0.0023 to +0.0003                                               |
| 2026 H1  |    8690 |                                                        -0.0003 | -0.0013 to +0.0007                                                 |                                                    -0.0004 | -0.0016 to +0.0008                                             |                                                      -0.0004 | -0.0015 to +0.0007                                               |
| 2026 H2  |    3473 |                                                        -0.0004 | -0.0018 to +0.0011                                                 |                                                    -0.0004 | -0.0021 to +0.0013                                             |                                                      -0.0006 | -0.0023 to +0.0011                                               |

## Rating mu as a logit input vs production inputs (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prodmu blend logit - prod blend logit | all     | 65634 |  0.0000 |  -0.0001 |   0.0001 |                  0.4915 |
| prodmu blend logit - prod blend logit | QLD     | 16991 | -0.0001 |  -0.0003 |   0.0000 |                  0.4949 |
| prodmu blend logit - prod blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0000 |   0.0003 |                  0.4912 |
| prodmu blend logit - prod blend logit | NSW     | 20018 | -0.0000 |  -0.0002 |   0.0001 |                  0.4889 |
| prodmu blend logit - prod blend logit | WA      |  7795 |  0.0001 |  -0.0002 |   0.0003 |                  0.4919 |
| prodmu model logit - prod model logit | all     | 65634 | -0.0037 |  -0.0043 |  -0.0030 |                  0.5137 |
| prodmu model logit - prod model logit | QLD     | 16991 | -0.0053 |  -0.0066 |  -0.0040 |                  0.5215 |
| prodmu model logit - prod model logit | VIC/SA  | 20830 | -0.0021 |  -0.0031 |  -0.0009 |                  0.5116 |
| prodmu model logit - prod model logit | NSW     | 20018 | -0.0034 |  -0.0046 |  -0.0023 |                  0.5059 |
| prodmu model logit - prod model logit | WA      |  7795 | -0.0051 |  -0.0071 |  -0.0031 |                  0.5220 |

| period   |   races |   prodmu blend logit - prod blend logit | prodmu blend logit - prod blend logit 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|
| 2023 H1  |    8777 |                                 -0.0000 | -0.0003 to +0.0002                          |
| 2023 H2  |    9187 |                                 -0.0000 | -0.0003 to +0.0002                          |
| 2024 H1  |    8782 |                                  0.0001 | -0.0002 to +0.0003                          |
| 2024 H2  |    9038 |                                 -0.0001 | -0.0004 to +0.0001                          |
| 2025 H1  |    8786 |                                  0.0001 | -0.0001 to +0.0003                          |
| 2025 H2  |    8901 |                                  0.0001 | -0.0001 to +0.0003                          |
| 2026 H1  |    8690 |                                  0.0001 | -0.0001 to +0.0002                          |
| 2026 H2  |    3473 |                                 -0.0002 | -0.0005 to +0.0001                          |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod blend logit - baseline blend logit   | all     | 65634 | -0.0001 |  -0.0003 |   0.0000 |                  0.5074 |
| prod blend logit - baseline blend logit   | QLD     | 16991 | -0.0006 |  -0.0009 |  -0.0003 |                  0.5286 |
| prod blend logit - baseline blend logit   | VIC/SA  | 20830 | -0.0000 |  -0.0003 |   0.0003 |                  0.5030 |
| prod blend logit - baseline blend logit   | NSW     | 20018 | -0.0002 |  -0.0005 |   0.0001 |                  0.5056 |
| prod blend logit - baseline blend logit   | WA      |  7795 |  0.0007 |   0.0003 |   0.0011 |                  0.4772 |
| prodmu blend logit - baseline blend logit | all     | 65634 | -0.0001 |  -0.0003 |   0.0000 |                  0.5060 |
| prodmu blend logit - baseline blend logit | QLD     | 16991 | -0.0007 |  -0.0011 |  -0.0004 |                  0.5276 |
| prodmu blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0002 |   0.0004 |                  0.5007 |
| prodmu blend logit - baseline blend logit | NSW     | 20018 | -0.0002 |  -0.0005 |   0.0002 |                  0.5047 |
| prodmu blend logit - baseline blend logit | WA      |  7795 |  0.0007 |   0.0003 |   0.0012 |                  0.4762 |
| prod model logit - baseline model logit   | all     | 65634 | -0.0055 |  -0.0065 |  -0.0044 |                  0.5108 |
| prod model logit - baseline model logit   | QLD     | 16991 | -0.0052 |  -0.0072 |  -0.0031 |                  0.5196 |
| prod model logit - baseline model logit   | VIC/SA  | 20830 | -0.0056 |  -0.0077 |  -0.0036 |                  0.5047 |
| prod model logit - baseline model logit   | NSW     | 20018 | -0.0062 |  -0.0081 |  -0.0042 |                  0.5193 |
| prod model logit - baseline model logit   | WA      |  7795 | -0.0037 |  -0.0064 |  -0.0011 |                  0.4858 |
| prodmu model logit - baseline model logit | all     | 65634 | -0.0091 |  -0.0103 |  -0.0078 |                  0.5193 |
| prodmu model logit - baseline model logit | QLD     | 16991 | -0.0105 |  -0.0128 |  -0.0082 |                  0.5262 |
| prodmu model logit - baseline model logit | VIC/SA  | 20830 | -0.0077 |  -0.0099 |  -0.0056 |                  0.5157 |
| prodmu model logit - baseline model logit | NSW     | 20018 | -0.0096 |  -0.0118 |  -0.0075 |                  0.5235 |
| prodmu model logit - baseline model logit | WA      |  7795 | -0.0088 |  -0.0124 |  -0.0055 |                  0.5034 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prod blend logit - baseline blend logit | prod blend logit - baseline blend logit 95%   |   prodmu blend logit - baseline blend logit | prodmu blend logit - baseline blend logit 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------------:|:------------------------------------------------|
| 2023 H1  |    8777 |                                   -0.0004 | -0.0009 to +0.0001                            |                                     -0.0004 | -0.0009 to +0.0001                              |
| 2023 H2  |    9187 |                                   -0.0005 | -0.0010 to +0.0001                            |                                     -0.0005 | -0.0010 to +0.0001                              |
| 2024 H1  |    8782 |                                   -0.0002 | -0.0007 to +0.0004                            |                                     -0.0001 | -0.0006 to +0.0005                              |
| 2024 H2  |    9038 |                                    0.0000 | -0.0005 to +0.0005                            |                                     -0.0001 | -0.0007 to +0.0005                              |
| 2025 H1  |    8786 |                                   -0.0001 | -0.0005 to +0.0003                            |                                     -0.0000 | -0.0005 to +0.0004                              |
| 2025 H2  |    8901 |                                    0.0001 | -0.0003 to +0.0005                            |                                      0.0002 | -0.0002 to +0.0007                              |
| 2026 H1  |    8690 |                                   -0.0000 | -0.0003 to +0.0003                            |                                      0.0000 | -0.0003 to +0.0003                              |
| 2026 H2  |    3473 |                                   -0.0000 | -0.0006 to +0.0005                            |                                     -0.0002 | -0.0007 to +0.0003                              |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   SP calibration c, NSW |   SP calibration c, WA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline logit a, NSW |   baseline logit b, NSW |   baseline logit a, WA |   baseline logit b, WA |   prod logit a |   prod logit b |   prod logit a, QLD |   prod logit b, QLD |   prod logit a, VIC/SA |   prod logit b, VIC/SA |   prod logit a, NSW |   prod logit b, NSW |   prod logit a, WA |   prod logit b, WA |   prodmu logit a |   prodmu logit b |   prodmu logit a, QLD |   prodmu logit b, QLD |   prodmu logit a, VIC/SA |   prodmu logit b, VIC/SA |   prodmu logit a, NSW |   prodmu logit b, NSW |   prodmu logit a, WA |   prodmu logit b, WA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|------------------------:|-----------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|------------------------:|------------------------:|-----------------------:|-----------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|--------------------:|--------------------:|-------------------:|-------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|----------------------:|----------------------:|---------------------:|---------------------:|
| 2023 |              1.167 | 10 Oct 2022 to 31 Dec 2022 |                   1.226 |                      1.169 |                   1.144 |                  1.119 |              0.110 |              1.093 |                   0.251 |                   1.053 |                      0.045 |                      1.139 |                   0.190 |                   1.015 |                 -0.310 |                  1.324 |          0.146 |          1.067 |               0.259 |               1.045 |                  0.095 |                  1.105 |               0.243 |               0.974 |             -0.311 |              1.328 |            0.146 |            1.065 |                 0.272 |                 1.033 |                    0.092 |                    1.107 |                 0.237 |                 0.975 |               -0.320 |                1.340 |
| 2024 |              1.117 | 14 Jul 2023 to 31 Dec 2023 |                   1.153 |                      1.080 |                   1.133 |                  1.098 |              0.111 |              1.039 |                   0.142 |                   1.043 |                      0.031 |                      1.060 |                   0.181 |                   1.010 |                 -0.005 |                  1.102 |          0.148 |          1.012 |               0.166 |               1.021 |                  0.080 |                  1.027 |               0.220 |               0.981 |              0.030 |              1.078 |            0.149 |            1.010 |                 0.175 |                 1.013 |                    0.075 |                    1.029 |                 0.215 |                 0.983 |                0.042 |                1.069 |
| 2025 |              1.156 | 17 Apr 2024 to 31 Dec 2024 |                   1.172 |                      1.148 |                   1.140 |                  1.182 |              0.082 |              1.097 |                   0.183 |                   1.030 |                      0.033 |                      1.125 |                   0.044 |                   1.109 |                  0.018 |                  1.170 |          0.110 |          1.075 |               0.204 |               1.010 |                  0.073 |                  1.096 |               0.071 |               1.088 |              0.034 |              1.158 |            0.113 |            1.072 |                 0.211 |                 1.004 |                    0.070 |                    1.098 |                 0.076 |                 1.084 |                0.036 |                1.156 |
| 2026 |              1.128 | 05 Jan 2025 to 31 Dec 2025 |                   1.113 |                      1.124 |                   1.137 |                  1.143 |              0.080 |              1.072 |                   0.165 |                   0.990 |                      0.049 |                      1.091 |                   0.050 |                   1.103 |                  0.012 |                  1.135 |          0.098 |          1.058 |               0.178 |               0.977 |                  0.069 |                  1.076 |               0.082 |               1.080 |              0.006 |              1.139 |            0.094 |            1.060 |                 0.183 |                 0.972 |                    0.058 |                    1.083 |                 0.080 |                 1.080 |               -0.005 |                1.147 |
