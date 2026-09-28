# Pace forecasts: new inputs and targets

- 38,370 VIC/SA/QLD test races 2023 to 2026 YTD (walk-forward); GPS pace known for 14,833. See the module docstring for models and inputs.

## Accuracy (pooled test races)

| projection | R2 early shape | corr early shape | corr GPS pace | corr leader value (weighted) |
|---|---|---|---|---|
| v3 | 0.094 | 0.326 | 0.251 | 0.037 |
| shape+ | 0.102 | 0.339 | 0.277 | 0.046 |
| gps | -1.925 | 0.160 | 0.553 | 0.009 |
| gps+ | -2.016 | 0.172 | 0.553 | 0.020 |
| lv+ | -0.232 | 0.091 | 0.036 | 0.128 |

By fold, R2 early shape:

|   fold |    v3 |   shape+ |    gps |   gps+ |    lv+ |
|-------:|------:|---------:|-------:|-------:|-------:|
|   2023 | 0.060 |    0.057 | -1.011 | -1.160 | -0.173 |
|   2024 | 0.104 |    0.115 | -2.155 | -2.220 | -0.291 |
|   2025 | 0.119 |    0.127 | -2.855 | -2.832 | -0.264 |
|   2026 | 0.126 |    0.157 | -2.489 | -2.648 | -0.247 |

## Leader value sorting

beta = change in the within-race WPR slope on projected settle share per SD of the projection (sign set so positive = races the projection rates faster / worse for leaders have less leader value). Slopes are WPR per unit settle share (negative = forward runners better).

| projection | beta per SD (95% CI) | slope, bottom fifth | slope, top fifth | spread |
|---|---|---|---|---|
| v3 | +0.700 (+0.490 to +0.898) | -1.60 | +0.34 | +1.94 |
| shape+ | +0.871 (+0.672 to +1.064) | -1.72 | +0.74 | +2.46 |
| gps | +0.108 (-0.077 to +0.302) | -0.80 | -0.34 | +0.46 |
| gps+ | +0.302 (+0.109 to +0.486) | -1.00 | -0.09 | +0.90 |
| lv+ | +2.277 (+2.072 to +2.488) | -4.13 | +2.19 | +6.32 |
| hindsight: actual early shape | +1.794 (+1.487 to +2.105) | -3.15 | +2.62 | +5.76 |
| hindsight: actual GPS pace | +1.608 (+1.316 to +1.866) | -2.01 | +2.61 | +4.62 |

## Combined projections (z-scores averaged)

| combo | beta per SD (95% CI) | spread |
|---|---|---|
| v3 + lv+ | +1.912 (+1.723 to +2.116) | +5.61 |
| shape+ + lv+ | +1.964 (+1.768 to +2.164) | +5.71 |
| gps+ + lv+ | +1.798 (+1.602 to +1.981) | +4.72 |
| shape+ + gps+ + lv+ | +1.678 (+1.494 to +1.878) | +4.22 |

## Correlations between projections

|        |   v3 |   shape+ |   gps |   gps+ |   lv+ |
|:-------|-----:|---------:|------:|-------:|------:|
| v3     | 1.00 |     0.87 |  0.43 |   0.38 |  0.18 |
| shape+ | 0.87 |     1.00 |  0.41 |   0.43 |  0.23 |
| gps    | 0.43 |     0.41 |  1.00 |   0.89 | -0.00 |
| gps+   | 0.38 |     0.43 |  0.89 |   1.00 |  0.04 |
| lv+    | 0.18 |     0.23 | -0.00 |   0.04 |  1.00 |
