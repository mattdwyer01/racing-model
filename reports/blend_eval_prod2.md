# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Variants: baseline, prod, prod2, prod2-fig2, prod2-gps, prod2-mu, prod2-v4 (see module docstring); all share the same fold builds
- Negative differences = first is better. 95% ranges: 2,000 race bootstrap resamples

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
| prod: model logit                   |     1.9278 |     1.9242 |     1.9310 |    1.9268 |     1.9275 |
| prod: blend logit                   |     1.7903 |     1.7867 |     1.7846 |    1.7751 |     1.7849 |
| prod: blend logit (per state)       |     1.7906 |     1.7866 |     1.7841 |    1.7748 |     1.7848 |
| prod2: model logit                  |     1.9259 |     1.9227 |     1.9304 |    1.9245 |     1.9260 |
| prod2: blend logit                  |     1.7903 |     1.7868 |     1.7848 |    1.7751 |     1.7850 |
| prod2: blend logit (per state)      |     1.7907 |     1.7866 |     1.7842 |    1.7748 |     1.7849 |
| prod2-fig2: model logit             |     1.9247 |     1.9206 |     1.9278 |    1.9228 |     1.9241 |
| prod2-fig2: blend logit             |     1.7903 |     1.7866 |     1.7847 |    1.7751 |     1.7850 |
| prod2-fig2: blend logit (per state) |     1.7907 |     1.7864 |     1.7842 |    1.7747 |     1.7848 |
| prod2-gps: model logit              |     1.9259 |     1.9227 |     1.9304 |    1.9245 |     1.9260 |
| prod2-gps: blend logit              |     1.7903 |     1.7868 |     1.7848 |    1.7751 |     1.7850 |
| prod2-gps: blend logit (per state)  |     1.7907 |     1.7866 |     1.7842 |    1.7748 |     1.7849 |
| prod2-mu: model logit               |     1.9260 |     1.9228 |     1.9307 |    1.9246 |     1.9261 |
| prod2-mu: blend logit               |     1.7904 |     1.7868 |     1.7848 |    1.7751 |     1.7851 |
| prod2-mu: blend logit (per state)   |     1.7907 |     1.7866 |     1.7842 |    1.7748 |     1.7849 |
| prod2-v4: model logit               |     1.9256 |     1.9231 |     1.9304 |    1.9246 |     1.9260 |
| prod2-v4: blend logit               |     1.7903 |     1.7868 |     1.7848 |    1.7751 |     1.7851 |
| prod2-v4: blend logit (per state)   |     1.7907 |     1.7866 |     1.7842 |    1.7748 |     1.7849 |

## Differences vs SP, pooled

| comparison                             | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:---------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit - SP raw          | all     | 37821 | -0.0048 |  -0.0061 |  -0.0036 |                  0.5939 |
| baseline blend logit - SP raw          | QLD     | 16991 | -0.0069 |  -0.0087 |  -0.0051 |                  0.5995 |
| baseline blend logit - SP raw          | VIC/SA  | 20830 | -0.0031 |  -0.0046 |  -0.0015 |                  0.5894 |
| baseline blend logit - SP calibrated   | all     | 37821 | -0.0011 |  -0.0017 |  -0.0005 |                  0.5238 |
| baseline blend logit - SP calibrated   | QLD     | 16991 | -0.0029 |  -0.0039 |  -0.0020 |                  0.5335 |
| baseline blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0003 |  -0.0004 |   0.0011 |                  0.5160 |
| prod blend logit - SP raw              | all     | 37821 | -0.0050 |  -0.0063 |  -0.0038 |                  0.5891 |
| prod blend logit - SP raw              | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0054 |                  0.5956 |
| prod blend logit - SP raw              | VIC/SA  | 20830 | -0.0031 |  -0.0047 |  -0.0014 |                  0.5838 |
| prod blend logit - SP calibrated       | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5225 |
| prod blend logit - SP calibrated       | QLD     | 16991 | -0.0034 |  -0.0046 |  -0.0023 |                  0.5323 |
| prod blend logit - SP calibrated       | VIC/SA  | 20830 |  0.0003 |  -0.0006 |   0.0013 |                  0.5145 |
| prod2 blend logit - SP raw             | all     | 37821 | -0.0049 |  -0.0062 |  -0.0037 |                  0.5882 |
| prod2 blend logit - SP raw             | QLD     | 16991 | -0.0074 |  -0.0092 |  -0.0053 |                  0.5954 |
| prod2 blend logit - SP raw             | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0013 |                  0.5824 |
| prod2 blend logit - SP calibrated      | all     | 37821 | -0.0013 |  -0.0020 |  -0.0005 |                  0.5213 |
| prod2 blend logit - SP calibrated      | QLD     | 16991 | -0.0034 |  -0.0046 |  -0.0023 |                  0.5325 |
| prod2 blend logit - SP calibrated      | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0014 |                  0.5121 |
| prod2-fig2 blend logit - SP raw        | all     | 37821 | -0.0050 |  -0.0062 |  -0.0038 |                  0.5879 |
| prod2-fig2 blend logit - SP raw        | QLD     | 16991 | -0.0076 |  -0.0094 |  -0.0057 |                  0.5947 |
| prod2-fig2 blend logit - SP raw        | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0012 |                  0.5823 |
| prod2-fig2 blend logit - SP calibrated | all     | 37821 | -0.0013 |  -0.0021 |  -0.0006 |                  0.5233 |
| prod2-fig2 blend logit - SP calibrated | QLD     | 16991 | -0.0036 |  -0.0048 |  -0.0024 |                  0.5358 |
| prod2-fig2 blend logit - SP calibrated | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0014 |                  0.5131 |
| prod2-gps blend logit - SP raw         | all     | 37821 | -0.0049 |  -0.0062 |  -0.0036 |                  0.5885 |
| prod2-gps blend logit - SP raw         | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0053 |                  0.5952 |
| prod2-gps blend logit - SP raw         | VIC/SA  | 20830 | -0.0029 |  -0.0046 |  -0.0013 |                  0.5831 |
| prod2-gps blend logit - SP calibrated  | all     | 37821 | -0.0013 |  -0.0020 |  -0.0005 |                  0.5212 |
| prod2-gps blend logit - SP calibrated  | QLD     | 16991 | -0.0034 |  -0.0045 |  -0.0022 |                  0.5329 |
| prod2-gps blend logit - SP calibrated  | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0014 |                  0.5116 |
| prod2-mu blend logit - SP raw          | all     | 37821 | -0.0049 |  -0.0062 |  -0.0037 |                  0.5883 |
| prod2-mu blend logit - SP raw          | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0055 |                  0.5957 |
| prod2-mu blend logit - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0012 |                  0.5822 |
| prod2-mu blend logit - SP calibrated   | all     | 37821 | -0.0012 |  -0.0020 |  -0.0005 |                  0.5213 |
| prod2-mu blend logit - SP calibrated   | QLD     | 16991 | -0.0034 |  -0.0045 |  -0.0023 |                  0.5325 |
| prod2-mu blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0014 |                  0.5122 |
| prod2-v4 blend logit - SP raw          | all     | 37821 | -0.0049 |  -0.0061 |  -0.0036 |                  0.5885 |
| prod2-v4 blend logit - SP raw          | QLD     | 16991 | -0.0074 |  -0.0093 |  -0.0056 |                  0.5953 |
| prod2-v4 blend logit - SP raw          | VIC/SA  | 20830 | -0.0029 |  -0.0045 |  -0.0013 |                  0.5830 |
| prod2-v4 blend logit - SP calibrated   | all     | 37821 | -0.0012 |  -0.0020 |  -0.0005 |                  0.5219 |
| prod2-v4 blend logit - SP calibrated   | QLD     | 16991 | -0.0034 |  -0.0045 |  -0.0023 |                  0.5327 |
| prod2-v4 blend logit - SP calibrated   | VIC/SA  | 20830 |  0.0005 |  -0.0004 |   0.0015 |                  0.5132 |

## By 6-month period: blend minus SP calibrated

| period   |   races |   baseline logit | baseline logit 95%   |   prod logit | prod logit 95%     |   prod2 logit | prod2 logit 95%    |   prod2-fig2 logit | prod2-fig2 logit 95%   |   prod2-gps logit | prod2-gps logit 95%   |   prod2-mu logit | prod2-mu logit 95%   |   prod2-v4 logit | prod2-v4 logit 95%   |
|:---------|--------:|-----------------:|:---------------------|-------------:|:-------------------|--------------:|:-------------------|-------------------:|:-----------------------|------------------:|:----------------------|-----------------:|:---------------------|-----------------:|:---------------------|
| 2023 H1  |    5012 |          -0.0028 | -0.0049 to -0.0009   |      -0.0032 | -0.0055 to -0.0009 |       -0.0032 | -0.0054 to -0.0009 |            -0.0032 | -0.0056 to -0.0010     |           -0.0032 | -0.0054 to -0.0009    |          -0.0031 | -0.0054 to -0.0009   |          -0.0033 | -0.0054 to -0.0010   |
| 2023 H2  |    5233 |           0.0001 | -0.0018 to +0.0021   |      -0.0002 | -0.0027 to +0.0021 |       -0.0002 | -0.0025 to +0.0021 |            -0.0003 | -0.0027 to +0.0022     |           -0.0002 | -0.0025 to +0.0021    |          -0.0003 | -0.0024 to +0.0021   |          -0.0002 | -0.0025 to +0.0023   |
| 2024 H1  |    5145 |          -0.0016 | -0.0028 to -0.0003   |      -0.0020 | -0.0038 to -0.0001 |       -0.0019 | -0.0037 to -0.0002 |            -0.0021 | -0.0039 to -0.0001     |           -0.0019 | -0.0036 to -0.0002    |          -0.0019 | -0.0038 to -0.0001   |          -0.0020 | -0.0037 to -0.0001   |
| 2024 H2  |    5229 |          -0.0010 | -0.0024 to +0.0003   |      -0.0016 | -0.0034 to +0.0003 |       -0.0015 | -0.0031 to +0.0002 |            -0.0016 | -0.0034 to +0.0003     |           -0.0015 | -0.0031 to +0.0002    |          -0.0015 | -0.0032 to +0.0002   |          -0.0014 | -0.0031 to +0.0003   |
| 2025 H1  |    5065 |          -0.0011 | -0.0027 to +0.0006   |      -0.0013 | -0.0033 to +0.0008 |       -0.0011 | -0.0031 to +0.0009 |            -0.0013 | -0.0032 to +0.0007     |           -0.0011 | -0.0031 to +0.0009    |          -0.0011 | -0.0029 to +0.0010   |          -0.0011 | -0.0032 to +0.0008   |
| 2025 H2  |    5153 |          -0.0012 | -0.0027 to +0.0004   |      -0.0007 | -0.0026 to +0.0014 |       -0.0005 | -0.0025 to +0.0016 |            -0.0005 | -0.0026 to +0.0015     |           -0.0005 | -0.0024 to +0.0015    |          -0.0005 | -0.0024 to +0.0015   |          -0.0004 | -0.0023 to +0.0016   |
| 2026 H1  |    4992 |          -0.0002 | -0.0016 to +0.0013   |      -0.0003 | -0.0019 to +0.0014 |       -0.0001 | -0.0017 to +0.0014 |            -0.0002 | -0.0019 to +0.0015     |           -0.0001 | -0.0016 to +0.0015    |          -0.0001 | -0.0016 to +0.0015   |          -0.0002 | -0.0018 to +0.0014   |
| 2026 H2  |    1992 |          -0.0014 | -0.0036 to +0.0009   |      -0.0017 | -0.0044 to +0.0008 |       -0.0020 | -0.0044 to +0.0005 |            -0.0019 | -0.0044 to +0.0008     |           -0.0020 | -0.0044 to +0.0005    |          -0.0020 | -0.0045 to +0.0004   |          -0.0018 | -0.0042 to +0.0008   |

## Per-state weights (QLD vs VIC/SA fitted separately on the same blend window)

| comparison                                                                   | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:-----------------------------------------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| baseline blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0013 |  -0.0020 |  -0.0006 |                  0.5239 |
| baseline blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0026 |  -0.0042 |  -0.0011 |                  0.5211 |
| baseline blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0002 |  -0.0005 |   0.0001 |                  0.5261 |
| prod blend logit (per state) - SP calibrated (per state)                     | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5226 |
| prod blend logit (per state) - SP calibrated (per state)                     | QLD     | 16991 | -0.0030 |  -0.0047 |  -0.0012 |                  0.5217 |
| prod blend logit (per state) - SP calibrated (per state)                     | VIC/SA  | 20830 | -0.0004 |  -0.0009 |   0.0002 |                  0.5233 |
| prod2 blend logit (per state) - SP calibrated (per state)                    | all     | 37821 | -0.0015 |  -0.0023 |  -0.0006 |                  0.5218 |
| prod2 blend logit (per state) - SP calibrated (per state)                    | QLD     | 16991 | -0.0030 |  -0.0046 |  -0.0013 |                  0.5226 |
| prod2 blend logit (per state) - SP calibrated (per state)                    | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0002 |                  0.5212 |
| prod2-fig2 blend logit (per state) - SP calibrated (per state)               | all     | 37821 | -0.0016 |  -0.0023 |  -0.0007 |                  0.5228 |
| prod2-fig2 blend logit (per state) - SP calibrated (per state)               | QLD     | 16991 | -0.0031 |  -0.0048 |  -0.0014 |                  0.5239 |
| prod2-fig2 blend logit (per state) - SP calibrated (per state)               | VIC/SA  | 20830 | -0.0003 |  -0.0008 |   0.0002 |                  0.5219 |
| prod2-gps blend logit (per state) - SP calibrated (per state)                | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5216 |
| prod2-gps blend logit (per state) - SP calibrated (per state)                | QLD     | 16991 | -0.0030 |  -0.0047 |  -0.0013 |                  0.5226 |
| prod2-gps blend logit (per state) - SP calibrated (per state)                | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0002 |                  0.5208 |
| prod2-mu blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5219 |
| prod2-mu blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0029 |  -0.0046 |  -0.0013 |                  0.5219 |
| prod2-mu blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0002 |                  0.5219 |
| prod2-v4 blend logit (per state) - SP calibrated (per state)                 | all     | 37821 | -0.0015 |  -0.0023 |  -0.0007 |                  0.5226 |
| prod2-v4 blend logit (per state) - SP calibrated (per state)                 | QLD     | 16991 | -0.0029 |  -0.0047 |  -0.0013 |                  0.5238 |
| prod2-v4 blend logit (per state) - SP calibrated (per state)                 | VIC/SA  | 20830 | -0.0003 |  -0.0007 |   0.0002 |                  0.5217 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.5008 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | QLD     | 16991 |  0.0006 |  -0.0000 |   0.0013 |                  0.5381 |
| baseline blend logit (per state) - baseline blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0007 |  -0.0012 |  -0.0002 |                  0.4703 |
| prod blend logit (per state) - prod blend logit (pooled weights)             | all     | 37821 | -0.0001 |  -0.0005 |   0.0002 |                  0.5020 |
| prod blend logit (per state) - prod blend logit (pooled weights)             | QLD     | 16991 |  0.0008 |   0.0003 |   0.0014 |                  0.5370 |
| prod blend logit (per state) - prod blend logit (pooled weights)             | VIC/SA  | 20830 | -0.0009 |  -0.0013 |  -0.0004 |                  0.4735 |
| prod2 blend logit (per state) - prod2 blend logit (pooled weights)           | all     | 37821 | -0.0002 |  -0.0005 |   0.0003 |                  0.4991 |
| prod2 blend logit (per state) - prod2 blend logit (pooled weights)           | QLD     | 16991 |  0.0008 |   0.0002 |   0.0014 |                  0.5325 |
| prod2 blend logit (per state) - prod2 blend logit (pooled weights)           | VIC/SA  | 20830 | -0.0009 |  -0.0015 |  -0.0004 |                  0.4719 |
| prod2-fig2 blend logit (per state) - prod2-fig2 blend logit (pooled weights) | all     | 37821 | -0.0001 |  -0.0005 |   0.0003 |                  0.4993 |
| prod2-fig2 blend logit (per state) - prod2-fig2 blend logit (pooled weights) | QLD     | 16991 |  0.0009 |   0.0002 |   0.0015 |                  0.5303 |
| prod2-fig2 blend logit (per state) - prod2-fig2 blend logit (pooled weights) | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4741 |
| prod2-gps blend logit (per state) - prod2-gps blend logit (pooled weights)   | all     | 37821 | -0.0002 |  -0.0005 |   0.0002 |                  0.4992 |
| prod2-gps blend logit (per state) - prod2-gps blend logit (pooled weights)   | QLD     | 16991 |  0.0008 |   0.0002 |   0.0015 |                  0.5324 |
| prod2-gps blend logit (per state) - prod2-gps blend logit (pooled weights)   | VIC/SA  | 20830 | -0.0009 |  -0.0014 |  -0.0004 |                  0.4721 |
| prod2-mu blend logit (per state) - prod2-mu blend logit (pooled weights)     | all     | 37821 | -0.0002 |  -0.0006 |   0.0002 |                  0.4987 |
| prod2-mu blend logit (per state) - prod2-mu blend logit (pooled weights)     | QLD     | 16991 |  0.0008 |   0.0002 |   0.0015 |                  0.5318 |
| prod2-mu blend logit (per state) - prod2-mu blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4716 |
| prod2-v4 blend logit (per state) - prod2-v4 blend logit (pooled weights)     | all     | 37821 | -0.0002 |  -0.0005 |   0.0002 |                  0.4994 |
| prod2-v4 blend logit (per state) - prod2-v4 blend logit (pooled weights)     | QLD     | 16991 |  0.0008 |   0.0002 |   0.0015 |                  0.5328 |
| prod2-v4 blend logit (per state) - prod2-v4 blend logit (pooled weights)     | VIC/SA  | 20830 | -0.0010 |  -0.0015 |  -0.0005 |                  0.4722 |
| SP calibrated (per state) - SP calibrated (pooled)                           | all     | 37821 |  0.0001 |  -0.0001 |   0.0002 |                  0.4945 |
| SP calibrated (per state) - SP calibrated (pooled)                           | QLD     | 16991 |  0.0004 |   0.0001 |   0.0007 |                  0.5545 |
| SP calibrated (per state) - SP calibrated (pooled)                           | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0000 |                  0.4456 |

## Per-state blend minus per-state calibrated SP, by 6-month period

| period   |   races |   baseline blend logit (per state) - SP calibrated (per state) | baseline blend logit (per state) - SP calibrated (per state) 95%   |   prod blend logit (per state) - SP calibrated (per state) | prod blend logit (per state) - SP calibrated (per state) 95%   |   prod2 blend logit (per state) - SP calibrated (per state) | prod2 blend logit (per state) - SP calibrated (per state) 95%   |   prod2-fig2 blend logit (per state) - SP calibrated (per state) | prod2-fig2 blend logit (per state) - SP calibrated (per state) 95%   |   prod2-gps blend logit (per state) - SP calibrated (per state) | prod2-gps blend logit (per state) - SP calibrated (per state) 95%   |   prod2-mu blend logit (per state) - SP calibrated (per state) | prod2-mu blend logit (per state) - SP calibrated (per state) 95%   |   prod2-v4 blend logit (per state) - SP calibrated (per state) | prod2-v4 blend logit (per state) - SP calibrated (per state) 95%   |
|:---------|--------:|---------------------------------------------------------------:|:-------------------------------------------------------------------|-----------------------------------------------------------:|:---------------------------------------------------------------|------------------------------------------------------------:|:----------------------------------------------------------------|-----------------------------------------------------------------:|:---------------------------------------------------------------------|----------------------------------------------------------------:|:--------------------------------------------------------------------|---------------------------------------------------------------:|:-------------------------------------------------------------------|---------------------------------------------------------------:|:-------------------------------------------------------------------|
| 2023 H1  |    5012 |                                                        -0.0028 | -0.0051 to -0.0005                                                 |                                                    -0.0033 | -0.0060 to -0.0007                                             |                                                     -0.0031 | -0.0058 to -0.0004                                              |                                                          -0.0032 | -0.0060 to -0.0005                                                   |                                                         -0.0032 | -0.0058 to -0.0006                                                  |                                                        -0.0031 | -0.0057 to -0.0006                                                 |                                                        -0.0032 | -0.0058 to -0.0006                                                 |
| 2023 H2  |    5233 |                                                         0.0005 | -0.0020 to +0.0031                                                 |                                                     0.0002 | -0.0027 to +0.0029                                             |                                                      0.0002 | -0.0026 to +0.0031                                              |                                                           0.0002 | -0.0026 to +0.0031                                                   |                                                          0.0002 | -0.0026 to +0.0030                                                  |                                                         0.0002 | -0.0026 to +0.0031                                                 |                                                         0.0002 | -0.0024 to +0.0031                                                 |
| 2024 H1  |    5145 |                                                        -0.0013 | -0.0029 to +0.0001                                                 |                                                    -0.0017 | -0.0036 to +0.0001                                             |                                                     -0.0017 | -0.0035 to +0.0001                                              |                                                          -0.0018 | -0.0037 to +0.0001                                                   |                                                         -0.0017 | -0.0035 to +0.0001                                                  |                                                        -0.0017 | -0.0034 to +0.0002                                                 |                                                        -0.0017 | -0.0035 to +0.0000                                                 |
| 2024 H2  |    5229 |                                                        -0.0017 | -0.0032 to -0.0002                                                 |                                                    -0.0021 | -0.0040 to -0.0003                                             |                                                     -0.0022 | -0.0041 to -0.0004                                              |                                                          -0.0023 | -0.0042 to -0.0005                                                   |                                                         -0.0022 | -0.0042 to -0.0003                                                  |                                                        -0.0022 | -0.0040 to -0.0004                                                 |                                                        -0.0021 | -0.0039 to -0.0003                                                 |
| 2025 H1  |    5065 |                                                        -0.0011 | -0.0029 to +0.0005                                                 |                                                    -0.0014 | -0.0036 to +0.0006                                             |                                                     -0.0015 | -0.0035 to +0.0006                                              |                                                          -0.0015 | -0.0035 to +0.0005                                                   |                                                         -0.0015 | -0.0035 to +0.0005                                                  |                                                        -0.0014 | -0.0034 to +0.0006                                                 |                                                        -0.0015 | -0.0036 to +0.0005                                                 |
| 2025 H2  |    5153 |                                                        -0.0020 | -0.0037 to -0.0003                                                 |                                                    -0.0016 | -0.0037 to +0.0004                                             |                                                     -0.0014 | -0.0035 to +0.0006                                              |                                                          -0.0015 | -0.0036 to +0.0005                                                   |                                                         -0.0014 | -0.0035 to +0.0007                                                  |                                                        -0.0014 | -0.0034 to +0.0006                                                 |                                                        -0.0013 | -0.0034 to +0.0008                                                 |
| 2026 H1  |    4992 |                                                        -0.0005 | -0.0022 to +0.0012                                                 |                                                    -0.0006 | -0.0024 to +0.0012                                             |                                                     -0.0004 | -0.0023 to +0.0013                                              |                                                          -0.0006 | -0.0024 to +0.0012                                                   |                                                         -0.0004 | -0.0022 to +0.0013                                                  |                                                        -0.0004 | -0.0022 to +0.0014                                                 |                                                        -0.0005 | -0.0021 to +0.0013                                                 |
| 2026 H2  |    1992 |                                                        -0.0015 | -0.0041 to +0.0010                                                 |                                                    -0.0018 | -0.0049 to +0.0011                                             |                                                     -0.0023 | -0.0052 to +0.0004                                              |                                                          -0.0021 | -0.0049 to +0.0007                                                   |                                                         -0.0023 | -0.0050 to +0.0004                                                  |                                                        -0.0023 | -0.0050 to +0.0005                                                 |                                                        -0.0021 | -0.0048 to +0.0005                                                 |

## prod2 (production + v4 settle + GPS pace + figure v2 + rating mu) vs production, and what each part adds with the others present (paired by race)

| comparison                             | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:---------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod2 model logit - prod model logit   | all     | 37821 | -0.0015 |  -0.0027 |  -0.0003 |                  0.5019 |
| prod2 model logit - prod model logit   | QLD     | 16991 | -0.0038 |  -0.0057 |  -0.0018 |                  0.5072 |
| prod2 model logit - prod model logit   | VIC/SA  | 20830 |  0.0003 |  -0.0014 |   0.0020 |                  0.4976 |
| prod2 blend logit - prod blend logit   | all     | 37821 |  0.0001 |  -0.0001 |   0.0003 |                  0.4907 |
| prod2 blend logit - prod blend logit   | QLD     | 16991 |  0.0000 |  -0.0003 |   0.0003 |                  0.4883 |
| prod2 blend logit - prod blend logit   | VIC/SA  | 20830 |  0.0002 |  -0.0001 |   0.0004 |                  0.4928 |
| prod2 model logit - prod2 without fig2 | all     | 37821 |  0.0019 |   0.0013 |   0.0025 |                  0.4820 |
| prod2 model logit - prod2 without fig2 | QLD     | 16991 |  0.0019 |   0.0011 |   0.0028 |                  0.4804 |
| prod2 model logit - prod2 without fig2 | VIC/SA  | 20830 |  0.0018 |   0.0010 |   0.0026 |                  0.4833 |
| prod2 blend logit - prod2 without fig2 | all     | 37821 |  0.0001 |  -0.0000 |   0.0002 |                  0.4915 |
| prod2 blend logit - prod2 without fig2 | QLD     | 16991 |  0.0002 |   0.0000 |   0.0003 |                  0.4841 |
| prod2 blend logit - prod2 without fig2 | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0001 |                  0.4976 |
| prod2 model logit - prod2 without gps  | all     | 37821 | -0.0000 |  -0.0001 |   0.0001 |                  0.5038 |
| prod2 model logit - prod2 without gps  | QLD     | 16991 | -0.0000 |  -0.0001 |   0.0001 |                  0.5012 |
| prod2 model logit - prod2 without gps  | VIC/SA  | 20830 |  0.0000 |  -0.0001 |   0.0001 |                  0.5060 |
| prod2 blend logit - prod2 without gps  | all     | 37821 | -0.0000 |  -0.0000 |   0.0000 |                  0.5008 |
| prod2 blend logit - prod2 without gps  | QLD     | 16991 | -0.0000 |  -0.0000 |   0.0000 |                  0.4971 |
| prod2 blend logit - prod2 without gps  | VIC/SA  | 20830 | -0.0000 |  -0.0000 |   0.0000 |                  0.5038 |
| prod2 model logit - prod2 without mu   | all     | 37821 | -0.0001 |  -0.0003 |   0.0000 |                  0.4933 |
| prod2 model logit - prod2 without mu   | QLD     | 16991 | -0.0001 |  -0.0004 |   0.0002 |                  0.4963 |
| prod2 model logit - prod2 without mu   | VIC/SA  | 20830 | -0.0002 |  -0.0004 |   0.0001 |                  0.4908 |
| prod2 blend logit - prod2 without mu   | all     | 37821 | -0.0000 |  -0.0000 |   0.0000 |                  0.4876 |
| prod2 blend logit - prod2 without mu   | QLD     | 16991 | -0.0000 |  -0.0001 |   0.0000 |                  0.4895 |
| prod2 blend logit - prod2 without mu   | VIC/SA  | 20830 | -0.0000 |  -0.0001 |   0.0000 |                  0.4860 |
| prod2 model logit - prod2 without v4   | all     | 37821 | -0.0000 |  -0.0004 |   0.0003 |                  0.5023 |
| prod2 model logit - prod2 without v4   | QLD     | 16991 | -0.0004 |  -0.0009 |   0.0001 |                  0.5074 |
| prod2 model logit - prod2 without v4   | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0007 |                  0.4982 |
| prod2 blend logit - prod2 without v4   | all     | 37821 | -0.0000 |  -0.0001 |   0.0000 |                  0.5039 |
| prod2 blend logit - prod2 without v4   | QLD     | 16991 | -0.0000 |  -0.0001 |   0.0001 |                  0.5030 |
| prod2 blend logit - prod2 without v4   | VIC/SA  | 20830 | -0.0000 |  -0.0001 |   0.0000 |                  0.5047 |

| period   |   races |   prod2 model logit - prod model logit | prod2 model logit - prod model logit 95%   |   prod2 blend logit - prod blend logit | prod2 blend logit - prod blend logit 95%   |
|:---------|--------:|---------------------------------------:|:-------------------------------------------|---------------------------------------:|:-------------------------------------------|
| 2023 H1  |    5012 |                                -0.0029 | -0.0062 to +0.0005                         |                                 0.0000 | -0.0006 to +0.0007                         |
| 2023 H2  |    5233 |                                -0.0009 | -0.0045 to +0.0029                         |                                 0.0000 | -0.0006 to +0.0006                         |
| 2024 H1  |    5145 |                                -0.0011 | -0.0043 to +0.0022                         |                                 0.0001 | -0.0003 to +0.0005                         |
| 2024 H2  |    5229 |                                -0.0020 | -0.0053 to +0.0013                         |                                 0.0001 | -0.0004 to +0.0005                         |
| 2025 H1  |    5065 |                                -0.0005 | -0.0038 to +0.0029                         |                                 0.0002 | -0.0003 to +0.0007                         |
| 2025 H2  |    5153 |                                -0.0007 | -0.0041 to +0.0026                         |                                 0.0003 | -0.0002 to +0.0007                         |
| 2026 H1  |    4992 |                                -0.0005 | -0.0039 to +0.0030                         |                                 0.0002 | -0.0003 to +0.0006                         |
| 2026 H2  |    1992 |                                -0.0071 | -0.0125 to -0.0012                         |                                -0.0003 | -0.0010 to +0.0004                         |

## Variants vs baseline (paired by race)

| comparison                                    | races   |     n |    mean |   95% lo |   95% hi |   share of races better |
|:----------------------------------------------|:--------|------:|--------:|---------:|---------:|------------------------:|
| prod blend logit - baseline blend logit       | all     | 37821 | -0.0002 |  -0.0005 |   0.0000 |                  0.5095 |
| prod blend logit - baseline blend logit       | QLD     | 16991 | -0.0005 |  -0.0008 |  -0.0002 |                  0.5243 |
| prod blend logit - baseline blend logit       | VIC/SA  | 20830 |  0.0000 |  -0.0003 |   0.0003 |                  0.4974 |
| prod2 blend logit - baseline blend logit      | all     | 37821 | -0.0001 |  -0.0004 |   0.0001 |                  0.5046 |
| prod2 blend logit - baseline blend logit      | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5172 |
| prod2 blend logit - baseline blend logit      | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4943 |
| prod2-fig2 blend logit - baseline blend logit | all     | 37821 | -0.0002 |  -0.0005 |   0.0001 |                  0.5090 |
| prod2-fig2 blend logit - baseline blend logit | QLD     | 16991 | -0.0007 |  -0.0011 |  -0.0003 |                  0.5242 |
| prod2-fig2 blend logit - baseline blend logit | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4965 |
| prod2-gps blend logit - baseline blend logit  | all     | 37821 | -0.0001 |  -0.0004 |   0.0001 |                  0.5046 |
| prod2-gps blend logit - baseline blend logit  | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5168 |
| prod2-gps blend logit - baseline blend logit  | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4947 |
| prod2-mu blend logit - baseline blend logit   | all     | 37821 | -0.0001 |  -0.0004 |   0.0002 |                  0.5028 |
| prod2-mu blend logit - baseline blend logit   | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5138 |
| prod2-mu blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0005 |                  0.4938 |
| prod2-v4 blend logit - baseline blend logit   | all     | 37821 | -0.0001 |  -0.0004 |   0.0002 |                  0.5035 |
| prod2-v4 blend logit - baseline blend logit   | QLD     | 16991 | -0.0005 |  -0.0009 |  -0.0001 |                  0.5175 |
| prod2-v4 blend logit - baseline blend logit   | VIC/SA  | 20830 |  0.0002 |  -0.0002 |   0.0006 |                  0.4921 |
| prod model logit - baseline model logit       | all     | 37821 | -0.0056 |  -0.0071 |  -0.0041 |                  0.5127 |
| prod model logit - baseline model logit       | QLD     | 16991 | -0.0050 |  -0.0071 |  -0.0030 |                  0.5208 |
| prod model logit - baseline model logit       | VIC/SA  | 20830 | -0.0060 |  -0.0081 |  -0.0039 |                  0.5060 |
| prod2 model logit - baseline model logit      | all     | 37821 | -0.0071 |  -0.0090 |  -0.0053 |                  0.5128 |
| prod2 model logit - baseline model logit      | QLD     | 16991 | -0.0088 |  -0.0116 |  -0.0060 |                  0.5134 |
| prod2 model logit - baseline model logit      | VIC/SA  | 20830 | -0.0057 |  -0.0084 |  -0.0031 |                  0.5123 |
| prod2-fig2 model logit - baseline model logit | all     | 37821 | -0.0090 |  -0.0107 |  -0.0074 |                  0.5196 |
| prod2-fig2 model logit - baseline model logit | QLD     | 16991 | -0.0108 |  -0.0133 |  -0.0082 |                  0.5249 |
| prod2-fig2 model logit - baseline model logit | VIC/SA  | 20830 | -0.0075 |  -0.0098 |  -0.0052 |                  0.5152 |
| prod2-gps model logit - baseline model logit  | all     | 37821 | -0.0071 |  -0.0091 |  -0.0051 |                  0.5130 |
| prod2-gps model logit - baseline model logit  | QLD     | 16991 | -0.0088 |  -0.0117 |  -0.0059 |                  0.5138 |
| prod2-gps model logit - baseline model logit  | VIC/SA  | 20830 | -0.0057 |  -0.0084 |  -0.0032 |                  0.5123 |
| prod2-mu model logit - baseline model logit   | all     | 37821 | -0.0070 |  -0.0089 |  -0.0051 |                  0.5122 |
| prod2-mu model logit - baseline model logit   | QLD     | 16991 | -0.0087 |  -0.0116 |  -0.0058 |                  0.5124 |
| prod2-mu model logit - baseline model logit   | VIC/SA  | 20830 | -0.0055 |  -0.0081 |  -0.0030 |                  0.5120 |
| prod2-v4 model logit - baseline model logit   | all     | 37821 | -0.0071 |  -0.0089 |  -0.0052 |                  0.5126 |
| prod2-v4 model logit - baseline model logit   | QLD     | 16991 | -0.0084 |  -0.0112 |  -0.0057 |                  0.5140 |
| prod2-v4 model logit - baseline model logit   | VIC/SA  | 20830 | -0.0059 |  -0.0086 |  -0.0034 |                  0.5115 |

## Variants vs baseline by 6-month period (blend)

| period   |   races |   prod blend logit - baseline blend logit | prod blend logit - baseline blend logit 95%   |   prod2 blend logit - baseline blend logit | prod2 blend logit - baseline blend logit 95%   |   prod2-fig2 blend logit - baseline blend logit | prod2-fig2 blend logit - baseline blend logit 95%   |   prod2-gps blend logit - baseline blend logit | prod2-gps blend logit - baseline blend logit 95%   |   prod2-mu blend logit - baseline blend logit | prod2-mu blend logit - baseline blend logit 95%   |   prod2-v4 blend logit - baseline blend logit | prod2-v4 blend logit - baseline blend logit 95%   |
|:---------|--------:|------------------------------------------:|:----------------------------------------------|-------------------------------------------:|:-----------------------------------------------|------------------------------------------------:|:----------------------------------------------------|-----------------------------------------------:|:---------------------------------------------------|----------------------------------------------:|:--------------------------------------------------|----------------------------------------------:|:--------------------------------------------------|
| 2023 H1  |    5012 |                                   -0.0004 | -0.0011 to +0.0003                            |                                    -0.0004 | -0.0013 to +0.0005                             |                                         -0.0004 | -0.0013 to +0.0004                                  |                                        -0.0004 | -0.0013 to +0.0004                                 |                                       -0.0003 | -0.0012 to +0.0006                                |                                       -0.0004 | -0.0013 to +0.0004                                |
| 2023 H2  |    5233 |                                   -0.0003 | -0.0011 to +0.0004                            |                                    -0.0003 | -0.0012 to +0.0005                             |                                         -0.0004 | -0.0012 to +0.0005                                  |                                        -0.0003 | -0.0012 to +0.0006                                 |                                       -0.0004 | -0.0012 to +0.0006                                |                                       -0.0003 | -0.0012 to +0.0006                                |
| 2024 H1  |    5145 |                                   -0.0004 | -0.0011 to +0.0002                            |                                    -0.0003 | -0.0011 to +0.0005                             |                                         -0.0004 | -0.0012 to +0.0003                                  |                                        -0.0003 | -0.0011 to +0.0004                                 |                                       -0.0003 | -0.0011 to +0.0004                                |                                       -0.0004 | -0.0011 to +0.0004                                |
| 2024 H2  |    5229 |                                   -0.0005 | -0.0012 to +0.0001                            |                                    -0.0005 | -0.0012 to +0.0002                             |                                         -0.0006 | -0.0013 to +0.0001                                  |                                        -0.0005 | -0.0012 to +0.0003                                 |                                       -0.0005 | -0.0012 to +0.0003                                |                                       -0.0004 | -0.0011 to +0.0004                                |
| 2025 H1  |    5065 |                                   -0.0002 | -0.0009 to +0.0005                            |                                    -0.0001 | -0.0009 to +0.0007                             |                                         -0.0002 | -0.0009 to +0.0005                                  |                                        -0.0001 | -0.0008 to +0.0007                                 |                                       -0.0000 | -0.0009 to +0.0008                                |                                       -0.0001 | -0.0009 to +0.0007                                |
| 2025 H2  |    5153 |                                    0.0005 | -0.0003 to +0.0012                            |                                     0.0007 | -0.0001 to +0.0015                             |                                          0.0006 | -0.0001 to +0.0014                                  |                                         0.0007 | -0.0000 to +0.0016                                 |                                        0.0007 | -0.0001 to +0.0015                                |                                        0.0008 | +0.0000 to +0.0016                                |
| 2026 H1  |    4992 |                                   -0.0001 | -0.0006 to +0.0005                            |                                     0.0001 | -0.0005 to +0.0007                             |                                          0.0000 | -0.0005 to +0.0006                                  |                                         0.0001 | -0.0004 to +0.0007                                 |                                        0.0001 | -0.0005 to +0.0007                                |                                        0.0001 | -0.0005 to +0.0006                                |
| 2026 H2  |    1992 |                                   -0.0003 | -0.0011 to +0.0005                            |                                    -0.0006 | -0.0015 to +0.0004                             |                                         -0.0005 | -0.0014 to +0.0004                                  |                                        -0.0006 | -0.0015 to +0.0003                                 |                                       -0.0006 | -0.0015 to +0.0003                                |                                       -0.0004 | -0.0013 to +0.0005                                |

## Weights (fitted on training data only)

|      |   SP calibration c | blend window               |   SP calibration c, QLD |   SP calibration c, VIC/SA |   baseline logit a |   baseline logit b |   baseline logit a, QLD |   baseline logit b, QLD |   baseline logit a, VIC/SA |   baseline logit b, VIC/SA |   prod logit a |   prod logit b |   prod logit a, QLD |   prod logit b, QLD |   prod logit a, VIC/SA |   prod logit b, VIC/SA |   prod2 logit a |   prod2 logit b |   prod2 logit a, QLD |   prod2 logit b, QLD |   prod2 logit a, VIC/SA |   prod2 logit b, VIC/SA |   prod2-fig2 logit a |   prod2-fig2 logit b |   prod2-fig2 logit a, QLD |   prod2-fig2 logit b, QLD |   prod2-fig2 logit a, VIC/SA |   prod2-fig2 logit b, VIC/SA |   prod2-gps logit a |   prod2-gps logit b |   prod2-gps logit a, QLD |   prod2-gps logit b, QLD |   prod2-gps logit a, VIC/SA |   prod2-gps logit b, VIC/SA |   prod2-mu logit a |   prod2-mu logit b |   prod2-mu logit a, QLD |   prod2-mu logit b, QLD |   prod2-mu logit a, VIC/SA |   prod2-mu logit b, VIC/SA |   prod2-v4 logit a |   prod2-v4 logit b |   prod2-v4 logit a, QLD |   prod2-v4 logit b, QLD |   prod2-v4 logit a, VIC/SA |   prod2-v4 logit b, VIC/SA |
|-----:|-------------------:|:---------------------------|------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|---------------:|---------------:|--------------------:|--------------------:|-----------------------:|-----------------------:|----------------:|----------------:|---------------------:|---------------------:|------------------------:|------------------------:|---------------------:|---------------------:|--------------------------:|--------------------------:|-----------------------------:|-----------------------------:|--------------------:|--------------------:|-------------------------:|-------------------------:|----------------------------:|----------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|-------------------:|-------------------:|------------------------:|------------------------:|---------------------------:|---------------------------:|
| 2023 |              1.189 | 09 Oct 2022 to 31 Dec 2022 |                   1.225 |                      1.166 |              0.152 |              1.089 |                   0.263 |                   1.048 |                      0.050 |                      1.133 |          0.181 |          1.067 |               0.274 |               1.037 |                  0.096 |                  1.102 |           0.175 |           1.069 |                0.281 |                1.027 |                   0.079 |                   1.112 |                0.181 |                1.065 |                     0.289 |                     1.021 |                        0.084 |                        1.109 |               0.174 |               1.069 |                    0.279 |                    1.028 |                       0.080 |                       1.111 |              0.175 |              1.069 |                   0.279 |                   1.028 |                      0.081 |                      1.111 |              0.179 |              1.066 |                   0.282 |                   1.026 |                      0.086 |                      1.108 |
| 2024 |              1.111 | 15 Jul 2023 to 31 Dec 2023 |                   1.151 |                      1.081 |              0.101 |              1.042 |                   0.158 |                   1.032 |                      0.024 |                      1.065 |          0.135 |          1.016 |               0.183 |               1.009 |                  0.070 |                  1.035 |           0.135 |           1.016 |                0.190 |                1.003 |                   0.062 |                   1.040 |                0.141 |                1.011 |                     0.198 |                     0.996 |                        0.066 |                        1.037 |               0.135 |               1.016 |                    0.190 |                    1.003 |                       0.062 |                       1.040 |              0.137 |              1.014 |                   0.193 |                   1.002 |                      0.065 |                      1.038 |              0.134 |              1.016 |                   0.188 |                   1.005 |                      0.063 |                      1.039 |
| 2025 |              1.159 | 25 Apr 2024 to 31 Dec 2024 |                   1.174 |                      1.146 |              0.118 |              1.075 |                   0.179 |                   1.038 |                      0.048 |                      1.114 |          0.149 |          1.049 |               0.201 |               1.018 |                  0.091 |                  1.083 |           0.145 |           1.053 |                0.205 |                1.015 |                   0.080 |                   1.090 |                0.149 |                1.049 |                     0.207 |                     1.013 |                        0.086 |                        1.086 |               0.145 |               1.053 |                    0.205 |                    1.015 |                       0.080 |                       1.090 |              0.144 |              1.053 |                   0.205 |                   1.016 |                      0.079 |                      1.091 |              0.146 |              1.052 |                   0.204 |                   1.016 |                      0.082 |                      1.089 |
| 2026 |              1.119 | 09 Jan 2025 to 31 Dec 2025 |                   1.112 |                      1.125 |              0.108 |              1.045 |                   0.171 |                   0.988 |                      0.051 |                      1.091 |          0.124 |          1.032 |               0.182 |               0.976 |                  0.072 |                  1.076 |           0.115 |           1.038 |                0.185 |                0.973 |                   0.052 |                   1.090 |                0.119 |                1.034 |                     0.185 |                     0.972 |                        0.060 |                        1.084 |               0.115 |               1.038 |                    0.185 |                    0.973 |                       0.052 |                       1.089 |              0.115 |              1.038 |                   0.185 |                   0.973 |                      0.051 |                      1.090 |              0.116 |              1.037 |                   0.186 |                   0.972 |                      0.052 |                      1.090 |
