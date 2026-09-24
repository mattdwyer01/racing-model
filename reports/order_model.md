# Finishing-order model (place and exotics)

- Stagewise Plackett-Luce from out-of-sample win probabilities; 2nd and 3rd use p^l2, p^l3 (Harville: 1, 1)
- l2, l3 fitted on earlier test years only; evaluated 2024 to 2026 VIC/SA/QLD; place = TAB rules
- Log loss: exacta / trifecta per race (-log P(actual order)); place per runner (binary); lower is better

## Mean log loss (2024 to 2026)

|                               |   exacta |   trifecta |   place |
|:------------------------------|---------:|-----------:|--------:|
| SP calibrated / Harville      |   3.6081 |     5.4101 |  0.5130 |
| SP calibrated / discounted    |   3.5943 |     5.3547 |  0.5088 |
| blend prod / Harville         |   3.6056 |     5.4053 |  0.5125 |
| blend prod / discounted       |   3.5920 |     5.3507 |  0.5083 |
| blend sim / Harville          |   3.6057 |     5.4055 |  0.5125 |
| blend sim / discounted        |   3.5920 |     5.3508 |  0.5083 |
| blend prod + sim / Harville   |   3.6066 |     5.4067 |  0.5126 |
| blend prod + sim / discounted |   3.5928 |     5.3518 |  0.5085 |

## Paired differences (negative = first is better; 95% race bootstrap)

| first                         | minus                       | metric   |   races | all                          | QLD                          | VIC/SA                       |
|:------------------------------|:----------------------------|:---------|--------:|:-----------------------------|:-----------------------------|:-----------------------------|
| SP calibrated / discounted    | SP calibrated / Harville    | exacta   |   27451 | -0.0138 (-0.0159 to -0.0116) | -0.0139 (-0.0170 to -0.0107) | -0.0137 (-0.0169 to -0.0105) |
| SP calibrated / discounted    | SP calibrated / Harville    | trifecta |   27441 | -0.0554 (-0.0599 to -0.0507) | -0.0532 (-0.0597 to -0.0466) | -0.0571 (-0.0633 to -0.0513) |
| SP calibrated / discounted    | SP calibrated / Harville    | place    |   27046 | -0.0042 (-0.0046 to -0.0037) | -0.0039 (-0.0045 to -0.0033) | -0.0044 (-0.0050 to -0.0038) |
| blend prod / discounted       | blend prod / Harville       | exacta   |   27451 | -0.0137 (-0.0158 to -0.0114) | -0.0143 (-0.0176 to -0.0110) | -0.0132 (-0.0163 to -0.0100) |
| blend prod / discounted       | blend prod / Harville       | trifecta |   27441 | -0.0546 (-0.0593 to -0.0500) | -0.0538 (-0.0601 to -0.0471) | -0.0553 (-0.0615 to -0.0486) |
| blend prod / discounted       | blend prod / Harville       | place    |   27046 | -0.0041 (-0.0046 to -0.0037) | -0.0040 (-0.0046 to -0.0033) | -0.0042 (-0.0049 to -0.0036) |
| blend sim / discounted        | blend sim / Harville        | exacta   |   27451 | -0.0137 (-0.0160 to -0.0114) | -0.0142 (-0.0174 to -0.0108) | -0.0132 (-0.0163 to -0.0102) |
| blend sim / discounted        | blend sim / Harville        | trifecta |   27441 | -0.0547 (-0.0593 to -0.0503) | -0.0536 (-0.0602 to -0.0467) | -0.0555 (-0.0617 to -0.0492) |
| blend sim / discounted        | blend sim / Harville        | place    |   27046 | -0.0041 (-0.0046 to -0.0037) | -0.0040 (-0.0047 to -0.0033) | -0.0043 (-0.0049 to -0.0037) |
| blend prod + sim / discounted | blend prod + sim / Harville | exacta   |   27451 | -0.0138 (-0.0161 to -0.0115) | -0.0145 (-0.0181 to -0.0112) | -0.0133 (-0.0165 to -0.0103) |
| blend prod + sim / discounted | blend prod + sim / Harville | trifecta |   27441 | -0.0548 (-0.0591 to -0.0504) | -0.0541 (-0.0609 to -0.0474) | -0.0555 (-0.0615 to -0.0490) |
| blend prod + sim / discounted | blend prod + sim / Harville | place    |   27046 | -0.0041 (-0.0046 to -0.0037) | -0.0040 (-0.0047 to -0.0033) | -0.0043 (-0.0048 to -0.0036) |
| blend prod / discounted       | SP calibrated / discounted  | exacta   |   27451 | -0.0023 (-0.0034 to -0.0014) | -0.0052 (-0.0069 to -0.0036) | -0.0000 (-0.0014 to +0.0013) |
| blend prod / discounted       | SP calibrated / discounted  | trifecta |   27441 | -0.0041 (-0.0052 to -0.0029) | -0.0079 (-0.0098 to -0.0062) | -0.0009 (-0.0024 to +0.0005) |
| blend prod / discounted       | SP calibrated / discounted  | place    |   27046 | -0.0005 (-0.0006 to -0.0003) | -0.0009 (-0.0012 to -0.0007) | -0.0001 (-0.0003 to +0.0001) |
| blend sim / discounted        | SP calibrated / discounted  | exacta   |   27451 | -0.0023 (-0.0032 to -0.0014) | -0.0049 (-0.0063 to -0.0034) | -0.0002 (-0.0015 to +0.0010) |
| blend sim / discounted        | SP calibrated / discounted  | trifecta |   27441 | -0.0039 (-0.0050 to -0.0028) | -0.0074 (-0.0090 to -0.0058) | -0.0011 (-0.0025 to +0.0003) |
| blend sim / discounted        | SP calibrated / discounted  | place    |   27046 | -0.0005 (-0.0006 to -0.0003) | -0.0009 (-0.0011 to -0.0007) | -0.0001 (-0.0003 to +0.0000) |
| blend prod + sim / discounted | SP calibrated / discounted  | exacta   |   27451 | -0.0015 (-0.0026 to -0.0003) | -0.0044 (-0.0061 to -0.0026) | +0.0008 (-0.0008 to +0.0023) |
| blend prod + sim / discounted | SP calibrated / discounted  | trifecta |   27441 | -0.0029 (-0.0042 to -0.0016) | -0.0066 (-0.0086 to -0.0046) | +0.0001 (-0.0015 to +0.0017) |
| blend prod + sim / discounted | SP calibrated / discounted  | place    |   27046 | -0.0003 (-0.0005 to -0.0002) | -0.0007 (-0.0010 to -0.0004) | -0.0000 (-0.0002 to +0.0001) |

## Fitted discounts (l2, l3) by test year

|                  | 2024                                   | 2025                                   | 2026                                   |
|:-----------------|:---------------------------------------|:---------------------------------------|:---------------------------------------|
| SP calibrated    | (np.float64(0.754), np.float64(0.594)) | (np.float64(0.781), np.float64(0.64))  | (np.float64(0.782), np.float64(0.632)) |
| blend prod       | (np.float64(0.748), np.float64(0.591)) | (np.float64(0.776), np.float64(0.638)) | (np.float64(0.781), np.float64(0.632)) |
| blend prod + sim | (np.float64(0.748), np.float64(0.591)) | (np.float64(0.777), np.float64(0.638)) | (np.float64(0.78), np.float64(0.632))  |
| blend sim        | (np.float64(0.749), np.float64(0.592)) | (np.float64(0.777), np.float64(0.638)) | (np.float64(0.781), np.float64(0.632)) |
