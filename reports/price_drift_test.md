# TAB fixed-price movement and the model at bet time

- 656 races, 2026-09-18 to 2026-10-03, all states (TopRate's TAB snapshots). Bet price = last snapshot >= 10 min before the start (median 160 min before); open = first snapshot of the day (median 4.2 h earlier).

## 1. Does the move add to the bet-time price? (race log loss, lower = better)

- bet-time price alone: 1.7935; + drift: 1.7918; difference -0.0016 (-0.0051 to +0.0018); drift coefficient -0.36 (> 0: firmers win more than their bet-time price says)

## 2. By move from the open to bet time

| band           |   runners |   won % |   median bet price |   A/E vs bet price |   A/E price-matched |   ROI at bet price % |   ROI at SP % |
|:---------------|----------:|--------:|-------------------:|-------------------:|--------------------:|---------------------:|--------------:|
| drifted > 30%  |       460 |   3.261 |               51   |              1.093 |               1.203 |               10.978 |       -25.682 |
| drifted 10-30% |      1027 |   6.329 |               16   |              0.905 |               0.969 |              -43.671 |       -33.021 |
| drifted 3-10%  |       819 |  12.454 |                8.5 |              1.052 |               1.047 |              -19.365 |       -16.532 |
| steady         |      2814 |  10.519 |               10   |              0.982 |               0.978 |              -41.679 |       -42.298 |
| firmed 3-10%   |       418 |  16.268 |                5.5 |              0.98  |               0.946 |              -28.062 |       -27.972 |
| firmed 10-30%  |       518 |  16.409 |                7.5 |              1.193 |               1.167 |               14.34  |        29.591 |
| firmed > 30%   |       274 |   9.124 |                8.5 |              0.794 |               0.79  |              -43.376 |       -31.479 |

## 3. Model (racing_model.json at the time) on top of the bet-time price

- 368 races. Price alone 1.7254; + model 1.7306 (+0.0052 (-0.0014 to +0.0121); weights price 1.17, model 0.11); + model + drift 1.7314 (+0.0060 (-0.0021 to +0.0141))

