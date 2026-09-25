# Racing Model + TopRate rating + form factor (pre-race TopRate values)

- 2,786 VIC/SA/QLD races, 26 Apr to 23 Sep 2026; Racing Model out of sample (monthly retrain). Fitted blends: conditional logit, half-window swap.

## Log loss and top pick

| model                                                       |   log loss | top pick won   | ROI top pick at SP   |
|:------------------------------------------------------------|-----------:|:---------------|:---------------------|
| Racing Model                                                |     1.9515 | 27.5%          | -15.6%               |
| TopRate Combo                                               |     1.9798 | 27.2%          | -13.3%               |
| TopRate rating                                              |     2.0909 | 17.0%          | -27.1%               |
| form factor                                                 |     2.2378 | 8.0%           | -32.2%               |
| TopRate rating + form factor                                |     2.0904 | 17.1%          | -26.7%               |
| RM + TopRate rating + form factor, fixed Combo weights      |     1.9388 | 28.2%          | -14.1%               |
| RM + TopRate rating + form factor, fitted                   |     1.9435 | 28.2%          | -14.4%               |
| RM + TopRate rating, fitted                                 |     1.9431 | 28.2%          | -14.5%               |
| RM + form factor, fitted                                    |     1.9516 | 27.5%          | -15.6%               |
| SP (calibrated)                                             |     1.8346 | 32.6%          | -12.5%               |
| Racing Model + SP                                           |     1.8315 | 32.6%          | -11.8%               |
| TopRate Combo + SP                                          |     1.8329 | 32.7%          | -11.7%               |
| RM + TopRate rating + form factor, fixed Combo weights + SP |     1.8326 | 32.4%          | -12.5%               |
| RM + TopRate rating + form factor, fitted + SP              |     1.8332 | 32.4%          | -12.2%               |
| TopRate rating + form factor + SP                           |     1.8359 | 32.8%          | -11.4%               |

## Paired differences (negative = first is better; 95% race bootstrap)

| first                                                  | minus             | all                          | QLD                          | VIC/SA                       |
|:-------------------------------------------------------|:------------------|:-----------------------------|:-----------------------------|:-----------------------------|
| RM + TopRate rating + form factor, fitted              | Racing Model      | -0.0080 (-0.0144 to -0.0015) | -0.0067 (-0.0152 to +0.0020) | -0.0093 (-0.0192 to +0.0005) |
| RM + TopRate rating + form factor, fitted              | TopRate Combo     | -0.0362 (-0.0530 to -0.0197) | -0.0454 (-0.0688 to -0.0229) | -0.0267 (-0.0504 to -0.0036) |
| RM + TopRate rating + form factor, fixed Combo weights | TopRate Combo     | -0.0409 (-0.0552 to -0.0263) | -0.0401 (-0.0612 to -0.0194) | -0.0419 (-0.0627 to -0.0210) |
| RM + TopRate rating, fitted                            | Racing Model      | -0.0084 (-0.0146 to -0.0021) | -0.0072 (-0.0154 to +0.0014) | -0.0096 (-0.0184 to -0.0005) |
| RM + form factor, fitted                               | Racing Model      | +0.0001 (-0.0009 to +0.0011) | -0.0006 (-0.0021 to +0.0010) | +0.0008 (-0.0006 to +0.0021) |
| RM + TopRate rating + form factor, fitted + SP         | Racing Model + SP | +0.0017 (-0.0005 to +0.0039) | -0.0006 (-0.0033 to +0.0020) | +0.0041 (+0.0008 to +0.0072) |
| RM + TopRate rating + form factor, fitted + SP         | SP (calibrated)   | -0.0014 (-0.0052 to +0.0025) | -0.0046 (-0.0100 to +0.0005) | +0.0020 (-0.0033 to +0.0070) |
| Racing Model + SP                                      | SP (calibrated)   | -0.0031 (-0.0060 to -0.0002) | -0.0041 (-0.0082 to +0.0000) | -0.0021 (-0.0061 to +0.0021) |
| TopRate Combo + SP                                     | SP (calibrated)   | -0.0017 (-0.0039 to +0.0005) | -0.0017 (-0.0049 to +0.0015) | -0.0017 (-0.0051 to +0.0015) |
| TopRate rating + form factor + SP                      | SP (calibrated)   | +0.0013 (-0.0004 to +0.0031) | -0.0008 (-0.0031 to +0.0015) | +0.0035 (+0.0006 to +0.0062) |

