"""SQL functions for calculating player stats and fantasy points"""

# This will be used to generate SQL migrations
RECALC_PLAYER_WEEK_STATS_SQL = """
CREATE OR REPLACE FUNCTION public.recalc_player_week_stats(p_season INT, p_week INT)
RETURNS VOID AS $$
WITH plays AS (
  SELECT
    (raw->>'season')::int AS season,
    (raw->>'week')::int AS week,
    raw
  FROM pbp_raw
  WHERE season = p_season AND week = p_week
),
recv AS (
  -- Receptions & receiving yards per receiver
  SELECT
    raw->>'receiver_player_id' AS pid,
    COUNT(*) FILTER (WHERE (raw->>'complete_pass')::int = 1) AS receptions,
    COUNT(*) FILTER (WHERE (raw->>'pass_attempt')::int = 1) AS targets,
    COALESCE(SUM((raw->>'receiving_yards')::int), 0) AS rec_yds,
    COUNT(*) FILTER (WHERE (raw->>'pass_touchdown')::int = 1) AS rec_td
  FROM plays
  WHERE raw ? 'receiver_player_id'
  GROUP BY 1
),
pass AS (
  -- Passing stats per passer
  SELECT
    raw->>'passer_player_id' AS pid,
    COUNT(*) FILTER (WHERE (raw->>'pass_attempt')::int = 1) AS att,
    COUNT(*) FILTER (WHERE (raw->>'complete_pass')::int = 1) AS cmp,
    COALESCE(SUM((raw->>'passing_yards')::int), 0) AS pass_yds,
    COUNT(*) FILTER (WHERE (raw->>'pass_touchdown')::int = 1) AS pass_td,
    COUNT(*) FILTER (WHERE (raw->>'interception')::int = 1) AS ints
  FROM plays
  WHERE raw ? 'passer_player_id'
  GROUP BY 1
),
rush AS (
  -- Rushing stats per rusher
  SELECT
    raw->>'rusher_player_id' AS pid,
    COUNT(*) FILTER (WHERE (raw->>'rush_attempt')::int = 1) AS ra,
    COALESCE(SUM((raw->>'rushing_yards')::int), 0) AS rush_yds,
    COUNT(*) FILTER (WHERE (raw->>'rush_touchdown')::int = 1) AS rush_td
  FROM plays
  WHERE raw ? 'rusher_player_id'
  GROUP BY 1
),
misc AS (
  -- Misc stats (fumbles, 2pt, etc.)
  SELECT
    COALESCE(raw->>'rusher_player_id', raw->>'receiver_player_id', raw->>'passer_player_id') AS pid,
    COUNT(*) FILTER (WHERE (raw->>'fumble_lost')::int = 1) AS fumbles_lost,
    COUNT(*) FILTER (WHERE (raw->>'two_point_attempt')::int = 1 AND (raw->>'two_point_conv_result')::int = 1) AS two_pt,
    COUNT(*) FILTER (WHERE (raw->>'return_touchdown')::int = 1) AS return_td
  FROM plays
  GROUP BY 1
),
unioned AS (
  SELECT pid FROM recv
  UNION SELECT pid FROM pass
  UNION SELECT pid FROM rush
  UNION SELECT pid FROM misc
  WHERE pid IS NOT NULL
)
INSERT INTO player_week_stats (
  player_id, season, week,
  pass_attempts, pass_completions, passing_yards, pass_td, interceptions,
  rush_attempts, rushing_yards, rush_td,
  targets, receptions, receiving_yards, rec_td,
  fumbles_lost, two_pt_conv, return_td,
  created_at, updated_at, source
)
SELECT
  p.id,
  p_season, p_week,
  COALESCE(pass.att, 0), COALESCE(pass.cmp, 0), COALESCE(pass.pass_yds, 0), 
  COALESCE(pass.pass_td, 0), COALESCE(pass.ints, 0),
  COALESCE(rush.ra, 0), COALESCE(rush.rush_yds, 0), COALESCE(rush.rush_td, 0),
  COALESCE(recv.targets, 0), COALESCE(recv.receptions, 0), 
  COALESCE(recv.rec_yds, 0), COALESCE(recv.rec_td, 0),
  COALESCE(misc.fumbles_lost, 0), COALESCE(misc.two_pt, 0), COALESCE(misc.return_td, 0),
  NOW(), NOW(), 'nflfastr'
FROM unioned u
JOIN player p ON p.nfl_player_id = u.pid
LEFT JOIN pass ON pass.pid = u.pid
LEFT JOIN recv ON recv.pid = u.pid
LEFT JOIN rush ON rush.pid = u.pid
LEFT JOIN misc ON misc.pid = u.pid
ON CONFLICT (player_id, season, week, source) 
DO UPDATE SET
  pass_attempts = EXCLUDED.pass_attempts,
  pass_completions = EXCLUDED.pass_completions,
  passing_yards = EXCLUDED.passing_yards,
  pass_td = EXCLUDED.pass_td,
  interceptions = EXCLUDED.interceptions,
  rush_attempts = EXCLUDED.rush_attempts,
  rushing_yards = EXCLUDED.rushing_yards,
  rush_td = EXCLUDED.rush_td,
  targets = EXCLUDED.targets,
  receptions = EXCLUDED.receptions,
  receiving_yards = EXCLUDED.receiving_yards,
  rec_td = EXCLUDED.rec_td,
  fumbles_lost = EXCLUDED.fumbles_lost,
  two_pt_conv = EXCLUDED.two_pt_conv,
  return_td = EXCLUDED.return_td,
  updated_at = EXCLUDED.updated_at;
$$ LANGUAGE sql;
"""

RECALC_PLAYER_WEEK_POINTS_SQL = """
CREATE OR REPLACE FUNCTION public.recalc_player_week_points(p_season INT, p_week INT)
RETURNS VOID AS $$
INSERT INTO player_week_points (
  player_id, season, week, 
  std_points, half_ppr_points, ppr_points,
  points_breakdown, created_at, updated_at, source
)
SELECT 
  s.player_id, s.season, s.week,
  -- Standard scoring
  ROUND(
    (s.passing_yards * 0.04) + 
    (s.pass_td * 4) + 
    (s.interceptions * -2) +
    (s.rushing_yards * 0.1) + 
    (s.rush_td * 6) +
    (s.receiving_yards * 0.1) + 
    (s.rec_td * 6) +
    (s.two_pt_conv * 2) +
    (s.return_td * 6) +
    (s.fumbles_lost * -2), 2
  ) AS std_points,
  
  -- Half-PPR scoring
  ROUND(
    (s.passing_yards * 0.04) + 
    (s.pass_td * 4) + 
    (s.interceptions * -2) +
    (s.rushing_yards * 0.1) + 
    (s.rush_td * 6) +
    (s.receiving_yards * 0.1) + 
    (s.rec_td * 6) +
    (s.receptions * 0.5) +
    (s.two_pt_conv * 2) +
    (s.return_td * 6) +
    (s.fumbles_lost * -2), 2
  ) AS half_ppr_points,
  
  -- Full PPR scoring
  ROUND(
    (s.passing_yards * 0.04) + 
    (s.pass_td * 4) + 
    (s.interceptions * -2) +
    (s.rushing_yards * 0.1) + 
    (s.rush_td * 6) +
    (s.receiving_yards * 0.1) + 
    (s.rec_td * 6) +
    (s.receptions * 1.0) +
    (s.two_pt_conv * 2) +
    (s.return_td * 6) +
    (s.fumbles_lost * -2), 2
  ) AS ppr_points,
  
  -- Breakdown for debugging
  jsonb_build_object(
    'passing_yards', s.passing_yards,
    'pass_td', s.pass_td,
    'interceptions', s.interceptions,
    'rushing_yards', s.rushing_yards,
    'rush_td', s.rush_td,
    'receiving_yards', s.receiving_yards,
    'rec_td', s.rec_td,
    'receptions', s.receptions,
    'two_pt_conv', s.two_pt_conv,
    'return_td', s.return_td,
    'fumbles_lost', s.fumbles_lost
  ) AS points_breakdown,
  
  NOW(), NOW(), 'nflfastr'
  
FROM player_week_stats s
WHERE s.season = p_season AND s.week = p_week
ON CONFLICT (player_id, season, week, source) 
DO UPDATE SET
  std_points = EXCLUDED.std_points,
  half_ppr_points = EXCLUDED.half_ppr_points,
  ppr_points = EXCLUDED.ppr_points,
  points_breakdown = EXCLUDED.points_breakdown,
  updated_at = EXCLUDED.updated_at;
$$ LANGUAGE sql;
"""

CREATE_MATERIALIZED_VIEW_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS v_player_week_scoring AS
SELECT
  p.id AS player_id, 
  p.name AS player_name, 
  p.player_position,
  t.abbreviation AS team,
  s.season, 
  s.week,
  s.pass_attempts, 
  s.pass_completions, 
  s.passing_yards, 
  s.pass_td, 
  s.interceptions,
  s.rush_attempts, 
  s.rushing_yards, 
  s.rush_td,
  s.targets, 
  s.receptions, 
  s.receiving_yards, 
  s.rec_td,
  s.fumbles_lost,
  s.two_pt_conv,
  s.return_td,
  pwp.std_points, 
  pwp.half_ppr_points, 
  pwp.ppr_points
FROM player_week_stats s
JOIN player p ON p.id = s.player_id
LEFT JOIN team t ON t.id = p.team_id
JOIN player_week_points pwp ON pwp.player_id = s.player_id 
  AND pwp.season = s.season 
  AND pwp.week = s.week
  AND pwp.source = s.source;

CREATE INDEX IF NOT EXISTS v_pws_idx ON v_player_week_scoring (season, week, player_id);
"""
