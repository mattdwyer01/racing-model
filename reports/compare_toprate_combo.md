# Racing Model vs TopRate Combo

- VIC/SA/QLD races 2026-04-26 to 2026-09-23 with every runner scored by both (full fields, one winner, SP known).
- Racing Model retrained at the start of each month (out of sample); Combo = TopRate dashboard Cb column.
- Combo / Proj turned into win chances by a one-parameter logit fitted on the other half of the dates.
- Caveat: TopRate fields are the runners file's last values (may be refreshed after the race).

Races 2786, runners 27035. Same top pick in 58% of races.

## Top pick

| pick          |   races | top pick won   | winner in top 3   | ROI top pick at SP   |
|:--------------|--------:|:---------------|:------------------|:---------------------|
| Racing Model  |    2786 | 27.5%          | 61.0%             | -15.6%               |
| TopRate Combo |    2786 | 29.5%          | 63.6%             | -11.2%               |
| TopRate Proj  |    2786 | 25.8%          | 58.1%             | -15.8%               |
| SP favourite  |    2786 | 32.6%          | 67.0%             | -12.5%               |

## Log loss (lower is better)

|                    |   log loss |
|:-------------------|-----------:|
| Racing Model       |     1.9516 |
| TopRate Combo      |     1.9308 |
| TopRate Proj       |     2.0125 |
| SP (calibrated)    |     1.8346 |
| Racing Model + SP  |     1.8315 |
| TopRate Combo + SP |     1.8333 |

## Paired differences (negative = first is better; 95% race bootstrap)

| first              | minus              | diff                         |
|:-------------------|:-------------------|:-----------------------------|
| Racing Model       | TopRate Combo      | +0.0207 (+0.0035 to +0.0381) |
| Racing Model       | TopRate Proj       | -0.0610 (-0.0786 to -0.0423) |
| TopRate Combo      | TopRate Proj       | -0.0817 (-0.0945 to -0.0690) |
| Racing Model + SP  | TopRate Combo + SP | -0.0018 (-0.0048 to +0.0013) |
| Racing Model + SP  | SP (calibrated)    | -0.0031 (-0.0060 to -0.0001) |
| TopRate Combo + SP | SP (calibrated)    | -0.0013 (-0.0042 to +0.0016) |

## By state

| state   |   races | Racing Model won   | TopRate Combo won   | TopRate Proj won   | SP favourite won   |   LL model - combo |
|:--------|--------:|:-------------------|:--------------------|:-------------------|:-------------------|-------------------:|
| QLD     |    1415 | 27.3%              | 30.6%               | 27.1%              | 33.7%              |             0.0037 |
| VIC/SA  |    1371 | 27.6%              | 28.4%               | 24.5%              | 31.4%              |             0.0383 |

## Where Combo's accuracy comes from (races where TopRate rating is present for every runner, n = 2,431)

- Within-race correlation with log SP: TopRate rating 0.93, Combo 0.84, Racing Model 0.77, TopRate Proj 0.68.
- Log loss alone: TopRate rating 1.8678 (SP calibrated 1.8470), Combo 1.9481, Racing Model 1.9820, Proj 2.0423.
- With SP: TopRate rating + SP 1.8469, Racing Model + SP 1.8471, Proj + SP 1.8471 (SP 1.8470): none adds anything
  over SP on this subset.
- Reading: TopRate rating behaves like a market price (a form rating alone does not get within 0.02 of SP).
  Combo's lead over the Racing Model alone comes from its 25% TopRate rating share, not from independent form
  information; beyond the market neither side has a clear edge.
