# Racing Model + TopRate rating + form factor

- 2,786 VIC/SA/QLD races, 26 Apr to 23 Sep 2026; Racing Model out of sample (monthly retrain). Fitted blends: conditional logit, half-window swap.

## Log loss and top pick

| model                                                       |   log loss | top pick won   | ROI top pick at SP   |
|:------------------------------------------------------------|-----------:|:---------------|:---------------------|
| Racing Model                                                |     1.9515 | 27.5%          | -15.6%               |
| TopRate Combo                                               |     1.9308 | 29.5%          | -11.2%               |
| TopRate rating                                              |     1.8824 | 29.0%          | -16.7%               |
| form factor                                                 |     2.2378 | 8.0%           | -32.2%               |
| TopRate rating + form factor                                |     1.8824 | 29.0%          | -16.4%               |
| RM + TopRate rating + form factor, fixed Combo weights      |     1.9102 | 29.8%          | -11.4%               |
| RM + TopRate rating + form factor, fitted                   |     1.8664 | 30.9%          | -12.0%               |
| RM + TopRate rating, fitted                                 |     1.8658 | 30.9%          | -12.5%               |
| RM + form factor, fitted                                    |     1.9553 | 27.5%          | -15.6%               |
| SP (calibrated)                                             |     1.8346 | 32.6%          | -12.5%               |
| Racing Model + SP                                           |     1.8315 | 32.6%          | -11.8%               |
| TopRate Combo + SP                                          |     1.8333 | 32.3%          | -12.8%               |
| RM + TopRate rating + form factor, fixed Combo weights + SP |     1.8337 | 32.1%          | -13.0%               |
| RM + TopRate rating + form factor, fitted + SP              |     1.8322 | 32.5%          | -11.8%               |
| TopRate rating + form factor + SP                           |     1.8346 | 32.6%          | -12.5%               |

## Paired differences (negative = first is better; 95% race bootstrap)

| first                                                  | minus             | all                          | QLD                          | VIC/SA                       |
|:-------------------------------------------------------|:------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| RM + TopRate rating + form factor, fitted              | Racing Model      | -0.0851 (-0.0999 to -0.0702) | -0.0609 (-0.0823 to -0.0391) | -0.1102 (-0.1317 to -0.0892) |
| RM + TopRate rating + form factor, fitted              | TopRate Combo     | -0.0645 (-0.0795 to -0.0489) | -0.0569 (-0.0802 to -0.0343) | -0.0723 (-0.0915 to -0.0522) |
| RM + TopRate rating + form factor, fixed Combo weights | TopRate Combo     | -0.0206 (-0.0307 to -0.0105) | -0.0258 (-0.0416 to -0.0106) | -0.0153 (-0.0288 to -0.0017) |
| RM + TopRate rating, fitted                            | Racing Model      | -0.0857 (-0.1012 to -0.0709) | -0.0610 (-0.0817 to -0.0394) | -0.1112 (-0.1324 to -0.0897) |
| RM + form factor, fitted                               | Racing Model      | +0.0038 (+0.0002 to +0.0072) | +0.0017 (-0.0036 to +0.0071) | +0.0060 (+0.0012 to +0.0104) |
| RM + TopRate rating + form factor, fitted + SP         | Racing Model + SP | +0.0007 (-0.0003 to +0.0018) | +0.0007 (-0.0011 to +0.0024) | +0.0008 (-0.0003 to +0.0019) |
| RM + TopRate rating + form factor, fitted + SP         | SP (calibrated)   | -0.0024 (-0.0056 to +0.0009) | -0.0034 (-0.0082 to +0.0015) | -0.0013 (-0.0059 to +0.0032) |
| Racing Model + SP                                      | SP (calibrated)   | -0.0031 (-0.0060 to -0.0002) | -0.0041 (-0.0082 to +0.0000) | -0.0021 (-0.0061 to +0.0021) |
| TopRate Combo + SP                                     | SP (calibrated)   | -0.0013 (-0.0041 to +0.0015) | -0.0011 (-0.0052 to +0.0030) | -0.0016 (-0.0059 to +0.0025) |
| TopRate rating + form factor + SP                      | SP (calibrated)   | -0.0000 (-0.0008 to +0.0008) | -0.0003 (-0.0013 to +0.0007) | +0.0003 (-0.0006 to +0.0013) |

