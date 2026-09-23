# Race-day projection: walk-forward R2 (VIC/SA/QLD test races)

- Each model trained on 2019 to Y-1 (all AU; ground loss on QLD GPS runs), tested on year Y

| target                                            |   2023 |   2024 |   2025 |   2026 |   test n (all folds) |
|:--------------------------------------------------|-------:|-------:|-------:|-------:|---------------------:|
| ground loss: barrier share only (best linear fit) |  0.152 |  0.164 |  0.142 |  0.047 |            98473.000 |
| ground loss: projection (QLD GPS)                 |  0.161 |  0.187 |  0.166 |  0.016 |            98473.000 |
| race pace: projection                             |  0.041 |  0.069 |  0.073 |  0.070 |            32827.000 |
| settle: past-settle rank only                     | -0.083 | -0.087 | -0.087 | -0.082 |           327618.000 |
| settle: projection                                |  0.283 |  0.292 |  0.285 |  0.291 |           327618.000 |
