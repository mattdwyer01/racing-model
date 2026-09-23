# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, gpsx, comments (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

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
| baseline: model gbm               |     1.9187 |     1.9097 |     1.9039 |    1.8958 |     1.9080 |
| baseline: blend gbm               |     1.7915 |     1.7877 |     1.7845 |    1.7749 |     1.7855 |
| baseline: blend gbm (per state)   |     1.7912 |     1.7875 |     1.7839 |    1.7747 |     1.7852 |
| gpsx: model logit                 |     1.9504 |     1.9295 |     1.9342 |    1.9306 |     1.9366 |
| gpsx: blend logit                 |     1.7912 |     1.7872 |     1.7845 |    1.7752 |     1.7853 |
| gpsx: blend logit (per state)     |     1.7928 |     1.7870 |     1.7841 |    1.7749 |     1.7856 |
| gpsx: model gbm                   |     1.9189 |     1.9094 |     1.9016 |    1.8963 |     1.9074 |
| gpsx: blend gbm                   |     1.7915 |     1.7878 |     1.7844 |    1.7750 |     1.7855 |
| gpsx: blend gbm (per state)       |     1.7910 |     1.7877 |     1.7841 |    1.7747 |     1.7852 |
| comments: model logit             |     1.9286 |     1.9263 |     1.9316 |    1.9278 |     1.9286 |
| comments: blend logit             |     1.7903 |     1.7868 |     1.7845 |    1.7751 |     1.7850 |
| comments: blend logit (per state) |     1.7906 |     1.7867 |     1.7840 |    1.7749 |     1.7848 |
| comments: model gbm               |     1.9185 |     1.9140 |     1.9057 |    1.8980 |     1.9100 |
| comments: blend gbm               |     1.7915 |     1.7884 |     1.7849 |    1.7756 |     1.7859 |
| comments: blend gbm (per state)   |     1.7913 |     1.7880 |     1.7841 |    1.7753 |     1.7855 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5946 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5998 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5904 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5237 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5339 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5153 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0045 |  -0.0056 |  -0.0033 |                  0.5963 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0063 |  -0.0079 |  -0.0046 |                  0.6033 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0030 |  -0.0045 |  -0.0014 |                  0.5906 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5207 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0023 |  -0.0030 |  -0.0017 |                  0.5377 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0004 |  -0.0001 |   0.0010 |                  0.5068 |
| gpsx blend logit - SP raw            | all     | 37821 | -0.0047 |  -0.0059 |  -0.0034 |                  0.5930 |
| gpsx blend logit - SP raw            | QLD     | 16991 | -0.0066 |  -0.0084 |  -0.0045 |                  0.5972 |
| gpsx blend logit - SP raw            | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5895 |
| gpsx blend logit - SP calibrated     | all     | 37821 | -0.0010 |  -0.0016 |  -0.0004 |                  0.5227 |
| gpsx blend logit - SP calibrated     | QLD     | 16991 | -0.0026 |  -0.0036 |  -0.0016 |                  0.5347 |
| gpsx blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0004 |  -0.0004 |   0.0011 |                  0.5129 |
| gpsx blend gbm - SP raw              | all     | 37821 | -0.0045 |  -0.0055 |  -0.0033 |                  0.5943 |
| gpsx blend gbm - SP raw              | QLD     | 16991 | -0.0063 |  -0.0080 |  -0.0048 |                  0.6003 |
| gpsx blend gbm - SP raw              | VIC/SA  | 20830 | -0.0029 |  -0.0044 |  -0.0013 |                  0.5894 |
| gpsx blend gbm - SP calibrated       | all     | 37821 | -0.0008 |  -0.0012 |  -0.0003 |                  0.5224 |
| gpsx blend gbm - SP calibrated       | QLD     | 16991 | -0.0023 |  -0.0030 |  -0.0016 |                  0.5380 |
| gpsx blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0005 |  -0.0000 |   0.0011 |                  0.5096 |
| comments blend logit - SP raw        | all     | 37821 | -0.0050 |  -0.0063 |  -0.0036 |                  0.5891 |
| comments blend logit - SP raw        | QLD     | 16991 | -0.0074 |  -0.0094 |  -0.0053 |                  0.5963 |
| comments blend logit - SP raw        | VIC/SA  | 20830 | -0.0030 |  -0.0047 |  -0.0014 |                  0.5833 |
| comments blend logit - SP calibrated | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5226 |
| comments blend logit - SP calibrated | QLD     | 16991 | -0.0034 |  -0.0045 |  -0.0022 |                  0.5317 |
| comments blend logit - SP calibrated | VIC/SA  | 20830 |  0.0004 |  -0.0006 |   0.0014 |                  0.5153 |
| comments blend gbm - SP raw          | all     | 37821 | -0.0041 |  -0.0053 |  -0.0028 |                  0.5771 |
| comments blend gbm - SP raw          | QLD     | 16991 | -0.0072 |  -0.0091 |  -0.0053 |                  0.5875 |
| comments blend gbm - SP raw          | VIC/SA  | 20830 | -0.0015 |  -0.0032 |   0.0004 |                  0.5686 |
| comments blend gbm - SP calibrated   | all     | 37821 | -0.0004 |  -0.0012 |   0.0004 |                  0.5161 |
| comments blend gbm - SP calibrated   | QLD     | 16991 | -0.0032 |  -0.0044 |  -0.0020 |                  0.5334 |
| comments blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0019 |   0.0009 |   0.0029 |                  0.5021 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   gpsx logit | gpsx logit 95%     |   gpsx gbm | gpsx gbm 95%       |   comments logit | comments logit 95%   |   comments gbm | comments gbm 95%   |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|-----------------:|:---------------------|---------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0009   |        -0.0016 | -0.0027 to -0.0005 |      -0.0018 | -0.0039 to +0.0003 |    -0.0017 | -0.0028 to -0.0005 |          -0.0031 | -0.0054 to -0.0007   |        -0.0019 | -0.0039 to -0.0000 |
| 2023 H2  |    5233 |           0.0001 | -0.0020 to +0.0022   |         0.0004 | -0.0007 to +0.0015 |       0.0002 | -0.0021 to +0.0024 |     0.0005 | -0.0005 to +0.0016 |          -0.0003 | -0.0029 to +0.0020   |         0.0009 | -0.0011 to +0.0028 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |        -0.0011 | -0.0020 to -0.0002 |      -0.0016 | -0.0030 to -0.0003 |    -0.0008 | -0.0017 to +0.0001 |          -0.0020 | -0.0038 to -0.0002   |        -0.0007 | -0.0029 to +0.0012 |
| 2024 H2  |    5229 |          -0.0010 | -0.0024 to +0.0003   |        -0.0004 | -0.0012 to +0.0005 |      -0.0010 | -0.0024 to +0.0003 |    -0.0005 | -0.0015 to +0.0004 |          -0.0013 | -0.0031 to +0.0007   |         0.0005 | -0.0015 to +0.0027 |
| 2025 H1  |    5065 |          -0.0011 | -0.0027 to +0.0005   |        -0.0007 | -0.0019 to +0.0004 |      -0.0010 | -0.0026 to +0.0007 |    -0.0010 | -0.0023 to +0.0002 |          -0.0014 | -0.0033 to +0.0006   |        -0.0010 | -0.0032 to +0.0011 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0003   |        -0.0014 | -0.0025 to -0.0002 |      -0.0012 | -0.0028 to +0.0003 |    -0.0013 | -0.0025 to +0.0000 |          -0.0008 | -0.0027 to +0.0012   |        -0.0004 | -0.0025 to +0.0018 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0008 | -0.0022 to +0.0006 |      -0.0002 | -0.0017 to +0.0012 |    -0.0007 | -0.0022 to +0.0008 |          -0.0002 | -0.0019 to +0.0016   |         0.0000 | -0.0021 to +0.0022 |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0008   |        -0.0011 | -0.0034 to +0.0012 |      -0.0014 | -0.0036 to +0.0009 |    -0.0009 | -0.0032 to +0.0013 |          -0.0018 | -0.0046 to +0.0010   |        -0.0007 | -0.0044 to +0.0028 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5236 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0027 |  -0.0042 |  -0.0011 |                  0.5213 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5255 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0012 |  -0.0018 |  -0.0006 |                  0.5139 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0026 |  -0.0040 |  -0.0012 |                  0.5276 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0000 |  -0.0002 |   0.0001 |                  0.5027 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0008 |  -0.0016 |  -0.0000 |                  0.5236 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0016 |  -0.0033 |   0.0001 |                  0.5229 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5242 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5124 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0025 |  -0.0039 |  -0.0012 |                  0.5286 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0002 |                  0.4992 |
| comments blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0015 |  -0.0023 |  -0.0008 |                  0.5235 |
| comments blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0030 |  -0.0046 |  -0.0013 |                  0.5223 |
| comments blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0003 |  -0.0009 |   0.0002 |                  0.5244 |
| comments blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0009 |  -0.0017 |  -0.0000 |                  0.5156 |
| comments blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0025 |  -0.0043 |  -0.0008 |                  0.5254 |
| comments blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0004 |  -0.0002 |   0.0010 |                  0.5075 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5002 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5375 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0013 |  -0.0002 |                  0.4698 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5042 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0001 |  -0.0007 |   0.0009 |                  0.5388 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0006 |  -0.0012 |  -0.0000 |                  0.4759 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | all     | 37821 |  0.0002 |  -0.0002 |   0.0007 |                  0.5003 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | QLD     | 16991 |  0.0014 |   0.0007 |   0.0021 |                  0.5323 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4741 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5044 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | QLD     | 16991 |  0.0002 |  -0.0006 |   0.0010 |                  0.5355 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0007 |  -0.0013 |  -0.0000 |                  0.4790 |
| comments blend logit (per state) - comments blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0002 |                  0.5014 |
| comments blend logit (per state) - comments blend logit (pooled weights) | QLD     | 16991 |  0.0008 |   0.0002 |   0.0014 |                  0.5365 |
| comments blend logit (per state) - comments blend logit (pooled weights) | VIC/SA  | 20830 | -0.0009 |  -0.0014 |  -0.0004 |                  0.4729 |
| comments blend gbm (per state) - comments blend gbm (pooled weights)     | all     | 37821 | -0.0004 |  -0.0008 |  -0.0000 |                  0.5096 |
| comments blend gbm (per state) - comments blend gbm (pooled weights)     | QLD     | 16991 |  0.0011 |   0.0004 |   0.0018 |                  0.5372 |
| comments blend gbm (per state) - comments blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0017 |  -0.0021 |  -0.0012 |                  0.4871 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   gpsx blend logit (per state) - SP calibrated (per state) | gpsx blend logit (per state) - SP calibrated (per state) 95%   |   gpsx blend gbm (per state) - SP calibrated (per state) | gpsx blend gbm (per state) - SP calibrated (per state) 95%   |   comments blend logit (per state) - SP calibrated (per state) | comments blend logit (per state) - SP calibrated (per state) 95%   |   comments blend gbm (per state) - SP calibrated (per state) | comments blend gbm (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0003                                                 |                                                      -0.0024 | -0.0045 to -0.0003                                               |                                                    -0.0005 | -0.0034 to +0.0023                                             |                                                  -0.0026 | -0.0046 to -0.0006                                           |                                                        -0.0032 | -0.0058 to -0.0006                                                 |                                                      -0.0022 | -0.0046 to +0.0001                                               |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0021 to +0.0031                                                 |                                                       0.0005 | -0.0015 to +0.0028                                               |                                                     0.0017 | -0.0013 to +0.0049                                             |                                                   0.0003 | -0.0018 to +0.0025                                           |                                                         0.0000 | -0.0027 to +0.0029                                                 |                                                       0.0004 | -0.0020 to +0.0030                                               |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0002                                                 |                                                      -0.0002 | -0.0017 to +0.0011                                               |                                                    -0.0012 | -0.0027 to +0.0003                                             |                                                   0.0001 | -0.0013 to +0.0015                                           |                                                        -0.0017 | -0.0036 to +0.0002                                                 |                                                      -0.0006 | -0.0029 to +0.0014                                               |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0033 to -0.0002                                                 |                                                      -0.0017 | -0.0030 to -0.0004                                               |                                                    -0.0018 | -0.0034 to -0.0002                                             |                                                  -0.0017 | -0.0031 to -0.0003                                           |                                                        -0.0020 | -0.0039 to -0.0000                                                 |                                                      -0.0004 | -0.0027 to +0.0018                                               |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0029 to +0.0006                                                 |                                                      -0.0012 | -0.0027 to +0.0003                                               |                                                    -0.0011 | -0.0029 to +0.0006                                             |                                                  -0.0013 | -0.0029 to +0.0002                                           |                                                        -0.0015 | -0.0035 to +0.0004                                                 |                                                      -0.0017 | -0.0038 to +0.0003                                               |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0004                                                 |                                                      -0.0023 | -0.0038 to -0.0007                                               |                                                    -0.0019 | -0.0037 to -0.0002                                             |                                                  -0.0018 | -0.0034 to -0.0003                                           |                                                        -0.0017 | -0.0037 to +0.0003                                                 |                                                      -0.0014 | -0.0037 to +0.0008                                               |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0011                                                 |                                                      -0.0011 | -0.0027 to +0.0006                                               |                                                    -0.0006 | -0.0022 to +0.0011                                             |                                                  -0.0011 | -0.0028 to +0.0005                                           |                                                        -0.0005 | -0.0023 to +0.0014                                                 |                                                      -0.0003 | -0.0026 to +0.0020                                               |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0041 to +0.0011                                                 |                                                      -0.0010 | -0.0035 to +0.0016                                               |                                                    -0.0015 | -0.0040 to +0.0008                                             |                                                  -0.0009 | -0.0037 to +0.0019                                           |                                                        -0.0019 | -0.0047 to +0.0010                                                 |                                                      -0.0007 | -0.0045 to +0.0028                                               |

## Variants vs baseline (paired by race)

| comparison                                  | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| gpsx blend logit - baseline blend logit     | all     | 37821 |  0.0002 |  -0.0000 |   0.0004 |                  0.4703 |
| gpsx blend logit - baseline blend logit     | QLD     | 16991 |  0.0003 |  -0.0001 |   0.0008 |                  0.5009 |
| gpsx blend logit - baseline blend logit     | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0001 |                  0.4454 |
| gpsx blend gbm - baseline blend gbm         | all     | 37821 |  0.0000 |  -0.0001 |   0.0001 |                  0.4963 |
| gpsx blend gbm - baseline blend gbm         | QLD     | 16991 | -0.0000 |  -0.0002 |   0.0001 |                  0.4949 |
| gpsx blend gbm - baseline blend gbm         | VIC/SA  | 20830 |  0.0001 |  -0.0000 |   0.0002 |                  0.4975 |
| comments blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0004 |   0.0000 |                  0.5116 |
| comments blend logit - baseline blend logit | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0002 |                  0.5260 |
| comments blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0002 |   0.0004 |                  0.4999 |
| comments blend gbm - baseline blend gbm     | all     | 37821 |  0.0004 |  -0.0000 |   0.0008 |                  0.5024 |
| comments blend gbm - baseline blend gbm     | QLD     | 16991 | -0.0009 |  -0.0015 |  -0.0003 |                  0.5190 |
| comments blend gbm - baseline blend gbm     | VIC/SA  | 20830 |  0.0015 |   0.0009 |   0.0021 |                  0.4888 |
| gpsx model logit - baseline model logit     | all     | 37821 |  0.0036 |   0.0022 |   0.0050 |                  0.4608 |
| gpsx model logit - baseline model logit     | QLD     | 16991 |  0.0070 |   0.0039 |   0.0099 |                  0.4999 |
| gpsx model logit - baseline model logit     | VIC/SA  | 20830 |  0.0008 |   0.0003 |   0.0013 |                  0.4290 |
| gpsx model gbm - baseline model gbm         | all     | 37821 | -0.0006 |  -0.0017 |   0.0005 |                  0.4955 |
| gpsx model gbm - baseline model gbm         | QLD     | 16991 | -0.0022 |  -0.0042 |  -0.0003 |                  0.4959 |
| gpsx model gbm - baseline model gbm         | VIC/SA  | 20830 |  0.0008 |  -0.0005 |   0.0019 |                  0.4952 |
| comments model logit - baseline model logit | all     | 37821 | -0.0045 |  -0.0058 |  -0.0031 |                  0.5138 |
| comments model logit - baseline model logit | QLD     | 16991 | -0.0042 |  -0.0061 |  -0.0022 |                  0.5230 |
| comments model logit - baseline model logit | VIC/SA  | 20830 | -0.0047 |  -0.0065 |  -0.0027 |                  0.5062 |
| comments model gbm - baseline model gbm     | all     | 37821 |  0.0020 |   0.0001 |   0.0039 |                  0.4797 |
| comments model gbm - baseline model gbm     | QLD     | 16991 | -0.0010 |  -0.0035 |   0.0015 |                  0.4810 |
| comments model gbm - baseline model gbm     | VIC/SA  | 20830 |  0.0045 |   0.0017 |   0.0073 |                  0.4787 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   gpsx blend logit - baseline blend logit | gpsx blend logit - baseline blend logit 95%   |   gpsx blend gbm - baseline blend gbm | gpsx blend gbm - baseline blend gbm 95%   |   comments blend logit - baseline blend logit | comments blend logit - baseline blend logit 95%   |   comments blend gbm - baseline blend gbm | comments blend gbm - baseline blend gbm 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|----------------------------------------------:|:--------------------------------------------------|------------------------------------------:|:----------------------------------------------|
| 2023 H1  |    5012 |                                    0.0010 | +0.0002 to +0.0019                            |                               -0.0001 | -0.0003 to +0.0002                        |                                       -0.0003 | -0.0010 to +0.0004                                |                                   -0.0003 | -0.0014 to +0.0006                            |
| 2023 H2  |    5233 |                                    0.0001 | -0.0009 to +0.0012                            |                                0.0001 | -0.0001 to +0.0003                        |                                       -0.0004 | -0.0010 to +0.0003                                |                                    0.0004 | -0.0006 to +0.0014                            |
| 2024 H1  |    5145 |                                    0.0000 | -0.0002 to +0.0003                            |                                0.0003 | +0.0000 to +0.0005                        |                                       -0.0004 | -0.0010 to +0.0003                                |                                    0.0004 | -0.0010 to +0.0018                            |
| 2024 H2  |    5229 |                                   -0.0000 | -0.0003 to +0.0002                            |                               -0.0002 | -0.0004 to +0.0001                        |                                       -0.0003 | -0.0010 to +0.0003                                |                                    0.0009 | -0.0005 to +0.0023                            |
| 2025 H1  |    5065 |                                    0.0001 | -0.0002 to +0.0003                            |                               -0.0002 | -0.0006 to +0.0001                        |                                       -0.0003 | -0.0009 to +0.0003                                |                                   -0.0002 | -0.0014 to +0.0009                            |
| 2025 H2  |    5153 |                                    0.0000 | -0.0002 to +0.0003                            |                                0.0001 | -0.0002 to +0.0004                        |                                        0.0004 | -0.0003 to +0.0010                                |                                    0.0010 | -0.0002 to +0.0022                            |
| 2026 H1  |    4992 |                                   -0.0000 | -0.0003 to +0.0002                            |                                0.0001 | -0.0003 to +0.0005                        |                                        0.0000 | -0.0005 to +0.0005                                |                                    0.0008 | -0.0002 to +0.0019                            |
| 2026 H2  |    1992 |                                   -0.0001 | -0.0004 to +0.0003                            |                                0.0001 | -0.0005 to +0.0007                        |                                       -0.0004 | -0.0012 to +0.0004                                |                                    0.0003 | -0.0015 to +0.0021                            |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   gpsx logit a |   gpsx logit b |   gpsx logit a, QLD |   gpsx logit b, QLD |   gpsx logit a, VIC/SA |   gpsx logit b, VIC/SA |   gpsx gbm a |   gpsx gbm b |   gpsx gbm a, QLD |   gpsx gbm b, QLD |   gpsx gbm a, VIC/SA |   gpsx gbm b, VIC/SA |   comments logit a |   comments logit b |   comments logit a, QLD |   comments logit b, QLD |   comments logit a, VIC/SA |   comments logit b, VIC/SA |   comments gbm a |   comments gbm b |   comments gbm a, QLD |   comments gbm b, QLD |   comments gbm a, VIC/SA |   comments gbm b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.262 |                   1.048 |                      0.049 |                      1.134 |            0.091 |            1.126 |                 0.240 |                 1.061 |                   -0.021 |                    1.181 |          0.151 |          1.089 |               0.262 |               1.048 |                  0.049 |                  1.134 |        0.091 |        1.126 |             0.240 |             1.061 |               -0.021 |                1.181 |              0.180 |              1.068 |                   0.272 |                   1.038 |                      0.095 |                      1.103 |            0.151 |            1.083 |                 0.277 |                 1.034 |                    0.060 |                    1.123 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.102 |              1.041 |                   0.160 |                   1.030 |                      0.023 |                      1.066 |            0.077 |            1.055 |                 0.158 |                 1.029 |                   -0.020 |                    1.095 |          0.107 |          1.037 |               0.166 |               1.020 |                  0.022 |                  1.067 |        0.077 |        1.055 |             0.162 |             1.024 |               -0.027 |                1.099 |              0.138 |              1.015 |                   0.190 |                   1.004 |                      0.065 |                      1.038 |            0.172 |            0.983 |                 0.229 |                 0.973 |                    0.109 |                    1.002 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.180 |                   1.038 |                      0.047 |                      1.114 |            0.096 |            1.085 |                 0.181 |                 1.032 |                    0.007 |                    1.141 |          0.118 |          1.073 |               0.176 |               1.035 |                  0.048 |                  1.114 |        0.102 |        1.081 |             0.189 |             1.022 |                0.007 |                1.141 |              0.145 |              1.053 |                   0.200 |                   1.020 |                      0.083 |                      1.089 |            0.174 |            1.024 |                 0.248 |                 0.979 |                    0.102 |                    1.069 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.987 |                      0.051 |                      1.092 |            0.115 |            1.033 |                 0.189 |                 0.965 |                    0.049 |                    1.089 |          0.105 |          1.046 |               0.163 |               0.988 |                  0.051 |                  1.091 |        0.118 |        1.030 |             0.194 |             0.957 |                0.049 |                1.089 |              0.126 |              1.031 |                   0.185 |                   0.974 |                      0.071 |                      1.077 |            0.178 |            0.983 |                 0.242 |                 0.923 |                    0.125 |                    1.031 |
