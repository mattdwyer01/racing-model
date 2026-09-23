# Market-offset models: fixed-price backtest

- Test: 2,808 VIC/SA/QLD races 26 Apr to 13 Sep 2026; trained on 43,059 races before 26 Apr 2026 (SP as the market), GBM rounds 203
- At test time the fixed price replaces SP as the market input

## Log loss

| model                       |   log loss |   vs fixed (cal) |     se |
|:----------------------------|-----------:|-----------------:|-------:|
| fixed (calibrated)          |     1.8264 |           0.0000 | 0.0000 |
| logit: fixed + ability      |     1.8266 |           0.0002 | 0.0013 |
| logit: fixed + ability + jt |     1.8270 |           0.0005 | 0.0014 |
| gbm offset                  |     1.8247 |          -0.0017 | 0.0011 |

## Betting at the fixed price

| model                       |   edge >= | staking   |   bets |   strike |   avg price |   staked |   profit |    roi |   roi 95% lo |   roi 95% hi |
|:----------------------------|----------:|:----------|-------:|---------:|------------:|---------:|---------:|-------:|-------------:|-------------:|
| logit: fixed + ability + jt |     0.000 | flat      |    200 |    0.260 |       6.220 |  200.000 |  -17.850 | -0.089 |       -0.287 |        0.131 |
| logit: fixed + ability + jt |     0.000 | kelly     |    200 |    0.260 |       6.220 |  129.808 |   12.913 |  0.099 |       -0.220 |        0.376 |
| logit: fixed + ability + jt |     0.050 | flat      |     84 |    0.226 |       8.210 |   84.000 |   -8.100 | -0.096 |       -0.360 |        0.227 |
| logit: fixed + ability + jt |     0.050 | kelly     |     84 |    0.226 |       8.210 |   99.063 |   18.201 |  0.184 |       -0.178 |        0.535 |
| logit: fixed + ability + jt |     0.100 | flat      |     51 |    0.216 |       9.909 |   51.000 |   -8.050 | -0.158 |       -0.481 |        0.214 |
| logit: fixed + ability + jt |     0.100 | kelly     |     51 |    0.216 |       9.909 |   75.277 |   22.358 |  0.297 |       -0.145 |        0.681 |
| logit: fixed + ability + jt |     0.200 | flat      |     20 |    0.200 |       8.213 |   20.000 |   -3.650 | -0.183 |       -0.733 |        0.348 |
| logit: fixed + ability + jt |     0.200 | kelly     |     20 |    0.200 |       8.213 |   48.380 |   16.009 |  0.331 |       -0.468 |        0.902 |
| logit: fixed + ability + jt |     0.300 | flat      |     10 |    0.300 |       7.930 |   10.000 |    5.000 |  0.500 |      nan     |      nan     |
| logit: fixed + ability + jt |     0.300 | kelly     |     10 |    0.300 |       7.930 |   22.555 |   21.949 |  0.973 |      nan     |      nan     |
| gbm offset                  |     0.000 | flat      |    128 |    0.156 |       7.728 |  128.000 |  -34.250 | -0.268 |       -0.550 |        0.082 |
| gbm offset                  |     0.000 | kelly     |    128 |    0.156 |       7.728 |   92.529 |   -1.830 | -0.020 |       -0.410 |        0.281 |
| gbm offset                  |     0.050 | flat      |     70 |    0.143 |       9.164 |   70.000 |  -31.600 | -0.451 |       -0.705 |       -0.185 |
| gbm offset                  |     0.050 | kelly     |     70 |    0.143 |       9.164 |   81.731 |    3.253 |  0.040 |       -0.349 |        0.345 |
| gbm offset                  |     0.100 | flat      |     41 |    0.195 |      10.274 |   41.000 |   -8.750 | -0.213 |       -0.551 |        0.169 |
| gbm offset                  |     0.100 | kelly     |     41 |    0.195 |      10.274 |   64.445 |   13.550 |  0.210 |       -0.245 |        0.581 |
| gbm offset                  |     0.200 | flat      |     22 |    0.182 |       9.716 |   22.000 |   -5.650 | -0.257 |       -0.700 |        0.037 |
| gbm offset                  |     0.200 | kelly     |     22 |    0.182 |       9.716 |   49.222 |    7.302 |  0.148 |       -0.513 |        0.625 |
| gbm offset                  |     0.300 | flat      |     10 |    0.200 |      10.130 |   10.000 |    0.000 |  0.000 |      nan     |      nan     |
| gbm offset                  |     0.300 | kelly     |     10 |    0.200 |      10.130 |   21.373 |    7.382 |  0.345 |      nan     |      nan     |
