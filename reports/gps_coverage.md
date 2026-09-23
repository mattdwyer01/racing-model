# RQ GPS coverage and match to TopRate

- Files: rq_gps_runs 138,397 rows (101,885 runners that ran), rq_gps_sections 943,420 rows
- TopRate QLD runs from Oct 2022 with a duplicate date+venue+horse key: 30

## Coverage by year (runners that ran)

|   year |   meetings |    races |      runs |   dist_travelled |   any_rail |   all_sections_rail |   race_time |   rail_sections |
|-------:|-----------:|---------:|----------:|-----------------:|-----------:|--------------------:|------------:|----------------:|
|   2022 |     41.000 |  294.000 |  2577.000 |            1.000 |      1.000 |               0.998 |       0.000 |           0.999 |
|   2023 |    307.000 | 2374.000 | 22897.000 |            1.000 |      1.000 |               0.998 |       0.000 |           0.999 |
|   2024 |    365.000 | 2803.000 | 26860.000 |            1.000 |      1.000 |               0.997 |       0.000 |           0.999 |
|   2025 |    390.000 | 2974.000 | 27983.000 |            0.999 |      0.999 |               0.997 |       0.000 |           0.999 |
|   2026 |    291.000 | 2270.000 | 21568.000 |            0.999 |      0.999 |               0.971 |       0.000 |           0.974 |

## Match rate, RQ -> TopRate (date + venue + horse)

|   year |   rq_runs |   matched |   of_which_trials |
|-------:|----------:|----------:|------------------:|
|   2022 |      2577 |     0.979 |             0.000 |
|   2023 |     22897 |     0.993 |             0.000 |
|   2024 |     26860 |     0.998 |             0.000 |
|   2025 |     27983 |     0.998 |             0.000 |
|   2026 |     21568 |     0.979 |             0.000 |

## Match rate, TopRate -> RQ at meetings RQ covers

|   year |   tr_runs_at_gps_meetings |   matched |
|-------:|--------------------------:|----------:|
|   2022 |                  2680.000 |     0.942 |
|   2023 |                 23313.000 |     0.975 |
|   2024 |                 27102.000 |     0.989 |
|   2025 |                 28421.000 |     0.982 |
|   2026 |                 21754.000 |     0.971 |

## Share of all QLD TopRate race runs with GPS

|   year |   share_of_all_QLD_race_runs |
|-------:|-----------------------------:|
|   2022 |                        0.274 |
|   2023 |                        0.541 |
|   2024 |                        0.630 |
|   2025 |                        0.683 |
|   2026 |                        0.741 |

## GPS share by TopRate venue

| venue          |   tr_runs |   gps |
|:---------------|----------:|------:|
| Sunshine Coast | 17177.000 | 0.956 |
| Doomben        | 14214.000 | 0.932 |
| Eagle Farm     | 13510.000 | 0.914 |
| Ipswich        | 13172.000 | 0.944 |
| Gold Coast     | 12173.000 | 0.949 |
| Toowoomba      | 10901.000 | 0.961 |
| Townsville     |  9243.000 | 0.756 |
| Rockhampton    |  7722.000 | 0.646 |
| Mackay         |  6103.000 | 0.785 |
| Gatton         |  4984.000 | 0.256 |
| Cairns         |  4911.000 | 0.811 |
| Warwick        |  3664.000 | 0.234 |
| Kilcoy         |  3347.000 | 0.288 |
| Dalby          |  2859.000 | 0.274 |

## Unmatched RQ runners by venue (top 10)

| venue          |   n |
|:---------------|----:|
| Gold Coast     | 187 |
| Sunshine Coast | 166 |
| Eagle Farm     | 116 |
| Doomben        | 112 |
| Townsville     |  84 |
| Toowoomba      |  48 |
| Mackay         |  37 |
| Ipswich        |  29 |
| Rockhampton    |   5 |
