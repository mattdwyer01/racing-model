# Ground loss in the figure: QLD walk-forward

- Eval set: QLD races 2023 on, SP for every runner, one winner (16,991 races)
- Folds: test year Y (2024 to 2026 YTD), trained on QLD 2023 to Y-1
- Ground loss = GPS metres travelled vs field mean; rail = avg distance from rail vs field mean; decayed means over prior starts, 0 plus a missing flag where a past run has no GPS

## Log loss by fold

| fold   |      races |   figure |   figure + ground loss |   figure + ground loss + rail |   SP (calibrated) |   SP + figure |   SP + figure + ground loss + rail |
|:-------|-----------:|---------:|-----------------------:|------------------------------:|------------------:|--------------:|-----------------------------------:|
| 2024   |  4628.0000 |   1.9451 |                 1.9429 |                        1.9436 |            1.7473 |        1.7462 |                             1.7455 |
| 2025   |  4557.0000 |   1.9483 |                 1.9488 |                        1.9487 |            1.7618 |        1.7585 |                             1.7595 |
| 2026   |  3190.0000 |   1.9306 |                 1.9289 |                        1.9279 |            1.7388 |        1.7370 |                             1.7362 |
| pooled | 12375.0000 |   1.9426 |                 1.9415 |                        1.9414 |            1.7505 |        1.7484 |                             1.7483 |

## Paired differences (negative = first is better)

| model | vs | test races | diff | se |
|---|---|---|---|---|
| figure + ground loss | figure (all) | 12,375 | -0.0011 | 0.0005 |
| figure + ground loss | figure (field GPS history >= 60%) | 7,148 | -0.0023 | 0.0008 |
| figure + ground loss + rail | figure + ground loss (all) | 12,375 | -0.0000 | 0.0002 |
| figure + ground loss + rail | figure + ground loss (field GPS history >= 60%) | 7,148 | -0.0002 | 0.0002 |
| SP + figure | SP (calibrated) (all) | 12,375 | -0.0021 | 0.0008 |
| SP + figure | SP (calibrated) (field GPS history >= 60%) | 7,148 | +0.0014 | 0.0010 |
| SP + figure + ground loss + rail | SP + figure (all) | 12,375 | -0.0001 | 0.0004 |
| SP + figure + ground loss + rail | SP + figure (field GPS history >= 60%) | 7,148 | -0.0006 | 0.0005 |
| SP + figure + ground loss + rail | SP (calibrated) (all) | 12,375 | -0.0022 | 0.0009 |
| SP + figure + ground loss + rail | SP (calibrated) (field GPS history >= 60%) | 7,148 | +0.0008 | 0.0011 |

## Figure weights (fit on all QLD 2023 on, WPR points per unit)

| component | c_j |
|---|---|
| gl | +0.210 |
| rail | +0.790 |
| settle | -6.249 |
| pace | +0.770 |
| s_l600 | +0.238 |
