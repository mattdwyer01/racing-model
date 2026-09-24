# GPS pace target and VIC/SA ground loss

- gps_pace = 100 x log(leaders' speed 200 to 600m after the start / field median speed over the last 400m); QLD RQ and VIC/SA racing.com Triple S races of 1000m+

## Projection accuracy (test year)

| metric                                |     2023 |     2024 |     2025 |     2026 |
|:--------------------------------------|---------:|---------:|---------:|---------:|
| GPS pace R2: GPS pace model           |    0.145 |    0.296 |    0.364 |    0.357 |
| GPS pace corr: GPS pace model         |    0.399 |    0.546 |    0.605 |    0.605 |
| GPS pace corr: v3 shape projection    |    0.277 |    0.264 |    0.227 |    0.248 |
| GPS pace races in test                | 3010.000 | 4045.000 | 4310.000 | 3373.000 |
| GPS pace vs actual TopRate shape corr |    0.601 |    0.622 |    0.603 |    0.626 |
| ground loss R2 QLD: fit on QLD only   |    0.169 |    0.188 |    0.169 |    0.069 |
| ground loss R2 QLD: fit on all GPS    |    0.152 |    0.194 |    0.175 |    0.078 |
| ground loss R2 SA: fit on QLD only    |  nan     |    0.212 |    0.217 |    0.155 |
| ground loss R2 SA: fit on all GPS     |  nan     |    0.223 |    0.258 |    0.180 |
| ground loss R2 VIC: fit on QLD only   |    0.135 |    0.122 |    0.128 |    0.125 |
| ground loss R2 VIC: fit on all GPS    |    0.133 |    0.166 |    0.190 |    0.182 |

## WPR cost of GPS pace (within race, fitted before each fold)

on_pace x gps_pace: WPR per unit of gps_pace x (1 - settle share); negative = a hot pace costs on-pace runners

|                    |   2023 |   2024 |   2025 |   2026 |
|:-------------------|-------:|-------:|-------:|-------:|
| on_pace x gps_pace | -0.148 | -0.161 | -0.175 | -0.178 |
| settle             | -2.409 | -2.652 | -2.693 | -2.652 |

## Win logit, figure + projection (pooled race log loss)

|             |   log loss |
|:------------|-----------:|
| v3          |     1.9856 |
| gl QLD only |     1.9855 |
| + GPS pace  |     1.9856 |

## Paired differences (negative = first is better; 95% race bootstrap; state of the race)

| model      | vs          | all                          | QLD                          | VIC                          | SA                           |
|:-----------|:------------|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| v3         | gl QLD only | +0.0000 (-0.0000 to +0.0001) | +0.0000 (-0.0001 to +0.0001) | +0.0000 (-0.0001 to +0.0001) | -0.0000 (-0.0002 to +0.0002) |
| + GPS pace | v3          | +0.0000 (-0.0001 to +0.0001) | +0.0000 (-0.0001 to +0.0001) | -0.0000 (-0.0002 to +0.0001) | +0.0002 (-0.0000 to +0.0004) |
