# Price timing: model + market at T minutes before the jump (2026 races)

- Model trained on races before 2026 only; blend and calibration weights fitted on training data with SP (c = 1.119; logit: a = 0.108, b = 1.045; gbm: a = 0.113, b = 1.035)
- Price at T = last git snapshot of toprate_runners.csv at or before start - T. Snapshots are sparse, so the actual age is shown; T-2 and T-10 often use the same snapshot
- Caveat: snapshot prices are what the dashboard showed, not necessarily what TAB offered at that moment
- Negative DIFF = blend better than the calibrated price at T. 95% ranges: race bootstrap

## Coverage

|   T (min) |   races |   runners |   median minutes before jump |   90th pct |
|----------:|--------:|----------:|-----------------------------:|-----------:|
|      60.0 |  1669.0 |   16777.0 |                        178.7 |     1117.4 |
|      30.0 |  1684.0 |   16905.0 |                        143.7 |     1074.0 |
|      10.0 |  1696.0 |   17021.0 |                        115.7 |      938.9 |
|       2.0 |  1697.0 |   17030.0 |                         89.6 |      550.9 |

## Log loss

|   T (min) | model                                    |   log loss | races   |   95% lo |   95% hi |         n |
|----------:|:-----------------------------------------|-----------:|:--------|---------:|---------:|----------:|
|        60 | price at T raw                           |     1.8964 | nan     | nan      | nan      |  nan      |
|        60 | price at T calibrated                    |     1.8948 | nan     | nan      | nan      |  nan      |
|        60 | SP raw (same races)                      |     1.8561 | nan     | nan      | nan      |  nan      |
|        60 | model logit                              |     2.0195 | nan     | nan      | nan      |  nan      |
|        60 | blend logit + price at T                 |     1.8953 | nan     | nan      | nan      |  nan      |
|        60 | model gbm                                |     1.9946 | nan     | nan      | nan      |  nan      |
|        60 | blend gbm + price at T                   |     1.8956 | nan     | nan      | nan      |  nan      |
|        60 | DIFF blend logit - calibrated price at T |     0.0004 | all     |  -0.0017 |   0.0026 | 1669.0000 |
|        60 | DIFF blend logit - calibrated price at T |     0.0030 | QLD     |  -0.0003 |   0.0062 |  731.0000 |
|        60 | DIFF blend logit - calibrated price at T |    -0.0016 | VIC/SA  |  -0.0046 |   0.0014 |  938.0000 |
|        60 | DIFF blend gbm - calibrated price at T   |     0.0008 | all     |  -0.0015 |   0.0029 | 1669.0000 |
|        60 | DIFF blend gbm - calibrated price at T   |     0.0031 | QLD     |  -0.0002 |   0.0066 |  731.0000 |
|        60 | DIFF blend gbm - calibrated price at T   |    -0.0011 | VIC/SA  |  -0.0041 |   0.0018 |  938.0000 |
|        30 | price at T raw                           |     1.8932 | nan     | nan      | nan      |  nan      |
|        30 | price at T calibrated                    |     1.8915 | nan     | nan      | nan      |  nan      |
|        30 | SP raw (same races)                      |     1.8541 | nan     | nan      | nan      |  nan      |
|        30 | model logit                              |     2.0199 | nan     | nan      | nan      |  nan      |
|        30 | blend logit + price at T                 |     1.8922 | nan     | nan      | nan      |  nan      |
|        30 | model gbm                                |     1.9939 | nan     | nan      | nan      |  nan      |
|        30 | blend gbm + price at T                   |     1.8924 | nan     | nan      | nan      |  nan      |
|        30 | DIFF blend logit - calibrated price at T |     0.0007 | all     |  -0.0015 |   0.0029 | 1684.0000 |
|        30 | DIFF blend logit - calibrated price at T |     0.0030 | QLD     |  -0.0003 |   0.0063 |  734.0000 |
|        30 | DIFF blend logit - calibrated price at T |    -0.0010 | VIC/SA  |  -0.0042 |   0.0021 |  950.0000 |
|        30 | DIFF blend gbm - calibrated price at T   |     0.0009 | all     |  -0.0013 |   0.0031 | 1684.0000 |
|        30 | DIFF blend gbm - calibrated price at T   |     0.0031 | QLD     |  -0.0001 |   0.0064 |  734.0000 |
|        30 | DIFF blend gbm - calibrated price at T   |    -0.0007 | VIC/SA  |  -0.0038 |   0.0023 |  950.0000 |
|        10 | price at T raw                           |     1.8888 | nan     | nan      | nan      |  nan      |
|        10 | price at T calibrated                    |     1.8867 | nan     | nan      | nan      |  nan      |
|        10 | SP raw (same races)                      |     1.8540 | nan     | nan      | nan      |  nan      |
|        10 | model logit                              |     2.0201 | nan     | nan      | nan      |  nan      |
|        10 | blend logit + price at T                 |     1.8878 | nan     | nan      | nan      |  nan      |
|        10 | model gbm                                |     1.9927 | nan     | nan      | nan      |  nan      |
|        10 | blend gbm + price at T                   |     1.8879 | nan     | nan      | nan      |  nan      |
|        10 | DIFF blend logit - calibrated price at T |     0.0011 | all     |  -0.0012 |   0.0034 | 1696.0000 |
|        10 | DIFF blend logit - calibrated price at T |     0.0032 | QLD     |  -0.0003 |   0.0065 |  739.0000 |
|        10 | DIFF blend logit - calibrated price at T |    -0.0005 | VIC/SA  |  -0.0036 |   0.0025 |  957.0000 |
|        10 | DIFF blend gbm - calibrated price at T   |     0.0012 | all     |  -0.0012 |   0.0034 | 1696.0000 |
|        10 | DIFF blend gbm - calibrated price at T   |     0.0032 | QLD     |   0.0000 |   0.0064 |  739.0000 |
|        10 | DIFF blend gbm - calibrated price at T   |    -0.0004 | VIC/SA  |  -0.0034 |   0.0026 |  957.0000 |
|         2 | price at T raw                           |     1.8844 | nan     | nan      | nan      |  nan      |
|         2 | price at T calibrated                    |     1.8822 | nan     | nan      | nan      |  nan      |
|         2 | SP raw (same races)                      |     1.8540 | nan     | nan      | nan      |  nan      |
|         2 | model logit                              |     2.0201 | nan     | nan      | nan      |  nan      |
|         2 | blend logit + price at T                 |     1.8835 | nan     | nan      | nan      |  nan      |
|         2 | model gbm                                |     1.9927 | nan     | nan      | nan      |  nan      |
|         2 | blend gbm + price at T                   |     1.8837 | nan     | nan      | nan      |  nan      |
|         2 | DIFF blend logit - calibrated price at T |     0.0014 | all     |  -0.0008 |   0.0035 | 1697.0000 |
|         2 | DIFF blend logit - calibrated price at T |     0.0034 | QLD     |   0.0002 |   0.0067 |  739.0000 |
|         2 | DIFF blend logit - calibrated price at T |    -0.0002 | VIC/SA  |  -0.0032 |   0.0028 |  958.0000 |
|         2 | DIFF blend gbm - calibrated price at T   |     0.0015 | all     |  -0.0007 |   0.0037 | 1697.0000 |
|         2 | DIFF blend gbm - calibrated price at T   |     0.0035 | QLD     |   0.0001 |   0.0069 |  739.0000 |
|         2 | DIFF blend gbm - calibrated price at T   |    -0.0000 | VIC/SA  |  -0.0031 |   0.0031 |  958.0000 |

## Secondary: weights refitted on 2026 prices before 1 July, tested from 1 July

|   T (min) | model   |   fit races (before 1 Jul) |   test races (from 1 Jul) |    c_T |     a_T |    b_T |   blend - calibrated price at T |   95% lo |   95% hi |
|----------:|:--------|---------------------------:|--------------------------:|-------:|--------:|-------:|--------------------------------:|---------:|---------:|
|        60 | logit   |                        989 |                       680 | 1.0339 |  0.0159 | 1.0222 |                         -0.0002 |  -0.0007 |   0.0003 |
|        60 | gbm     |                        989 |                       680 | 1.0339 |  0.0082 | 1.0271 |                         -0.0001 |  -0.0003 |   0.0002 |
|        30 | logit   |                        994 |                       690 | 1.0345 |  0.0055 | 1.0305 |                         -0.0001 |  -0.0002 |   0.0001 |
|        30 | gbm     |                        994 |                       690 | 1.0345 | -0.0056 | 1.0392 |                          0.0000 |  -0.0001 |   0.0002 |
|        10 | logit   |                       1001 |                       695 | 1.0381 | -0.0087 | 1.0445 |                          0.0001 |  -0.0002 |   0.0003 |
|        10 | gbm     |                       1001 |                       695 | 1.0381 | -0.0160 | 1.0513 |                          0.0001 |  -0.0004 |   0.0006 |
|         2 | logit   |                       1001 |                       696 | 1.0390 | -0.0226 | 1.0556 |                          0.0001 |  -0.0005 |   0.0008 |
|         2 | gbm     |                       1001 |                       696 | 1.0390 | -0.0349 | 1.0677 |                          0.0002 |  -0.0008 |   0.0012 |
