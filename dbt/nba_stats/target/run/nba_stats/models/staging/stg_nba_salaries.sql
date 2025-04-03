
  create or replace   view MASTER.STAGE.stg_nba_salaries
  
   as (
    select * from MASTER.STAGE.salaries
  );

