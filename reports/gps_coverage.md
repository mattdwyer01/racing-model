# RQ GPS coverage and match to TopRate

- Files: rq_gps_runs 138,684 rows (102,089 runners that ran), rq_gps_sections 945,240 rows
- TopRate QLD runs from Oct 2022 with a duplicate date+venue+horse key: 30
- Race `race_time_s` minus winner `time_s`: median +1.91s, IQR +1.32 to +2.77s, 21 races off by more than 60s

## Coverage by year (runners that ran)

|   year |   meetings |    races |      runs |   dist_travelled |   any_rail |   all_sections_rail |   race_time |   rail_sections |
|-------:|-----------:|---------:|----------:|-----------------:|-----------:|--------------------:|------------:|----------------:|
|   2022 |     41.000 |  296.000 |  2599.000 |            1.000 |      1.000 |               0.998 |       1.000 |           0.999 |
|   2023 |    308.000 | 2393.000 | 23079.000 |            1.000 |      1.000 |               0.998 |       1.000 |           0.999 |
|   2024 |    365.000 | 2803.000 | 26860.000 |            1.000 |      1.000 |               0.997 |       1.000 |           0.999 |
|   2025 |    390.000 | 2974.000 | 27983.000 |            0.999 |      0.999 |               0.997 |       1.000 |           0.999 |
|   2026 |    291.000 | 2270.000 | 21568.000 |            0.999 |      0.999 |               0.971 |       1.000 |           0.974 |

## Match rate, RQ -> TopRate (date + venue + horse)

|   year |   rq_runs |   matched |   of_which_trials |
|-------:|----------:|----------:|------------------:|
|   2022 |      2599 |     0.980 |             0.000 |
|   2023 |     23079 |     0.993 |             0.000 |
|   2024 |     26860 |     0.998 |             0.000 |
|   2025 |     27983 |     0.998 |             0.000 |
|   2026 |     21568 |     0.979 |             0.000 |

## Match rate, TopRate -> RQ at meetings RQ covers

|   year |   tr_runs_at_gps_meetings |   matched |
|-------:|--------------------------:|----------:|
|   2022 |                  2680.000 |     0.950 |
|   2023 |                 23366.000 |     0.981 |
|   2024 |                 27102.000 |     0.989 |
|   2025 |                 28421.000 |     0.982 |
|   2026 |                 21754.000 |     0.971 |

## Share of all QLD TopRate race runs with GPS

|   year |   share_of_all_QLD_race_runs |
|-------:|-----------------------------:|
|   2022 |                        0.277 |
|   2023 |                        0.545 |
|   2024 |                        0.630 |
|   2025 |                        0.683 |
|   2026 |                        0.741 |

## GPS share by TopRate venue

| venue          |   tr_runs |   gps |
|:---------------|----------:|------:|
| Sunshine Coast | 17177.000 | 0.959 |
| Doomben        | 14214.000 | 0.932 |
| Eagle Farm     | 13510.000 | 0.914 |
| Ipswich        | 13172.000 | 0.948 |
| Gold Coast     | 12173.000 | 0.949 |
| Toowoomba      | 10901.000 | 0.964 |
| Townsville     |  9243.000 | 0.756 |
| Rockhampton    |  7722.000 | 0.646 |
| Mackay         |  6103.000 | 0.793 |
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
| Ipswich        |  30 |
| Rockhampton    |   5 |
