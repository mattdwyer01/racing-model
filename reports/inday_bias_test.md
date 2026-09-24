# In-day track bias on top of the production model

- VIC/SA/QLD races 2026-04-26 to 2026-09-11: 3,731 races, 36,053 runners; 2,739 races have an earlier race that day with a result (race order known).
- (a) upper bound: all other races at the meeting, actual 800m positions and WPR residuals (not usable live: later races, and positions arrive the next day).
- (b) in-day: earlier races only, finish margin, pre-race expected position, barrier (usable live).

## Log loss

|                                                                                        |   log loss |
|:---------------------------------------------------------------------------------------|-----------:|
| model                                                                                  |     1.9494 |
| model + SP                                                                             |     1.8136 |
| model + same-day bias, all other races, actual positions + WPR (upper bound)           |     1.9466 |
| model + SP + same-day bias, all other races, actual positions + WPR (upper bound)      |     1.8112 |
| model + in-day bias, earlier races, finish margin + expected positions (live now)      |     1.9492 |
| model + SP + in-day bias, earlier races, finish margin + expected positions (live now) |     1.8140 |
| model + in-day bias, earlier races, actual positions + WPR                             |     1.9492 |
| model + SP + in-day bias, earlier races, actual positions + WPR                        |     1.8139 |
| model + same-day bias, all other races, finish margin + expected positions             |     1.9469 |
| model + SP + same-day bias, all other races, finish margin + expected positions        |     1.8118 |
| model + in-day bias, earlier races, actual positions + finish margin                   |     1.9510 |
| model + SP + in-day bias, earlier races, actual positions + finish margin              |     1.8155 |

## Paired differences (negative = better; 95% race bootstrap)

| first                                                                                  | minus      | diff                         |
|:---------------------------------------------------------------------------------------|:-----------|:-----------------------------|
| model + same-day bias, all other races, actual positions + WPR (upper bound)           | model      | -0.0028 (-0.0054 to -0.0004) |
| model + in-day bias, earlier races, finish margin + expected positions (live now)      | model      | -0.0002 (-0.0016 to +0.0012) |
| model + in-day bias, earlier races, actual positions + WPR                             | model      | -0.0002 (-0.0013 to +0.0010) |
| model + same-day bias, all other races, finish margin + expected positions             | model      | -0.0025 (-0.0048 to -0.0003) |
| model + in-day bias, earlier races, actual positions + finish margin                   | model      | +0.0016 (+0.0000 to +0.0031) |
| model + SP + same-day bias, all other races, actual positions + WPR (upper bound)      | model + SP | -0.0024 (-0.0048 to +0.0001) |
| model + SP + in-day bias, earlier races, finish margin + expected positions (live now) | model + SP | +0.0003 (-0.0009 to +0.0016) |
| model + SP + in-day bias, earlier races, actual positions + WPR                        | model + SP | +0.0002 (-0.0010 to +0.0016) |
| model + SP + same-day bias, all other races, finish margin + expected positions        | model + SP | -0.0019 (-0.0040 to +0.0002) |
| model + SP + in-day bias, earlier races, actual positions + finish margin              | model + SP | +0.0019 (+0.0005 to +0.0033) |

## Race 5 onwards only (1,468 races): in-day versions

| first                                                                                  | minus      | diff                         |
|:---------------------------------------------------------------------------------------|:-----------|:-----------------------------|
| model + in-day bias, earlier races, finish margin + expected positions (live now)      | model      | +0.0005 (-0.0021 to +0.0032) |
| model + in-day bias, earlier races, actual positions + WPR                             | model      | -0.0006 (-0.0028 to +0.0016) |
| model + in-day bias, earlier races, actual positions + finish margin                   | model      | +0.0011 (-0.0019 to +0.0040) |
| model + SP + in-day bias, earlier races, finish margin + expected positions (live now) | model + SP | +0.0010 (-0.0014 to +0.0034) |
| model + SP + in-day bias, earlier races, actual positions + WPR                        | model + SP | -0.0003 (-0.0027 to +0.0021) |
| model + SP + in-day bias, earlier races, actual positions + finish margin              | model + SP | +0.0016 (-0.0012 to +0.0041) |

Reading: the same-day signal comes from LATER races (hindsight): using earlier races only adds nothing, even with perfect information (actual positions + WPR). A live in-day update cannot capture it.

