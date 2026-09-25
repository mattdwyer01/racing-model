# Combo redesign on pre-race TopRate values

- 695 VIC/SA/QLD races 2026-08-22 to 2026-09-23; TopRate inputs as they stood before each race; our race-day adjustment out of sample. Within-race sd: TopRate speed map 0.26, ours 1.02 WPR.

## Log loss and top pick

| model                                |   log loss | top pick won   | ROI top pick at SP   |
|:-------------------------------------|-----------:|:---------------|:---------------------|
| A Combo as shipped (pre-race)        |     1.9439 | 29.2%          | -10.3%               |
| B Combo, our race-day adj            |     1.9445 | 28.9%          | -12.7%               |
| C B without TopRate rating           |     1.9905 | 28.1%          | -12.7%               |
| D B without form factor              |     1.9250 | 29.9%          | -13.1%               |
| E our adjusted projection alone      |     2.0129 | 26.8%          | -19.6%               |
| G B + past ground loss (GPS)         |     1.9447 | 28.9%          | -12.7%               |
| H G + position value                 |     1.9451 | 28.6%          | -13.8%               |
| F fitted weights                     |     1.8872 | 29.9%          | -16.4%               |
| I fitted weights + GPS               |     1.8927 | 30.1%          | -15.8%               |
| SP (calibrated)                      |     1.8039 | 31.9%          | -18.3%               |
| A Combo as shipped (pre-race) + SP   |     1.8131 | 32.2%          | -16.6%               |
| B Combo, our race-day adj + SP       |     1.8135 | 32.1%          | -17.2%               |
| C B without TopRate rating + SP      |     1.8149 | 31.9%          | -17.6%               |
| D B without form factor + SP         |     1.8157 | 32.1%          | -17.3%               |
| E our adjusted projection alone + SP |     1.8171 | 32.2%          | -16.7%               |
| G B + past ground loss (GPS) + SP    |     1.8138 | 31.9%          | -17.7%               |
| H G + position value + SP            |     1.8138 | 31.9%          | -17.9%               |
| F fitted weights + SP                |     1.8126 | 32.4%          | -16.9%               |
| I fitted weights + GPS + SP          |     1.8192 | 31.4%          | -19.5%               |

## Paired differences vs A (negative = better; 95% race bootstrap)

| first                                | minus                              | diff                         |
|:-------------------------------------|:-----------------------------------|:-----------------------------|
| B Combo, our race-day adj            | A Combo as shipped (pre-race)      | +0.0006 (-0.0039 to +0.0050) |
| C B without TopRate rating           | A Combo as shipped (pre-race)      | +0.0465 (+0.0370 to +0.0564) |
| D B without form factor              | A Combo as shipped (pre-race)      | -0.0190 (-0.0357 to -0.0030) |
| E our adjusted projection alone      | A Combo as shipped (pre-race)      | +0.0690 (+0.0463 to +0.0925) |
| G B + past ground loss (GPS)         | A Combo as shipped (pre-race)      | +0.0007 (-0.0040 to +0.0053) |
| H G + position value                 | A Combo as shipped (pre-race)      | +0.0011 (-0.0047 to +0.0070) |
| F fitted weights                     | A Combo as shipped (pre-race)      | -0.0567 (-0.0829 to -0.0291) |
| I fitted weights + GPS               | A Combo as shipped (pre-race)      | -0.0513 (-0.0769 to -0.0245) |
| B Combo, our race-day adj + SP       | A Combo as shipped (pre-race) + SP | +0.0003 (-0.0005 to +0.0012) |
| C B without TopRate rating + SP      | A Combo as shipped (pre-race) + SP | +0.0018 (+0.0003 to +0.0033) |
| D B without form factor + SP         | A Combo as shipped (pre-race) + SP | +0.0026 (-0.0013 to +0.0064) |
| E our adjusted projection alone + SP | A Combo as shipped (pre-race) + SP | +0.0039 (-0.0008 to +0.0084) |
| G B + past ground loss (GPS) + SP    | A Combo as shipped (pre-race) + SP | +0.0007 (-0.0003 to +0.0016) |
| H G + position value + SP            | A Combo as shipped (pre-race) + SP | +0.0007 (-0.0005 to +0.0018) |
| F fitted weights + SP                | A Combo as shipped (pre-race) + SP | -0.0005 (-0.0072 to +0.0064) |
| I fitted weights + GPS + SP          | A Combo as shipped (pre-race) + SP | +0.0061 (-0.0022 to +0.0145) |
| G B + past ground loss (GPS)         | B Combo, our race-day adj          | +0.0001 (-0.0005 to +0.0008) |
| H G + position value                 | G B + past ground loss (GPS)       | +0.0004 (-0.0016 to +0.0023) |
| A Combo as shipped (pre-race) + SP   | SP (calibrated)                    | +0.0092 (+0.0031 to +0.0155) |

Fitted weights (I, all races; per unit): proj_base +0.043, ours +0.015, trr_pre_f +0.399, trr_pre_m +0.000, pfm_pre_f -0.002, pfm_pre_m -0.288, glp -0.007, pv +0.046

