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
