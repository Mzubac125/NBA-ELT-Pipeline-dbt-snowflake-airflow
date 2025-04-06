create table master.stage.salaries(
    Player STRING,
    Team STRING,
    "2024-25" STRING,
    "2025-26" STRING,
    "2026-27" STRING,
    "2027-28" STRING,
    "2028-29" STRING,
    "2029-30" STRING,
    Guaranteed STRING
);

CREATE TABLE master.stage.nba_stats (
    Player STRING,
    Age INT,
    Team STRING,
    Pos STRING,
    G INT,
    GS INT,
    MP DECIMAL(5,1),
    FG INT,
    FGA INT,
    "FG%" DECIMAL(5,3),
    "3P" INT,
    "3PA" INT,
    "3P%" DECIMAL(5,3),
    "2P" INT,
    "2PA" INT,
    "2P%" DECIMAL(5,3),
    "eFG%" DECIMAL(5,3),
    FT INT,
    FTA INT,
    "FT%" DECIMAL(5,3),
    ORB INT,
    DRB INT,
    TRB INT,
    AST INT,
    STL INT,
    BLK INT,
    TOV INT,
    PF INT,
    PTS INT,
    Trp_Dbl INT,
    Awards STRING,
    Year INT
);

drop table master.prod.salaries;
create schema master.prod;

CREATE STAGE master.stage.nba_stats_stage
  URL = 'azure://nbastorage.blob.core.windows.net/nbastorage'
  CREDENTIALS = (AZURE_SAS_TOKEN = 'sp=racwdlmeo&st=2025-03-27T14:40:37Z&se=2025-05-29T22:40:37Z&spr=https&sv=2024-11-04&sr=c&sig=Ro3t4ytg8QHSwlzGPrdOY%2BicQq6OnljduGMdUqxmmBo%3D')
  FILE_FORMAT = (TYPE = 'CSV', FIELD_OPTIONALLY_ENCLOSED_BY = '"', SKIP_HEADER = 1);

CREATE OR REPLACE FILE FORMAT parquet_format
  TYPE = 'PARQUET';
ALTER STAGE nba_stats_stage
  SET FILE_FORMAT = parquet_format;

LIST @master.stage.nba_stats_stage;
  
select * from master.stage.nba_stats;

select * from master.stage.factplayer;

SHOW TABLES IN MASTER.STAGE;

select * from(select player, team, row_number() OVER (partition by player order by player) rn from master.stage.salaries) where rn > 1;

select * from master.stage.salaries
where player = 'Marcus Bagley';

select player,
	CAST(replace(replace("2024-25",'$',''),',','') AS FLOAT) as salary,
	from master.stage.salaries
	QUALIFY ROW_NUMBER() OVER (PARTITION BY player ORDER BY "2024-25" desc) = 1;

select * from 
(select player,team,row_number() OVER (Partition by player order by player) rn from master.stage.nba_stats where year = 2025) 
where rn > 1;

select * from master.stage.nba_stats
where player = 'Dorian Finney-Smith'
and year = 2025;

select x.*,
case when t.player is null then x.team
else t.team
end as team
from master.stage.nba_stats x
left join 
(select player, team 
from master.stage.nba_stats
where team = '2TM'
and year = 2025) t
on x.player = t.player
where x.player = 'Dorian Finney-Smith'
and year = 2025;


SELECT 
    player,
    pts,
    CASE 
        WHEN COUNT(DISTINCT team) OVER (PARTITION BY player, year) > 1 THEN '2TM'
        ELSE team
    END AS final_team
FROM master.stage.nba_stats
WHERE year = 2025
AND player = 'Dorian Finney-Smith'
QUALIFY ROW_NUMBER() OVER (PARTITION BY player, year ORDER BY team) = 1;  

select player,
	age,
	CASE 
        WHEN COUNT(DISTINCT team) OVER (PARTITION BY player, year) > 1 THEN '2TM'
        ELSE team
    END AS team,
	pos,
	round(mp/g,1) as mpg,
	round(pts/g,1) as ppg,
	round(trb/g,1) as rpg,
	round(ast/g,1) as apg,
	round(stl/g,1) as spg,
	round(blk/g,1) as bpg,
	round(tov/g,1) as topg,
	"FG%",
	"3P%",
	"FT%"
	from master.stage.nba_stats
	where year = year(current_date)
	QUALIFY ROW_NUMBER() OVER (PARTITION BY player, year ORDER BY team) = 1;-- Keep only one row per player
