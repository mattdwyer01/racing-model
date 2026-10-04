# Leave-one-group-out, production logit (walk-forward 2023 to 2026, VIC/SA/QLD)

- 38,310 races. Full model: model alone 1.9228, blend 1.7842, SP 1.7894. Differences = without the group minus full (positive = the group helps).

| dropped group                      |   inputs | model alone                  | blend                        | blend QLD                    | blend VIC/SA                 |
|:-----------------------------------|---------:|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| comments + ground loss (past runs) |       20 | +0.0003 (-0.0005 to +0.0012) | +0.0001 (-0.0001 to +0.0002) | +0.0002 (+0.0000 to +0.0004) | -0.0000 (-0.0002 to +0.0002) |

Blend weight on the model (a) per fold:

|      |   full |   - comments + ground loss (past runs) |
|-----:|-------:|---------------------------------------:|
| 2023 |  0.183 |                                  0.166 |
| 2024 |  0.136 |                                  0.124 |
| 2025 |  0.153 |                                  0.138 |
| 2026 |  0.118 |                                  0.111 |

