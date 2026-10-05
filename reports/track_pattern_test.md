# Track pattern: where winners settle / draw at a track under today's conditions

- 100,217 races 2017 on with 800m positions (VIC/SA/QLD/NSW/WA). Pattern per race = the winner's
  settle (or barrier) share minus the field mean: negative = winners came from forward (inside).

## Stability: even vs odd years (cells with 10+ races in each half)

| cells                           | pattern   |   cells used |   median races |   split-half r |   sd of cell means |   lambda |
|:--------------------------------|:----------|-------------:|---------------:|---------------:|-------------------:|---------:|
| track                           | settle    |          194 |            318 |          0.709 |              0.052 |    130.3 |
| track                           | barrier   |          194 |            318 |          0.374 |              0.051 |    533.4 |
| track x distance                | settle    |          447 |            136 |          0.686 |              0.067 |     62.3 |
| track x distance                | barrier   |          447 |            136 |          0.293 |              0.056 |    327.5 |
| track x going                   | settle    |          411 |            163 |          0.524 |              0.059 |    147.8 |
| track x going                   | barrier   |          411 |            163 |          0.241 |              0.057 |    513   |
| track x rail                    | settle    |          351 |            247 |          0.592 |              0.053 |    170.3 |
| track x rail                    | barrier   |          351 |            247 |          0.309 |              0.052 |    552.1 |
| track x distance x going        | settle    |          815 |             76 |          0.505 |              0.075 |     74.6 |
| track x distance x going        | barrier   |          815 |             76 |          0.191 |              0.064 |    322   |
| track x distance x going x rail | settle    |         1213 |             50 |          0.41  |              0.081 |     71.8 |
| track x distance x going x rail | barrier   |         1213 |             50 |          0.175 |              0.076 |    236.4 |

## On top of the live Proj (walk-forward 2024 to Sep 2026, weight fitted on the previous year)

- 28,065 races; lines set to hold 3.03 / 4.62 runners a race; winners per 100 races vs live.

| term                                       | weights (2024 / 25 / 26)            | inside 3 vs live       | inside 5 vs live       | top pick % (live)   |
|:-------------------------------------------|:------------------------------------|:-----------------------|:-----------------------|:--------------------|
| settle: track                              | 0.03 / 0.10 / 0.02                  | -0.33 (-0.46 to -0.21) | +0.04 (-0.06 to +0.14) | 28.73 (28.77)       |
| barrier: track                             | 0.09 / -0.31 / -0.29                | +0.07 (-0.03 to +0.19) | +0.01 (-0.09 to +0.11) | 28.73 (28.77)       |
| settle: track x distance                   | 0.05 / 0.11 / 0.03                  | -0.36 (-0.50 to -0.22) | -0.04 (-0.15 to +0.07) | 28.72 (28.77)       |
| barrier: track x distance                  | -0.04 / -0.22 / -0.24               | +0.06 (-0.03 to +0.15) | +0.02 (-0.06 to +0.10) | 28.73 (28.77)       |
| settle: track x going                      | 0.03 / 0.10 / 0.02                  | -0.32 (-0.43 to -0.19) | +0.07 (-0.02 to +0.17) | 28.69 (28.77)       |
| barrier: track x going                     | 0.17 / -0.19 / -0.24                | +0.00 (-0.10 to +0.10) | -0.06 (-0.13 to +0.02) | 28.78 (28.77)       |
| settle: track x rail                       | 0.04 / 0.13 / 0.03                  | -0.37 (-0.51 to -0.25) | -0.01 (-0.12 to +0.09) | 28.73 (28.77)       |
| barrier: track x rail                      | 0.15 / -0.18 / -0.12                | +0.00 (-0.08 to +0.10) | -0.01 (-0.08 to +0.07) | 28.78 (28.77)       |
| settle: track x distance x going           | 0.06 / 0.12 / 0.03                  | -0.35 (-0.48 to -0.21) | +0.00 (-0.10 to +0.11) | 28.70 (28.77)       |
| barrier: track x distance x going          | 0.10 / -0.23 / -0.19                | +0.02 (-0.07 to +0.10) | -0.03 (-0.10 to +0.04) | 28.80 (28.77)       |
| settle: track x distance x going x rail    | 0.08 / 0.16 / 0.02                  | -0.30 (-0.42 to -0.17) | +0.02 (-0.09 to +0.12) | 28.68 (28.77)       |
| barrier: track x distance x going x rail   | 0.20 / -0.13 / -0.11                | +0.01 (-0.07 to +0.08) | -0.08 (-0.14 to -0.02) | 28.88 (28.77)       |
| settle + barrier: track x distance x going | 0.06,0.10 / 0.12,-0.22 / 0.03,-0.19 | -0.31 (-0.44 to -0.17) | -0.06 (-0.17 to +0.04) | 28.74 (28.77)       |

