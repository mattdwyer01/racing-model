# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prod, posmap, gpsx (see module docstring); all share the same fold builds
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
| baseline: model gbm               |     1.9190 |     1.9105 |     1.9040 |    1.8965 |     1.9084 |
| baseline: blend gbm               |     1.7914 |     1.7878 |     1.7846 |    1.7749 |     1.7855 |
| baseline: blend gbm (per state)   |     1.7911 |     1.7875 |     1.7841 |    1.7747 |     1.7852 |
| prod: model logit                 |     1.9278 |     1.9242 |     1.9310 |    1.9268 |     1.9275 |
| prod: blend logit                 |     1.7903 |     1.7867 |     1.7846 |    1.7751 |     1.7849 |
| prod: blend logit (per state)     |     1.7906 |     1.7866 |     1.7841 |    1.7748 |     1.7848 |
| prod: model gbm                   |     1.9179 |     1.9139 |     1.9056 |    1.8980 |     1.9098 |
| prod: blend gbm                   |     1.7912 |     1.7887 |     1.7850 |    1.7755 |     1.7859 |
| prod: blend gbm (per state)       |     1.7911 |     1.7883 |     1.7843 |    1.7752 |     1.7856 |
| posmap: model logit               |     1.9282 |     1.9243 |     1.9302 |    1.9271 |     1.9275 |
| posmap: blend logit               |     1.7904 |     1.7867 |     1.7846 |    1.7752 |     1.7850 |
| posmap: blend logit (per state)   |     1.7906 |     1.7865 |     1.7841 |    1.7750 |     1.7849 |
| posmap: model gbm                 |     1.9166 |     1.9138 |     1.9055 |    1.8984 |     1.9095 |
| posmap: blend gbm                 |     1.7912 |     1.7885 |     1.7851 |    1.7756 |     1.7859 |
| posmap: blend gbm (per state)     |     1.7909 |     1.7880 |     1.7845 |    1.7753 |     1.7855 |
| gpsx: model logit                 |     1.9396 |     1.9286 |     1.9317 |    1.9278 |     1.9323 |
| gpsx: blend logit                 |     1.7912 |     1.7873 |     1.7845 |    1.7751 |     1.7853 |
| gpsx: blend logit (per state)     |     1.7919 |     1.7870 |     1.7841 |    1.7750 |     1.7853 |
| gpsx: model gbm                   |     1.9162 |     1.9078 |     1.8977 |    1.8930 |     1.9046 |
| gpsx: blend gbm                   |     1.7916 |     1.7879 |     1.7843 |    1.7749 |     1.7855 |
| gpsx: blend gbm (per state)       |     1.7913 |     1.7877 |     1.7839 |    1.7747 |     1.7852 |

## Differences vs SP, pooled

| comparison                           | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw        | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5939 |
| baseline blend logit - SP raw        | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5995 |
| baseline blend logit - SP raw        | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5894 |
| baseline blend logit - SP calibrated | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5238 |
| baseline blend logit - SP calibrated | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5335 |
| baseline blend logit - SP calibrated | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5160 |
| baseline blend gbm - SP raw          | all     | 37821 | -0.0044 |  -0.0055 |  -0.0033 |                  0.5971 |
| baseline blend gbm - SP raw          | QLD     | 16991 | -0.0062 |  -0.0078 |  -0.0046 |                  0.6033 |
| baseline blend gbm - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0014 |                  0.5920 |
| baseline blend gbm - SP calibrated   | all     | 37821 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5200 |
| baseline blend gbm - SP calibrated   | QLD     | 16991 | -0.0022 |  -0.0029 |  -0.0016 |                  0.5341 |
| baseline blend gbm - SP calibrated   | VIC/SA  | 20830 |  0.0005 |  -0.0000 |   0.0010 |                  0.5084 |
| prod blend logit - SP raw            | all     | 37821 | -0.0050 |  -0.0063 |  -0.0037 |                  0.5891 |
| prod blend logit - SP raw            | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0053 |                  0.5956 |
| prod blend logit - SP raw            | VIC/SA  | 20830 | -0.0031 |  -0.0047 |  -0.0014 |                  0.5838 |
| prod blend logit - SP calibrated     | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5225 |
| prod blend logit - SP calibrated     | QLD     | 16991 | -0.0034 |  -0.0046 |  -0.0023 |                  0.5323 |
| prod blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0003 |  -0.0006 |   0.0013 |                  0.5145 |
| prod blend gbm - SP raw              | all     | 37821 | -0.0040 |  -0.0053 |  -0.0028 |                  0.5774 |
| prod blend gbm - SP raw              | QLD     | 16991 | -0.0070 |  -0.0088 |  -0.0052 |                  0.5883 |
| prod blend gbm - SP raw              | VIC/SA  | 20830 | -0.0016 |  -0.0033 |   0.0001 |                  0.5685 |
| prod blend gbm - SP calibrated       | all     | 37821 | -0.0004 |  -0.0011 |   0.0004 |                  0.5139 |
| prod blend gbm - SP calibrated       | QLD     | 16991 | -0.0030 |  -0.0042 |  -0.0018 |                  0.5272 |
| prod blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0018 |   0.0008 |   0.0028 |                  0.5031 |
| posmap blend logit - SP raw          | all     | 37821 | -0.0050 |  -0.0063 |  -0.0036 |                  0.5886 |
| posmap blend logit - SP raw          | QLD     | 16991 | -0.0074 |  -0.0094 |  -0.0053 |                  0.5964 |
| posmap blend logit - SP raw          | VIC/SA  | 20830 | -0.0030 |  -0.0047 |  -0.0013 |                  0.5823 |
| posmap blend logit - SP calibrated   | all     | 37821 | -0.0013 |  -0.0021 |  -0.0005 |                  0.5230 |
| posmap blend logit - SP calibrated   | QLD     | 16991 | -0.0034 |  -0.0046 |  -0.0021 |                  0.5342 |
| posmap blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0004 |  -0.0006 |   0.0014 |                  0.5138 |
| posmap blend gbm - SP raw            | all     | 37821 | -0.0040 |  -0.0053 |  -0.0028 |                  0.5759 |
| posmap blend gbm - SP raw            | QLD     | 16991 | -0.0072 |  -0.0091 |  -0.0052 |                  0.5861 |
| posmap blend gbm - SP raw            | VIC/SA  | 20830 | -0.0015 |  -0.0032 |   0.0003 |                  0.5677 |
| posmap blend gbm - SP calibrated     | all     | 37821 | -0.0004 |  -0.0012 |   0.0004 |                  0.5148 |
| posmap blend gbm - SP calibrated     | QLD     | 16991 | -0.0032 |  -0.0044 |  -0.0020 |                  0.5315 |
| posmap blend gbm - SP calibrated     | VIC/SA  | 20830 |  0.0019 |   0.0008 |   0.0030 |                  0.5012 |
| gpsx blend logit - SP raw            | all     | 37821 | -0.0046 |  -0.0058 |  -0.0034 |                  0.5927 |
| gpsx blend logit - SP raw            | QLD     | 16991 | -0.0067 |  -0.0086 |  -0.0049 |                  0.5969 |
| gpsx blend logit - SP raw            | VIC/SA  | 20830 | -0.0029 |  -0.0044 |  -0.0013 |                  0.5892 |
| gpsx blend logit - SP calibrated     | all     | 37821 | -0.0010 |  -0.0016 |  -0.0004 |                  0.5227 |
| gpsx blend logit - SP calibrated     | QLD     | 16991 | -0.0027 |  -0.0036 |  -0.0018 |                  0.5320 |
| gpsx blend logit - SP calibrated     | VIC/SA  | 20830 |  0.0005 |  -0.0002 |   0.0013 |                  0.5152 |
| gpsx blend gbm - SP raw              | all     | 37821 | -0.0045 |  -0.0056 |  -0.0032 |                  0.5929 |
| gpsx blend gbm - SP raw              | QLD     | 16991 | -0.0065 |  -0.0081 |  -0.0048 |                  0.5978 |
| gpsx blend gbm - SP raw              | VIC/SA  | 20830 | -0.0028 |  -0.0045 |  -0.0012 |                  0.5890 |
| gpsx blend gbm - SP calibrated       | all     | 37821 | -0.0008 |  -0.0012 |  -0.0003 |                  0.5200 |
| gpsx blend gbm - SP calibrated       | QLD     | 16991 | -0.0025 |  -0.0032 |  -0.0017 |                  0.5343 |
| gpsx blend gbm - SP calibrated       | VIC/SA  | 20830 |  0.0006 |  -0.0000 |   0.0012 |                  0.5084 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   baseline gbm | baseline gbm 95%   |   prod logit | prod logit 95%     |   prod gbm | prod gbm 95%       |   posmap logit | posmap logit 95%   |   posmap gbm | posmap gbm 95%     |   gpsx logit | gpsx logit 95%     |   gpsx gbm | gpsx gbm 95%       |
|:---------|--------:|-----------------:|:---------------------|---------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|---------------:|:-------------------|-------------:|:-------------------|-------------:|:-------------------|-----------:|:-------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0008   |        -0.0018 | -0.0029 to -0.0006 |      -0.0032 | -0.0055 to -0.0008 |    -0.0023 | -0.0040 to -0.0004 |        -0.0032 | -0.0057 to -0.0007 |      -0.0024 | -0.0044 to -0.0004 |      -0.0024 | -0.0044 to -0.0003 |    -0.0017 | -0.0031 to -0.0003 |
| 2023 H2  |    5233 |           0.0001 | -0.0018 to +0.0021   |         0.0005 | -0.0007 to +0.0017 |      -0.0002 | -0.0025 to +0.0022 |     0.0006 | -0.0013 to +0.0023 |        -0.0001 | -0.0025 to +0.0024 |       0.0006 | -0.0015 to +0.0026 |       0.0006 | -0.0014 to +0.0028 |     0.0008 | -0.0006 to +0.0021 |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0003   |        -0.0009 | -0.0018 to -0.0001 |      -0.0020 | -0.0037 to -0.0003 |     0.0000 | -0.0023 to +0.0022 |        -0.0021 | -0.0040 to -0.0002 |      -0.0003 | -0.0025 to +0.0017 |      -0.0013 | -0.0028 to +0.0001 |    -0.0006 | -0.0016 to +0.0004 |
| 2024 H2  |    5229 |          -0.0010 | -0.0023 to +0.0003   |        -0.0004 | -0.0012 to +0.0004 |      -0.0016 | -0.0034 to +0.0002 |     0.0004 | -0.0018 to +0.0026 |        -0.0015 | -0.0034 to +0.0002 |       0.0004 | -0.0018 to +0.0025 |      -0.0010 | -0.0024 to +0.0003 |    -0.0006 | -0.0015 to +0.0004 |
| 2025 H1  |    5065 |          -0.0011 | -0.0026 to +0.0005   |        -0.0006 | -0.0017 to +0.0004 |      -0.0013 | -0.0032 to +0.0007 |    -0.0009 | -0.0032 to +0.0012 |        -0.0013 | -0.0034 to +0.0010 |      -0.0007 | -0.0028 to +0.0015 |      -0.0011 | -0.0027 to +0.0005 |    -0.0011 | -0.0023 to +0.0002 |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |        -0.0013 | -0.0024 to -0.0003 |      -0.0007 | -0.0028 to +0.0013 |    -0.0003 | -0.0023 to +0.0019 |        -0.0007 | -0.0029 to +0.0013 |      -0.0002 | -0.0023 to +0.0021 |      -0.0011 | -0.0027 to +0.0004 |    -0.0015 | -0.0027 to -0.0002 |
| 2026 H1  |    4992 |          -0.0002 | -0.0017 to +0.0013   |        -0.0007 | -0.0021 to +0.0006 |      -0.0003 | -0.0019 to +0.0016 |    -0.0002 | -0.0023 to +0.0018 |        -0.0002 | -0.0019 to +0.0016 |      -0.0002 | -0.0025 to +0.0020 |      -0.0002 | -0.0016 to +0.0012 |    -0.0007 | -0.0022 to +0.0008 |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0009   |        -0.0011 | -0.0033 to +0.0013 |      -0.0017 | -0.0045 to +0.0009 |    -0.0002 | -0.0041 to +0.0033 |        -0.0015 | -0.0041 to +0.0013 |       0.0001 | -0.0033 to +0.0035 |      -0.0016 | -0.0038 to +0.0005 |    -0.0011 | -0.0034 to +0.0014 |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)             | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5239 |
| baseline blend logit (per state) - SP calibrated (per state)             | QLD     | 16991 | -0.0026 |  -0.0041 |  -0.0012 |                  0.5211 |
| baseline blend logit (per state) - SP calibrated (per state)             | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5261 |
| baseline blend gbm (per state) - SP calibrated (per state)               | all     | 37821 | -0.0011 |  -0.0018 |  -0.0006 |                  0.5072 |
| baseline blend gbm (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0026 |  -0.0039 |  -0.0012 |                  0.5276 |
| baseline blend gbm (per state) - SP calibrated (per state)               | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0001 |                  0.4905 |
| prod blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5226 |
| prod blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0030 |  -0.0046 |  -0.0013 |                  0.5217 |
| prod blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0004 |  -0.0009 |   0.0002 |                  0.5233 |
| prod blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0008 |  -0.0017 |  -0.0000 |                  0.5137 |
| prod blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0023 |  -0.0041 |  -0.0006 |                  0.5202 |
| prod blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 |  0.0005 |  -0.0002 |   0.0011 |                  0.5084 |
| posmap blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5233 |
| posmap blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0029 |  -0.0045 |  -0.0013 |                  0.5243 |
| posmap blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0010 |   0.0003 |                  0.5225 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0009 |  -0.0017 |  -0.0000 |                  0.5141 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0026 |  -0.0043 |  -0.0009 |                  0.5247 |
| posmap blend gbm (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 |  0.0005 |  -0.0002 |   0.0012 |                  0.5054 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0010 |  -0.0017 |  -0.0003 |                  0.5227 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0021 |  -0.0037 |  -0.0005 |                  0.5212 |
| gpsx blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0001 |                  0.5239 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | all     | 37821 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5138 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | QLD     | 16991 | -0.0025 |  -0.0038 |  -0.0010 |                  0.5266 |
| gpsx blend gbm (per state) - SP calibrated (per state)                   | VIC/SA  | 20830 | -0.0000 |  -0.0002 |   0.0002 |                  0.5035 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5008 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights) | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4703 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5033 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | QLD     | 16991 |  0.0000 |  -0.0008 |   0.0008 |                  0.5380 |
| baseline blend gbm (per state) - baseline blend gbm (pooled weights)     | VIC/SA  | 20830 | -0.0006 |  -0.0012 |  -0.0001 |                  0.4750 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | all     | 37821 | -0.0001 |  -0.0005 |   0.0002 |                  0.5020 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | QLD     | 16991 |  0.0008 |   0.0003 |   0.0014 |                  0.5370 |
| prod blend logit (per state) - prod blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4735 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | all     | 37821 | -0.0004 |  -0.0008 |   0.0000 |                  0.5072 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | QLD     | 16991 |  0.0010 |   0.0004 |   0.0017 |                  0.5343 |
| prod blend gbm (per state) - prod blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0015 |  -0.0020 |  -0.0011 |                  0.4850 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | all     | 37821 | -0.0001 |  -0.0005 |   0.0002 |                  0.5037 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | QLD     | 16991 |  0.0009 |   0.0003 |   0.0014 |                  0.5398 |
| posmap blend logit (per state) - posmap blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0009 |  -0.0014 |  -0.0005 |                  0.4742 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | all     | 37821 | -0.0004 |  -0.0008 |  -0.0001 |                  0.5089 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | QLD     | 16991 |  0.0010 |   0.0004 |   0.0016 |                  0.5362 |
| posmap blend gbm (per state) - posmap blend gbm (pooled weights)         | VIC/SA  | 20830 | -0.0016 |  -0.0020 |  -0.0011 |                  0.4867 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | all     | 37821 | -0.0000 |  -0.0004 |   0.0004 |                  0.4994 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | QLD     | 16991 |  0.0010 |   0.0003 |   0.0017 |                  0.5342 |
| gpsx blend logit (per state) - gpsx blend logit (pooled weights)         | VIC/SA  | 20830 | -0.0008 |  -0.0014 |  -0.0003 |                  0.4709 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | all     | 37821 | -0.0003 |  -0.0008 |   0.0002 |                  0.5049 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | QLD     | 16991 |  0.0004 |  -0.0004 |   0.0012 |                  0.5361 |
| gpsx blend gbm (per state) - gpsx blend gbm (pooled weights)             | VIC/SA  | 20830 | -0.0008 |  -0.0014 |  -0.0002 |                  0.4794 |
| SP calibrated (per state) - SP calibrated (pooled)                       | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                       | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                       | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   baseline blend gbm (per state) - SP calibrated (per state) | baseline blend gbm (per state) - SP calibrated (per state) 95%   |   prod blend logit (per state) - SP calibrated (per state) | prod blend logit (per state) - SP calibrated (per state) 95%   |   prod blend gbm (per state) - SP calibrated (per state) | prod blend gbm (per state) - SP calibrated (per state) 95%   |   posmap blend logit (per state) - SP calibrated (per state) | posmap blend logit (per state) - SP calibrated (per state) 95%   |   posmap blend gbm (per state) - SP calibrated (per state) | posmap blend gbm (per state) - SP calibrated (per state) 95%   |   gpsx blend logit (per state) - SP calibrated (per state) | gpsx blend logit (per state) - SP calibrated (per state) 95%   |   gpsx blend gbm (per state) - SP calibrated (per state) | gpsx blend gbm (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|-------------------------------------------------------------:|:-----------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|---------------------------------------------------------:|:-------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0052 to -0.0003                                                 |                                                      -0.0026 | -0.0047 to -0.0005                                               |                                                    -0.0033 | -0.0059 to -0.0007                                             |                                                  -0.0024 | -0.0049 to +0.0000                                           |                                                      -0.0033 | -0.0060 to -0.0006                                               |                                                    -0.0028 | -0.0051 to -0.0005                                             |                                                    -0.0020 | -0.0046 to +0.0005                                             |                                                  -0.0027 | -0.0050 to -0.0004                                           |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0031                                                 |                                                       0.0004 | -0.0019 to +0.0026                                               |                                                     0.0002 | -0.0026 to +0.0030                                             |                                                   0.0003 | -0.0022 to +0.0027                                           |                                                       0.0002 | -0.0026 to +0.0029                                               |                                                     0.0002 | -0.0020 to +0.0025                                             |                                                     0.0015 | -0.0014 to +0.0042                                             |                                                   0.0009 | -0.0014 to +0.0034                                           |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0027 to +0.0002                                                 |                                                      -0.0003 | -0.0015 to +0.0009                                               |                                                    -0.0017 | -0.0037 to +0.0001                                             |                                                   0.0000 | -0.0022 to +0.0021                                           |                                                      -0.0018 | -0.0037 to -0.0000                                               |                                                    -0.0003 | -0.0026 to +0.0020                                             |                                                    -0.0011 | -0.0027 to +0.0005                                             |                                                   0.0001 | -0.0014 to +0.0014                                           |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0032 to -0.0002                                                 |                                                      -0.0016 | -0.0029 to -0.0005                                               |                                                    -0.0021 | -0.0039 to -0.0002                                             |                                                  -0.0005 | -0.0028 to +0.0016                                           |                                                      -0.0021 | -0.0038 to -0.0002                                               |                                                    -0.0006 | -0.0028 to +0.0017                                             |                                                    -0.0018 | -0.0035 to -0.0002                                             |                                                  -0.0017 | -0.0031 to -0.0003                                           |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0006                                                 |                                                      -0.0009 | -0.0024 to +0.0006                                               |                                                    -0.0014 | -0.0034 to +0.0007                                             |                                                  -0.0016 | -0.0038 to +0.0008                                           |                                                      -0.0014 | -0.0035 to +0.0006                                               |                                                    -0.0013 | -0.0035 to +0.0009                                             |                                                    -0.0012 | -0.0028 to +0.0006                                             |                                                  -0.0014 | -0.0030 to +0.0002                                           |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0004                                                 |                                                      -0.0021 | -0.0035 to -0.0006                                               |                                                    -0.0016 | -0.0036 to +0.0005                                             |                                                  -0.0011 | -0.0033 to +0.0012                                           |                                                      -0.0016 | -0.0037 to +0.0005                                               |                                                    -0.0011 | -0.0035 to +0.0012                                             |                                                    -0.0020 | -0.0037 to -0.0003                                             |                                                  -0.0021 | -0.0037 to -0.0004                                           |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0021 to +0.0012                                                 |                                                      -0.0011 | -0.0027 to +0.0005                                               |                                                    -0.0006 | -0.0024 to +0.0013                                             |                                                  -0.0006 | -0.0029 to +0.0015                                           |                                                      -0.0004 | -0.0023 to +0.0014                                               |                                                    -0.0005 | -0.0028 to +0.0017                                             |                                                    -0.0004 | -0.0020 to +0.0013                                             |                                                  -0.0010 | -0.0027 to +0.0007                                           |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0040 to +0.0009                                                 |                                                      -0.0008 | -0.0033 to +0.0019                                               |                                                    -0.0018 | -0.0046 to +0.0009                                             |                                                  -0.0003 | -0.0040 to +0.0033                                           |                                                      -0.0016 | -0.0045 to +0.0010                                               |                                                    -0.0001 | -0.0040 to +0.0038                                             |                                                    -0.0017 | -0.0044 to +0.0007                                             |                                                  -0.0012 | -0.0039 to +0.0015                                           |

## Position map vs production inputs (paired by race)

| comparison                            | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| posmap blend logit - prod blend logit | all     | 37821 |  0.0001 |  -0.0000 |   0.0001 |                  0.4989 |
| posmap blend logit - prod blend logit | QLD     | 16991 |  0.0000 |  -0.0001 |   0.0002 |                  0.4989 |
| posmap blend logit - prod blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0000 |   0.0002 |                  0.4988 |
| posmap blend gbm - prod blend gbm     | all     | 37821 | -0.0000 |  -0.0002 |   0.0002 |                  0.5055 |
| posmap blend gbm - prod blend gbm     | QLD     | 16991 | -0.0002 |  -0.0004 |   0.0001 |                  0.5084 |
| posmap blend gbm - prod blend gbm     | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0004 |                  0.5031 |
| posmap model logit - prod model logit | all     | 37821 | -0.0000 |  -0.0005 |   0.0005 |                  0.5004 |
| posmap model logit - prod model logit | QLD     | 16991 | -0.0001 |  -0.0009 |   0.0008 |                  0.4979 |
| posmap model logit - prod model logit | VIC/SA  | 20830 |  0.0000 |  -0.0006 |   0.0007 |                  0.5025 |
| posmap model gbm - prod model gbm     | all     | 37821 | -0.0003 |  -0.0014 |   0.0007 |                  0.5009 |
| posmap model gbm - prod model gbm     | QLD     | 16991 | -0.0011 |  -0.0025 |   0.0005 |                  0.5032 |
| posmap model gbm - prod model gbm     | VIC/SA  | 20830 |  0.0002 |  -0.0012 |   0.0016 |                  0.4991 |

| period   |   races |   posmap blend logit - prod blend logit | posmap blend logit - prod blend logit 95%   |   posmap blend gbm - prod blend gbm | posmap blend gbm - prod blend gbm 95%   |
|:---------|--------:|----------------------------------------:|:--------------------------------------------|------------------------------------:|:----------------------------------------|
| 2023 H1  |    5012 |                                  0.0000 | -0.0003 to +0.0004                          |                             -0.0001 | -0.0006 to +0.0004                      |
| 2023 H2  |    5233 |                                  0.0001 | -0.0002 to +0.0005                          |                             -0.0000 | -0.0005 to +0.0005                      |
| 2024 H1  |    5145 |                                 -0.0000 | -0.0002 to +0.0001                          |                             -0.0003 | -0.0008 to +0.0001                      |
| 2024 H2  |    5229 |                                  0.0000 | -0.0001 to +0.0002                          |                             -0.0001 | -0.0005 to +0.0004                      |
| 2025 H1  |    5065 |                                  0.0000 | -0.0001 to +0.0002                          |                              0.0002 | -0.0002 to +0.0007                      |
| 2025 H2  |    5153 |                                 -0.0000 | -0.0002 to +0.0002                          |                              0.0001 | -0.0004 to +0.0005                      |
| 2026 H1  |    4992 |                                  0.0001 | -0.0001 to +0.0003                          |                              0.0000 | -0.0004 to +0.0005                      |
| 2026 H2  |    1992 |                                  0.0002 | -0.0000 to +0.0005                          |                              0.0003 | -0.0004 to +0.0011                      |

## Variants vs baseline (paired by race)

| comparison                                | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod blend logit - baseline blend logit   | all     | 37821 | -0.0002 |  -0.0005 |   0.0000 |                  0.5095 |
| prod blend logit - baseline blend logit   | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5244 |
| prod blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0000 |  -0.0003 |   0.0003 |                  0.4974 |
| prod blend gbm - baseline blend gbm       | all     | 37821 |  0.0004 |  -0.0000 |   0.0008 |                  0.4984 |
| prod blend gbm - baseline blend gbm       | QLD     | 16991 | -0.0008 |  -0.0014 |  -0.0001 |                  0.5122 |
| prod blend gbm - baseline blend gbm       | VIC/SA  | 20830 |  0.0013 |   0.0007 |   0.0020 |                  0.4872 |
| posmap blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5123 |
| posmap blend logit - baseline blend logit | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5269 |
| posmap blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0001 |  -0.0003 |   0.0004 |                  0.5005 |
| posmap blend gbm - baseline blend gbm     | all     | 37821 |  0.0004 |  -0.0001 |   0.0008 |                  0.4998 |
| posmap blend gbm - baseline blend gbm     | QLD     | 16991 | -0.0010 |  -0.0016 |  -0.0003 |                  0.5150 |
| posmap blend gbm - baseline blend gbm     | VIC/SA  | 20830 |  0.0015 |   0.0008 |   0.0021 |                  0.4874 |
| gpsx blend logit - baseline blend logit   | all     | 37821 |  0.0002 |   0.0000 |   0.0003 |                  0.4896 |
| gpsx blend logit - baseline blend logit   | QLD     | 16991 |  0.0002 |  -0.0001 |   0.0004 |                  0.4875 |
| gpsx blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0002 |   0.0000 |   0.0003 |                  0.4913 |
| gpsx blend gbm - baseline blend gbm       | all     | 37821 | -0.0000 |  -0.0002 |   0.0001 |                  0.4999 |
| gpsx blend gbm - baseline blend gbm       | QLD     | 16991 | -0.0002 |  -0.0005 |  -0.0000 |                  0.5096 |
| gpsx blend gbm - baseline blend gbm       | VIC/SA  | 20830 |  0.0001 |  -0.0001 |   0.0003 |                  0.4919 |
| prod model logit - baseline model logit   | all     | 37821 | -0.0056 |  -0.0070 |  -0.0041 |                  0.5127 |
| prod model logit - baseline model logit   | QLD     | 16991 | -0.0050 |  -0.0071 |  -0.0030 |                  0.5208 |
| prod model logit - baseline model logit   | VIC/SA  | 20830 | -0.0060 |  -0.0080 |  -0.0040 |                  0.5060 |
| prod model gbm - baseline model gbm       | all     | 37821 |  0.0014 |  -0.0006 |   0.0033 |                  0.4829 |
| prod model gbm - baseline model gbm       | QLD     | 16991 |  0.0001 |  -0.0027 |   0.0029 |                  0.4804 |
| prod model gbm - baseline model gbm       | VIC/SA  | 20830 |  0.0024 |  -0.0004 |   0.0052 |                  0.4850 |
| posmap model logit - baseline model logit | all     | 37821 | -0.0056 |  -0.0071 |  -0.0040 |                  0.5130 |
| posmap model logit - baseline model logit | QLD     | 16991 | -0.0051 |  -0.0073 |  -0.0029 |                  0.5167 |
| posmap model logit - baseline model logit | VIC/SA  | 20830 | -0.0060 |  -0.0081 |  -0.0038 |                  0.5101 |
| posmap model gbm - baseline model gbm     | all     | 37821 |  0.0010 |  -0.0010 |   0.0031 |                  0.4849 |
| posmap model gbm - baseline model gbm     | QLD     | 16991 | -0.0010 |  -0.0039 |   0.0019 |                  0.4840 |
| posmap model gbm - baseline model gbm     | VIC/SA  | 20830 |  0.0027 |  -0.0003 |   0.0057 |                  0.4857 |
| gpsx model logit - baseline model logit   | all     | 37821 | -0.0008 |  -0.0018 |   0.0004 |                  0.5076 |
| gpsx model logit - baseline model logit   | QLD     | 16991 |  0.0011 |  -0.0008 |   0.0030 |                  0.5003 |
| gpsx model logit - baseline model logit   | VIC/SA  | 20830 | -0.0023 |  -0.0036 |  -0.0010 |                  0.5135 |
| gpsx model gbm - baseline model gbm       | all     | 37821 | -0.0038 |  -0.0052 |  -0.0025 |                  0.5035 |
| gpsx model gbm - baseline model gbm       | QLD     | 16991 | -0.0030 |  -0.0050 |  -0.0010 |                  0.5001 |
| gpsx model gbm - baseline model gbm       | VIC/SA  | 20830 | -0.0045 |  -0.0063 |  -0.0026 |                  0.5063 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prod blend logit - baseline blend logit | prod blend logit - baseline blend logit 95%   |   prod blend gbm - baseline blend gbm | prod blend gbm - baseline blend gbm 95%   |   posmap blend logit - baseline blend logit | posmap blend logit - baseline blend logit 95%   |   posmap blend gbm - baseline blend gbm | posmap blend gbm - baseline blend gbm 95%   |   gpsx blend logit - baseline blend logit | gpsx blend logit - baseline blend logit 95%   |   gpsx blend gbm - baseline blend gbm | gpsx blend gbm - baseline blend gbm 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|--------------------------------------------:|:------------------------------------------------|----------------------------------------:|:--------------------------------------------|------------------------------------------:|:----------------------------------------------|--------------------------------------:|:------------------------------------------|
| 2023 H1  |    5012 |                                   -0.0004 | -0.0011 to +0.0003                            |                               -0.0005 | -0.0014 to +0.0004                        |                                     -0.0004 | -0.0013 to +0.0005                              |                                 -0.0006 | -0.0016 to +0.0005                          |                                    0.0004 | -0.0001 to +0.0010                            |                                0.0000 | -0.0004 to +0.0005                        |
| 2023 H2  |    5233 |                                   -0.0003 | -0.0011 to +0.0004                            |                                0.0001 | -0.0008 to +0.0009                        |                                     -0.0002 | -0.0011 to +0.0007                              |                                  0.0001 | -0.0010 to +0.0012                          |                                    0.0005 | -0.0001 to +0.0012                            |                                0.0003 | -0.0002 to +0.0007                        |
| 2024 H1  |    5145 |                                   -0.0004 | -0.0011 to +0.0002                            |                                0.0009 | -0.0006 to +0.0024                        |                                     -0.0004 | -0.0012 to +0.0003                              |                                  0.0006 | -0.0009 to +0.0020                          |                                    0.0003 | +0.0000 to +0.0005                            |                                0.0003 | +0.0000 to +0.0006                        |
| 2024 H2  |    5229 |                                   -0.0005 | -0.0012 to +0.0001                            |                                0.0008 | -0.0007 to +0.0023                        |                                     -0.0005 | -0.0012 to +0.0002                              |                                  0.0007 | -0.0007 to +0.0022                          |                                   -0.0000 | -0.0002 to +0.0003                            |                               -0.0002 | -0.0005 to +0.0001                        |
| 2025 H1  |    5065 |                                   -0.0002 | -0.0009 to +0.0005                            |                               -0.0003 | -0.0015 to +0.0011                        |                                     -0.0002 | -0.0010 to +0.0006                              |                                 -0.0001 | -0.0014 to +0.0013                          |                                   -0.0001 | -0.0003 to +0.0002                            |                               -0.0005 | -0.0009 to -0.0001                        |
| 2025 H2  |    5153 |                                    0.0005 | -0.0003 to +0.0012                            |                                0.0010 | -0.0002 to +0.0024                        |                                      0.0004 | -0.0003 to +0.0012                              |                                  0.0011 | -0.0002 to +0.0024                          |                                    0.0001 | -0.0002 to +0.0004                            |                               -0.0002 | -0.0006 to +0.0002                        |
| 2026 H1  |    4992 |                                   -0.0001 | -0.0006 to +0.0005                            |                                0.0004 | -0.0006 to +0.0015                        |                                      0.0000 | -0.0005 to +0.0006                              |                                  0.0005 | -0.0007 to +0.0016                          |                                    0.0000 | -0.0002 to +0.0003                            |                               -0.0000 | -0.0005 to +0.0004                        |
| 2026 H2  |    1992 |                                   -0.0003 | -0.0012 to +0.0005                            |                                0.0008 | -0.0009 to +0.0025                        |                                     -0.0001 | -0.0010 to +0.0008                              |                                  0.0011 | -0.0007 to +0.0029                          |                                   -0.0002 | -0.0006 to +0.0002                            |                               -0.0000 | -0.0008 to +0.0007                        |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   baseline gbm a |   baseline gbm b |   baseline gbm a, QLD |   baseline gbm b, QLD |   baseline gbm a, VIC/SA |   baseline gbm b, VIC/SA |   prod logit a |   prod logit b |   prod logit a, QLD |   prod logit b, QLD |   prod logit a, VIC/SA |   prod logit b, VIC/SA |   prod gbm a |   prod gbm b |   prod gbm a, QLD |   prod gbm b, QLD |   prod gbm a, VIC/SA |   prod gbm b, VIC/SA |   posmap logit a |   posmap logit b |   posmap logit a, QLD |   posmap logit b, QLD |   posmap logit a, VIC/SA |   posmap logit b, VIC/SA |   posmap gbm a |   posmap gbm b |   posmap gbm a, QLD |   posmap gbm b, QLD |   posmap gbm a, VIC/SA |   posmap gbm b, VIC/SA |   gpsx logit a |   gpsx logit b |   gpsx logit a, QLD |   gpsx logit b, QLD |   gpsx logit a, VIC/SA |   gpsx logit b, VIC/SA |   gpsx gbm a |   gpsx gbm b |   gpsx gbm a, QLD |   gpsx gbm b, QLD |   gpsx gbm a, VIC/SA |   gpsx gbm b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|-----------------:|-----------------:|----------------------:|----------------------:|-------------------------:|-------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|-------------:|-------------:|------------------:|------------------:|---------------------:|---------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |            0.093 |            1.123 |                 0.247 |                 1.054 |                   -0.018 |                    1.179 |          0.181 |          1.067 |               0.274 |               1.037 |                  0.096 |                  1.102 |        0.142 |        1.088 |             0.267 |             1.038 |                0.053 |                1.127 |            0.192 |            1.061 |                 0.273 |                 1.037 |                    0.117 |                    1.089 |          0.157 |          1.080 |               0.249 |               1.055 |                  0.092 |                  1.101 |          0.150 |          1.088 |               0.266 |               1.045 |                  0.053 |                  1.130 |        0.112 |        1.110 |             0.263 |             1.044 |                0.002 |                1.165 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |            0.070 |            1.060 |                 0.146 |                 1.039 |                   -0.021 |                    1.095 |          0.135 |          1.016 |               0.183 |               1.009 |                  0.070 |                  1.035 |        0.178 |        0.979 |             0.232 |             0.971 |                0.118 |                0.995 |            0.138 |            1.014 |                 0.182 |                 1.009 |                    0.077 |                    1.031 |          0.175 |          0.980 |               0.237 |               0.966 |                  0.109 |                  1.001 |          0.106 |          1.037 |               0.169 |               1.021 |                  0.024 |                  1.065 |        0.081 |        1.050 |             0.168 |             1.019 |               -0.020 |                1.095 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |            0.088 |            1.092 |                 0.177 |                 1.035 |                   -0.006 |                    1.151 |          0.149 |          1.049 |               0.201 |               1.018 |                  0.091 |                  1.083 |        0.177 |        1.021 |             0.244 |             0.981 |                0.111 |                1.060 |            0.154 |            1.046 |                 0.202 |                 1.018 |                    0.101 |                    1.076 |          0.180 |          1.019 |               0.246 |               0.979 |                  0.114 |                  1.059 |          0.116 |          1.074 |               0.181 |               1.034 |                  0.044 |                  1.115 |        0.104 |        1.078 |             0.200 |             1.015 |                0.004 |                1.143 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |            0.115 |            1.033 |                 0.189 |                 0.966 |                    0.050 |                    1.088 |          0.124 |          1.032 |               0.182 |               0.976 |                  0.072 |                  1.076 |        0.177 |        0.983 |             0.238 |             0.924 |                0.126 |                1.030 |            0.127 |            1.029 |                 0.185 |                 0.973 |                    0.075 |                    1.074 |          0.179 |          0.983 |               0.237 |               0.927 |                  0.131 |                  1.027 |          0.107 |          1.044 |               0.171 |               0.985 |                  0.051 |                  1.090 |        0.127 |        1.022 |             0.195 |             0.958 |                0.067 |                1.075 |
