# Speed map checks (walk-forward race-day projection, 2023 to Sep 2026, VIC/SA/QLD)

- 33,225 races, 313,360 runners with form. Surprise = (WPR - prior ability) - the model's position adjustment, vs the race: > 0 = ran better than the projection allowed.

## 1. Projected position x barrier

|                   |   runners |   model adj (WPR) |   actual (WPR) |   surprise | surprise 95%   |   actually led % |   A/E at SP |   A/E price-matched |
|:------------------|----------:|------------------:|---------------:|-----------:|:---------------|-----------------:|------------:|--------------------:|
| ('front', '1-4')  |     30768 |             0.786 |          0.304 |     -0.482 | -0.58 to -0.39 |           26.554 |       1.04  |               1.022 |
| ('front', '5-9')  |     26529 |             0.631 |         -0.204 |     -0.835 | -0.94 to -0.73 |           27.031 |       1.054 |               1.051 |
| ('front', '10+')  |      6619 |             0.453 |         -0.703 |     -1.156 | -1.38 to -0.93 |           29.415 |       1.046 |               1.074 |
| ('middle', '1-4') |     86206 |             0.09  |          0.534 |      0.444 | +0.39 to +0.50 |            5.161 |       0.984 |               0.975 |
| ('middle', '5-9') |     80489 |            -0.071 |         -0.083 |     -0.012 | -0.07 to +0.05 |            6.326 |       0.996 |               0.997 |
| ('middle', '10+') |     19930 |            -0.159 |         -0.723 |     -0.564 | -0.69 to -0.44 |            7.16  |       1.018 |               1.059 |
| ('back', '1-4')   |     13468 |            -0.646 |         -0.195 |      0.451 | +0.30 to +0.61 |            1.01  |       0.916 |               0.908 |
| ('back', '5-9')   |     34035 |            -0.716 |         -0.381 |      0.335 | +0.24 to +0.43 |            1.299 |       0.935 |               0.955 |
| ('back', '10+')   |     15316 |            -0.635 |         -0.562 |      0.073 | -0.07 to +0.22 |            1.371 |       1.002 |               1.069 |

Projected leader (rank 1) by barrier:

| bar3   |   projected leaders |   actually led % |   model adj |   actual |   surprise | surprise 95%   |   A/E price-matched |
|:-------|--------------------:|-----------------:|------------:|---------:|-----------:|:---------------|--------------------:|
| 1-4    |               16399 |           34.935 |       0.939 |    0.334 |     -0.605 | -0.74 to -0.47 |               1.019 |
| 5-9    |               13885 |           35.42  |       0.784 |    0.002 |     -0.782 | -0.93 to -0.63 |               1.069 |
| 10+    |                2950 |           38.644 |       0.618 |   -0.783 |     -1.401 | -1.73 to -1.04 |               1.08  |

- Corrections tested on 24,353 races 2024 to Sep 2026; x_track nonzero for 99% of runners.

## 2. Corrections in a conditional logit (leave-one-year-out, 2024 to 2026; negative = better)

| variant               | vs            | all races                    | soft 7+ / heavy              | weights                                                                     |
|:----------------------|:--------------|:-----------------------------|:-----------------------------|:----------------------------------------------------------------------------|
| + wet                 | ability + adj | +0.0000 (-0.0001 to +0.0001) | +0.0005 (-0.0001 to +0.0010) | h_d +0.134, adj_d +0.208, x_wet -0.018                                      |
| + wide front          | ability + adj | +0.0001 (-0.0000 to +0.0003) | -0.0002 (-0.0005 to +0.0002) | h_d +0.134, adj_d +0.217, x_wide_front -0.035                               |
| + track               | ability + adj | -0.0006 (-0.0011 to -0.0002) | +0.0010 (-0.0005 to +0.0025) | h_d +0.134, adj_d +0.178, x_track -0.195                                    |
| + all three           | ability + adj | -0.0005 (-0.0010 to +0.0000) | +0.0006 (-0.0007 to +0.0020) | h_d +0.134, adj_d +0.188, x_wet +0.031, x_wide_front -0.038, x_track -0.208 |
| SP + adj + wet        | SP + adj      | -0.0002 (-0.0005 to +0.0001) | -0.0016 (-0.0033 to +0.0003) | lsp +1.125, adj_d +0.055, x_wet +0.080                                      |
| SP + adj + wide front | SP + adj      | -0.0002 (-0.0004 to +0.0001) | +0.0006 (-0.0001 to +0.0013) | lsp +1.124, adj_d +0.024, x_wide_front +0.101                               |
| SP + adj + track      | SP + adj      | -0.0001 (-0.0004 to +0.0001) | -0.0006 (-0.0013 to +0.0000) | lsp +1.126, adj_d +0.060, x_track +0.095                                    |
| SP + adj + all three  | SP + adj      | -0.0004 (-0.0008 to +0.0000) | -0.0008 (-0.0029 to +0.0011) | lsp +1.127, adj_d +0.042, x_wet +0.064, x_wide_front +0.104, x_track +0.072 |

Tracks (2023-2025, >= 150 races): slope of WPR on settle share (negative = leaders favoured).
gap > 0 = model more pro-leader than results.

| track               |   races |   actual slope |   model slope |   gap |
|:--------------------|--------:|---------------:|--------------:|------:|
| Swan Hill           |     193 |          -3.22 |         -2.5  | -0.71 |
| Gawler              |     331 |          -2.87 |         -2.85 | -0.02 |
| Moe                 |     273 |          -0.9  |         -1.1  |  0.2  |
| Beaudesert          |     203 |          -4.16 |         -4.71 |  0.56 |
| Flemington          |     532 |           1.91 |          1.19 |  0.72 |
| Kilcoy              |     241 |          -5.23 |         -5.95 |  0.73 |
| Caulfield           |     470 |           0.19 |         -0.59 |  0.78 |
| Mornington          |     361 |           1.52 |          0.61 |  0.91 |
| Moonee Valley       |     494 |           0.64 |         -2.35 |  2.99 |
| Rockhampton         |     637 |          -0.88 |         -3.9  |  3.02 |
| Cranbourne          |     434 |           0.81 |         -2.24 |  3.05 |
| Morphettville Parks |     510 |           0.53 |         -2.55 |  3.08 |
| Gold Coast          |     324 |           0.77 |         -2.53 |  3.29 |
| Port Augusta        |     169 |          -4.25 |         -7.65 |  3.4  |
| Townsville          |     634 |          -0.69 |         -4.46 |  3.77 |
| Mackay              |     504 |           0.42 |         -3.43 |  3.85 |

## 3. By going: leader value actual vs model

| going      |   races |   actual slope |   model slope |   projected leader A/E pm |   front third surprise |   back third surprise |
|:-----------|--------:|---------------:|--------------:|--------------------------:|-----------------------:|----------------------:|
| good 1-4   |   21974 |         -1.064 |        -2.835 |                     0.981 |                 -0.661 |                 0.226 |
| soft 5-6   |    7230 |         -0.2   |        -2.488 |                     0.896 |                 -0.769 |                 0.333 |
| soft 7-8   |    2943 |         -0.088 |        -2.547 |                     1.142 |                 -0.765 |                 0.54  |
| heavy 9-10 |    1035 |          0.598 |        -2.422 |                     0.78  |                 -0.76  |                 0.82  |

