# Early-price backtest

- Prices: git history of toprate_runners.csv (86,943 runners, 26 Apr to 23 Sep 2026); snapshots every ~20 to 40 min on race days
- Models trained on races before 26 Apr 2026 with SP as the market (GBM rounds 145); at test time the price at T is the market input and the bet price
- Eval: VIC/SA/QLD races where every final-field runner has a price at T and a final price
- CLV = mean log(price at T / final price) over bets; > 0 = beat the close

## Coverage

|   T (min) |   races |   runners |   median actual minutes before jump |
|----------:|--------:|----------:|------------------------------------:|
|       0.0 |  1698.0 |   17041.0 |                                79.4 |
|      10.0 |  1696.0 |   17021.0 |                               115.7 |
|      30.0 |  1684.0 |   16905.0 |                               143.7 |
|      60.0 |  1669.0 |   16777.0 |                               178.7 |
|     120.0 |  1570.0 |   15802.0 |                               342.1 |
|     240.0 |  1413.0 |   14288.0 |                               442.9 |

## Log loss (vs final price; negative = better than the final market)

|   T (min) | model                 |   log loss |   vs final |     se |
|----------:|:----------------------|-----------:|-----------:|-------:|
|         0 | final price (raw)     |     1.8541 |     0.0000 | 0.0000 |
|         0 | price at T (raw)      |     1.8816 |     0.0275 | 0.0046 |
|         0 | logit: + ability + jt |     1.8809 |     0.0267 | 0.0055 |
|         0 | gbm offset            |     1.8789 |     0.0248 | 0.0053 |
|        10 | final price (raw)     |     1.8542 |     0.0000 | 0.0000 |
|        10 | price at T (raw)      |     1.8888 |     0.0346 | 0.0052 |
|        10 | logit: + ability + jt |     1.8878 |     0.0336 | 0.0060 |
|        10 | gbm offset            |     1.8863 |     0.0321 | 0.0059 |
|        30 | final price (raw)     |     1.8543 |     0.0000 | 0.0000 |
|        30 | price at T (raw)      |     1.8932 |     0.0388 | 0.0056 |
|        30 | logit: + ability + jt |     1.8925 |     0.0382 | 0.0064 |
|        30 | gbm offset            |     1.8913 |     0.0369 | 0.0063 |
|        60 | final price (raw)     |     1.8565 |     0.0000 | 0.0000 |
|        60 | price at T (raw)      |     1.8964 |     0.0400 | 0.0057 |
|        60 | logit: + ability + jt |     1.8957 |     0.0393 | 0.0065 |
|        60 | gbm offset            |     1.8949 |     0.0384 | 0.0064 |
|       120 | final price (raw)     |     1.8600 |     0.0000 | 0.0000 |
|       120 | price at T (raw)      |     1.9001 |     0.0401 | 0.0062 |
|       120 | logit: + ability + jt |     1.8984 |     0.0384 | 0.0069 |
|       120 | gbm offset            |     1.8974 |     0.0374 | 0.0068 |
|       240 | final price (raw)     |     1.8697 |     0.0000 | 0.0000 |
|       240 | price at T (raw)      |     1.9155 |     0.0458 | 0.0068 |
|       240 | logit: + ability + jt |     1.9149 |     0.0453 | 0.0075 |
|       240 | gbm offset            |     1.9135 |     0.0438 | 0.0074 |

## Betting at the price at T (flat 1 unit)

|   T (min) | model                 |   edge >= |   bets |   avg price |    roi |   roi 95% lo |   roi 95% hi |   clv (mean log) |   clv se |   share shortened |
|----------:|:----------------------|----------:|-------:|------------:|-------:|-------------:|-------------:|-----------------:|---------:|------------------:|
|         0 | logit: + ability + jt |     0.050 |    166 |      13.957 |  0.461 |       -0.207 |        1.498 |            0.283 |    0.029 |             0.687 |
|         0 | logit: + ability + jt |     0.100 |    122 |      13.234 | -0.009 |       -0.342 |        0.441 |            0.299 |    0.034 |             0.680 |
|         0 | logit: + ability + jt |     0.200 |     61 |      11.758 |  0.315 |       -0.250 |        1.141 |            0.362 |    0.054 |             0.721 |
|         0 | gbm offset            |     0.050 |    152 |      11.850 | -0.057 |       -0.358 |        0.303 |            0.275 |    0.029 |             0.684 |
|         0 | gbm offset            |     0.100 |    112 |      11.326 |  0.045 |       -0.316 |        0.510 |            0.312 |    0.037 |             0.696 |
|         0 | gbm offset            |     0.200 |     59 |      10.501 |  0.256 |       -0.320 |        1.037 |            0.374 |    0.055 |             0.746 |
|        10 | logit: + ability + jt |     0.050 |    165 |      13.592 |  0.438 |       -0.215 |        1.507 |            0.284 |    0.030 |             0.703 |
|        10 | logit: + ability + jt |     0.100 |    122 |      13.048 | -0.048 |       -0.383 |        0.397 |            0.287 |    0.036 |             0.680 |
|        10 | logit: + ability + jt |     0.200 |     62 |      11.378 |  0.297 |       -0.251 |        1.054 |            0.349 |    0.057 |             0.742 |
|        10 | gbm offset            |     0.050 |    146 |      12.016 | -0.043 |       -0.354 |        0.330 |            0.272 |    0.032 |             0.685 |
|        10 | gbm offset            |     0.100 |    112 |      11.251 |  0.011 |       -0.341 |        0.444 |            0.296 |    0.040 |             0.696 |
|        10 | gbm offset            |     0.200 |     61 |      10.352 |  0.218 |       -0.314 |        0.979 |            0.363 |    0.055 |             0.754 |
|        30 | logit: + ability + jt |     0.050 |    177 |      13.101 |  0.414 |       -0.212 |        1.380 |            0.272 |    0.029 |             0.701 |
|        30 | logit: + ability + jt |     0.100 |    130 |      12.702 | -0.009 |       -0.341 |        0.428 |            0.290 |    0.034 |             0.700 |
|        30 | logit: + ability + jt |     0.200 |     67 |      10.962 |  0.276 |       -0.241 |        1.000 |            0.347 |    0.053 |             0.761 |
|        30 | gbm offset            |     0.050 |    157 |      11.885 | -0.030 |       -0.311 |        0.359 |            0.280 |    0.030 |             0.701 |
|        30 | gbm offset            |     0.100 |    124 |      11.036 |  0.015 |       -0.325 |        0.458 |            0.301 |    0.037 |             0.710 |
|        30 | gbm offset            |     0.200 |     67 |       9.987 |  0.239 |       -0.255 |        0.926 |            0.360 |    0.050 |             0.776 |
|        60 | logit: + ability + jt |     0.050 |    180 |      12.902 |  0.391 |       -0.231 |        1.346 |            0.273 |    0.029 |             0.700 |
|        60 | logit: + ability + jt |     0.100 |    131 |      12.524 | -0.017 |       -0.365 |        0.412 |            0.289 |    0.034 |             0.695 |
|        60 | logit: + ability + jt |     0.200 |     67 |      10.947 |  0.276 |       -0.239 |        0.990 |            0.346 |    0.053 |             0.746 |
|        60 | gbm offset            |     0.050 |    160 |      11.739 | -0.048 |       -0.313 |        0.330 |            0.280 |    0.030 |             0.700 |
|        60 | gbm offset            |     0.100 |    124 |      11.029 |  0.015 |       -0.314 |        0.442 |            0.301 |    0.037 |             0.702 |
|        60 | gbm offset            |     0.200 |     67 |       9.972 |  0.239 |       -0.247 |        0.902 |            0.359 |    0.050 |             0.761 |
|       120 | logit: + ability + jt |     0.050 |    330 |      13.463 |  0.336 |       -0.124 |        0.906 |            0.311 |    0.021 |             0.767 |
|       120 | logit: + ability + jt |     0.100 |    238 |      13.023 |  0.208 |       -0.164 |        0.690 |            0.341 |    0.025 |             0.769 |
|       120 | logit: + ability + jt |     0.200 |    115 |      10.947 |  0.260 |       -0.143 |        0.723 |            0.389 |    0.040 |             0.783 |
|       120 | gbm offset            |     0.050 |    300 |      11.957 |  0.189 |       -0.126 |        0.582 |            0.321 |    0.021 |             0.770 |
|       120 | gbm offset            |     0.100 |    218 |      10.899 |  0.109 |       -0.150 |        0.408 |            0.340 |    0.026 |             0.761 |
|       120 | gbm offset            |     0.200 |    117 |      10.200 |  0.152 |       -0.210 |        0.619 |            0.406 |    0.037 |             0.812 |
|       240 | logit: + ability + jt |     0.050 |    389 |      13.658 |  0.501 |       -0.013 |        1.201 |            0.345 |    0.020 |             0.789 |
|       240 | logit: + ability + jt |     0.100 |    279 |      13.219 |  0.533 |       -0.009 |        1.228 |            0.391 |    0.024 |             0.810 |
|       240 | logit: + ability + jt |     0.200 |    139 |      12.513 |  0.868 |        0.055 |        2.170 |            0.483 |    0.040 |             0.835 |
|       240 | gbm offset            |     0.050 |    355 |      12.275 |  0.432 |        0.000 |        0.991 |            0.361 |    0.021 |             0.803 |
|       240 | gbm offset            |     0.100 |    259 |      11.578 |  0.418 |       -0.060 |        1.080 |            0.387 |    0.026 |             0.803 |
|       240 | gbm offset            |     0.200 |    139 |      12.227 |  0.745 |       -0.074 |        1.963 |            0.489 |    0.039 |             0.849 |

## Checks and caveats
- Baseline, all runners at T=0: CLV -0.068, 26% shortened (every price band negative). Model picks: CLV +0.27 to +0.37,
  68 to 75% shortened, se about 0.03. The picks' CLV is not a long-shot artefact.
- Snapshots are sparse: at T=0 the price used is on median 79 minutes old; 43% of runners have only one recorded price
  in the file (the dashboard did not refresh them), and for those the "final" price equals that one price.
- So "price at T" is what the dashboard showed, not necessarily what TAB offered then. The model may partly be picking
  stale dashboard prices that TAB had already cut. This cannot be settled from this file.
- Verify against the Vultr poller log (every TAB read, timestamped) before trusting CLV or ROI. Until then: no betting.
