with stats as (
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
	from {{ source('nba', 'nba_stats') }}
	where year = year(current_date)
	QUALIFY ROW_NUMBER() OVER (PARTITION BY player, year ORDER BY team) = 1
),
salaries as (
	select player,
	CAST(replace(replace("2024-25",'$',''),',','') AS FLOAT) as salary,
	from {{ source('nba', 'salaries') }}
	where player is not null
	QUALIFY ROW_NUMBER() OVER (PARTITION BY player ORDER BY "2024-25") = 1
)

select
	stats.player,
	stats.age,
	stats.team,
	stats.pos,
	stats.mpg,
	stats.ppg,
	stats.rpg,
	stats.apg,
	stats.spg,
	stats.bpg,
	stats.topg,
	stats."FG%",
	stats."3P%",
	stats."FT%",
	salaries.salary
from stats
left join salaries
on stats.player = salaries.player