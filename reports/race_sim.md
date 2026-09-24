# Race-shape simulation

- Settle: v4 projection; pace: GPS pace model (terciles of distance-relative GPS pace)
- 400 joint draws per race of settling positions and pace; position value V(position, pace | track, distance, going, rail) in WPR points; win probability exact per draw under the logit's Gumbel noise
- Base logit = production inputs minus the settle / pace projection terms (replaced by the simulation); k = weight on simulated position value, fitted on the blend window
- Walk-forward 2023 to 2026, VIC/SA/QLD; blend weights and k never see the test year

## Log loss by fold

|                  |   2023 |   2024 |   2025 |   2026 |   pooled |
|:-----------------|-------:|-------:|-------:|-------:|---------:|
| SP calibrated    | 1.7920 | 1.7885 | 1.7856 | 1.7757 |   1.7863 |
| model prod       | 1.9278 | 1.9242 | 1.9310 | 1.9268 |   1.9275 |
| blend prod       | 1.7903 | 1.7867 | 1.7846 | 1.7751 |   1.7849 |
| model sim        | 1.9301 | 1.9255 | 1.9308 | 1.9280 |   1.9286 |
| blend sim        | 1.7907 | 1.7870 | 1.7844 | 1.7751 |   1.7851 |
| model base       | 1.9302 | 1.9257 | 1.9307 | 1.9279 |   1.9287 |
| blend base       | 1.7908 | 1.7870 | 1.7845 | 1.7751 |   1.7852 |
| blend prod + sim | 1.7899 | 1.7864 | 1.7856 | 1.7750 |   1.7850 |

## Paired differences (negative = first is better; 95% race bootstrap)

| first            | minus         | all                          | QLD                          | VIC/SA                       |
|:-----------------|:--------------|:-----------------------------|:-----------------------------|:-----------------------------|
| blend sim        | blend prod    | +0.0002 (+0.0000 to +0.0003) | +0.0004 (+0.0001 to +0.0006) | -0.0000 (-0.0002 to +0.0002) |
| blend prod + sim | blend prod    | +0.0001 (-0.0002 to +0.0004) | +0.0000 (-0.0005 to +0.0005) | +0.0001 (-0.0003 to +0.0006) |
| blend prod       | SP calibrated | -0.0013 (-0.0021 to -0.0007) | -0.0034 (-0.0046 to -0.0023) | +0.0003 (-0.0006 to +0.0013) |
| blend sim        | SP calibrated | -0.0012 (-0.0018 to -0.0005) | -0.0030 (-0.0041 to -0.0020) | +0.0003 (-0.0005 to +0.0012) |
| blend prod + sim | SP calibrated | -0.0013 (-0.0021 to -0.0005) | -0.0034 (-0.0047 to -0.0020) | +0.0005 (-0.0006 to +0.0016) |
| model sim        | model base    | -0.0001 (-0.0004 to +0.0003) | -0.0003 (-0.0009 to +0.0002) | +0.0001 (-0.0002 to +0.0006) |
| model sim        | model prod    | +0.0011 (+0.0002 to +0.0020) | +0.0004 (-0.0009 to +0.0017) | +0.0017 (+0.0004 to +0.0029) |

## Simulated leader calibration (test years)

| bin            |    runners |   sim |   actual |
|:---------------|-----------:|------:|---------:|
| (-0.001, 0.05] | 151935.000 | 0.019 |    0.024 |
| (0.05, 0.1]    |  61077.000 | 0.074 |    0.066 |
| (0.1, 0.2]     |  60631.000 | 0.144 |    0.129 |
| (0.2, 0.3]     |  27723.000 | 0.246 |    0.234 |
| (0.3, 0.5]     |  21614.000 | 0.379 |    0.410 |
| (0.5, 1.0]     |   4143.000 | 0.578 |    0.658 |

## Fitted values by fold

|                       | 2023                                                       | 2024                                                      | 2025                                                       | 2026                                                      |
|:----------------------|:-----------------------------------------------------------|:----------------------------------------------------------|:-----------------------------------------------------------|:----------------------------------------------------------|
| k                     | 0.34968262581668846                                        | 0.6284626858819573                                        | 0.4484242627136557                                         | 0.3257450967825207                                        |
| unit                  | 0.11861031369815958                                        | 0.13116451482243094                                       | 0.13317427661562953                                        | 0.13469152448841493                                       |
| pace b                | 1.2316627122029329                                         | 0.08638372862078138                                       | 0.04843058353354757                                        | 0.18236363608524866                                       |
| pace sd               | 5.334948664455504                                          | 4.4525429787701745                                        | 4.397643345543147                                          | 4.585555485307595                                         |
| pace cuts             | (np.float64(-2.3), np.float64(2.29))                       | (np.float64(-2.19), np.float64(2.13))                     | (np.float64(-2.04), np.float64(2.15))                      | (np.float64(-2.03), np.float64(2.15))                     |
| GPS pace holdout corr | 0.3102951724296391                                         | 0.4324537383274333                                        | 0.5199541572153921                                         | 0.5353613835589099                                        |
| blend prod a/b        | (np.float64(0.181), np.float64(1.067))                     | (np.float64(0.135), np.float64(1.016))                    | (np.float64(0.149), np.float64(1.049))                     | (np.float64(0.124), np.float64(1.032))                    |
| blend sim a/b         | (np.float64(0.166), np.float64(1.078))                     | (np.float64(0.121), np.float64(1.026))                    | (np.float64(0.129), np.float64(1.064))                     | (np.float64(0.117), np.float64(1.037))                    |
| 3-way prod/sim/sp     | (np.float64(0.463), np.float64(-0.289), np.float64(1.072)) | (np.float64(0.417), np.float64(-0.288), np.float64(1.02)) | (np.float64(0.677), np.float64(-0.537), np.float64(1.057)) | (np.float64(0.301), np.float64(-0.18), np.float64(1.034)) |
