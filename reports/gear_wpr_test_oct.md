# Gear changes and TopRate wpr_nett on top of the production model

- Window 2026-04-26 to 2026-10-02 (runners file only); production trained before 2026-04-26, scores every race out of sample. States: NSW, QLD, SA, VIC, WA
- Offset logits (log p_production + inputs) fitted on one half of the window, tested on the other, swapped
- wpr_nett: whole window, races 6422, runners 61409
- Gear: gear_changes is only filled from 01 Sep 2026, so gear is tested on that sub-window only (same half swap): races 1430, runners 13415. Gear counts: {'g_blink_ft': 424, 'g_blink_off': 429, 'g_winkers_ft': 218, 'g_tongue_ft': 348, 'g_earmuff_ft': 512, 'g_gelded': 50, 'g_other_ft': 1401, 'g_n': 4460}

## wpr_nett, whole window: mean race log loss

|                  |   log loss |
|:-----------------|-----------:|
| production       |     1.9220 |
| + wpr_nett       |     1.9146 |
| wpr_nett alone   |     2.0147 |
| SP alone         |     1.7844 |
| production blend |     1.7834 |
| + wpr_nett blend |     1.7835 |

## wpr_nett, whole window: paired differences (negative = first is better; 95% race bootstrap)

| first            | minus            | states   |   races | diff                         |
|:-----------------|:-----------------|:---------|--------:|:-----------------------------|
| + wpr_nett       | production       | all      |    6422 | -0.0074 (-0.0106 to -0.0043) |
| + wpr_nett       | production       | QLD      |    1850 | -0.0068 (-0.0129 to -0.0007) |
| + wpr_nett       | production       | VIC/SA   |    1878 | -0.0087 (-0.0142 to -0.0030) |
| + wpr_nett       | production       | NSW      |    1934 | -0.0072 (-0.0126 to -0.0016) |
| + wpr_nett       | production       | WA       |     760 | -0.0063 (-0.0151 to +0.0023) |
| + wpr_nett blend | production blend | all      |    6422 | +0.0001 (-0.0002 to +0.0004) |
| + wpr_nett blend | production blend | QLD      |    1850 | +0.0001 (-0.0004 to +0.0005) |
| + wpr_nett blend | production blend | VIC/SA   |    1878 | +0.0002 (-0.0004 to +0.0008) |
| + wpr_nett blend | production blend | NSW      |    1934 | +0.0000 (-0.0005 to +0.0006) |
| + wpr_nett blend | production blend | WA       |     760 | -0.0001 (-0.0009 to +0.0007) |
| production blend | SP alone         | all      |    6422 | -0.0010 (-0.0021 to +0.0001) |
| production blend | SP alone         | QLD      |    1850 | -0.0034 (-0.0057 to -0.0013) |
| production blend | SP alone         | VIC/SA   |    1878 | -0.0006 (-0.0028 to +0.0016) |
| production blend | SP alone         | NSW      |    1934 | +0.0002 (-0.0016 to +0.0021) |
| production blend | SP alone         | WA       |     760 | +0.0009 (-0.0022 to +0.0042) |
| wpr_nett alone   | SP alone         | all      |    6422 | +0.2302 (+0.2146 to +0.2470) |
| wpr_nett alone   | SP alone         | QLD      |    1850 | +0.1951 (+0.1675 to +0.2221) |
| wpr_nett alone   | SP alone         | VIC/SA   |    1878 | +0.2304 (+0.2007 to +0.2594) |
| wpr_nett alone   | SP alone         | NSW      |    1934 | +0.2564 (+0.2251 to +0.2878) |
| wpr_nett alone   | SP alone         | WA       |     760 | +0.2484 (+0.2009 to +0.2971) |
| wpr_nett alone   | production       | all      |    6422 | +0.0927 (+0.0790 to +0.1058) |
| wpr_nett alone   | production       | QLD      |    1850 | +0.0841 (+0.0591 to +0.1092) |
| wpr_nett alone   | production       | VIC/SA   |    1878 | +0.0806 (+0.0572 to +0.1041) |
| wpr_nett alone   | production       | NSW      |    1934 | +0.1048 (+0.0798 to +0.1286) |
| wpr_nett alone   | production       | WA       |     760 | +0.1125 (+0.0735 to +0.1531) |

Leakage check: 'wpr_nett alone - SP alone' well above 0 is expected for a pre-race rating; near or below 0 suggests wpr_nett includes the race's own result.

## Gear (and wpr_nett again), 01 Sep to 2026-10-02: mean race log loss

|                  |   log loss |
|:-----------------|-----------:|
| production       |     1.8839 |
| + gear           |     1.8986 |
| + wpr_nett       |     1.8764 |
| + both           |     1.8923 |
| wpr_nett alone   |     1.9925 |
| SP alone         |     1.7382 |
| production blend |     1.7411 |
| + gear blend     |     1.7558 |
| + wpr_nett blend |     1.7414 |
| + both blend     |     1.7566 |

## Gear sub-window: paired differences

| first            | minus            |   races | diff                         |
|:-----------------|:-----------------|--------:|:-----------------------------|
| + gear           | production       |    1430 | +0.0147 (+0.0068 to +0.0246) |
| + wpr_nett       | production       |    1430 | -0.0074 (-0.0135 to -0.0012) |
| + both           | production       |    1430 | +0.0084 (-0.0020 to +0.0195) |
| + both           | + wpr_nett       |    1430 | +0.0159 (+0.0077 to +0.0251) |
| + gear blend     | production blend |    1430 | +0.0147 (+0.0065 to +0.0241) |
| + wpr_nett blend | production blend |    1430 | +0.0003 (-0.0007 to +0.0013) |
| + both blend     | production blend |    1430 | +0.0154 (+0.0071 to +0.0249) |
| wpr_nett alone   | SP alone         |    1430 | +0.2544 (+0.2135 to +0.2901) |

## Fitted weights, whole window (half 1 fit, half 2 fit)

|                  | 0                                                            | 1                                                            |
|:-----------------|:-------------------------------------------------------------|:-------------------------------------------------------------|
| + wpr_nett       | lp_model +0.829, wn_rel +0.048, wn_miss +0.061               | lp_model +0.839, wn_rel +0.050, wn_miss +0.195               |
| + wpr_nett blend | lp_model +0.086, wn_rel -0.001, wn_miss -0.083, lp_sp +1.073 | lp_model +0.096, wn_rel +0.004, wn_miss +0.009, lp_sp +1.060 |
| SP alone         | lp_sp +1.135                                                 | lp_sp +1.141                                                 |
| production       | lp_model +0.992                                              | lp_model +1.002                                              |
| production blend | lp_model +0.086, lp_sp +1.071                                | lp_model +0.107, lp_sp +1.065                                |
| wpr_nett alone   | wn_rel +0.167, wn_miss +0.130                                | wn_rel +0.169, wn_miss +0.350                                |

## Fitted weights, gear sub-window (half 1 fit, half 2 fit)

|                  | 0                                                                                                                                                                                                                 | 1                                                                                                                                                                                                                 |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| + both           | lp_model +0.848, wn_rel +0.046, wn_miss +0.431, g_blink_ft -0.578, g_blink_off -0.003, g_winkers_ft -0.588, g_tongue_ft +0.208, g_earmuff_ft -0.268, g_gelded +1.041, g_other_ft -0.316, g_n +0.137               | lp_model +0.955, wn_rel +0.051, wn_miss +0.158, g_blink_ft -0.230, g_blink_off -0.177, g_winkers_ft +0.187, g_tongue_ft +0.008, g_earmuff_ft +0.234, g_gelded -2.302, g_other_ft +0.106, g_n -0.058               |
| + both blend     | lp_model +0.029, wn_rel -0.001, wn_miss +0.074, g_blink_ft -0.490, g_blink_off -0.039, g_winkers_ft -0.474, g_tongue_ft +0.236, g_earmuff_ft -0.381, g_gelded +0.685, g_other_ft -0.275, g_n +0.110, lp_sp +1.130 | lp_model +0.252, wn_rel +0.011, wn_miss -0.068, g_blink_ft -0.208, g_blink_off -0.188, g_winkers_ft +0.266, g_tongue_ft -0.067, g_earmuff_ft +0.196, g_gelded -2.525, g_other_ft +0.054, g_n -0.040, lp_sp +0.955 |
| + gear           | lp_model +0.990, g_blink_ft -0.580, g_blink_off -0.009, g_winkers_ft -0.531, g_tongue_ft +0.246, g_earmuff_ft -0.194, g_gelded +0.982, g_other_ft -0.273, g_n +0.114                                              | lp_model +1.118, g_blink_ft -0.258, g_blink_off -0.169, g_winkers_ft +0.180, g_tongue_ft -0.025, g_earmuff_ft +0.191, g_gelded -2.363, g_other_ft +0.094, g_n -0.061                                              |
| + gear blend     | lp_model +0.024, g_blink_ft -0.476, g_blink_off -0.037, g_winkers_ft -0.461, g_tongue_ft +0.247, g_earmuff_ft -0.356, g_gelded +0.680, g_other_ft -0.266, g_n +0.105, lp_sp +1.131                                | lp_model +0.281, g_blink_ft -0.220, g_blink_off -0.189, g_winkers_ft +0.251, g_tongue_ft -0.097, g_earmuff_ft +0.154, g_gelded -2.509, g_other_ft +0.041, g_n -0.035, lp_sp +0.963                                |
| + wpr_nett       | lp_model +0.843, wn_rel +0.046, wn_miss +0.315                                                                                                                                                                    | lp_model +0.951, wn_rel +0.052, wn_miss +0.238                                                                                                                                                                    |
| + wpr_nett blend | lp_model +0.020, wn_rel -0.001, wn_miss -0.050, lp_sp +1.136                                                                                                                                                      | lp_model +0.248, wn_rel +0.012, wn_miss -0.004, lp_sp +0.954                                                                                                                                                      |
| SP alone         | lp_sp +1.147                                                                                                                                                                                                      | lp_sp +1.154                                                                                                                                                                                                      |
| production       | lp_model +0.985                                                                                                                                                                                                   | lp_model +1.115                                                                                                                                                                                                   |
| production blend | lp_model +0.020, lp_sp +1.133                                                                                                                                                                                     | lp_model +0.278, lp_sp +0.964                                                                                                                                                                                     |
| wpr_nett alone   | wn_rel +0.165, wn_miss +0.434                                                                                                                                                                                     | wn_rel +0.184, wn_miss +0.479                                                                                                                                                                                     |
