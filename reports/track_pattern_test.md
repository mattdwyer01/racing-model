# Track pattern: where winners settle / draw at a track under today's conditions

- 100,217 races 2017 on with 800m positions (VIC/SA/QLD/NSW/WA). Pattern per race = the winner's
  settle (or barrier) share minus the field mean: negative = winners came from forward (inside).

## Stability: even vs odd years (cells with 10+ races in each half)

| cells                           | pattern   |   cells used |   median races |   split-half r |   sd of cell means |   lambda |
|:--------------------------------|:----------|-------------:|---------------:|---------------:|-------------------:|---------:|
| track                           | settle    |          194 |            318 |          0.709 |              0.052 |    130.4 |
| track                           | barrier   |          194 |            318 |          0.375 |              0.051 |    529.4 |
| track x distance                | settle    |          447 |            136 |          0.685 |              0.067 |     62.5 |
| track x distance                | barrier   |          447 |            136 |          0.294 |              0.056 |    327   |
| track x going                   | settle    |          411 |            163 |          0.525 |              0.059 |    147.7 |
| track x going                   | barrier   |          411 |            163 |          0.241 |              0.057 |    512.1 |
| track x rail                    | settle    |          351 |            247 |          0.591 |              0.053 |    170.7 |
| track x rail                    | barrier   |          351 |            247 |          0.31  |              0.052 |    550.4 |
| track x distance x going        | settle    |          815 |             76 |          0.505 |              0.075 |     74.4 |
| track x distance x going        | barrier   |          815 |             76 |          0.191 |              0.064 |    322.6 |
| track x distance x going x rail | settle    |         1213 |             50 |          0.41  |              0.081 |     71.8 |
| track x distance x going x rail | barrier   |         1213 |             50 |          0.174 |              0.076 |    236.8 |

## On top of the live Proj (walk-forward 2024 to Sep 2026, weight fitted on the previous year)

- 28,065 races; lines set to hold 3.03 / 4.62 runners a race; winners per 100 races vs live.

| term                                       | weights (2024 / 25 / 26)          | inside 3 vs live       | inside 5 vs live       | top pick % (live)   |
|:-------------------------------------------|:----------------------------------|:-----------------------|:-----------------------|:--------------------|
| settle: track                              | -0.06 / -0.09 / 0.02              | -0.02 (-0.08 to +0.05) | -0.01 (-0.07 to +0.04) | 28.79 (28.77)       |
| barrier: track                             | 0.18 / -0.15 / 0.20               | +0.02 (-0.07 to +0.11) | -0.01 (-0.10 to +0.06) | 28.82 (28.77)       |
| settle: track x distance                   | 0.10 / 0.02 / 0.10                | -0.00 (-0.08 to +0.07) | -0.06 (-0.12 to +0.00) | 28.74 (28.77)       |
| barrier: track x distance                  | 0.00 / -0.03 / 0.15               | -0.03 (-0.08 to +0.02) | -0.04 (-0.09 to +0.02) | 28.76 (28.77)       |
| settle: track x going                      | -0.05 / -0.18 / -0.04             | -0.02 (-0.10 to +0.05) | -0.05 (-0.12 to +0.02) | 28.74 (28.77)       |
| barrier: track x going                     | 0.36 / 0.17 / 0.30                | -0.08 (-0.18 to +0.02) | -0.12 (-0.21 to -0.04) | 28.76 (28.77)       |
| settle: track x rail                       | -0.08 / 0.02 / 0.06               | -0.03 (-0.08 to +0.02) | -0.01 (-0.06 to +0.03) | 28.80 (28.77)       |
| barrier: track x rail                      | 0.19 / 0.03 / 0.42                | -0.04 (-0.12 to +0.05) | -0.10 (-0.16 to -0.02) | 28.84 (28.77)       |
| settle: track x distance x going           | 0.12 / 0.07 / 0.08                | +0.01 (-0.07 to +0.09) | -0.04 (-0.11 to +0.02) | 28.74 (28.77)       |
| barrier: track x distance x going          | 0.25 / 0.05 / 0.24                | -0.04 (-0.11 to +0.04) | -0.06 (-0.12 to +0.01) | 28.77 (28.77)       |
| settle: track x distance x going x rail    | 0.17 / 0.20 / 0.03                | -0.01 (-0.11 to +0.09) | -0.04 (-0.12 to +0.03) | 28.75 (28.77)       |
| barrier: track x distance x going x rail   | 0.27 / 0.11 / 0.27                | -0.07 (-0.16 to +0.01) | -0.02 (-0.09 to +0.04) | 28.82 (28.77)       |
| settle + barrier: track x distance x going | 0.13,0.25 / 0.07,0.05 / 0.08,0.24 | -0.02 (-0.12 to +0.07) | -0.11 (-0.19 to -0.03) | 28.77 (28.77)       |

