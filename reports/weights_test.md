# Carried weight: real vs race average

- 37,821 VIC/SA/QLD test races, folds 2023 to 2026 YTD, walk-forward (blend_eval, logit). The two runs differ only in carried weight (the 'without' run sets runs.weight_kg = 57 for every run: weight vs field = 0, sectional weight correction off).
- with minus without; negative = it helps. 95% race bootstrap.

## Paired differences

| model                 | all (n=37,821)               | VIC/SA (n=20,830)            | VIC (n=15,646)               | SA (n=5,184)                 | QLD (n=16,991)               |
|:----------------------|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| baseline: model logit | -0.0028 (-0.0036 to -0.0020) | -0.0027 (-0.0037 to -0.0017) | -0.0024 (-0.0034 to -0.0012) | -0.0037 (-0.0060 to -0.0015) | -0.0029 (-0.0041 to -0.0017) |
| baseline: blend logit | -0.0002 (-0.0003 to -0.0001) | +0.0000 (-0.0001 to +0.0001) | +0.0000 (-0.0001 to +0.0002) | -0.0001 (-0.0004 to +0.0001) | -0.0004 (-0.0005 to -0.0002) |
| prodmu: model logit   | -0.0029 (-0.0038 to -0.0021) | -0.0026 (-0.0036 to -0.0015) | -0.0023 (-0.0035 to -0.0012) | -0.0033 (-0.0059 to -0.0009) | -0.0034 (-0.0047 to -0.0020) |
| prodmu: blend logit   | -0.0002 (-0.0004 to -0.0001) | +0.0000 (-0.0001 to +0.0002) | +0.0001 (-0.0001 to +0.0002) | -0.0001 (-0.0004 to +0.0003) | -0.0005 (-0.0007 to -0.0003) |

## By fold (all races)

|      |   baseline: model logit |   baseline: blend logit |   prodmu: model logit |   prodmu: blend logit |
|-----:|------------------------:|------------------------:|----------------------:|----------------------:|
| 2023 |                 -0.0032 |                 -0.0003 |               -0.0034 |               -0.0004 |
| 2024 |                 -0.0027 |                 -0.0002 |               -0.0027 |               -0.0002 |
| 2025 |                 -0.0019 |                 -0.0000 |               -0.0020 |               -0.0000 |
| 2026 |                 -0.0036 |                 -0.0001 |               -0.0039 |               -0.0002 |

## Log loss by state

|                               |    QLD |     SA |    VIC |
|:------------------------------|-------:|-------:|-------:|
| baseline: model logit with    | 1.8818 | 2.0445 | 1.9518 |
| baseline: model logit without | 1.8847 | 2.0483 | 1.9541 |
| baseline: blend logit with    | 1.7463 | 1.9085 | 1.7865 |
| baseline: blend logit without | 1.7467 | 1.9086 | 1.7865 |
| prodmu: model logit with      | 1.8715 | 2.0398 | 1.9430 |
| prodmu: model logit without   | 1.8749 | 2.0431 | 1.9454 |
| prodmu: blend logit with      | 1.7456 | 1.9090 | 1.7866 |
| prodmu: blend logit without   | 1.7462 | 1.9091 | 1.7865 |
| SP calibrated with            | 1.7492 | 1.9083 | 1.7861 |

