# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prod, posmap (see module docstring); all share the same fold builds
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
| baseline: model gbm               |     1.9176 |     1.9091 |     1.9043 |    1.8981 |     1.9081 |
| baseline: blend gbm               |     1.7914 |     1.7877 |     1.7846 |    1.7750 |     1.7855 |
| baseline: blend gbm (per state)   |     1.7912 |     1.7875 |     1.7841 |    1.7749 |     1.7853 |
| prod: model logit                 |     1.9295 |     1.9257 |     1.9315 |    1.9270 |     1.9286 |
| prod: blend logit                 |     1.7903 |     1.7868 |     1.7845 |    1.7750 |     1.7849 |
| prod: blend logit (per state)     |     1.7903 |     1.7866 |     1.7840 |    1.7748 |     1.7847 |
| prod: model gbm                   |     1.9194 |     1.9149 |     1.9066 |    1.8970 |     1.9106 |
| prod: blend gbm                   |     1.7915 |     1.7888 |     1.7850 |    1.7753 |     1.7860 |
| prod: blend gbm (per state)       |     1.7913 |     1.7884 |     1.7843 |    1.7750 |     1.7856 |
| posmap: model logit               |     1.9299 |     1.9255 |     1.9307 |    1.9270 |     1.9284 |
| posmap: blend logit               |     1.7903 |     1.7868 |     1.7845 |    1.7751 |     1.7850 |
| posmap: blend logit (per state)   |     1.7903 |     1.7866 |     1.7840 |    1.7749 |     1.7848 |
| posmap: model gbm                 |     1.9173 |     1.9141 |     1.9052 |    1.8985 |     1.9097 |
| posmap: blend gbm                 |     1.7914 |     1.7886 |     1.7849 |    1.7756 |     1.7859 |
| posmap: blend gbm (per state)     |     1.7913 |     1.7881 |     1.7843 |    1.7753 |     1.7856 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5946 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5998 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5904 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5237 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5339 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5153 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0033 |                  0.5962 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0062 |  -0.0078 |  -0.0046 |                  0.6017 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0030 |  -0.0045 |  -0.0014 |                  0.5917 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5192 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0022 |  -0.0029 |  -0.0016 |                  0.5336 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0004 |  -0.0001 |   0.0010 |                  0.5073 |
| prod blend logit - SP raw            | all     | 37821 | -0.0050 |  -0.0063 |  -0.0038 |                  0.5896 |
| prod blend logit - SP raw            | QLD     | 16991 | -0.0075 |  -0.0093 |  -0.0054 |                  0.5966 |
| prod blend logit - SP raw            | VIC/SA  | 20830 | -0.0031 |  -0.0047 |  -0.0014 |                  0.5840 |
| prod blend logit - SP calibrated     | all     | 37821 | -0.0013 |  -0.0021 |  -0.0007 |                  0.5234 |
| prod blend logit - SP calibrated     | QLD     | 16991 | -0.0035 |  -0.0046 |  -0.0023 |                  0.5339 |
| prod blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0004 |  -0.0005 |   0.0013 |                  0.5149 |
| prod blend gbm - SP raw              | all     | 37821 | -0.0040 |  -0.0053 |  -0.0027 |                  0.5771 |
| prod blend gbm - SP raw              | QLD     | 16991 | -0.0070 |  -0.0089 |  -0.0052 |                  0.5867 |
| prod blend gbm - SP raw              | VIC/SA  | 20830 | -0.0015 |  -0.0032 |   0.0003 |                  0.5692 |
| prod blend gbm - SP calibrated       | all     | 37821 | -0.0003 |  -0.0010 |   0.0005 |                  0.5157 |
| prod blend gbm - SP calibrated       | QLD     | 16991 | -0.0030 |  -0.0042 |  -0.0018 |                  0.5313 |
| prod blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0019 |   0.0009 |   0.0029 |                  0.5029 |
| posmap blend logit - SP raw          | all     | 37821 | -0.0050 |  -0.0063 |  -0.0036 |                  0.5896 |
| posmap blend logit - SP raw          | QLD     | 16991 | -0.0074 |  -0.0094 |  -0.0054 |                  0.5970 |
| posmap blend logit - SP raw          | VIC/SA  | 20830 | -0.0030 |  -0.0047 |  -0.0014 |                  0.5835 |
| posmap blend logit - SP calibrated   | all     | 37821 | -0.0013 |  -0.0021 |  -0.0005 |                  0.5221 |
| posmap blend logit - SP calibrated   | QLD     | 16991 | -0.0035 |  -0.0046 |  -0.0022 |                  0.5335 |
| posmap blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0004 |  -0.0006 |   0.0014 |                  0.5128 |
| posmap blend gbm - SP raw            | all     | 37821 | -0.0040 |  -0.0053 |  -0.0028 |                  0.5783 |
| posmap blend gbm - SP raw            | QLD     | 16991 | -0.0071 |  -0.0089 |  -0.0051 |                  0.5885 |
| posmap blend gbm - SP raw            | VIC/SA  | 20830 | -0.0015 |  -0.0033 |   0.0003 |                  0.5699 |
| posmap blend gbm - SP calibrated     | all     | 37821 | -0.0003 |  -0.0012 |   0.0004 |                  0.5157 |
| posmap blend gbm - SP calibrated     | QLD     | 16991 | -0.0031 |  -0.0043 |  -0.0019 |                  0.5335 |
| posmap blend gbm - SP calibrated     | VIC/SA  | 20830 |  0.0019 |   0.0008 |   0.0030 |                  0.5012 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   prod logit | prod logit 95%     |   prod gbm | prod gbm 95%       |   posmap logit | posmap logit 95%   |   posmap gbm | posmap gbm 95%     |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|---------------:|:-------------------|-------------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0009   |        -0.0017 | -0.0029 to -0.0005 |      -0.0031 | -0.0052 to -0.0009 |    -0.0020 | -0.0038 to -0.0001 |        -0.0031 | -0.0054 to -0.0008 |      -0.0022 | -0.0044 to -0.0001 |
| 2023 H2  |    5233 |           0.0001 | -0.0020 to +0.0022   |         0.0004 | -0.0008 to +0.0015 |      -0.0004 | -0.0026 to +0.0017 |     0.0008 | -0.0010 to +0.0026 |        -0.0003 | -0.0028 to +0.0020 |       0.0009 | -0.0013 to +0.0030 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |        -0.0011 | -0.0020 to -0.0003 |      -0.0020 | -0.0037 to -0.0002 |    -0.0002 | -0.0023 to +0.0021 |        -0.0020 | -0.0038 to -0.0002 |      -0.0003 | -0.0027 to +0.0017 |
| 2024 H2  |    5229 |          -0.0010 | -0.0024 to +0.0003   |        -0.0003 | -0.0012 to +0.0006 |      -0.0014 | -0.0031 to +0.0003 |     0.0008 | -0.0014 to +0.0029 |        -0.0014 | -0.0031 to +0.0005 |       0.0006 | -0.0017 to +0.0029 |
| 2025 H1  |    5065 |          -0.0011 | -0.0027 to +0.0005   |        -0.0007 | -0.0018 to +0.0003 |      -0.0012 | -0.0032 to +0.0009 |    -0.0008 | -0.0029 to +0.0012 |        -0.0012 | -0.0032 to +0.0008 |      -0.0008 | -0.0029 to +0.0013 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0003   |        -0.0012 | -0.0023 to -0.0002 |      -0.0009 | -0.0029 to +0.0011 |    -0.0004 | -0.0025 to +0.0017 |        -0.0009 | -0.0029 to +0.0012 |      -0.0005 | -0.0026 to +0.0016 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0006 | -0.0020 to +0.0008 |      -0.0003 | -0.0020 to +0.0015 |    -0.0003 | -0.0025 to +0.0020 |        -0.0002 | -0.0019 to +0.0017 |      -0.0000 | -0.0021 to +0.0020 |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0008   |        -0.0011 | -0.0033 to +0.0012 |      -0.0018 | -0.0044 to +0.0008 |    -0.0008 | -0.0043 to +0.0027 |        -0.0017 | -0.0045 to +0.0011 |      -0.0006 | -0.0041 to +0.0028 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5236 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0027 |  -0.0042 |  -0.0011 |                  0.5213 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5255 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5066 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0025 |  -0.0039 |  -0.0011 |                  0.5250 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0002 |                  0.4916 |
| prod blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0016 |  -0.0024 |  -0.0009 |                  0.5239 |
| prod blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0032 |  -0.0048 |  -0.0017 |                  0.5243 |
| prod blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5236 |
| prod blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0008 |  -0.0016 |   0.0001 |                  0.5164 |
| prod blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0023 |  -0.0040 |  -0.0006 |                  0.5259 |
| prod blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 |  0.0005 |  -0.0001 |   0.0010 |                  0.5087 |
| posmap blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0016 |  -0.0024 |  -0.0009 |                  0.5226 |
| posmap blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0032 |  -0.0047 |  -0.0017 |                  0.5234 |
| posmap blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0009 |   0.0003 |                  0.5219 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0008 |  -0.0016 |   0.0001 |                  0.5158 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0023 |  -0.0041 |  -0.0005 |                  0.5267 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 |  0.0004 |  -0.0003 |   0.0011 |                  0.5068 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5002 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5375 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0013 |  -0.0002 |                  0.4698 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5043 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0001 |  -0.0007 |   0.0009 |                  0.5389 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0006 |  -0.0012 |   0.0000 |                  0.4760 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5024 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | QLD     | 16991 |  0.0006 |   0.0001 |   0.0011 |                  0.5389 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4727 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | all     | 37821 | -0.0004 |  -0.0008 |  -0.0000 |                  0.5092 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | QLD     | 16991 |  0.0011 |   0.0004 |   0.0018 |                  0.5389 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0016 |  -0.0021 |  -0.0012 |                  0.4849 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5034 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | QLD     | 16991 |  0.0006 |   0.0001 |   0.0011 |                  0.5415 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4723 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | all     | 37821 | -0.0004 |  -0.0007 |   0.0000 |                  0.5091 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | QLD     | 16991 |  0.0012 |   0.0006 |   0.0018 |                  0.5358 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | VIC/SA  | 20830 | -0.0016 |  -0.0020 |  -0.0011 |                  0.4874 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   prod blend logit (per state) - SP calibrated (per state) | prod blend logit (per state) - SP calibrated (per state) 95%   |   prod blend gbm (per state) - SP calibrated (per state) | prod blend gbm (per state) - SP calibrated (per state) 95%   |   posmap blend logit (per state) - SP calibrated (per state) | posmap blend logit (per state) - SP calibrated (per state) 95%   |   posmap blend gbm (per state) - SP calibrated (per state) | posmap blend gbm (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0003                                                 |                                                      -0.0025 | -0.0046 to -0.0004                                               |                                                    -0.0033 | -0.0055 to -0.0010                                             |                                                  -0.0024 | -0.0049 to +0.0000                                           |                                                      -0.0033 | -0.0057 to -0.0010                                               |                                                    -0.0024 | -0.0049 to -0.0001                                             |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0021 to +0.0031                                                 |                                                       0.0006 | -0.0015 to +0.0029                                               |                                                    -0.0005 | -0.0028 to +0.0019                                             |                                                   0.0007 | -0.0018 to +0.0031                                           |                                                      -0.0004 | -0.0029 to +0.0021                                               |                                                     0.0007 | -0.0018 to +0.0033                                             |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0002                                                 |                                                      -0.0003 | -0.0017 to +0.0011                                               |                                                    -0.0016 | -0.0034 to +0.0002                                             |                                                  -0.0002 | -0.0024 to +0.0021                                           |                                                      -0.0017 | -0.0036 to +0.0001                                               |                                                    -0.0004 | -0.0027 to +0.0017                                             |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0033 to -0.0002                                                 |                                                      -0.0016 | -0.0029 to -0.0003                                               |                                                    -0.0021 | -0.0039 to -0.0003                                             |                                                  -0.0000 | -0.0023 to +0.0022                                           |                                                      -0.0020 | -0.0040 to -0.0002                                               |                                                    -0.0003 | -0.0028 to +0.0021                                             |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0029 to +0.0006                                                 |                                                      -0.0010 | -0.0025 to +0.0004                                               |                                                    -0.0014 | -0.0035 to +0.0007                                             |                                                  -0.0015 | -0.0036 to +0.0006                                           |                                                      -0.0014 | -0.0034 to +0.0007                                               |                                                    -0.0013 | -0.0034 to +0.0008                                             |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0004                                                 |                                                      -0.0021 | -0.0037 to -0.0005                                               |                                                    -0.0018 | -0.0039 to +0.0003                                             |                                                  -0.0013 | -0.0036 to +0.0008                                           |                                                      -0.0018 | -0.0039 to +0.0003                                               |                                                    -0.0014 | -0.0036 to +0.0008                                             |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0011                                                 |                                                      -0.0009 | -0.0025 to +0.0008                                               |                                                    -0.0006 | -0.0026 to +0.0013                                             |                                                  -0.0007 | -0.0030 to +0.0015                                           |                                                      -0.0005 | -0.0023 to +0.0014                                               |                                                    -0.0004 | -0.0026 to +0.0019                                             |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0041 to +0.0011                                                 |                                                      -0.0009 | -0.0033 to +0.0016                                               |                                                    -0.0019 | -0.0048 to +0.0009                                             |                                                  -0.0009 | -0.0046 to +0.0028                                           |                                                      -0.0018 | -0.0046 to +0.0011                                               |                                                    -0.0007 | -0.0044 to +0.0029                                             |

## Position map vs production inputs (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| posmap blend logit - prod blend logit | all     | 37821 |  0.0000 |  -0.0000 |   0.0001 |                  0.4973 |
| posmap blend logit - prod blend logit | QLD     | 16991 |  0.0000 |  -0.0001 |   0.0001 |                  0.4982 |
| posmap blend logit - prod blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0000 |   0.0002 |                  0.4965 |
| posmap blend gbm - prod blend gbm     | all     | 37821 | -0.0001 |  -0.0002 |   0.0001 |                  0.5003 |
| posmap blend gbm - prod blend gbm     | QLD     | 16991 | -0.0001 |  -0.0003 |   0.0002 |                  0.5021 |
| posmap blend gbm - prod blend gbm     | VIC/SA  | 20830 | -0.0000 |  -0.0003 |   0.0002 |                  0.4988 |
| posmap model logit - prod model logit | all     | 37821 | -0.0002 |  -0.0006 |   0.0003 |                  0.5000 |
| posmap model logit - prod model logit | QLD     | 16991 | -0.0001 |  -0.0008 |   0.0007 |                  0.4959 |
| posmap model logit - prod model logit | VIC/SA  | 20830 | -0.0002 |  -0.0008 |   0.0003 |                  0.5033 |
| posmap model gbm - prod model gbm     | all     | 37821 | -0.0009 |  -0.0019 |   0.0001 |                  0.5059 |
| posmap model gbm - prod model gbm     | QLD     | 16991 | -0.0004 |  -0.0019 |   0.0011 |                  0.5018 |
| posmap model gbm - prod model gbm     | VIC/SA  | 20830 | -0.0013 |  -0.0027 |  -0.0000 |                  0.5093 |

| period   |   races |   posmap blend logit - prod blend logit | posmap blend logit - prod blend logit 95%   |   posmap blend gbm - prod blend gbm | posmap blend gbm - prod blend gbm 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|------------------------------------:|:----------------------------------------|
| 2023 H1  |    5012 |                                 -0.0000 | -0.0003 to +0.0003                          |                             -0.0002 | -0.0008 to +0.0004                      |
| 2023 H2  |    5233 |                                  0.0001 | -0.0002 to +0.0004                          |                              0.0000 | -0.0005 to +0.0006                      |
| 2024 H1  |    5145 |                                 -0.0000 | -0.0002 to +0.0001                          |                             -0.0002 | -0.0007 to +0.0003                      |
| 2024 H2  |    5229 |                                  0.0000 | -0.0001 to +0.0002                          |                             -0.0002 | -0.0007 to +0.0003                      |
| 2025 H1  |    5065 |                                  0.0000 | -0.0001 to +0.0002                          |                             -0.0000 | -0.0004 to +0.0004                      |
| 2025 H2  |    5153 |                                 -0.0000 | -0.0002 to +0.0002                          |                             -0.0001 | -0.0005 to +0.0003                      |
| 2026 H1  |    4992 |                                  0.0001 | -0.0000 to +0.0003                          |                              0.0003 | -0.0002 to +0.0007                      |
| 2026 H2  |    1992 |                                  0.0001 | -0.0001 to +0.0003                          |                              0.0002 | -0.0005 to +0.0010                      |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod blend logit - baseline blend logit   | all     | 37821 | -0.0002 |  -0.0005 |   0.0000 |                  0.5096 |
| prod blend logit - baseline blend logit   | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0002 |                  0.5227 |
| prod blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0000 |  -0.0003 |   0.0003 |                  0.4988 |
| prod blend gbm - baseline blend gbm       | all     | 37821 |  0.0005 |   0.0001 |   0.0009 |                  0.4995 |
| prod blend gbm - baseline blend gbm       | QLD     | 16991 | -0.0008 |  -0.0015 |  -0.0002 |                  0.5144 |
| prod blend gbm - baseline blend gbm       | VIC/SA  | 20830 |  0.0015 |   0.0009 |   0.0021 |                  0.4874 |
| posmap blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0004 |   0.0001 |                  0.5098 |
| posmap blend logit - baseline blend logit | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5216 |
| posmap blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0002 |   0.0004 |                  0.5001 |
| posmap blend gbm - baseline blend gbm     | all     | 37821 |  0.0004 |  -0.0000 |   0.0009 |                  0.5003 |
| posmap blend gbm - baseline blend gbm     | QLD     | 16991 | -0.0008 |  -0.0015 |  -0.0002 |                  0.5173 |
| posmap blend gbm - baseline blend gbm     | VIC/SA  | 20830 |  0.0014 |   0.0008 |   0.0021 |                  0.4864 |
| prod model logit - baseline model logit   | all     | 37821 | -0.0045 |  -0.0060 |  -0.0030 |                  0.5103 |
| prod model logit - baseline model logit   | QLD     | 16991 | -0.0045 |  -0.0067 |  -0.0023 |                  0.5138 |
| prod model logit - baseline model logit   | VIC/SA  | 20830 | -0.0045 |  -0.0064 |  -0.0026 |                  0.5074 |
| prod model gbm - baseline model gbm       | all     | 37821 |  0.0025 |   0.0006 |   0.0045 |                  0.4831 |
| prod model gbm - baseline model gbm       | QLD     | 16991 | -0.0006 |  -0.0033 |   0.0021 |                  0.4836 |
| prod model gbm - baseline model gbm       | VIC/SA  | 20830 |  0.0051 |   0.0024 |   0.0076 |                  0.4828 |
| posmap model logit - baseline model logit | all     | 37821 | -0.0047 |  -0.0063 |  -0.0032 |                  0.5088 |
| posmap model logit - baseline model logit | QLD     | 16991 | -0.0045 |  -0.0069 |  -0.0021 |                  0.5118 |
| posmap model logit - baseline model logit | VIC/SA  | 20830 | -0.0048 |  -0.0068 |  -0.0029 |                  0.5064 |
| posmap model gbm - baseline model gbm     | all     | 37821 |  0.0016 |  -0.0005 |   0.0036 |                  0.4831 |
| posmap model gbm - baseline model gbm     | QLD     | 16991 | -0.0010 |  -0.0038 |   0.0018 |                  0.4824 |
| posmap model gbm - baseline model gbm     | VIC/SA  | 20830 |  0.0037 |   0.0008 |   0.0064 |                  0.4837 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prod blend logit - baseline blend logit | prod blend logit - baseline blend logit 95%   |   prod blend gbm - baseline blend gbm | prod blend gbm - baseline blend gbm 95%   |   posmap blend logit - baseline blend logit | posmap blend logit - baseline blend logit 95%   |   posmap blend gbm - baseline blend gbm | posmap blend gbm - baseline blend gbm 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|--------------------------------------------:|:------------------------------------------------|----------------------------------------:|:--------------------------------------------|
| 2023 H1  |    5012 |                                   -0.0003 | -0.0010 to +0.0004                            |                               -0.0003 | -0.0012 to +0.0006                        |                                     -0.0003 | -0.0011 to +0.0004                              |                                 -0.0005 | -0.0017 to +0.0007                          |
| 2023 H2  |    5233 |                                   -0.0005 | -0.0012 to +0.0002                            |                                0.0004 | -0.0004 to +0.0013                        |                                     -0.0004 | -0.0012 to +0.0004                              |                                  0.0005 | -0.0007 to +0.0017                          |
| 2024 H1  |    5145 |                                   -0.0003 | -0.0010 to +0.0003                            |                                0.0010 | -0.0005 to +0.0024                        |                                     -0.0004 | -0.0011 to +0.0003                              |                                  0.0008 | -0.0006 to +0.0022                          |
| 2024 H2  |    5229 |                                   -0.0004 | -0.0010 to +0.0002                            |                                0.0011 | -0.0003 to +0.0026                        |                                     -0.0004 | -0.0010 to +0.0002                              |                                  0.0009 | -0.0006 to +0.0024                          |
| 2025 H1  |    5065 |                                   -0.0002 | -0.0008 to +0.0005                            |                               -0.0000 | -0.0011 to +0.0012                        |                                     -0.0001 | -0.0009 to +0.0006                              |                                 -0.0000 | -0.0012 to +0.0012                          |
| 2025 H2  |    5153 |                                    0.0003 | -0.0004 to +0.0009                            |                                0.0008 | -0.0003 to +0.0019                        |                                      0.0003 | -0.0004 to +0.0010                              |                                  0.0007 | -0.0005 to +0.0020                          |
| 2026 H1  |    4992 |                                   -0.0001 | -0.0005 to +0.0005                            |                                0.0003 | -0.0007 to +0.0014                        |                                      0.0001 | -0.0005 to +0.0006                              |                                  0.0005 | -0.0006 to +0.0016                          |
| 2026 H2  |    1992 |                                   -0.0004 | -0.0012 to +0.0004                            |                                0.0003 | -0.0014 to +0.0018                        |                                     -0.0003 | -0.0012 to +0.0005                              |                                  0.0005 | -0.0012 to +0.0022                          |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   prod logit a |   prod logit b |   prod logit a, QLD |   prod logit b, QLD |   prod logit a, VIC/SA |   prod logit b, VIC/SA |   prod gbm a |   prod gbm b |   prod gbm a, QLD |   prod gbm b, QLD |   prod gbm a, VIC/SA |   prod gbm b, VIC/SA |   posmap logit a |   posmap logit b |   posmap logit a, QLD |   posmap logit b, QLD |   posmap logit a, VIC/SA |   posmap logit b, VIC/SA |   posmap gbm a |   posmap gbm b |   posmap gbm a, QLD |   posmap gbm b, QLD |   posmap gbm a, VIC/SA |   posmap gbm b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.151 |              1.089 |                   0.262 |                   1.048 |                      0.049 |                      1.134 |            0.096 |            1.122 |                 0.248 |                 1.054 |                   -0.018 |                    1.178 |          0.168 |          1.076 |               0.227 |               1.069 |                  0.095 |                  1.103 |        0.144 |        1.087 |             0.274 |             1.035 |                0.053 |                1.128 |            0.176 |            1.071 |                 0.228 |                 1.069 |                    0.112 |                    1.092 |          0.173 |          1.065 |               0.277 |               1.030 |                  0.100 |                  1.093 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.102 |              1.041 |                   0.160 |                   1.030 |                      0.023 |                      1.066 |            0.076 |            1.056 |                 0.159 |                 1.028 |                   -0.022 |                    1.097 |          0.135 |          1.016 |               0.186 |               1.006 |                  0.063 |                  1.040 |        0.180 |        0.979 |             0.234 |             0.971 |                0.121 |                0.994 |            0.136 |            1.015 |                 0.185 |                 1.006 |                    0.067 |                    1.037 |          0.181 |          0.976 |               0.242 |               0.962 |                  0.115 |                  0.997 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.180 |                   1.038 |                      0.047 |                      1.114 |            0.090 |            1.089 |                 0.178 |                 1.034 |                   -0.002 |                    1.147 |          0.147 |          1.052 |               0.203 |               1.017 |                  0.083 |                  1.089 |        0.166 |        1.031 |             0.239 |             0.987 |                0.094 |                1.075 |            0.153 |            1.048 |                 0.205 |                 1.015 |                    0.092 |                    1.083 |          0.172 |          1.026 |               0.243 |               0.983 |                  0.102 |                  1.069 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.987 |                      0.051 |                      1.092 |            0.112 |            1.035 |                 0.187 |                 0.967 |                    0.046 |                    1.091 |          0.125 |          1.031 |               0.184 |               0.974 |                  0.071 |                  1.077 |        0.175 |        0.985 |             0.235 |             0.928 |                0.125 |                1.031 |            0.128 |            1.029 |                 0.187 |                 0.971 |                    0.075 |                    1.075 |          0.173 |          0.987 |               0.240 |               0.924 |                  0.117 |                  1.037 |
