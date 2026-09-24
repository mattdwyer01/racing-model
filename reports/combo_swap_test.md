# TopRate Combo with the Racing Model's race-day adjustment

- VIC/SA/QLD races 2026-08-22 to 2026-09-23 (TopRate's speed_map term exists from 22 Aug 2026 only).
- Our race-day adjustment out of sample (monthly retrain); both adjustments demeaned within the race.
- Races 790, runners 7608. Within-race sd: TopRate speed map 0.46, ours 1.01 WPR points; correlation 0.33.

## Top pick

| pick                                   | top pick won   | winner in top 3   | ROI at SP   |
|:---------------------------------------|:---------------|:------------------|:------------|
| Combo (as shipped)                     | 29.5%          | 62.9%             | -11.7%      |
| Combo, no speed map                    | 29.7%          | 63.2%             | -10.9%      |
| Combo, our race-day adj                | 29.6%          | 63.0%             | -11.9%      |
| Combo, our adj (replaces SM + barrier) | 29.6%          | 63.0%             | -11.9%      |
| Racing Model                           | 28.0%          | 59.4%             | -15.9%      |
| SP favourite                           | 32.7%          | 68.4%             | -16.2%      |

## Log loss (lower is better)

|                                             |   log loss |
|:--------------------------------------------|-----------:|
| Combo (as shipped)                          |     1.9001 |
| Combo, no speed map                         |     1.9011 |
| Combo, our race-day adj                     |     1.9006 |
| Combo, our adj (replaces SM + barrier)      |     1.9006 |
| Combo no SM + k x our adj (fitted)          |     1.9006 |
| Racing Model                                |     1.9376 |
| SP (calibrated)                             |     1.7924 |
| Combo (as shipped) + SP                     |     1.7934 |
| Combo, our race-day adj + SP                |     1.7931 |
| Combo, our adj (replaces SM + barrier) + SP |     1.7931 |
| Racing Model + SP                           |     1.7949 |

## Paired differences (negative = first is better; 95% race bootstrap)

| first                                       | minus                   | diff                         |
|:--------------------------------------------|:------------------------|:-----------------------------|
| Combo, our race-day adj                     | Combo (as shipped)      | +0.0005 (-0.0039 to +0.0045) |
| Combo, our adj (replaces SM + barrier)      | Combo (as shipped)      | +0.0005 (-0.0036 to +0.0046) |
| Combo, no speed map                         | Combo (as shipped)      | +0.0011 (-0.0010 to +0.0030) |
| Combo no SM + k x our adj (fitted)          | Combo (as shipped)      | +0.0005 (-0.0024 to +0.0034) |
| Combo, our race-day adj + SP                | Combo (as shipped) + SP | -0.0003 (-0.0009 to +0.0003) |
| Combo, our adj (replaces SM + barrier) + SP | Combo (as shipped) + SP | -0.0003 (-0.0009 to +0.0003) |
| Combo, our race-day adj + SP                | SP (calibrated)         | +0.0007 (-0.0028 to +0.0045) |
| Racing Model + SP                           | SP (calibrated)         | +0.0025 (-0.0044 to +0.0094) |

