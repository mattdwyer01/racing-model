# Gear changes and TopRate wpr_nett on top of the production model

- Window 2026-04-26 to 2026-09-23 (runners file only); production trained before 2026-04-26, scores every race out of sample. States: NSW, QLD, SA, VIC, WA
- Offset logits (log p_production + inputs) fitted on one half of the window, tested on the other, swapped
- wpr_nett: whole window, races 5984, runners 57380
- Gear: gear_changes is only filled from 01 Sep 2026, so gear is tested on that sub-window only (same half swap): races 992, runners 9386. Gear counts: {'g_blink_ft': 290, 'g_blink_off': 291, 'g_winkers_ft': 157, 'g_tongue_ft': 249, 'g_earmuff_ft': 353, 'g_gelded': 38, 'g_other_ft': 953, 'g_n': 3069}

## wpr_nett, whole window: mean race log loss

|                  |   log loss |
|:-----------------|-----------:|
| production       |     1.9312 |
| + wpr_nett       |     1.9239 |
| wpr_nett alone   |     2.0207 |
| SP alone         |     1.7939 |
| production blend |     1.7931 |
| + wpr_nett blend |     1.7931 |

## wpr_nett, whole window: paired differences (negative = first is better; 95% race bootstrap)

| first            | minus            | states   |   races | diff                         |
|:-----------------|:-----------------|:---------|--------:|:-----------------------------|
| + wpr_nett       | production       | all      |    5984 | -0.0073 (-0.0107 to -0.0042) |
| + wpr_nett       | production       | QLD      |    1730 | -0.0067 (-0.0130 to -0.0003) |
| + wpr_nett       | production       | VIC/SA   |    1759 | -0.0097 (-0.0155 to -0.0041) |
| + wpr_nett       | production       | NSW      |    1780 | -0.0062 (-0.0120 to -0.0002) |
| + wpr_nett       | production       | WA       |     715 | -0.0052 (-0.0143 to +0.0043) |
| + wpr_nett blend | production blend | all      |    5984 | +0.0000 (-0.0003 to +0.0003) |
| + wpr_nett blend | production blend | QLD      |    1730 | +0.0000 (-0.0004 to +0.0005) |
| + wpr_nett blend | production blend | VIC/SA   |    1759 | -0.0001 (-0.0006 to +0.0004) |
| + wpr_nett blend | production blend | NSW      |    1780 | +0.0002 (-0.0004 to +0.0007) |
| + wpr_nett blend | production blend | WA       |     715 | +0.0000 (-0.0007 to +0.0008) |
| production blend | SP alone         | all      |    5984 | -0.0008 (-0.0018 to +0.0003) |
| production blend | SP alone         | QLD      |    1730 | -0.0028 (-0.0047 to -0.0008) |
| production blend | SP alone         | VIC/SA   |    1759 | -0.0008 (-0.0028 to +0.0013) |
| production blend | SP alone         | NSW      |    1780 | +0.0004 (-0.0014 to +0.0023) |
| production blend | SP alone         | WA       |     715 | +0.0013 (-0.0016 to +0.0044) |
| wpr_nett alone   | SP alone         | all      |    5984 | +0.2268 (+0.2089 to +0.2434) |
| wpr_nett alone   | SP alone         | QLD      |    1730 | +0.1926 (+0.1644 to +0.2218) |
| wpr_nett alone   | SP alone         | VIC/SA   |    1759 | +0.2217 (+0.1912 to +0.2515) |
| wpr_nett alone   | SP alone         | NSW      |    1780 | +0.2560 (+0.2236 to +0.2877) |
| wpr_nett alone   | SP alone         | WA       |     715 | +0.2489 (+0.1994 to +0.3011) |
| wpr_nett alone   | production       | all      |    5984 | +0.0895 (+0.0755 to +0.1023) |
| wpr_nett alone   | production       | QLD      |    1730 | +0.0815 (+0.0579 to +0.1060) |
| wpr_nett alone   | production       | VIC/SA   |    1759 | +0.0753 (+0.0507 to +0.0992) |
| wpr_nett alone   | production       | NSW      |    1780 | +0.1027 (+0.0775 to +0.1277) |
| wpr_nett alone   | production       | WA       |     715 | +0.1111 (+0.0713 to +0.1489) |

Leakage check: 'wpr_nett alone - SP alone' well above 0 is expected for a pre-race rating; near or below 0 suggests wpr_nett includes the race's own result.

## Gear (and wpr_nett again), 01 Sep to 2026-09-23: mean race log loss

|                  |   log loss |
|:-----------------|-----------:|
| production       |     1.9120 |
| + gear           |     1.9162 |
| + wpr_nett       |     1.9080 |
| + both           |     1.9121 |
| wpr_nett alone   |     2.0199 |
| SP alone         |     1.7841 |
| production blend |     1.7903 |
| + gear blend     |     1.7957 |
| + wpr_nett blend |     1.7915 |
| + both blend     |     1.7968 |

## Gear sub-window: paired differences

| first            | minus            |   races | diff                         |
|:-----------------|:-----------------|--------:|:-----------------------------|
| + gear           | production       |     992 | +0.0042 (-0.0034 to +0.0123) |
| + wpr_nett       | production       |     992 | -0.0040 (-0.0112 to +0.0035) |
| + both           | production       |     992 | +0.0002 (-0.0112 to +0.0115) |
| + both           | + wpr_nett       |     992 | +0.0041 (-0.0034 to +0.0117) |
| + gear blend     | production blend |     992 | +0.0053 (-0.0017 to +0.0124) |
| + wpr_nett blend | production blend |     992 | +0.0012 (-0.0008 to +0.0036) |
| + both blend     | production blend |     992 | +0.0065 (-0.0011 to +0.0142) |
| wpr_nett alone   | SP alone         |     992 | +0.2359 (+0.1917 to +0.2809) |

## Fitted weights, whole window (half 1 fit, half 2 fit)

|                  | 0                                                            | 1                                                            |
|:-----------------|:-------------------------------------------------------------|:-------------------------------------------------------------|
| + wpr_nett       | lp_model +0.806, wn_rel +0.051, wn_miss +0.059               | lp_model +0.835, wn_rel +0.046, wn_miss +0.160               |
| + wpr_nett blend | lp_model +0.063, wn_rel +0.002, wn_miss -0.083, lp_sp +1.071 | lp_model +0.103, wn_rel +0.001, wn_miss -0.015, lp_sp +1.058 |
| SP alone         | lp_sp +1.125                                                 | lp_sp +1.135                                                 |
| production       | lp_model +0.980                                              | lp_model +0.988                                              |
| production blend | lp_model +0.070, lp_sp +1.073                                | lp_model +0.105, lp_sp +1.059                                |
| wpr_nett alone   | wn_rel +0.167, wn_miss +0.123                                | wn_rel +0.165, wn_miss +0.303                                |

## Fitted weights, gear sub-window (half 1 fit, half 2 fit)

|                  | 0                                                                                                                                                                                                                 | 1                                                                                                                                                                                                                 |
|:-----------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| + both           | lp_model +0.887, wn_rel +0.050, wn_miss +0.502, g_blink_ft -0.429, g_blink_off -0.032, g_winkers_ft -0.750, g_tongue_ft +0.359, g_earmuff_ft -0.234, g_gelded +1.147, g_other_ft -0.201, g_n +0.161               | lp_model +0.852, wn_rel +0.038, wn_miss +0.043, g_blink_ft -0.752, g_blink_off -0.206, g_winkers_ft -0.218, g_tongue_ft -0.417, g_earmuff_ft -0.031, g_gelded +0.554, g_other_ft -0.319, g_n +0.111               |
| + both blend     | lp_model -0.013, wn_rel -0.002, wn_miss +0.136, g_blink_ft -0.364, g_blink_off -0.150, g_winkers_ft -0.659, g_tongue_ft +0.416, g_earmuff_ft -0.367, g_gelded +0.800, g_other_ft -0.219, g_n +0.152, lp_sp +1.260 | lp_model +0.278, wn_rel +0.001, wn_miss -0.201, g_blink_ft -0.691, g_blink_off -0.125, g_winkers_ft -0.129, g_tongue_ft -0.423, g_earmuff_ft -0.049, g_gelded +0.339, g_other_ft -0.246, g_n +0.085, lp_sp +0.822 |
| + gear           | lp_model +1.035, g_blink_ft -0.421, g_blink_off -0.046, g_winkers_ft -0.667, g_tongue_ft +0.401, g_earmuff_ft -0.132, g_gelded +1.012, g_other_ft -0.149, g_n +0.136                                              | lp_model +0.976, g_blink_ft -0.806, g_blink_off -0.203, g_winkers_ft -0.230, g_tongue_ft -0.434, g_earmuff_ft -0.047, g_gelded +0.510, g_other_ft -0.316, g_n +0.108                                              |
| + gear blend     | lp_model -0.024, g_blink_ft -0.345, g_blink_off -0.149, g_winkers_ft -0.633, g_tongue_ft +0.439, g_earmuff_ft -0.315, g_gelded +0.782, g_other_ft -0.201, g_n +0.142, lp_sp +1.263                                | lp_model +0.284, g_blink_ft -0.715, g_blink_off -0.131, g_winkers_ft -0.155, g_tongue_ft -0.457, g_earmuff_ft -0.094, g_gelded +0.343, g_other_ft -0.262, g_n +0.095, lp_sp +0.820                                |
| + wpr_nett       | lp_model +0.882, wn_rel +0.048, wn_miss +0.429                                                                                                                                                                    | lp_model +0.843, wn_rel +0.040, wn_miss -0.023                                                                                                                                                                    |
| + wpr_nett blend | lp_model -0.024, wn_rel -0.003, wn_miss +0.036, lp_sp +1.264                                                                                                                                                      | lp_model +0.270, wn_rel +0.002, wn_miss -0.268, lp_sp +0.826                                                                                                                                                      |
| SP alone         | lp_sp +1.239                                                                                                                                                                                                      | lp_sp +1.016                                                                                                                                                                                                      |
| production       | lp_model +1.025                                                                                                                                                                                                   | lp_model +0.973                                                                                                                                                                                                   |
| production blend | lp_model -0.035, lp_sp +1.263                                                                                                                                                                                     | lp_model +0.281, lp_sp +0.823                                                                                                                                                                                     |
| wpr_nett alone   | wn_rel +0.170, wn_miss +0.548                                                                                                                                                                                     | wn_rel +0.160, wn_miss +0.175                                                                                                                                                                                     |
