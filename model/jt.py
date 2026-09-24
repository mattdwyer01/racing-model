"""Jockey / trainer / horse market-relative form (pre-race, windows end the day before).

For each entity over a trailing window: starts n, wins w, and market-expected wins e
(sum of SP-implied probabilities, normalised within the race). Features:
    *_ae    log((w + 3) / (e + 3))     wins vs market expectation, shrunk (A/E)
    *_sr    (w + 1) / (n + 10)         strike rate, shrunk
    jockey 365d, jockey 90d, trainer 365d, jockey+trainer combo 730d,
    trainer first-up A/E 730d (applied only when today is first up),
    horse A/E over its career (prior starts),
    jockey change since last start and jockey upgrade (jockey 365d sr now minus the last-start jockey's then).
"""
import duckdb

SQL = """
create or replace temp table jt_base as
select r.run_id, r.horse_id, r.race_date, r.jockey, r.trainer, r.prep_run,
  r.res_won::int won,
  case when r.sp > 1 then (1 / r.sp) / sum(case when r.sp > 1 then 1 / r.sp end) over (partition by r.race_id) end p
from runs r where not r.is_trial_or_jumpout;

create or replace temp table jt_feat as
select run_id, horse_id, race_date, jockey, prep_run,
  -- jockey 365d
  count(p)  over j365 j_n, sum(won * (p is not null)::int) over j365 j_w, sum(p) over j365 j_e,
  count(p)  over j90 j90_n, sum(won * (p is not null)::int) over j90 j90_w, sum(p) over j90 j90_e,
  count(p)  over t365 t_n, sum(won * (p is not null)::int) over t365 t_w, sum(p) over t365 t_e,
  count(p)  over c730 c_n, sum(won * (p is not null)::int) over c730 c_w, sum(p) over c730 c_e,
  sum(case when prep_run = 1 then won * (p is not null)::int end) over t730 tfu_w,
  sum(case when prep_run = 1 then p end) over t730 tfu_e,
  sum(won * (p is not null)::int) over hw h_w, sum(p) over hw h_e,
  lag(jockey) over h1 last_jockey
from jt_base
window j365 as (partition by jockey order by race_date range between interval 365 days preceding and interval 1 day preceding),
       j90  as (partition by jockey order by race_date range between interval 90 days preceding and interval 1 day preceding),
       t365 as (partition by trainer order by race_date range between interval 365 days preceding and interval 1 day preceding),
       t730 as (partition by trainer order by race_date range between interval 730 days preceding and interval 1 day preceding),
       c730 as (partition by jockey, trainer order by race_date range between interval 730 days preceding and interval 1 day preceding),
       hw   as (partition by horse_id order by race_date range between unbounded preceding and interval 1 day preceding),
       h1   as (partition by horse_id order by race_date, run_id);

create or replace temp table jt_out as
select run_id,
  ln((coalesce(j_w,0) + 3) / (coalesce(j_e,0) + 3)) j_ae,
  (coalesce(j_w,0) + 1) / (coalesce(j_n,0) + 10) j_sr,
  ln((coalesce(j90_w,0) + 3) / (coalesce(j90_e,0) + 3)) j90_ae,
  ln((coalesce(t_w,0) + 3) / (coalesce(t_e,0) + 3)) t_ae,
  (coalesce(t_w,0) + 1) / (coalesce(t_n,0) + 10) t_sr,
  ln((coalesce(c_w,0) + 3) / (coalesce(c_e,0) + 3)) c_ae,
  case when prep_run = 1 then ln((coalesce(tfu_w,0) + 3) / (coalesce(tfu_e,0) + 3)) else 0 end tfu_ae,
  ln((coalesce(h_w,0) + 3) / (coalesce(h_e,0) + 3)) h_ae,
  (last_jockey is not null and last_jockey <> jockey)::int j_change,
  case when last_jockey is null then 0
       else (coalesce(j_w,0) + 1) / (coalesce(j_n,0) + 10)
            - lag((coalesce(j_w,0) + 1) / (coalesce(j_n,0) + 10)) over (partition by horse_id order by race_date, run_id)
  end j_upgrade
from jt_feat;
"""
COLS = ["j_ae", "j_sr", "j90_ae", "t_ae", "t_sr", "c_ae", "tfu_ae", "h_ae", "j_change", "j_upgrade"]


def features(con):
    con.execute(SQL)
    return con.sql("select * from jt_out").df()


if __name__ == "__main__":
    import time
    from pathlib import Path
    t = time.time()
    con = duckdb.connect(str(Path(__file__).resolve().parents[1] / "data/db/racing.duckdb"), read_only=True)
    f = features(con)
    print(len(f), f"{time.time() - t:.0f}s")
    print(f[COLS].describe().T.round(3))
