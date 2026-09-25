# racing.com (VIC/SA) GPS: with vs without

- 37,821 VIC/SA/QLD test races, folds 2023 to 2026 YTD, walk-forward (blend_eval, logit). The two runs differ only in the racing.com rows of gps_runs (ground-loss projection target, past ground-loss credit).
- with minus without; negative = racing.com GPS helps. 95% race bootstrap.

## Paired differences

| model                 | all (n=37,821)               | VIC/SA (n=20,830)            | VIC (n=15,646)               | SA (n=5,184)                 | QLD (n=16,991)               |
|:----------------------|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| baseline: model logit | +0.0000 (-0.0001 to +0.0001) | +0.0000 (-0.0001 to +0.0001) | +0.0000 (-0.0001 to +0.0002) | -0.0001 (-0.0003 to +0.0002) | -0.0000 (-0.0001 to +0.0001) |
| baseline: blend logit | +0.0000 (-0.0000 to +0.0000) | -0.0000 (-0.0000 to +0.0000) | +0.0000 (-0.0000 to +0.0000) | -0.0000 (-0.0000 to +0.0000) | +0.0000 (+0.0000 to +0.0000) |
| prodmu: model logit   | -0.0001 (-0.0006 to +0.0005) | -0.0000 (-0.0005 to +0.0005) | +0.0001 (-0.0004 to +0.0008) | -0.0006 (-0.0015 to +0.0004) | -0.0001 (-0.0012 to +0.0009) |
| prodmu: blend logit   | -0.0000 (-0.0001 to +0.0001) | -0.0000 (-0.0001 to +0.0000) | -0.0000 (-0.0001 to +0.0000) | -0.0001 (-0.0002 to +0.0001) | -0.0000 (-0.0002 to +0.0002) |

## By fold (all races)

|      |   baseline: model logit |   baseline: blend logit |   prodmu: model logit |   prodmu: blend logit |
|-----:|------------------------:|------------------------:|----------------------:|----------------------:|
| 2023 |                 +0.0001 |                 +0.0000 |               -0.0002 |               -0.0000 |
| 2024 |                 -0.0001 |                 +0.0000 |               -0.0005 |               -0.0001 |
| 2025 |                 +0.0000 |                 +0.0000 |               +0.0004 |               +0.0000 |
| 2026 |                 -0.0001 |                 -0.0000 |               +0.0001 |               -0.0000 |

## Log loss by state

|                               |    QLD |     SA |    VIC |
|:------------------------------|-------:|-------:|-------:|
| baseline: model logit with    | 1.8818 | 2.0445 | 1.9518 |
| baseline: model logit without | 1.8818 | 2.0446 | 1.9517 |
| baseline: blend logit with    | 1.7463 | 1.9085 | 1.7865 |
| baseline: blend logit without | 1.7463 | 1.9085 | 1.7865 |
| prodmu: model logit with      | 1.8715 | 2.0398 | 1.9430 |
| prodmu: model logit without   | 1.8716 | 2.0404 | 1.9429 |
| prodmu: blend logit with      | 1.7456 | 1.9090 | 1.7866 |
| prodmu: blend logit without   | 1.7457 | 1.9091 | 1.7866 |
| SP calibrated with            | 1.7492 | 1.9083 | 1.7861 |

