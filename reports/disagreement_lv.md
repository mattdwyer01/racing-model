# Disagreement test (base model: production with leader value)

- Per factor: runners whose out-of-sample blended probability moves most when the factor is added (d = log p_with - log p_without), 2023 to 2026 test years, VIC/SA/QLD
- A/E SP = wins / SP-implied wins; A/E cal = wins / calibrated-SP wins (removes the favourite-longshot bias)
- ROI at SP: flat 1 unit on every runner in the group; control ROI: all runners at the same SP price bands (reweighted to the group's price mix). Positive ROI minus control = the factor finds value the market misses
- 95% ranges: race bootstrap (2,000)

| factor       | group           | races   |   shift (median d) |   runners |   avg SP |   wins |   A/E SP | A/E SP 95%   |   A/E cal | A/E cal 95%   |   ROI at SP |   control ROI | ROI - control 95%   |
|:-------------|:----------------|:--------|-------------------:|----------:|---------:|-------:|---------:|:-------------|----------:|:--------------|------------:|--------------:|:--------------------|
| leader value | UP top 5%       | all     |              0.008 |     18131 |   32.819 |   1518 |    1.075 | 1.03 to 1.12 |     1.118 | 1.07 to 1.17  |      -0.258 |        -0.318 | +0.002 to +0.125    |
| leader value | UP top 5%       | QLD     |              0.008 |      8075 |   28.632 |    738 |    1.067 | 1.00 to 1.13 |     1.107 | 1.04 to 1.17  |      -0.283 |        -0.302 | -0.067 to +0.120    |
| leader value | UP top 5%       | VIC/SA  |              0.008 |     10056 |   36.182 |    780 |    1.083 | 1.02 to 1.15 |     1.128 | 1.06 to 1.20  |      -0.237 |        -0.331 | +0.021 to +0.176    |
| leader value | UP top 10%      | all     |              0.006 |     36261 |   30.940 |   3194 |    1.052 | 1.02 to 1.08 |     1.082 | 1.05 to 1.11  |      -0.283 |        -0.311 | -0.012 to +0.069    |
| leader value | UP top 10%      | QLD     |              0.006 |     15797 |   26.872 |   1549 |    1.070 | 1.02 to 1.12 |     1.098 | 1.05 to 1.15  |      -0.296 |        -0.296 | -0.058 to +0.062    |
| leader value | UP top 10%      | VIC/SA  |              0.006 |     20464 |   34.080 |   1645 |    1.035 | 0.99 to 1.08 |     1.067 | 1.02 to 1.11  |      -0.273 |        -0.323 | +0.000 to +0.100    |
| leader value | DOWN bottom 10% | all     |             -0.006 |     36261 |   28.686 |   2828 |    0.930 | 0.90 to 0.96 |     0.961 | 0.93 to 0.99  |      -0.347 |        -0.301 | -0.082 to -0.008    |
| leader value | DOWN bottom 10% | QLD     |             -0.006 |     16591 |   25.338 |   1344 |    0.908 | 0.87 to 0.95 |     0.939 | 0.89 to 0.98  |      -0.388 |        -0.289 | -0.150 to -0.045    |
| leader value | DOWN bottom 10% | VIC/SA  |             -0.006 |     19670 |   31.510 |   1484 |    0.950 | 0.91 to 0.99 |     0.982 | 0.94 to 1.02  |      -0.312 |        -0.311 | -0.050 to +0.054    |
| leader value | DOWN bottom 5%  | all     |             -0.008 |     18131 |   30.340 |   1287 |    0.908 | 0.86 to 0.95 |     0.949 | 0.90 to 0.99  |      -0.366 |        -0.308 | -0.110 to +0.000    |
| leader value | DOWN bottom 5%  | QLD     |             -0.008 |      8422 |   26.482 |    613 |    0.865 | 0.80 to 0.93 |     0.903 | 0.84 to 0.97  |      -0.430 |        -0.294 | -0.204 to -0.051    |
| leader value | DOWN bottom 5%  | VIC/SA  |             -0.008 |      9709 |   33.687 |    674 |    0.951 | 0.89 to 1.02 |     0.994 | 0.93 to 1.06  |      -0.311 |        -0.320 | -0.067 to +0.094    |
