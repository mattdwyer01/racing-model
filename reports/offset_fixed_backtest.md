# Market-offset models: fixed-price backtest

- Test: 2,808 VIC/SA/QLD races 26 Apr to 13 Sep 2026; trained on 43,059 races before 26 Apr 2026 (SP as the market), GBM rounds 136
- At test time the fixed price replaces SP as the market input

## Log loss

| model                                    |   log loss |   vs fixed (cal) |     se |
|:-----------------------------------------|-----------:|-----------------:|-------:|
| fixed (calibrated)                       |     1.8264 |           0.0000 | 0.0000 |
| logit: fixed + ability                   |     1.8266 |           0.0002 | 0.0013 |
| logit: fixed + ability + jt              |     1.8270 |           0.0005 | 0.0014 |
| logit: fixed + ability + jt + projection |     1.8270 |           0.0006 | 0.0014 |
| gbm offset, no projection                |     1.8244 |          -0.0020 | 0.0012 |
| gbm offset                               |     1.8254 |          -0.0010 | 0.0009 |

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
| gbm offset                  |     0.000 | flat      |     91 |    0.198 |       7.993 |   91.000 |  -23.250 | -0.255 |       -0.489 |        0.014 |
| gbm offset                  |     0.000 | kelly     |     91 |    0.198 |       7.993 |   79.301 |   15.323 |  0.193 |       -0.204 |        0.523 |
| gbm offset                  |     0.050 | flat      |     55 |    0.182 |       9.649 |   55.000 |  -14.550 | -0.265 |       -0.577 |        0.134 |
| gbm offset                  |     0.050 | kelly     |     55 |    0.182 |       9.649 |   72.656 |   15.417 |  0.212 |       -0.230 |        0.602 |
| gbm offset                  |     0.100 | flat      |     40 |    0.225 |       9.854 |   40.000 |   -3.350 | -0.084 |       -0.426 |        0.292 |
| gbm offset                  |     0.100 | kelly     |     40 |    0.225 |       9.854 |   66.859 |   19.508 |  0.292 |       -0.163 |        0.715 |
| gbm offset                  |     0.200 | flat      |     19 |    0.263 |       7.697 |   19.000 |    1.750 |  0.092 |       -0.476 |        0.724 |
| gbm offset                  |     0.200 | kelly     |     19 |    0.263 |       7.697 |   47.492 |   18.992 |  0.400 |       -0.267 |        1.056 |
| gbm offset                  |     0.300 | flat      |      9 |    0.222 |       6.233 |    9.000 |    1.000 |  0.111 |       -1.000 |        0.636 |
| gbm offset                  |     0.300 | kelly     |      9 |    0.222 |       6.233 |   24.078 |    7.066 |  0.293 |       -1.000 |        1.315 |
