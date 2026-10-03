# TopRate WPR projection: which adjustments help? (pre-race 08:00 values)

- 1,530 races, 25 Aug to 02 Oct 2026, all states. Log loss per race, 2-fold by date (fit on one half, score the other). Positive difference = the first is worse.

- Projection 1.9785, base (no adjustments) 1.9995: base minus projection +0.0210 (+0.0090 to +0.0324). With SP: projection + SP 1.7501, base + SP 1.7481 (-0.0020 (-0.0033 to -0.0007)), SP alone 1.7469.

## Leave one component out (projection minus that component vs full projection)

| component      |   share non-zero % |   sd vs field (WPR) | drop it: alone               | drop it: with SP             |
|:---------------|-------------------:|--------------------:|:-----------------------------|:-----------------------------|
| own_distance   |               28.5 |                0.42 | -0.0012 (-0.0047 to +0.0022) | +0.0002 (-0.0002 to +0.0007) |
| own_going      |               26.7 |                0.39 | -0.0032 (-0.0065 to +0.0001) | -0.0002 (-0.0006 to +0.0002) |
| own_first_up   |               10.7 |                0.41 | -0.0004 (-0.0032 to +0.0024) | +0.0001 (-0.0002 to +0.0004) |
| own_second_up  |                8.9 |                0.36 | -0.0004 (-0.0028 to +0.0021) | +0.0005 (+0.0002 to +0.0008) |
| own_trend      |                2   |                0.2  | -0.0019 (-0.0039 to +0.0001) | -0.0003 (-0.0006 to -0.0001) |
| own_long_spell |                1.3 |                0.13 | +0.0004 (-0.0001 to +0.0009) | -0.0000 (-0.0001 to +0.0001) |
| track_barrier  |               46.1 |                0.19 | -0.0014 (-0.0029 to +0.0001) | -0.0007 (-0.0010 to -0.0004) |
| closing_merit  |               87.3 |                0.49 | +0.0014 (-0.0018 to +0.0048) | +0.0007 (+0.0003 to +0.0011) |
| trainer_merit  |               87.7 |                0.67 | +0.0097 (+0.0049 to +0.0142) | -0.0002 (-0.0007 to +0.0002) |
| jockey_merit   |               87.8 |                0.69 | +0.0108 (+0.0055 to +0.0163) | -0.0012 (-0.0018 to -0.0005) |
| pace_shape     |               25   |                0.16 | +0.0003 (-0.0011 to +0.0015) | -0.0002 (-0.0004 to -0.0000) |
| pop_distance   |               61.7 |                0.48 | +0.0019 (-0.0016 to +0.0052) | -0.0004 (-0.0007 to -0.0001) |
| pop_going      |               61.3 |                0.32 | -0.0004 (-0.0029 to +0.0018) | -0.0002 (-0.0004 to -0.0000) |
| speed_map      |               43.5 |                0.31 | +0.0025 (+0.0004 to +0.0047) | -0.0001 (-0.0003 to +0.0000) |

- Positive = removing the component makes the projection worse (it helps); negative = it hurts (noise or wrong sign).

## Free weights (base + every component fitted separately)

- Free weights alone 1.9968 vs projection +0.0183 (+0.0069 to +0.0288); with SP 1.7758 vs projection + SP +0.0257 (+0.0160 to +0.0352).

| input | weight per WPR point | relative to base (1.0 = TopRate's weight) | with SP, relative |
|---|---|---|---|
| wprp_base | +0.1581 | +1.00 | +1.00 |
| own_distance | +0.0333 | +0.21 | +2.48 |
| own_going | -0.0066 | -0.04 | -2.06 |
| own_first_up | +0.0405 | +0.26 | -11.20 |
| own_second_up | +0.0552 | +0.35 | +2.93 |
| own_trend | -0.0619 | -0.39 | -11.24 |
| own_long_spell | +0.4480 | +2.83 | +68.81 |
| track_barrier | +0.1948 | +1.23 | -7.27 |
| closing_merit | +0.1397 | +0.88 | +3.37 |
| trainer_merit | +0.2088 | +1.32 | -2.79 |
| jockey_merit | +0.2136 | +1.35 | +0.68 |
| pace_shape | +0.5920 | +3.74 | +62.42 |
| pop_distance | +0.1169 | +0.74 | -9.66 |
| pop_going | +0.0372 | +0.24 | -8.26 |
| speed_map | +0.1399 | +0.88 | +3.80 |

## Dropping several together (same races, 2-fold)

| dropped | alone | with SP | top pick win % (full 27.5) |
|---|---|---|---|
| own_going + own_trend + own_distance | -0.0060 (-0.0115 to -0.0009) | -0.0003 (-0.0010 to +0.0003) | 27.6 |
| + track_barrier | -0.0073 (-0.0128 to -0.0018) | -0.0010 (-0.0018 to -0.0003) | 27.9 |
| track_barrier + speed_map (what the dashboard already swaps for the Racing Model's adj) | +0.0012 (-0.0015 to +0.0038) | -0.0008 (-0.0011 to -0.0004) | 27.9 |
| all five | -0.0046 (-0.0108 to +0.0012) | -0.0011 (-0.0019 to -0.0004) | 28.4 |

- Negative = better without them. wprp_contrib only exists in the 08:00 file from 25 Aug, hence 1,530 races.
