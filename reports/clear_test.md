# Points clear of the next horse

- 70,291 races (4+ runners, SP for all, one winner), 2023 to Sep 2026, every state; production model retrained at the start of each year, out of sample. Gap = top-rated runner's rating minus the second's (WPR points).
- A/E = winners / expected winners at SP (normalised 1 / SP); it is above 1 for any short-priced group (favourite-longshot bias). A/E price-matched = winners / win rate of ALL runners at the same SP (12 bands): what the model adds beyond the price. ROI = flat 1 unit at SP. avg SP is the median.

## All races by gap

| band   |   races |   won % |   avg SP |   SP fav % |   A/E |   A/E price-matched | A/E pm 95%   |   ROI % | ROI 95%    |
|:-------|--------:|--------:|---------:|-----------:|------:|--------------------:|:-------------|--------:|:-----------|
| 0-1    |  19,734 |    22.8 |     4    |         39 |  1.06 |               1.026 | 1.00 to 1.05 |   -14.5 | -17 to -12 |
| 1-2    |  15,179 |    26.1 |     3.6  |         49 |  1.09 |               1.048 | 1.02 to 1.08 |   -12.2 | -15 to -9  |
| 2-3    |  11,075 |    28.4 |     3.2  |         57 |  1.07 |               1.022 | 0.99 to 1.05 |   -14.8 | -18 to -12 |
| 3-4    |   7,885 |    31.1 |     2.9  |         65 |  1.06 |               1.013 | 0.98 to 1.05 |   -13   | -16 to -10 |
| 4-6    |   9,205 |    36.5 |     2.5  |         75 |  1.1  |               1.042 | 1.02 to 1.07 |   -10   | -13 to -7  |
| 6-8    |   4,199 |    44.3 |     2.15 |         84 |  1.15 |               1.087 | 1.05 to 1.12 |    -5.5 | -9 to -2   |
| 8+     |   3,014 |    52.9 |     1.75 |         90 |  1.14 |               1.08  | 1.04 to 1.11 |    -6.5 | -10 to -2  |

## Top pick is NOT the SP favourite

| band   |   races |   won % |   avg SP |   SP fav % |   A/E |   A/E price-matched | A/E pm 95%   |   ROI % | ROI 95%    |
|:-------|--------:|--------:|---------:|-----------:|------:|--------------------:|:-------------|--------:|:-----------|
| 0-1    |  11,983 |    16.5 |      5   |          0 |  1.03 |               1.029 | 0.99 to 1.07 |   -16.5 | -20 to -13 |
| 1-2    |   7,769 |    17.5 |      4.8 |          0 |  1.03 |               1.014 | 0.97 to 1.06 |   -16.3 | -21 to -12 |
| 2-3    |   4,765 |    18   |      4.6 |          0 |  1    |               0.981 | 0.93 to 1.04 |   -20   | -25 to -14 |
| 3-4    |   2,740 |    20.4 |      4.4 |          0 |  1.08 |               1.055 | 0.98 to 1.13 |   -11.3 | -18 to -4  |
| 4-6    |   2,305 |    21.8 |      4   |          0 |  1.11 |               1.064 | 0.99 to 1.15 |   -12   | -19 to -4  |
| 6-8    |     672 |    26.2 |      3.8 |          0 |  1.27 |               1.202 | 1.05 to 1.35 |     1.8 | -13 to +16 |
| 8+     |     287 |    25.4 |      3.8 |          0 |  1.23 |               1.132 | 0.91 to 1.35 |     1.3 | -23 to +30 |

## Top pick IS the SP favourite

| band   |   races |   won % |   avg SP |   SP fav % |   A/E |   A/E price-matched | A/E pm 95%   |   ROI % | ROI 95%    |
|:-------|--------:|--------:|---------:|-----------:|------:|--------------------:|:-------------|--------:|:-----------|
| 0-1    |   7,751 |    32.5 |     2.8  |        100 |  1.08 |               1.024 | 0.99 to 1.05 |   -11.5 | -14 to -9  |
| 1-2    |   7,410 |    35.1 |     2.7  |        100 |  1.12 |               1.066 | 1.03 to 1.10 |    -7.8 | -11 to -5  |
| 2-3    |   6,310 |    36.2 |     2.6  |        100 |  1.09 |               1.038 | 1.00 to 1.07 |   -10.8 | -14 to -8  |
| 3-4    |   5,145 |    36.8 |     2.45 |        100 |  1.06 |               1.001 | 0.97 to 1.04 |   -14   | -17 to -11 |
| 4-6    |   6,900 |    41.3 |     2.25 |        100 |  1.1  |               1.039 | 1.01 to 1.07 |    -9.3 | -12 to -7  |
| 6-8    |   3,527 |    47.7 |     2    |        100 |  1.14 |               1.076 | 1.04 to 1.11 |    -6.9 | -10 to -3  |
| 8+     |   2,727 |    55.7 |     1.65 |        100 |  1.14 |               1.078 | 1.04 to 1.11 |    -7.3 | -11 to -4  |

## By state group (gap 4+ vs under 4)

|                        |   races |   won % |   avg SP |   SP fav % |   A/E |   A/E price-matched | A/E pm 95%   |   ROI % | ROI 95%    |
|:-----------------------|--------:|--------:|---------:|-----------:|------:|--------------------:|:-------------|--------:|:-----------|
| ('NSW/WA/other', '4+') |   7,663 |    41.7 |     2.25 |         81 |  1.11 |               1.062 | 1.03 to 1.09 |    -9.2 | -12 to -7  |
| ('NSW/WA/other', '<4') |  24,618 |    26.4 |     3.6  |         50 |  1.06 |               1.032 | 1.01 to 1.05 |   -14.5 | -17 to -12 |
| ('QLD', '4+')          |   4,431 |    42.1 |     2.25 |         79 |  1.17 |               1.063 | 1.03 to 1.10 |    -7   | -11 to -3  |
| ('QLD', '<4')          |  12,638 |    26.8 |     3.4  |         49 |  1.09 |               1.011 | 0.98 to 1.04 |   -12.7 | -16 to -10 |
| ('SA', '4+')           |     935 |    39   |     2.4  |         82 |  1.1  |               1.056 | 0.98 to 1.13 |    -8.5 | -16 to -0  |
| ('SA', '<4')           |   4,287 |    24   |     3.8  |         49 |  1.05 |               1.029 | 0.98 to 1.08 |   -13.8 | -19 to -8  |
| ('VIC', '4+')          |   3,389 |    40.8 |     2.35 |         80 |  1.11 |               1.067 | 1.02 to 1.11 |    -7.2 | -12 to -3  |
| ('VIC', '<4')          |  12,330 |    25.4 |     3.7  |         48 |  1.06 |               1.041 | 1.01 to 1.07 |   -13   | -16 to -10 |

## By year (gap 4+)

|   year |   races |   won % |   avg SP |   SP fav % |   A/E |   A/E price-matched | A/E pm 95%   |   ROI % | ROI 95%   |
|-------:|--------:|--------:|---------:|-----------:|------:|--------------------:|:-------------|--------:|:----------|
|   2023 |   4,552 |    40.9 |     2.3  |         80 |  1.13 |               1.073 | 1.04 to 1.11 |    -6   | -10 to -2 |
|   2024 |   4,450 |    41.3 |     2.25 |         80 |  1.12 |               1.056 | 1.02 to 1.09 |    -8.9 | -13 to -5 |
|   2025 |   4,352 |    42.2 |     2.25 |         81 |  1.13 |               1.069 | 1.03 to 1.10 |    -8.7 | -12 to -5 |
|   2026 |   3,064 |    41.4 |     2.25 |         80 |  1.12 |               1.05  | 1.01 to 1.09 |    -9.7 | -14 to -5 |
## Reading

- Every band loses at SP (ROI -5% to -20%): no gap on its own beats the takeout.
- Price-matched, the top pick wins 1% to 5% more often than its price says when the gap is under 6 WPR, and about 8% more at 6+ (95% range about 1.04 to 1.12). The edge grows with the gap but stays below the takeout.
- Top pick NOT the SP favourite and 6-8 clear: 672 races, price-matched A/E 1.20 (1.05 to 1.35), ROI +1.8% (-13 to +16); 8+ clear 287 races, ROI +1.3%. The only bands near break-even: small samples, at SP, worth tracking at bet-time fixed prices.
- 4+ clear is similar in every state group (price-matched A/E 1.06).

