# racing-model: context for Claude Code sessions

Owner: Matt. Style: direct, concise dot points, no em dashes in any output.

## Goal
Win-probability model for VIC, SA and QLD thoroughbred races, bet on TAB fixed odds.
Structure: per-run performance figure -> current ability per horse -> race-day projection
(settle position, width, ground loss) -> conditional logit -> blend with market -> fractional Kelly.

## Data sources (decided)
- TopRate yearly results files (backbone, 2017 on; near-complete for all AU from 2022; sectionals from 2019).
  Raw files are NOT in git (in `data/raw/toprate/`, to be uploaded to the `data` release).
- GPS (Triple S): QLD via RQ meeting ZIP XML (Oct 2022 on, per-200m rail distance);
  VIC/SA via racing.com GraphQL getRaceForm (Triple S VIC metro from Aug 2021; whole-race avg rail distance).
  PDFs are a fallback only (`ingest/tsd_gps_pdf.py`).
- TAB fixed odds: the TopRate repo's poller logs every read on the Vultr box (`~/racing-data/tab_prices/`);
  `tab_price_archive.yml` ships it to the store. Pre-Sep 2026 prices: `fixed_prices_final` (dashboard
  runners file, Apr 2026 on) and `tools/extract_prices_from_git.py` (git history of toprate_runners.csv).
- Punting Form: dropped (no lift over SP in testing, borrowed login).

## Future sources (not built)
- NSW metro (ATC) Swiss Timing sectional PDFs:
  `feed.australianturfclub.com.au/sectionals/swiss-timing/{year}/{DDMM}{TRACK}-{race}.pdf` (e.g. `1909RAND-1.pdf`).
  Per horse: DT-W (distance travelled vs winner, m), barrier, 200m cumulative times with positions,
  splits, top speed. No rail distance.
- WA sectional workbooks: times only, no distance travelled. Skip.

## Rules
- In `runs`, columns prefixed `res_` are in-race results: never inputs for the same race.
  TopRate `wpr` in the raw files is the rating OF that run (post-race).
- Train/test from 2022; walk-forward splits by date only; backtest at SP or captured fixed price, never top fluc.
- TopRate has no race number; `race_times` (from the dashboard runners file) has it from Apr 2026.
- RQ XML `DrawNumber` repeats the saddlecloth number; barrier comes from TopRate.
- Adoption rule: keep a change that improves the model alone (walk-forward, significant) even if the SP blend is
  unchanged, as long as the blend is not significantly worse. Model quality matters beyond the SP blend (bet-time
  fixed prices, place / exotics, selection). Test additions together (they overlap) with leave-one-out variants.

## Automation
- Data store = assets on the GitHub release tagged `data` (`pipeline/store.py`), not git. Store repo = variable
  `DATA_REPO` (private, e.g. `mattdwyer01/racing-data`) with secret `DATA_TOKEN`; falls back to this repo.
  `python pipeline/store.py migrate mattdwyer01/racing-model` copies the old store across.
- `gps_daily.yml` (06:00 AEST), `gps_backfill.yml` (manual), `tab_price_archive.yml` (Vultr runner).
- `health_check.yml` (07:15 and 13:30 AEST): `tools/health_check.py` checks the served files (results fresh / final,
  weights, racing_model.json fresh + model self-check `health` from `race_card.model_health`, payload fresh / split /
  weights, race-day adjustments). Fails the job and opens / comments on a "Data health" issue.
- My workspace and GitHub-hosted runners may be blocked by TAB (confirmed) and possibly RQ / racing.com;
  set repo variable `SCRAPER_RUNNER=vultr-au` to move scraping to the Vultr self-hosted runner.

## Baseline (fixed; compare every change against it, race by race)
- `model/blend_eval.py` at commit 95f42f7, report `reports/baseline_blend_eval.md`, per-race losses in
  `reports/blend_per_race.csv.gz` (variant `baseline`). Leak-free (`tools/leakage_check.py` passes).
- Test: 37,821 VIC/SA/QLD races, folds 2023 to 2026 YTD; model = figure + ability + jockey/trainer +
  race-day projection v3, no market inputs; blend = softmax(a log p_model + b log p_SP), a/b fitted on the
  last 25% of each training window from out-of-sample predictions.
- Pooled log loss: SP raw 1.7900, SP calibrated 1.7863, logit 1.9332, GBM 1.9090, logit blend 1.7852,
  GBM blend 1.7856. Logit blend minus SP calibrated -0.0011 (95% -0.0017 to -0.0005); minus SP raw -0.0048.
  Ahead or level in all 8 half-years, significant in 2 (2023 H1, 2024 H1); weight on model a = 0.10-0.15.

- Since then (all vs the baseline, paired by race; runs with `--tag` keep their own report / per-race file):
  - Edge is QLD only: logit blend minus SP calibrated QLD -0.0029 (95% -0.0039 to -0.0020), VIC/SA +0.0004
    (n.s.). Fitted weight on the model: QLD 0.16-0.26, VIC/SA 0.02-0.05 (logit), about 0 (GBM).
  - Per-state blend weights (`blend_eval_det.md`): no net gain (-0.0001 logit, -0.0003 GBM, n.s.); they only
    turn the model down in VIC/SA. Pooled weights kept.
  - GPS ground-loss history (`blend_eval_gl.md`): blend -0.0001, n.s. Not adopted.
  - Figure v2 (`ability.fit_coef_next`, `blend_eval_fig2.md`): next-start WPR regression weights (settle +0.17
    not -5.6; corrections for missing sectionals, heavy defeats, heavy going, track class). Logit model alone
    -0.0033 (QLD -0.0055), but blend +0.0001 n.s. and GBM no gain. Not adopted for the blend.
  - Run comments (`extra_history.CM_FEATS`) + past ground loss = production model (`model/production.py`, WPR
    points in `reports/logit_wpr_table.md`, race cards via `tools/race_card.py`). Latest rerun with VIC/SA
    racing.com GPS in `gps_runs` (`blend_eval_vicsa.md`): prod logit blend minus baseline -0.0002 (n.s.),
    QLD -0.0005 (95% -0.0009 to -0.0001), VIC/SA 0.0000; prod logit model alone -0.0056. Prod GBM blend is worse
    in VIC/SA (+0.0013, significant): use the logit blend.
  - Rating (Thurstone) model: +0.0009 worse. Position value map (`position_map.py`): 0.0000 vs prod. VIC/SA
    GPS section history (`gpsx`): +0.0002 logit blend, 0.0000 GBM blend. None adopted.
  - Price timing (`reports/price_timing.md`, 2026, git snapshots): the snapshots are 1.5 to 3 hours old even at
    "T-2" and far behind SP (1.88 vs 1.854). Blend minus calibrated price: VIC/SA -0.0016 at T-60 to -0.0002 at
    T-2 (n.s.); QLD +0.0030 to +0.0034 (worse). Inconclusive; needs the Vultr TAB log at true T-10 / T-2.
  - prod2 (`blend_eval_prod2.md`, leave-one-out): production + rating mu + v4 settle + GPS pace, without figure
    v2, is -0.0034 model alone (QLD -0.0057), blend level. Figure v2 hurts once rating mu is in (+0.0019);
    v4 settle and GPS pace add 0.0000 on top. So the gain is rating mu: ADOPTED in `production.py`
    (r_mu, r_sigma; rating model refitted inside each training window). v4 / GPS pace kept for the speed map.
  - Race simulation (`race_sim.md`): no gain (blend +0.0002). Finishing-order model (`order_model.md`):
    discounted Plackett-Luce (2nd 0.75-0.78, 3rd 0.59-0.64) beats Harville by a wide margin; blend vs SP in QLD
    exacta -0.0052, trifecta -0.0079. Betting test at SP (`betting_test.md`): nothing significant.
  - Disagreement on prod2 (`disagreement_prod2.md`): position map (top 5% up A/E 1.09) and past ground loss
    (top 10% up A/E 1.07, both states) still beat the market; figure v2 harmful both ways. As blend weights
    (`signal_blend.md`) they add 0.0000 (unstable weights): selection filters only, test at bet-time prices.
  - Staged model (`staged.md`): ability from a WPR regression is far weaker (+0.035 model alone); the race-shape
    stage S3 adds -0.0071 inside it, but on top of production (`staged_prod_s3.md`) +0.0002 n.s. Not adopted.
    TopRate 2023 res_shape_mid has absurd outliers (sd 9.8 vs 2.5): clip |x| > 12 (done in staged.py only).
  - vs TopRate Combo (`tools/compare_toprate_combo.py`, `compare_toprate_combo.md`, 2,786 races Apr to Sep 2026,
    monthly retrain): top pick won 27.5% (Combo 29.5%, Proj 25.8%, SP fav 32.6%); model alone 1.9516 vs Combo
    1.9308 (+0.021, significant); with SP ours 1.8315 vs Combo 1.8333 (-0.0018 n.s.), ours vs SP -0.0031.
    Combo's lead is its TopRate rating share: that rating correlates 0.93 with log SP and alone scores 1.868 vs SP
    1.847, i.e. it behaves like a market price, not independent form.
  - TopRate rating is LOOK-AHEAD in the runners file: its final value is rewritten after the jump (on 24 Sep the change
    from the morning file correlated 0.33 with -log SP, winners +0.27 vs their race). Pre-race values from git history
    (`tools/toprate_rating_snapshots.py`, 08:00 / 12:00 / 15:00 AEST, latest >= 10 min before the start;
    `data/interim/toprate_rating_prerace.csv.gz`, 75% filled). Same 2,786 races (`rm_toprate_blend_test_prerace.md`):
    TopRate rating alone 2.0909 (top pick 17%) vs 1.8824 with final values; Combo 1.9798 vs 1.9308; RM 1.9515 beats
    Combo by 0.028. So the Combo comparison above and its "TopRate rating share" conclusion were look-ahead.
    RM + pre-race TopRate rating (fitted): model alone -0.0080 (-0.0144 to -0.0015), with SP +0.0017 (-0.0005 to
    +0.0039; VIC/SA +0.0041 significant, QLD -0.0006). Form factor adds nothing. Not adopted: blend not better and
    worse in VIC/SA; final-value version (`rm_toprate_blend_test.md`) is invalid.
  - Combo redesign on PRE-RACE TopRate values (`tools/combo_redesign_test.py`, `combo_redesign_test.md`, 22 Aug to
    23 Sep 2026, ~790 races): our race-day adj in place of TopRate's speed_map + track_barrier +0.0006 (n.s.), + GPS
    past ground loss +0.0007, + position value +0.0011 (all n.s., with SP too). Dropping the form factor -0.019 alone
    (significant), +0.0026 with SP (n.s.): ADOPTED in TopRate (Combo = 2/3 WPR projection + 1/3 TopRate rating).
    Combo + SP is worse than SP here (+0.0092). Dashboard now shows Combo (user decision) with our adjustments.
  - Combo with our race-day adj in place of TopRate's speed_map term (`tools/combo_swap_test.py`,
    `combo_swap_test.md`, 790 races 22 Aug to 23 Sep 2026, the only window with speed_map): no change (+0.0005
    alone, -0.0003 with SP, both n.s.; fitted weight no better). TopRate's own speed_map is worth +0.0011 n.s.
    Position terms are small inside Combo (sd 0.46 / 1.01 WPR vs a field spread of ~8, 50% weight).
  - In-day track bias (`model/inday_bias_test.py`, `inday_bias_test.md`, 3,731 races 26 Apr to 11 Sep 2026, on top of
    production OOS): same-day bias from ALL other races at the meeting helps (-0.0028 model, -0.0024 with SP) but
    that uses later races (hindsight). Earlier races only add nothing, even with perfect information (actual
    positions + WPR: -0.0002 model, +0.0002 with SP; race 5 onwards also n.s.). Not built. The race page shows
    the model's projected bias from past meetings instead (`dashboard_export.race_bias`).
  - Gap-from-top lines for the dashboard table (4,061 VIC/SA/QLD races Apr to Sep 2026, OOS; gap WPR = 6.843 x
    ln(p_top / p)): within 4 WPR A/E at SP 1.08 (2.6 runners, 56% of winners); beyond 8 WPR A/E 0.86, ROI -43%
    (79% of winners inside). Stable Apr-Jul vs Aug-Sep. TopRate table shows 4 / 8 WPR lines (RaceDetail).
  - Points clear of the next horse (`tools/clear_test.py`, `clear_test.md`, 70,291 races 2023 to Sep 2026, all
    states, yearly retrain OOS): every gap band loses at SP (-5% to -20%). Price-matched A/E (vs all runners at the
    same SP; plain normalised-SP A/E is inflated by favourite-longshot bias) 1.01-1.05 under 6 WPR, 1.08 at 6+.
    Top pick not SP favourite and 6-8 clear: 672 races, A/E 1.20 (1.05-1.35), ROI +1.8% n.s. Similar in all states.
    Also: missing carried weight from 14 Sep made the v1 figure fit NaN (every horse a debutant); fixed in
    figure.figure / ability.fit_coef, past dashboard races rescored (`dashboard_export --rescore-from`).
  - racing.com (VIC/SA) GPS with vs without (`tools/rc_gps_test.py`, `rc_gps_test.md`, 37,821 races, prodmu logit;
    "without" deletes the rc rows of gps_runs): no effect anywhere. Model alone -0.0001 (-0.0006 to +0.0005), VIC
    +0.0001, SA -0.0006 n.s.; blend -0.0000. Kept (harmless, feeds the speed map / ground-loss display); it is in
    training already (projection y_gl and h_gl / h_rail read gps_runs, all sources).
  - Carried weight real vs race average (`tools/rc_gps_test.py weights`, `weights_test.md`, 37,821 races, prodmu logit):
    model alone -0.0029 (95% -0.0038 to -0.0021; every state and fold), blend -0.0002 (QLD -0.0005, VIC/SA 0.0000).
    Weights matter: keep them filled (TAB race cards + TopRate weightHandicap).
  - TopRate race_results_2026.csv.gz stopped at 13 Sep 2026 and kept PRELIMINARY WPRs for its last week (8 Sep
    Muswellbrook 74.0 vs final ~62.5): TopRate PR 249 adds --refresh-preliminary and a daily run.
  - Combo lines (`tools/combo_lines_test.py`, `combo_lines_test.md`, 1,027 races Apr to Sep 2026, pre-race values, Combo =
    2/3 WPR proj + 1/3 TopRate rating): within 10 WPR holds 90% of winners (outside A/E 0.86, ROI -46%), within 4 WPR 58% in
    2.8 runners (A/E 1.04), within 5 WPR 64% (A/E 1.02), beyond 15 WPR 2%. Dashboard Combo stays on the WPR scale (user
    decision); lines at 10 and 4 WPR (TopRate PR #253).
    Live Combo (our race-day adj + past ground loss in place of TopRate's speed_map / barrier; `combo_lines_test.py live`,
    `combo_lines_live.md`, 695 races 22 Aug to 23 Sep): gap corr 0.990 with the tested Combo, ~5% of runners change
    side of each line; within 10 holds 87% of winners (outside ROI -50%), within 4 holds 54% (A/E 1.01). Lines kept.
    Quaddie bands (2 Oct, 304 quaddies 22 Aug to 30 Sep, est dividends from SP, 600 cap): inner x outer x first starters
    grid; first starters hurt almost everywhere, outer 8 beats outer 10 at every inner (4/8 no FS -12% vs 4/10 -39%,
    user rule 4/10 + FS -47%); inner 2-4 within noise. Dashboard outer line now 8 WPR (TopRate PR #259). Combo cap:
    300-600 best (-8 to -12%), no cap -30% (14 quaddies over 1,000 combos lose most); all CIs include the 20% take.
    Real dividends vs the SP estimate (user-reported, 2 Oct): Launceston $48 vs $40 (1.20), Moruya $185 vs $139 (1.33),
    Pakenham $133 vs $81 (1.64); geometric mean 1.38. At that ratio the 4/8 rule's -12% would be about +21%.
  - Real TAB dividends: TopRate `tab_dividends.py` logs every pool per race from 2 Oct 2026 (`tab_dividends.csv`; TAB's API
    serves no past dates). Exotic rules (`tools/exotics_test.py`, `exotics_test.md`, 22 Aug to 1 Oct, 265 meetings, SP-based
    discounted PL estimate calibrated per pool on 2 Oct's 287 real dividends: real x fair-SP chance Win 0.85, Quinella 0.83,
    Exacta 0.82, Trifecta 0.79, First Four 0.75, Running Double 0.87, slope ~1): vs the SAME number of runners picked by SP
    (flexi, paired), box within-4 beats SP in Quinella +8.4 pts (-1.3 to +18.0), Exacta +8.5 (-1.1 to +18.5), Trifecta
    +23 (-5 to +56), A/A/B trifecta +15 (-7 to +37); First Four -4, multi-race pools no gain (doubles / treble / quaddies
    have 5-6 real dividends each: too few to calibrate). Absolute: trifecta A/A/B +13% flexi, box A +12%, exacta / quinella
    box A +2 / +4% (one-day calibration). Re-test on real dividends after ~3 weeks of capture.
    Caps (flexi, est.): trifecta A/A/B 36, box A 24, exacta 12, quinella 6, quaddie 400; first starter in the race / any
    leg hurts trifecta (-18% vs +23%) and quaddie (-58% vs +65%). Early quaddie legs = the 4 races before the main
    (races 1-4 at 7 races or fewer; user correction, `exotics_test.multi_legs`): 61 of 201 qualify, est. +119% (-15 to
    +285) vs -40% for SP picks. Dashboard race pages show these live (TopRate `lib/betRules.ts`, PRs #267 / #268).
  - NSW / WA (`RACING_EXTRA_STATES=NSW,WA`, `blend_eval_nswwa.md`; control = VIC/SA/QLD-only rerun on the same DB,
    `blend_eval_ctl.md`, identical to `mu` on shared races; paired `blend_eval_nswwa_vs_ctl.md`, 37,821 races):
    - NSW/WA in training helps VIC/SA/QLD: prodmu model alone -0.0011 (95% -0.0018 to -0.0004; QLD -0.0021,
      VIC/SA -0.0002 n.s.), logit blend -0.0004 (-0.0006 to -0.0002; QLD 0.0000, VIC/SA -0.0006). Half the blend
      gain is SP calibration fitted on more races (SP calibrated -0.0003). Better in 2023-2025, model alone
      +0.0010 in 2026.
    - Within NSW (20,018 races) / WA (7,795): SP calibrated 1.7467 / 1.7836, prodmu model alone 1.8962 / 1.9371,
      logit blend 1.7465 / 1.7860. Blend minus SP calibrated: NSW -0.0002 (-0.0011 to +0.0006), WA +0.0024
      (+0.0011 to +0.0036, worse every fold). No edge in either; QLD edge unchanged (-0.0034).
    - Fitted weight on the model a (prodmu, per state): QLD 0.18-0.27, VIC/SA 0.06-0.09, NSW 0.24 / 0.22
      (2023-24) then 0.08, WA -0.32 (2023) then -0.01 to 0.04; pooled 0.09-0.15. Per-state weights vs pooled
      +0.0003 n.s. (QLD +0.0009, NSW +0.0006 worse): keep pooled weights, but pooled a hurts WA (per-state a ~0
      brings WA to SP level). Rating mu still helps model alone in NSW (-0.0034) and WA (-0.0051).
    - Verdict: training on all 5 states ADOPTED (`production.TRAIN_EXTRA_STATES`, applied by
      `production.use_training_scope()` in production.py / race_card / dashboard; an explicit RACING_EXTRA_STATES
      overrides, research scripts keep VIC/SA/QLD). Race cards stay VIC/SA/QLD (`core_scope`). Bet QLD only;
      NSW / WA not worth betting on this model.
  - Gear / wpr_nett (`gear_wpr_test.md`, 26 Apr to 23 Sep 2026, 5 states, half-window swap offset logits):
    - wpr_nett on top of production: model alone -0.0073 (95% -0.0107 to -0.0042; all states negative), blend
      +0.0000 (-0.0003 to +0.0003). Leakage line passes: wpr_nett alone is +0.2268 behind SP (+0.2089 to
      +0.2434) and +0.0895 behind production. It is 89% explained by pre-race WPR stats; adding the race's own
      WPR lifts that only to 89.5%. Meets the adoption rule, but exists only in the runners file (Apr 2026 on),
      so it can only be an offset layer on production, not a walk-forward input. Not adopted yet.
    - Gear: `gear_changes` is only filled from 1 Sep 2026 (992 races). There + gear is +0.0042 (-0.0034 to
      +0.0123) model alone, +0.0053 blend: no evidence, overfits. Retest after a few months of gear data.
  - Leader value by projected pace / track (`tools/pace_leader_test.py`, `pace_leader_test.md`, 37,986 races 2023 to
    Sep 2026, walk-forward v3): within-race slope of (WPR - prior avg WPR) on projected settle share goes from -1.61
    (slowest projected fifth) to +0.36 (fastest); proj_adj + bias_adj goes -3.72 to -1.83, so the pace GRADIENT is
    right but the level is ~2 WPR more pro-leader (partly because prior WPR already holds a horse's usual position).
    Actual pace (hindsight) -3.14 to +2.62: pace matters a lot, the forecast (R2 0.11) catches a fraction. At SP the
    projected leader is A/E 1.10 in slow races, 1.00 in the fastest fifth (back third 0.92 to 1.03); settle x pace
    over SP + adj: beta right sign, -0.0001 n.s. Staying races (1701m+) favour back-markers (+0.69). Tracks: actual
    vs model slope corr 0.84 (split-half 0.53); model much more pro-leader than results at Townsville, Mackay,
    Longreach, Thangool, Emerald; Flemington, Mornington, Morphettville, Eagle Farm, Sunshine Coast favour
    back-markers. The production logit has no pace term of its own (proj_pace -0.05, proj_shape 0 WPR per unit).
  - Settle x race shape in the production logit (`blend_eval.py --variants prodmu shape shape-pace shape-dist
    --logit-only --tag shape`, `blend_eval_shape.md`, 37,821 races): sx_pace = settle vs race mean x proj_shape,
    sx_dist = same x log(dist / 1200). Model alone -0.0001 (-0.0002 to +0.0001; QLD -0.0002 n.s.), blend 0.0000
    (QLD -0.00004). Distance term adds nothing. Not adopted: proj_adj already carries the pace gradient, and the
    rest of pace is not forecastable from pre-race data (R2 0.11).
  - Pace forecasts (`tools/pace_forecast_test.py`, `pace_forecast_test.md`, 38,370 races): new pace inputs (horse lead
    history, early speed contest, jockey / barrier of the fastest, class, track x distance past shape) lift early
    shape R2 0.094 -> 0.102 and the leader-value spread (slowest vs fastest fifth) 1.9 -> 2.5 WPR. GPS pace target
    sorts leader value worse (0.5-0.9). A DIRECT leader-value target (race's within-race slope of WPR - prior WPR on
    projected settle, weighted) sorts best: spread 6.3 WPR, beta +2.28 per SD (hindsight actual shape +1.79); main
    inputs track, distance, front runners' pace history. Beyond proj_adj + bias_adj it still adds +1.40 per SD; at
    SP (SP + adj + settle) -0.0004 (-0.0007 to -0.0001), stable beta; pace-only projections 0.0000.
  - Leader value in the production logit (`model/leader_value.py`, `blend_eval.py --variants prodmu lv --logit-only
    --tag lv`, `blend_eval_lv.md`, 37,821 races): lv_x = settle vs race mean x projected leader value (yearly
    out-of-sample fits, so training rows see OOS values). Model alone -0.0006 (-0.0008 to -0.0004; QLD -0.0009,
    VIC/SA -0.0002), blend -0.0001 (-0.0001 to -0.0000; QLD -0.0001); better in every fold. ADOPTED
    (`production.py` sets `om.LEADER_VALUE`; lean dashboard build included; shown in "race-day projection").
    Disagreement at SP (`model/disagreement.py --lv`, `disagreement_lv.md`, 2023 to 2026): pushed UP top 5% A/E SP
    1.075 (1.03-1.12; QLD 1.07, VIC/SA 1.08), ROI -25.8% vs price-matched control -31.8% (+0.002 to +0.125); DOWN
    bottom 10% A/E 0.93 (QLD 0.91), bottom 5% QLD 0.865, ROI below control (QLD -0.150 to -0.045). Groups are
    longshots (avg SP ~30), every group loses flat at SP: a selection / avoid filter, not a standalone bet.
    At 2026 git-snapshot fixed prices (`tools/lv_fixed_price_check.py`, `lv_fixed_price_check.md`, 1,922 races,
    median age 114 min): nothing significant (CIs +/-0.2 to 0.3). Retest on the Vultr TAB log.
  - Dashboard review on PRE-RACE values (`tools/dashboard_snapshots.py` rebuilds what the dashboard showed from TopRate
    git history, `tools/dashboard_review.py`, `dashboard_review.md`, 1,614 races 22 Aug to 30 Sep, all states; Combo /
    speed map as the dashboard builds them now): Combo top 30.4% wins, ROI -14.9% at SP (SP fav 34.6%, -12.8%);
    speed map tag: favoured A/E 1.1, unfavoured 1.0 (not a negative signal). User rule (Combo top 4+ clear, speed map
    not unfavoured, no first starter): 307 bets, 41.0%, ROI -5.1% SP (-19 to +9), -4.4% at stored fixed; favoured-only
    223 bets +6.7% (-10 to +24), n.s.; first-starter filter makes no difference. Quaddie rule (within 4 + 4-10 not
    unfavoured + first starters, <= 600 combos): hit 35% at ~300 combos, estimated ROI -47% (-66 to -25; dividends
    estimated from SP, 20% take: needs real dividends 1.9x the estimate to break even); within-4 only -26% n.s.
    No quaddie dividends anywhere in the data: capture them in TopRate's TAB results poller.
  - Wet / heavy form (`model/wet_form.py`, `blend_eval.py --variants prodmu lv wet wet-sire --logit-only --tag wet`,
    `blend_eval_wet.md`, 37,821 races): heavy-band and soft-band form (dev vs the horse's prior level), untried
    wet / heavy, sire wet / heavy form (progeny, earlier dates). vs production: all races model alone -0.0002 n.s.,
    blend -0.0001 (significant, tiny); heavy 9-10 (1,248 races) model alone -0.0033 (-0.0079 to +0.0015), blend
    -0.0006 (-0.0013 to 0.0000); soft 7-8 blend -0.0004 n.s.; sire inputs carry part of it. Production edge vs SP by
    going: good/soft 1-6 -0.0017 (significant), soft 7-8 +0.0002, heavy +0.0025 (n.s.): no edge on wet tracks.
  - Model-improvement round (3 Oct 2026, user "test all"):
    - Betting on the model's own probabilities (`tools/model_bet_test.py`, `model_bet_test.md`, 67,391 races 2023 to Sep
      2026, clear_test OOS scores): win overlays at SP (blend x SP > 1 + m) no edge (-4%, -13 to +4 at m 0); first run
      showed a fake +56% from ~1,000 races whose SPs sum below 100% (now dropped: overround kept 1.08-1.6). At the
      dashboard's stale fixed prices +12% but the same bets lose 28% at SP (stale prices, not edge). Exotics by blend
      order chances vs the same number of SP-picked combos: level at low margins; at margin 0.1 trifecta hits 1.91x
      SP-implied vs 1.58x, exacta 1.84x vs 1.48x (estimated dividends too generous: SP picks also show profit). Lead only.
    - Price movement (`tools/price_drift_test.py`, `price_drift_test.md`, 656 races 18 Sep to 3 Oct, TopRate TAB
      snapshots, bet price median 160 min before): drift adds -0.0016 (n.s.); model on top of that price +0.0052 (n.s.).
      Needs the Vultr TAB log: `tab_price_archive.yml` is skipped every night (VULTR_RUNNER not set for this repo).
    - Gear / wpr_nett rerun to 2 Oct (`gear_wpr_test_oct.md`): wpr_nett model alone -0.0074 (-0.0106 to -0.0043, every
      state), blend +0.0001 n.s. (same as before). Gear (1 Sep to 2 Oct, 1,430 races) +0.0147 worse, unstable signs.
    - WPR revisions (`tools/wpr_revision_test.py`, `wpr_revision_test.md`, 35,334 runners Apr to Oct 2026): 93% of
      last-start WPRs differ from the race-morning value (mean |change| 1.8, 19% > 3), old runs too (TopRate re-rates
      history). No flattering: revised-up horses ran A/E 0.88 next start. Train / serve mismatch; keep dated copies.
    - Bad SPs: 436 VIC/SA/QLD races since 2023 have SPs summing below 100% (impossible); QLD has 1,533 races over 160%
      (thin country markets, likely real). Exclude the first group from training and evaluation.
    - Bad-SP filter (`blend_eval.py --variants lv --logit-only --sp-check --tag spcheck`, 38,077 clean races of 38,310):
      blend / SP calibration fitted without races whose SPs sum below 100%: lv blend -0.00002 (-0.00004 to -0.00001),
      weights barely move (a 0.117-0.184 vs 0.122-0.185). ADOPTED in `production.train` (consistency; tiny gain).
    - wpr_nett top layer ADOPTED (`model/wpr_nett_layer.py`, applied in `race_card.score` -> race cards / dashboard;
      `model % (base)` keeps production's own chance; RACING_WPR_NETT=0 switches it off). Weights 0.834 log p_model,
      0.049 per wpr_nett point vs field, 0.128 missing (mean of the half-window fits). Smoke test 26 Sep to 2 Oct
      (334 races, weights partly in-sample): model log loss 1.7984 -> 1.7863. Refit with gear_wpr_test.py as data grows.
    - Combo strike rate (`tools/combo_strike_test.py`, `combo_strike_test.md`, 1,753 races 22 Aug to 3 Oct, pre-race):
      top pick wins Combo 30.7%, projection only 26.6%, RM only 29.1%, TopRate rating only 33.3%, SP fav 34.4%. Rating
      share 0.7: 33.0% (both halves), ROI -14% -> -11%, top pick = SP fav 59% -> 69%; non-fav top picks A/E pm 1.10 -> 1.18
      (projection-only disagreements are the weak ones, -23%). ADOPTED in TopRate (PR #284): Combo 0.3 proj + 0.7 rating,
      lines 4 / 8 -> 5 / 10 (same coverage: 2.51 runners / 61% of winners inside 5, 4.57 / 82% inside 10; exotic hit A/E
      unchanged); bet_log.py matches. Value stays the Racing Model's job.
    - NSW ATC sectionals feed: unreachable from GitHub-hosted runners (connect timeout; `reports/atc_probe.md`) and here;
      try the Vultr AU runner.
  - Data quirks found: store RQ GPS parquets have `tab_no` / `cum_dist_m` as strings (now coerced in
    `gps_link`, `extra_history.read_rq_sections`); TopRate results have no carried weight from 12 Sep 2026, so
    the latest races get no model output (`blend_eval` drops them and says so; `--report-only` rebuilds).
  - LightGBM runs are deterministic (`deterministic`, `force_row_wise`, fixed row order in `build_features`).
  - Caveat: history uses each past run's CURRENT WPR (TopRate revises Preliminary to Final); on race day some
    were still preliminary. Mild look-ahead the leakage test cannot catch; needs dated WPR snapshots.

## Model status (log loss, 2023-2026 walk-forward, VIC/SA/QLD; SP calibrated = 1.786)
- Per-run figure (`model/figure.py`, `validate_figure.py`): WPR + sectionals + pace (settle x early shape).
  WPR is already weight adjusted; pace is the main lift. Figure alone 1.997; SP + figure beats SP by 0.001.
- Ability (`model/ability.py`): form, trials, distance change, age/sex. 1.968 alone; adds ~0 over SP + figure.
- Jockey/trainer (`model/jt.py`): A/E vs market, strike rates, jockey change/upgrade. ~0 in a logit;
  used by the GBM through interactions.
- Market-offset GBM (`model/offset_model.py`): calibrated SP + LightGBM trees (per-race softmax).
  Tuning grid did not help (off by default).
- Race-day projection v3 (`model/projection.py`, report `reports/projection_validation.md`):
  - settle (800m position share): settle and early-speed history matched to distance / first-up / going,
    speed map, barrier (+ by track and distance), jockey/trainer forward tendency, trials, weight/claim.
    R2 0.32-0.33 (debutants 0.08-0.12, first-up 0.26-0.27); projected leader leads at the 800m 39-40%.
  - pace (race early shape) R2 0.06-0.12; ground loss (QLD GPS) R2 0.17-0.19.
  - cost in WPR (stable): leader to last -2.6; on-pace per unit early shape -0.35; -0.14 to -0.21 per metre.
  - track bias from past meetings (settle and barrier slopes; long-run + same rail within 35 days) persists
    (corr 0.2-0.3) and is calibrated; the one addition that helped (-0.0023).
  - v3 + track bias vs figure: -0.0119 (se 0.0009). With SP: -0.0015 vs SP (se 0.0005), QLD -0.0032.
  - no gain: pace x running style, a separate GPS early-position model, and track x distance barrier /
    speed map as direct win-model terms (their value comes through the settle / gl models).
- Ground loss (`ingest/gps_link.py` -> `gps_runs`): +0.21 WPR per extra metre as a figure input; adds
  nothing over SP from past runs (market prices it).
- Prices (parked): `fixed_prices_final` looks written after the jump (about SP). Git history of
  toprate_runners.csv (`tools/extract_prices_from_git.py`) gives sparse pre-jump snapshots from Apr 2026;
  model picks show large CLV there but prices may be stale dashboard values. Verify against the Vultr log.
- Data issues: RQ distance travelled at Doomben and Ipswich from 2026 no longer tracks barrier or settle
  (masked in `gps_link.SUSPECT_DIST`); 2026 ground-loss R2 falls elsewhere too. RQ `race_time_s` is about
  1.9s longer than the official time; use the winner's `time_s`.

## Next build step
Stage B: v3 projection in the market-offset GBM; QLD-only vs all-state fits on QLD races.
(VIC/SA racing.com GPS is in the store and in training: no measurable gain, `rc_gps_test.md`.)
