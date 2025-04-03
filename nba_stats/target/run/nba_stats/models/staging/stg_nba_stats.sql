
  create or replace   view MASTER.STAGE.stg_nba_stats
  
   as (
    select * from MASTER.STAGE.nba_stats
  );

