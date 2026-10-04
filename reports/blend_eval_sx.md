# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races (plus RACING_EXTRA_STATES), one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, wet, wet-sx-wet, wet-sx-track, wet-sx-both (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                                       |       2023 |       2024 |       2025 |      2026 |     pooled |
|:--------------------------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races                                 | 10245.0000 | 10374.0000 | 10218.0000 | 7473.0000 | 38310.0000 |
| SP raw                                |     1.7934 |     1.7934 |     1.7891 |    1.7789 |     1.7894 |
| SP calibrated                         |     1.7920 |     1.7885 |     1.7856 |    1.7735 |     1.7857 |
| SP calibrated (per state)             |     1.7921 |     1.7885 |     1.7857 |    1.7735 |     1.7858 |
| baseline: model logit                 |     1.9340 |     1.9306 |     1.9348 |    1.9300 |     1.9325 |
| baseline: blend logit                 |     1.7907 |     1.7872 |     1.7844 |    1.7727 |     1.7846 |
| baseline: blend logit (per state)     |     1.7911 |     1.7870 |     1.7841 |    1.7724 |     1.7844 |
| wet: model logit                      |     1.9236 |     1.9206 |     1.9269 |    1.9192 |     1.9228 |
| wet: blend logit                      |     1.7901 |     1.7866 |     1.7846 |    1.7725 |     1.7843 |
| wet: blend logit (per state)          |     1.7905 |     1.7864 |     1.7841 |    1.7721 |     1.7841 |
| wet-sx-wet: model logit               |     1.9236 |     1.9205 |     1.9268 |    1.9188 |     1.9227 |
| wet-sx-wet: blend logit               |     1.7901 |     1.7866 |     1.7846 |    1.7725 |     1.7842 |
| wet-sx-wet: blend logit (per state)   |     1.7905 |     1.7864 |     1.7841 |    1.7721 |     1.7841 |
| wet-sx-track: model logit             |     1.9258 |     1.9208 |     1.9278 |    1.9194 |     1.9237 |
| wet-sx-track: blend logit             |     1.7903 |     1.7865 |     1.7847 |    1.7725 |     1.7843 |
| wet-sx-track: blend logit (per state) |     1.7908 |     1.7863 |     1.7841 |    1.7720 |     1.7841 |
| wet-sx-both: model logit              |     1.9258 |     1.9207 |     1.9277 |    1.9190 |     1.9236 |
| wet-sx-both: blend logit              |     1.7903 |     1.7865 |     1.7847 |    1.7724 |     1.7843 |
| wet-sx-both: blend logit (per state)  |     1.7907 |     1.7863 |     1.7841 |    1.7719 |     1.7841 |

## Differences vs SP, pooled

| comparison                               | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-----------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw            | all     | 38310 | -0.0049 |  -0.0061 |  -0.0036 |                  0.5942 |
| baseline blend logit - SP raw            | QLD     | 17228 | -0.0070 |  -0.0088 |  -0.0052 |                  0.6001 |
| baseline blend logit - SP raw            | VIC/SA  | 21082 | -0.0031 |  -0.0046 |  -0.0014 |                  0.5894 |
| baseline blend logit - SP calibrated     | all     | 38310 | -0.0011 |  -0.0018 |  -0.0005 |                  0.5241 |
| baseline blend logit - SP calibrated     | QLD     | 17228 | -0.0030 |  -0.0040 |  -0.0021 |                  0.5343 |
| baseline blend logit - SP calibrated     | VIC/SA  | 21082 |  0.0004 |  -0.0004 |   0.0011 |                  0.5157 |
| wet blend logit - SP raw                 | all     | 38310 | -0.0052 |  -0.0065 |  -0.0039 |                  0.5877 |
| wet blend logit - SP raw                 | QLD     | 17228 | -0.0078 |  -0.0098 |  -0.0059 |                  0.5954 |
| wet blend logit - SP raw                 | VIC/SA  | 21082 | -0.0030 |  -0.0047 |  -0.0013 |                  0.5815 |
| wet blend logit - SP calibrated          | all     | 38310 | -0.0015 |  -0.0022 |  -0.0007 |                  0.5233 |
| wet blend logit - SP calibrated          | QLD     | 17228 | -0.0038 |  -0.0049 |  -0.0026 |                  0.5362 |
| wet blend logit - SP calibrated          | VIC/SA  | 21082 |  0.0004 |  -0.0005 |   0.0013 |                  0.5128 |
| wet-sx-wet blend logit - SP raw          | all     | 38310 | -0.0052 |  -0.0065 |  -0.0039 |                  0.5881 |
| wet-sx-wet blend logit - SP raw          | QLD     | 17228 | -0.0079 |  -0.0097 |  -0.0059 |                  0.5959 |
| wet-sx-wet blend logit - SP raw          | VIC/SA  | 21082 | -0.0030 |  -0.0047 |  -0.0013 |                  0.5818 |
| wet-sx-wet blend logit - SP calibrated   | all     | 38310 | -0.0015 |  -0.0022 |  -0.0007 |                  0.5235 |
| wet-sx-wet blend logit - SP calibrated   | QLD     | 17228 | -0.0038 |  -0.0049 |  -0.0027 |                  0.5369 |
| wet-sx-wet blend logit - SP calibrated   | VIC/SA  | 21082 |  0.0004 |  -0.0005 |   0.0013 |                  0.5126 |
| wet-sx-track blend logit - SP raw        | all     | 38310 | -0.0051 |  -0.0065 |  -0.0039 |                  0.5871 |
| wet-sx-track blend logit - SP raw        | QLD     | 17228 | -0.0080 |  -0.0100 |  -0.0060 |                  0.5953 |
| wet-sx-track blend logit - SP raw        | VIC/SA  | 21082 | -0.0028 |  -0.0045 |  -0.0011 |                  0.5804 |
| wet-sx-track blend logit - SP calibrated | all     | 38310 | -0.0014 |  -0.0021 |  -0.0007 |                  0.5222 |
| wet-sx-track blend logit - SP calibrated | QLD     | 17228 | -0.0039 |  -0.0051 |  -0.0027 |                  0.5346 |
| wet-sx-track blend logit - SP calibrated | VIC/SA  | 21082 |  0.0006 |  -0.0004 |   0.0017 |                  0.5120 |
| wet-sx-both blend logit - SP raw         | all     | 38310 | -0.0051 |  -0.0064 |  -0.0039 |                  0.5873 |
| wet-sx-both blend logit - SP raw         | QLD     | 17228 | -0.0080 |  -0.0100 |  -0.0060 |                  0.5958 |
| wet-sx-both blend logit - SP raw         | VIC/SA  | 21082 | -0.0028 |  -0.0045 |  -0.0010 |                  0.5804 |
| wet-sx-both blend logit - SP calibrated  | all     | 38310 | -0.0014 |  -0.0022 |  -0.0006 |                  0.5216 |
| wet-sx-both blend logit - SP calibrated  | QLD     | 17228 | -0.0040 |  -0.0052 |  -0.0027 |                  0.5347 |
| wet-sx-both blend logit - SP calibrated  | VIC/SA  | 21082 |  0.0006 |  -0.0003 |   0.0016 |                  0.5109 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   wet logit | wet logit 95%      |   wet-sx-wet logit | wet-sx-wet logit 95%   |   wet-sx-track logit | wet-sx-track logit 95%   |   wet-sx-both logit | wet-sx-both logit 95%   |
|:---------|--------:|-----------------:|:---------------------|------------:|:-------------------|-------------------:|:-----------------------|---------------------:|:-------------------------|--------------------:|:------------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0047 to -0.0009   |     -0.0036 | -0.0061 to -0.0010 |            -0.0036 | -0.0060 to -0.0012     |              -0.0035 | -0.0062 to -0.0009       |             -0.0035 | -0.0061 to -0.0010      |
| 2023 H2  |    5233 |           0.0001 | -0.0018 to +0.0021   |     -0.0003 | -0.0029 to +0.0020 |            -0.0004 | -0.0028 to +0.0021     |               0.0000 | -0.0028 to +0.0027       |             -0.0000 | -0.0026 to +0.0027      |
| 2024 H1  |    5145 |          -0.0016 | -0.0029 to -0.0004   |     -0.0021 | -0.0039 to -0.0003 |            -0.0021 | -0.0039 to -0.0003     |              -0.0022 | -0.0040 to -0.0004       |             -0.0022 | -0.0041 to -0.0004      |
| 2024 H2  |    5229 |          -0.0010 | -0.0024 to +0.0003   |     -0.0017 | -0.0034 to +0.0000 |            -0.0017 | -0.0035 to +0.0000     |              -0.0017 | -0.0036 to +0.0001       |             -0.0018 | -0.0036 to +0.0001      |
| 2025 H1  |    5065 |          -0.0011 | -0.0026 to +0.0005   |     -0.0013 | -0.0033 to +0.0007 |            -0.0013 | -0.0032 to +0.0007     |              -0.0013 | -0.0035 to +0.0008       |             -0.0013 | -0.0035 to +0.0009      |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |     -0.0006 | -0.0026 to +0.0014 |            -0.0006 | -0.0026 to +0.0014     |              -0.0005 | -0.0027 to +0.0017       |             -0.0005 | -0.0026 to +0.0017      |
| 2026 H1  |    4992 |          -0.0002 | -0.0018 to +0.0012   |     -0.0003 | -0.0019 to +0.0014 |            -0.0003 | -0.0020 to +0.0015     |              -0.0003 | -0.0021 to +0.0014       |             -0.0003 | -0.0021 to +0.0014      |
| 2026 H2  |    2481 |          -0.0018 | -0.0037 to +0.0003   |     -0.0023 | -0.0046 to +0.0000 |            -0.0024 | -0.0046 to +0.0001     |              -0.0024 | -0.0047 to -0.0001       |             -0.0024 | -0.0046 to -0.0000      |

## Per-state weights (QLD, VIC/SA, NSW, WA fitted separately on the same blend window)

| comparison                                                                       | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:---------------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)                     | all     | 38310 | -0.0013 |  -0.0020 |  -0.0007 |                  0.5241 |
| baseline blend logit (per state) - SP calibrated (per state)                     | QLD     | 17228 | -0.0027 |  -0.0043 |  -0.0012 |                  0.5221 |
| baseline blend logit (per state) - SP calibrated (per state)                     | VIC/SA  | 21082 | -0.0002 |  -0.0005 |   0.0001 |                  0.5258 |
| wet blend logit (per state) - SP calibrated (per state)                          | all     | 38310 | -0.0017 |  -0.0025 |  -0.0009 |                  0.5234 |
| wet blend logit (per state) - SP calibrated (per state)                          | QLD     | 17228 | -0.0033 |  -0.0050 |  -0.0016 |                  0.5254 |
| wet blend logit (per state) - SP calibrated (per state)                          | VIC/SA  | 21082 | -0.0003 |  -0.0008 |   0.0002 |                  0.5218 |
| wet-sx-wet blend logit (per state) - SP calibrated (per state)                   | all     | 38310 | -0.0017 |  -0.0025 |  -0.0009 |                  0.5240 |
| wet-sx-wet blend logit (per state) - SP calibrated (per state)                   | QLD     | 17228 | -0.0034 |  -0.0050 |  -0.0016 |                  0.5258 |
| wet-sx-wet blend logit (per state) - SP calibrated (per state)                   | VIC/SA  | 21082 | -0.0003 |  -0.0008 |   0.0002 |                  0.5225 |
| wet-sx-track blend logit (per state) - SP calibrated (per state)                 | all     | 38310 | -0.0017 |  -0.0025 |  -0.0008 |                  0.5228 |
| wet-sx-track blend logit (per state) - SP calibrated (per state)                 | QLD     | 17228 | -0.0033 |  -0.0052 |  -0.0015 |                  0.5246 |
| wet-sx-track blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 21082 | -0.0003 |  -0.0008 |   0.0002 |                  0.5213 |
| wet-sx-both blend logit (per state) - SP calibrated (per state)                  | all     | 38310 | -0.0017 |  -0.0025 |  -0.0009 |                  0.5227 |
| wet-sx-both blend logit (per state) - SP calibrated (per state)                  | QLD     | 17228 | -0.0034 |  -0.0052 |  -0.0016 |                  0.5248 |
| wet-sx-both blend logit (per state) - SP calibrated (per state)                  | VIC/SA  | 21082 | -0.0003 |  -0.0008 |   0.0002 |                  0.5210 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)         | all     | 38310 | -0.0001 |  -0.0005 |   0.0003 |                  0.5012 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)         | QLD     | 17228 |  0.0006 |  -0.0000 |   0.0012 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)         | VIC/SA  | 21082 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4710 |
| wet blend logit (per state) - wet blend logit (pooled weights)                   | all     | 38310 | -0.0002 |  -0.0005 |   0.0002 |                  0.5003 |
| wet blend logit (per state) - wet blend logit (pooled weights)                   | QLD     | 17228 |  0.0008 |   0.0001 |   0.0014 |                  0.5335 |
| wet blend logit (per state) - wet blend logit (pooled weights)                   | VIC/SA  | 21082 | -0.0009 |  -0.0014 |  -0.0005 |                  0.4731 |
| wet-sx-wet blend logit (per state) - wet-sx-wet blend logit (pooled weights)     | all     | 38310 | -0.0002 |  -0.0005 |   0.0002 |                  0.4999 |
| wet-sx-wet blend logit (per state) - wet-sx-wet blend logit (pooled weights)     | QLD     | 17228 |  0.0008 |   0.0002 |   0.0014 |                  0.5331 |
| wet-sx-wet blend logit (per state) - wet-sx-wet blend logit (pooled weights)     | VIC/SA  | 21082 | -0.0009 |  -0.0015 |  -0.0005 |                  0.4728 |
| wet-sx-track blend logit (per state) - wet-sx-track blend logit (pooled weights) | all     | 38310 | -0.0002 |  -0.0006 |   0.0002 |                  0.5005 |
| wet-sx-track blend logit (per state) - wet-sx-track blend logit (pooled weights) | QLD     | 17228 |  0.0009 |   0.0003 |   0.0016 |                  0.5327 |
| wet-sx-track blend logit (per state) - wet-sx-track blend logit (pooled weights) | VIC/SA  | 21082 | -0.0011 |  -0.0016 |  -0.0006 |                  0.4743 |
| wet-sx-both blend logit (per state) - wet-sx-both blend logit (pooled weights)   | all     | 38310 | -0.0002 |  -0.0006 |   0.0002 |                  0.4998 |
| wet-sx-both blend logit (per state) - wet-sx-both blend logit (pooled weights)   | QLD     | 17228 |  0.0009 |   0.0003 |   0.0015 |                  0.5315 |
| wet-sx-both blend logit (per state) - wet-sx-both blend logit (pooled weights)   | VIC/SA  | 21082 | -0.0011 |  -0.0016 |  -0.0006 |                  0.4740 |
| SP calibrated (per state) - SP calibrated (pooled)                               | all     | 38310 |  0.0001 |  -0.0001 |   0.0002 |                  0.4946 |
| SP calibrated (per state) - SP calibrated (pooled)                               | QLD     | 17228 |  0.0004 |   0.0001 |   0.0007 |                  0.5523 |
| SP calibrated (per state) - SP calibrated (pooled)                               | VIC/SA  | 21082 | -0.0002 |  -0.0004 |   0.0000 |                  0.4474 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   wet blend logit (per state) - SP calibrated (per state) | wet blend logit (per state) - SP calibrated (per state) 95%   |   wet-sx-wet blend logit (per state) - SP calibrated (per state) | wet-sx-wet blend logit (per state) - SP calibrated (per state) 95%   |   wet-sx-track blend logit (per state) - SP calibrated (per state) | wet-sx-track blend logit (per state) - SP calibrated (per state) 95%   |   wet-sx-both blend logit (per state) - SP calibrated (per state) | wet-sx-both blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|----------------------------------------------------------:|:--------------------------------------------------------------|-----------------------------------------------------------------:|:---------------------------------------------------------------------|-------------------------------------------------------------------:|:-----------------------------------------------------------------------|------------------------------------------------------------------:|:----------------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0051 to -0.0004                                                 |                                                   -0.0035 | -0.0064 to -0.0007                                            |                                                          -0.0034 | -0.0061 to -0.0006                                                   |                                                            -0.0034 | -0.0065 to -0.0003                                                     |                                                           -0.0034 | -0.0065 to -0.0004                                                    |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0029                                                 |                                                    0.0001 | -0.0028 to +0.0029                                            |                                                           0.0000 | -0.0029 to +0.0029                                                   |                                                             0.0005 | -0.0027 to +0.0036                                                     |                                                            0.0005 | -0.0026 to +0.0037                                                    |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0028 to +0.0002                                                 |                                                   -0.0018 | -0.0037 to +0.0001                                            |                                                          -0.0018 | -0.0037 to +0.0001                                                   |                                                            -0.0019 | -0.0038 to -0.0000                                                     |                                                           -0.0019 | -0.0039 to -0.0000                                                    |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0033 to -0.0001                                                 |                                                   -0.0023 | -0.0042 to -0.0004                                            |                                                          -0.0024 | -0.0043 to -0.0004                                                   |                                                            -0.0025 | -0.0044 to -0.0004                                                     |                                                           -0.0025 | -0.0044 to -0.0005                                                    |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0028 to +0.0005                                                 |                                                   -0.0016 | -0.0037 to +0.0006                                            |                                                          -0.0016 | -0.0036 to +0.0006                                                   |                                                            -0.0016 | -0.0038 to +0.0005                                                     |                                                           -0.0016 | -0.0039 to +0.0006                                                    |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0036 to -0.0004                                                 |                                                   -0.0015 | -0.0037 to +0.0006                                            |                                                          -0.0015 | -0.0037 to +0.0006                                                   |                                                            -0.0015 | -0.0036 to +0.0008                                                     |                                                           -0.0015 | -0.0037 to +0.0007                                                    |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0011                                                 |                                                   -0.0007 | -0.0026 to +0.0011                                            |                                                          -0.0007 | -0.0027 to +0.0011                                                   |                                                            -0.0008 | -0.0028 to +0.0011                                                     |                                                           -0.0008 | -0.0027 to +0.0010                                                    |
| 2026 H2  |    2481 |                                                        -0.0022 | -0.0045 to -0.0001                                                 |                                                   -0.0028 | -0.0055 to -0.0003                                            |                                                          -0.0029 | -0.0054 to -0.0003                                                   |                                                            -0.0030 | -0.0056 to -0.0004                                                     |                                                           -0.0030 | -0.0056 to -0.0004                                                    |

## Variants vs baseline (paired by race)

| comparison                                      | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| wet blend logit - baseline blend logit          | all     | 38310 | -0.0003 |  -0.0006 |  -0.0000 |                  0.5100 |
| wet blend logit - baseline blend logit          | QLD     | 17228 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5221 |
| wet blend logit - baseline blend logit          | VIC/SA  | 21082 |  0.0001 |  -0.0003 |   0.0005 |                  0.5001 |
| wet-sx-wet blend logit - baseline blend logit   | all     | 38310 | -0.0003 |  -0.0006 |  -0.0001 |                  0.5102 |
| wet-sx-wet blend logit - baseline blend logit   | QLD     | 17228 | -0.0008 |  -0.0012 |  -0.0004 |                  0.5239 |
| wet-sx-wet blend logit - baseline blend logit   | VIC/SA  | 21082 |  0.0001 |  -0.0003 |   0.0005 |                  0.4990 |
| wet-sx-track blend logit - baseline blend logit | all     | 38310 | -0.0003 |  -0.0006 |   0.0001 |                  0.5098 |
| wet-sx-track blend logit - baseline blend logit | QLD     | 17228 | -0.0009 |  -0.0014 |  -0.0005 |                  0.5215 |
| wet-sx-track blend logit - baseline blend logit | VIC/SA  | 21082 |  0.0003 |  -0.0001 |   0.0007 |                  0.5003 |
| wet-sx-both blend logit - baseline blend logit  | all     | 38310 | -0.0003 |  -0.0006 |   0.0001 |                  0.5098 |
| wet-sx-both blend logit - baseline blend logit  | QLD     | 17228 | -0.0010 |  -0.0015 |  -0.0005 |                  0.5233 |
| wet-sx-both blend logit - baseline blend logit  | VIC/SA  | 21082 |  0.0003 |  -0.0002 |   0.0007 |                  0.4988 |
| wet model logit - baseline model logit          | all     | 38310 | -0.0097 |  -0.0114 |  -0.0080 |                  0.5234 |
| wet model logit - baseline model logit          | QLD     | 17228 | -0.0113 |  -0.0139 |  -0.0088 |                  0.5294 |
| wet model logit - baseline model logit          | VIC/SA  | 21082 | -0.0084 |  -0.0107 |  -0.0061 |                  0.5186 |
| wet-sx-wet model logit - baseline model logit   | all     | 38310 | -0.0098 |  -0.0115 |  -0.0081 |                  0.5245 |
| wet-sx-wet model logit - baseline model logit   | QLD     | 17228 | -0.0115 |  -0.0141 |  -0.0090 |                  0.5297 |
| wet-sx-wet model logit - baseline model logit   | VIC/SA  | 21082 | -0.0085 |  -0.0108 |  -0.0061 |                  0.5202 |
| wet-sx-track model logit - baseline model logit | all     | 38310 | -0.0088 |  -0.0106 |  -0.0070 |                  0.5208 |
| wet-sx-track model logit - baseline model logit | QLD     | 17228 | -0.0104 |  -0.0132 |  -0.0078 |                  0.5258 |
| wet-sx-track model logit - baseline model logit | VIC/SA  | 21082 | -0.0075 |  -0.0100 |  -0.0051 |                  0.5167 |
| wet-sx-both model logit - baseline model logit  | all     | 38310 | -0.0089 |  -0.0108 |  -0.0071 |                  0.5208 |
| wet-sx-both model logit - baseline model logit  | QLD     | 17228 | -0.0105 |  -0.0131 |  -0.0078 |                  0.5257 |
| wet-sx-both model logit - baseline model logit  | VIC/SA  | 21082 | -0.0077 |  -0.0103 |  -0.0052 |                  0.5168 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   wet blend logit - baseline blend logit | wet blend logit - baseline blend logit 95%   |   wet-sx-wet blend logit - baseline blend logit | wet-sx-wet blend logit - baseline blend logit 95%   |   wet-sx-track blend logit - baseline blend logit | wet-sx-track blend logit - baseline blend logit 95%   |   wet-sx-both blend logit - baseline blend logit | wet-sx-both blend logit - baseline blend logit 95%   |
|:---------|--------:|-----------------------------------------:|:---------------------------------------------|------------------------------------------------:|:----------------------------------------------------|--------------------------------------------------:|:------------------------------------------------------|-------------------------------------------------:|:-----------------------------------------------------|
| 2023 H1  |    5012 |                                  -0.0008 | -0.0017 to +0.0001                           |                                         -0.0008 | -0.0016 to +0.0001                                  |                                           -0.0007 | -0.0019 to +0.0004                                    |                                          -0.0007 | -0.0018 to +0.0004                                   |
| 2023 H2  |    5233 |                                  -0.0004 | -0.0013 to +0.0005                           |                                         -0.0005 | -0.0013 to +0.0004                                  |                                           -0.0001 | -0.0012 to +0.0010                                    |                                          -0.0001 | -0.0012 to +0.0010                                   |
| 2024 H1  |    5145 |                                  -0.0005 | -0.0012 to +0.0002                           |                                         -0.0005 | -0.0012 to +0.0002                                  |                                           -0.0006 | -0.0014 to +0.0002                                    |                                          -0.0006 | -0.0014 to +0.0002                                   |
| 2024 H2  |    5229 |                                  -0.0006 | -0.0014 to +0.0001                           |                                         -0.0007 | -0.0014 to +0.0001                                  |                                           -0.0007 | -0.0015 to +0.0001                                    |                                          -0.0007 | -0.0015 to +0.0001                                   |
| 2025 H1  |    5065 |                                  -0.0003 | -0.0010 to +0.0005                           |                                         -0.0003 | -0.0011 to +0.0006                                  |                                           -0.0002 | -0.0011 to +0.0007                                    |                                          -0.0002 | -0.0011 to +0.0006                                   |
| 2025 H2  |    5153 |                                   0.0006 | -0.0002 to +0.0014                           |                                          0.0006 | -0.0002 to +0.0014                                  |                                            0.0007 | -0.0002 to +0.0015                                    |                                           0.0007 | -0.0002 to +0.0016                                   |
| 2026 H1  |    4992 |                                  -0.0000 | -0.0006 to +0.0005                           |                                         -0.0001 | -0.0006 to +0.0005                                  |                                           -0.0001 | -0.0007 to +0.0005                                    |                                          -0.0001 | -0.0007 to +0.0005                                   |
| 2026 H2  |    2481 |                                  -0.0006 | -0.0014 to +0.0002                           |                                         -0.0006 | -0.0014 to +0.0002                                  |                                           -0.0006 | -0.0015 to +0.0002                                    |                                          -0.0007 | -0.0015 to +0.0002                                   |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   wet logit a |   wet logit b |   wet logit a, QLD |   wet logit b, QLD |   wet logit a, VIC/SA |   wet logit b, VIC/SA |   wet-sx-wet logit a |   wet-sx-wet logit b |   wet-sx-wet logit a, QLD |   wet-sx-wet logit b, QLD |   wet-sx-wet logit a, VIC/SA |   wet-sx-wet logit b, VIC/SA |   wet-sx-track logit a |   wet-sx-track logit b |   wet-sx-track logit a, QLD |   wet-sx-track logit b, QLD |   wet-sx-track logit a, VIC/SA |   wet-sx-track logit b, VIC/SA |   wet-sx-both logit a |   wet-sx-both logit b |   wet-sx-both logit a, QLD |   wet-sx-both logit b, QLD |   wet-sx-both logit a, VIC/SA |   wet-sx-both logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|--------------:|--------------:|-------------------:|-------------------:|----------------------:|----------------------:|---------------------:|---------------------:|--------------------------:|--------------------------:|-----------------------------:|-----------------------------:|-----------------------:|-----------------------:|----------------------------:|----------------------------:|-------------------------------:|-------------------------------:|----------------------:|----------------------:|---------------------------:|---------------------------:|------------------------------:|------------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |         0.183 |         1.063 |              0.291 |              1.018 |                 0.086 |                 1.108 |                0.182 |                1.063 |                     0.290 |                     1.019 |                        0.085 |                        1.108 |                  0.198 |                  1.053 |                       0.306 |                       1.010 |                          0.104 |                          1.095 |                 0.197 |                 1.053 |                      0.305 |                      1.010 |                         0.103 |                         1.095 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |         0.138 |         1.012 |              0.197 |              0.997 |                 0.062 |                 1.040 |                0.139 |                1.012 |                     0.197 |                     0.996 |                        0.062 |                        1.039 |                  0.142 |                  1.010 |                       0.202 |                       0.993 |                          0.063 |                          1.038 |                 0.142 |                 1.009 |                      0.202 |                      0.992 |                         0.064 |                         1.038 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |         0.152 |         1.046 |              0.209 |              1.011 |                 0.090 |                 1.083 |                0.153 |                1.046 |                     0.211 |                     1.009 |                        0.090 |                        1.083 |                  0.158 |                  1.042 |                       0.214 |                       1.006 |                          0.094 |                          1.080 |                 0.159 |                 1.041 |                      0.217 |                      1.005 |                         0.094 |                         1.080 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |         0.122 |         1.031 |              0.191 |              0.967 |                 0.061 |                 1.083 |                0.123 |                1.031 |                     0.191 |                     0.966 |                        0.062 |                        1.082 |                  0.124 |                  1.030 |                       0.195 |                       0.964 |                          0.060 |                          1.083 |                 0.125 |                 1.030 |                      0.196 |                      0.963 |                         0.061 |                         1.083 |
