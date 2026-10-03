# Past-run WPR revisions (pre-race value vs current)

- 35,334 runners with a last start, 2026-04-27 00:00:00 to 2026-10-02 00:00:00. Pre-race value = `wpr_last1` in the 08:00 AEST runners file; current = DB `prev_wpr` (results files now).

- Exactly equal (|rev| < 0.05): 6.7%; |rev| > 1: 60.5%; > 3: 19.3%; mean |rev| 1.84; mean rev -0.01; corr(pre, current) 0.981

## By days since the last start (recent runs are the ones still preliminary)

| gapband   |   runners |   % revised (>0.05) |   mean |rev| |   % |rev| > 3 |
|:----------|----------:|--------------------:|-------------:|--------------:|
| <=7 d     |      2498 |               94.52 |         2.06 |         22.86 |
| 8-14 d    |     10723 |               93.04 |         1.88 |         20.63 |
| 15-28 d   |     13325 |               93.4  |         1.82 |         18.79 |
| 29+ d     |      8788 |               93.29 |         1.75 |         17.41 |

## Next-race result by revision (leak check: A/E should be ~flat if revisions carry no future info)

| band     |   runners |   won % |   A/E at SP |
|:---------|----------:|--------:|------------:|
| < -3     |      3625 |   7.034 |       0.99  |
| -3 to -1 |      8119 |   8.868 |       1.009 |
| -1 to 0  |      5121 |   9.705 |       0.93  |
| 0        |      2353 |  10.582 |       0.995 |
| 0 to 1   |      6362 |  11.427 |       0.975 |
| 1 to 3   |      6521 |  12.943 |       0.953 |
| > 3      |      3233 |  14.166 |       0.883 |

