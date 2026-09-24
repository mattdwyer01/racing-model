# SP vs model vs blend (same test races)

- Test: VIC/SA/QLD races, one year per fold (2023 to 2026 YTD), every runner with an SP and one winner
- Model: no market inputs (figure + ability + jockey/trainer + race-day projection); logit and LightGBM
- Blend and SP-calibration weights fitted on the last 25% of each fold's training window, using out-of-sample model predictions from a model fitted on the first 75%; never on test data
- Negative differences = blend (or model) better than SP. 95% ranges: 2,000 race bootstrap resamples

## Log loss by fold

|                   |       2023 |       2024 |       2025 |      2026 |     pooled |
|:------------------|-----------:|-----------:|-----------:|----------:|-----------:|
| races             | 10245.0000 | 10374.0000 | 10218.0000 | 6984.0000 | 37821.0000 |
| SP raw            |     1.7934 |     1.7934 |     1.7891 |    1.7811 |     1.7900 |
| SP calibrated     |     1.7920 |     1.7885 |     1.7856 |    1.7757 |     1.7863 |
| model: logit      |     1.9338 |     1.9309 |     1.9352 |    1.9328 |     1.9332 |
| blend: logit + SP |     1.7907 |     1.7872 |     1.7845 |    1.7752 |     1.7852 |
| model: gbm        |     1.9188 |     1.9112 |     1.9047 |    1.8978 |     1.9090 |
| blend: gbm + SP   |     1.7916 |     1.7879 |     1.7846 |    1.7750 |     1.7856 |

## Differences vs SP, pooled over all test races

| comparison                            |    mean |   95% lo |   95% hi |   share of races better |
|:--------------------------------------|--------:|---------:|---------:|------------------------:|
| blend: logit + SP minus SP raw        | -0.0048 |  -0.0061 |  -0.0036 |                  0.5947 |
| model: logit minus SP raw             |  0.1432 |   0.1382 |   0.1488 |                  0.3848 |
| blend: logit + SP minus SP calibrated | -0.0011 |  -0.0017 |  -0.0005 |                  0.5235 |
| model: logit minus SP calibrated      |  0.1469 |   0.1412 |   0.1525 |                  0.3793 |
| blend: gbm + SP minus SP raw          | -0.0044 |  -0.0055 |  -0.0032 |                  0.5947 |
| model: gbm minus SP raw               |  0.1190 |   0.1145 |   0.1237 |                  0.3999 |
| blend: gbm + SP minus SP calibrated   | -0.0007 |  -0.0011 |  -0.0003 |                  0.5194 |
| model: gbm minus SP calibrated        |  0.1227 |   0.1174 |   0.1280 |                  0.3880 |

## By 6-month period (blend minus SP, with 95% range)

| period   |   races |   SP raw |   SP calibrated |   logit blend - SP raw | logit vs raw 95%   |   logit blend - SP cal | logit vs cal 95%   |   gbm blend - SP raw | gbm vs raw 95%     |   gbm blend - SP cal | gbm vs cal 95%     |
|:---------|--------:|---------:|----------------:|-----------------------:|:-------------------|-----------------------:|:-------------------|---------------------:|:-------------------|---------------------:|:-------------------|
| 2023 H1  |    5012 |   1.7919 |          1.7910 |                -0.0037 | -0.0079 to +0.0004 |                -0.0028 | -0.0048 to -0.0010 |              -0.0028 | -0.0069 to +0.0013 |              -0.0019 | -0.0034 to -0.0005 |
| 2023 H2  |    5233 |   1.7949 |          1.7930 |                -0.0018 | -0.0059 to +0.0022 |                 0.0000 | -0.0019 to +0.0019 |              -0.0010 | -0.0047 to +0.0029 |               0.0009 | -0.0005 to +0.0023 |
| 2024 H1  |    5145 |   1.7858 |          1.7815 |                -0.0059 | -0.0084 to -0.0034 |                -0.0016 | -0.0029 to -0.0003 |              -0.0053 | -0.0075 to -0.0030 |              -0.0010 | -0.0018 to -0.0001 |
| 2024 H2  |    5229 |   1.8008 |          1.7953 |                -0.0066 | -0.0090 to -0.0041 |                -0.0010 | -0.0024 to +0.0003 |              -0.0058 | -0.0080 to -0.0035 |              -0.0002 | -0.0010 to +0.0006 |
| 2025 H1  |    5065 |   1.7740 |          1.7700 |                -0.0051 | -0.0084 to -0.0016 |                -0.0010 | -0.0026 to +0.0005 |              -0.0048 | -0.0081 to -0.0015 |              -0.0007 | -0.0019 to +0.0004 |
| 2025 H2  |    5153 |   1.8039 |          1.8009 |                -0.0041 | -0.0074 to -0.0009 |                -0.0011 | -0.0026 to +0.0005 |              -0.0042 | -0.0074 to -0.0012 |              -0.0013 | -0.0024 to -0.0001 |
| 2026 H1  |    4992 |   1.7745 |          1.7694 |                -0.0053 | -0.0081 to -0.0028 |                -0.0002 | -0.0016 to +0.0013 |              -0.0057 | -0.0084 to -0.0031 |              -0.0006 | -0.0021 to +0.0008 |
| 2026 H2  |    1992 |   1.7978 |          1.7917 |                -0.0075 | -0.0116 to -0.0033 |                -0.0014 | -0.0038 to +0.0009 |              -0.0070 | -0.0110 to -0.0030 |              -0.0008 | -0.0031 to +0.0015 |

## Blend weights (fitted on training data only)

|   fold | blend window               |   SP calibration c |   logit a |   logit b |   gbm a |   gbm b |
|-------:|:---------------------------|-------------------:|----------:|----------:|--------:|--------:|
|   2023 | 09 Oct 2022 to 31 Dec 2022 |              1.189 |     0.151 |     1.089 |   0.117 |   1.107 |
|   2024 | 15 Jul 2023 to 31 Dec 2023 |              1.111 |     0.102 |     1.042 |   0.070 |   1.060 |
|   2025 | 25 Apr 2024 to 31 Dec 2024 |              1.159 |     0.117 |     1.076 |   0.096 |   1.085 |
|   2026 | 09 Jan 2025 to 31 Dec 2025 |              1.119 |     0.109 |     1.045 |   0.119 |   1.030 |
