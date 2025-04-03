
  create or replace   view MASTER.STAGE.nba_stats
  
   as (
    select * from MASTER.STAGE.salaries
  );

