"""Build the core tables from raw TopRate yearly files.

    python ingest/build_core.py

Tables written to data/db/racing.duckdb:
    tr_raw   raw union of every yearly file (untouched)
    tracks   track -> venue, state, location class, surface, in_scope (from ingest/tracks.csv)
    races    one row per race (races and trials)
    runs     one row per runner per race, with pre-race history fields; upcoming races from the dashboard
             runners file (not yet in the results files) are included with every res_ field null
    gps_runs GPS ground loss and rail distance per run (see ingest/gps_link.py), if GPS files present

Column naming in `runs`:
    no prefix   known before the race (safe to use as a model input)
    res_        the result or anything measured in the race (never a same-race input)
"""
from pathlib import Path

import duckdb

try:
    from ingest import gps_link
except ImportError:   # run as a script: python ingest/build_core.py
    import gps_link

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/db/racing.duckdb"
RAW = ROOT / "data/raw/toprate/*.csv.gz"
TRACKS = ROOT / "ingest/tracks.csv"

SPELL_DAYS = 60          # a gap this long or longer starts a new preparation
FULL_COVERAGE_FROM = "2022-01-01"   # TopRate covers ~all AU races from here; earlier years are partial

SQL = f"""
create or replace table tr_raw as
select *, regexp_extract(filename, 'race_results_(\\d{{4}})', 1)::int as src_year
from read_csv('{RAW}', union_by_name = true, filename = true, sample_size = -1);

create or replace table tracks as select * from read_csv('{TRACKS}');
"""

TABLE_SQL = f"""
-- ------------------------------------------------------------------ races
create or replace table races as
with r as (
  select
    race_id, any_value(meeting_id) meeting_id, any_value(date)::date race_date,
    any_value(track) track, any_value(venue) venue,
    any_value(distance) distance, any_value(field_size) field_size,
    any_value(race_class) race_class, any_value(blackType) black_type,
    any_value(weight_restriction) weight_type, any_value(age_restriction) age_restriction,
    any_value(jockey_restriction) jockey_restriction,
    any_value(going) going, any_value(trackGrading) going_num,
    any_value(rail_position) rail_text,
    nullif(any_value(winners_time), 0) res_winners_time_s,
    any_value(sect_ld_early) res_leader_early_rating,
    any_value(raceShapeEarly) res_shape_early, any_value(raceShapeMid) res_shape_mid,
    any_value(raceShapeLate) res_shape_late,
    bool_or(isBarrierTrial) is_trial, bool_or(is_jumpout) is_jumpout
  from tr_raw group by race_id
)
select r.*,
  t.state, t.location_class, t.in_scope,
  case when r.going in ('Synthetic','Sand','Dirt') then r.going else coalesce(t.surface,'Turf') end surface,
  -- class parsing
  case when race_class like 'BM%' then 'BM' when race_class like 'CLS%' then 'CLS'
       when race_class like 'RST%' then 'RST' when race_class = 'MAI' then 'MDN'
       when race_class like 'R_MW%' then 'RMW' when race_class = 'OPEN' then 'OPEN'
       else race_class end class_type,
  try_cast(regexp_extract(race_class, '(\\d+)', 1) as int) class_level,
  race_class like '%+' class_plus,
  -- rail: first offset quoted (metres out from true); 0 when true
  case when rail_text ilike 'true%' or rail_text ilike 'normal%' then 0.0
       else try_cast(regexp_extract(rail_text, '(?i)(\\d+(?:\\.\\d+)?)\\s*(?:m\\b|metre|meter|m )', 1) as double) end rail_m,
  regexp_matches(rail_text, '(?i)remainder|cutaway|wp|winning post|\\d+m-\\d+m') rail_varies,
  r.race_date >= date '{FULL_COVERAGE_FROM}' full_coverage
from r left join tracks t using (track);

-- ------------------------------------------------------------------ runs
create or replace table runs as
with base as (
  select
    run_id, race_id, horse_id, horse, date::date race_date,
    isBarrierTrial or is_jumpout is_trial_or_jumpout,
    barrier, weightCarried weight_kg, weight_adjustment weight_claim_kg,
    jockey, trainer, horse_age age, horse_sex sex, sire_id, sire, dam_id, dam, sire_country, dam_country,
    priceStarting sp, price_top top_fluc,
    -- results
    positionFinish res_finish, positionFinish is null res_dnf,
    case when marginFinish >= 99 then null when marginFinish < 0 then 0 else marginFinish end res_margin_l,
    case when marginFinish < 0 then -marginFinish end res_win_margin_l,
    positionFinish = 1 res_won,
    position800m res_pos800, position600m res_pos600, position400m res_pos400, position200m res_pos200,
    margin800m res_marg800, margin600m res_marg600, margin400m res_marg400, margin200m res_marg200,
    sect_i_time res_s_time, sect_i_early res_s_early, sect_i_to600 res_s_to600, sect_i_to800 res_s_to800,
    sect_i_800_600 res_s_800_600, sect_i_600_400 res_s_600_400, sect_i_400_200 res_s_400_200,
    sect_i_l200 res_s_l200, sect_i_l400 res_s_l400, sect_i_l600 res_s_l600, sect_i_l800 res_s_l800,
    sect_i_800_400 res_s_800_400,
    wpr res_wpr, wprStatus res_wpr_status, atw res_atw,
    comments_steward res_stewards, comments_video res_video
  from tr_raw
),
-- history is built over race starts only (trials are tracked separately below)
starts as (
  select b.*,
    lag(race_date) over w prev_start_date,
    lag(res_wpr)   over w prev_wpr,
    lag(race_id)   over w prev_race_id,
    row_number()   over w - 1 career_starts_in_data
  from base b where not is_trial_or_jumpout
  window w as (partition by horse_id order by race_date, run_id)
),
starts2 as (
  select *, (race_date - prev_start_date) days_since_start,
    sum(case when prev_start_date is null or race_date - prev_start_date >= {SPELL_DAYS} then 1 else 0 end)
      over (partition by horse_id order by race_date, run_id) prep_no
  from starts
),
starts3 as (
  select *, row_number() over (partition by horse_id, prep_no order by race_date, run_id) prep_run
  from starts2
),
trials as (
  select horse_id, race_date trial_date from base where is_trial_or_jumpout
)
select s.* exclude (prep_no),
  (select count(*) from trials t where t.horse_id = s.horse_id
     and t.trial_date < s.race_date and t.trial_date > coalesce(s.prev_start_date, date '1900-01-01')) trials_since_last_start,
  (select max(trial_date) from trials t where t.horse_id = s.horse_id and t.trial_date < s.race_date) last_trial_date
from starts3 s

union all by name

select b.*, null prev_start_date, null prev_wpr, null prev_race_id, null career_starts_in_data,
  null days_since_start, null prep_run, null trials_since_last_start, null last_trial_date
from base b where is_trial_or_jumpout;
"""


LIVE = ROOT / "data/raw/live/toprate_runners.csv"   # copy of the TopRate dashboard's runners file

LIVE_SQL = f"""
create or replace table live_runners as
select * from read_csv('{LIVE}', sample_size = -1);

-- race number and start time for every race the dashboard has seen (Apr 2026 onward)
create or replace table race_times as
select race_id, any_value(race) race_no, min(start_time)::timestamptz start_utc
from live_runners where race_id is not null group by race_id;

-- near-jump fixed price for backtesting (last value the dashboard captured before the result)
create or replace table fixed_prices_final as
select run_id, race_id, fixed_win_price, open_price, starting_price_sp, scratched
from live_runners where run_id is not null;
"""


# Upcoming and recently run races: in the dashboard runners file but not yet in the results files (TopRate's
# results backfill runs by hand, so the runners file is days ahead). Recent races carry provisional results from
# the runners file (finish, margin, WPR, SP, comments; no in-running positions or sectionals). Mapped to the results-file
# columns (class names to TopRate codes; track = the venue's usual track, or its synthetic track when the going
# is Synthetic; age / sex / breeding from the horse's latest results row). Scratched runners are left out.
# toprate.au stopped supplying weights (results from 12 Sep 2026). TopRate's poller now fills the runners file's
# weight_carried from TAB race cards (TopRate tab_fields.py): copy it into resulted rows that have none.
WEIGHT_FILL_SQL = """
update tr_raw set weightCarried = l.weight_carried
from (select run_id, max(try_cast(weight_carried as double)) weight_carried from live_runners
      where try_cast(weight_carried as double) is not null group by run_id) l
where tr_raw.weightCarried is null and tr_raw.run_id = l.run_id;
"""

UPCOMING_SQL = """
create or replace temp table _venue_track as
select venue, arg_max(track, n + case when track = venue then 1e9 else 0 end) track, arg_max(track, case when going in ('Synthetic','Sand','Dirt') then n end) synth_track
from (select venue, track, going, count(*) n from tr_raw where src_year >= 2024 group by all) group by venue;

create or replace temp table _horse as
select horse_id, arg_max(horse_age, date) horse_age, max(date) last_date, arg_max(horse_sex, date) horse_sex,
  arg_max(sire_id, date) sire_id, arg_max(sire, date) sire, arg_max(dam_id, date) dam_id, arg_max(dam, date) dam,
  arg_max(sire_country, date) sire_country, arg_max(dam_country, date) dam_country
from tr_raw group by horse_id;

insert into tr_raw by name
select l.race_id, l.run_id, l.horse_id::bigint horse_id, l.horse, l.date::timestamp date, l.venue,
  case when l.going in ('Synthetic','Sand','Dirt') then coalesce(v.synth_track, v.track, l.venue)
       else coalesce(v.track, l.venue) end track,
  l.race raceNumber, l.distance, l.going, l.track_grading trackGrading, l.rail_position, l.race_name,
  case when l.race_class = 'Maiden' then 'MAI' when l.race_class = 'Open' then 'OPEN'
       when l.race_class like 'Benchmark %' then 'BM' || regexp_extract(l.race_class, 'Benchmark (\\d+\\+?)', 1)
       when l.race_class like 'Class %' then 'CLS' || regexp_extract(l.race_class, 'Class (\\w+)', 1)
       when regexp_matches(l.race_class, '^Restricted \\d+$') then 'RST' || regexp_extract(l.race_class, '(\\d+)', 1)
       when l.race_class like 'Restricted % Metro Wins Last Year' then 'R' || regexp_extract(l.race_class, '(\\d+)', 1) || 'MWLY'
       when l.race_class like 'Restricted % Metro Wins' then 'R' || regexp_extract(l.race_class, '(\\d+)', 1) || 'MW'
       else upper(l.race_class) end race_class,
  nullif(l.barrier, 0) barrier, try_cast(l.weight_carried as double) weightCarried, l.jockey, l.trainer,
  h.horse_age + coalesce(year(l.date::date) - year(h.last_date), 0) horse_age, h.horse_sex,
  h.sire_id, h.sire, h.dam_id, h.dam, h.sire_country, h.dam_country,
  count(*) over (partition by l.race_id) field_size,
  case when l.resulted = 1 then l.finish_position end positionFinish,
  case when l.resulted = 1 then l.margin_finish end marginFinish,
  case when l.resulted = 1 then l.wpr_actual end wpr, case when l.resulted = 1 then 'Provisional' end wprStatus,
  case when l.resulted = 1 then l.starting_price_sp end priceStarting,
  case when l.resulted = 1 then l.comments_steward end comments_steward,
  case when l.resulted = 1 then l.comments_video end comments_video,
  false isBarrierTrial, false is_jumpout, year(l.date::date) src_year
from live_runners l
left join _venue_track v on v.venue = l.venue
left join _horse h on h.horse_id = l.horse_id::bigint
where l.race_id is not null and l.run_id is not null and coalesce(l.scratched, 0) = 0
  and l.race_id not in (select distinct race_id from tr_raw);
"""


def build(db=DB):
    Path(db).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db))
    con.execute(SQL)
    if LIVE.exists():
        con.execute(LIVE_SQL)
        con.execute(UPCOMING_SQL)
        con.execute(WEIGHT_FILL_SQL)
    con.execute(TABLE_SQL)
    gps_link.build(con)   # table gps_runs, when GPS parquets are in data/interim
    return con


if __name__ == "__main__":
    con = build()
    for t in [r[0] for r in con.sql("show tables").fetchall()]:
        print(t, con.sql(f"select count(*) from {t}").fetchone()[0])
