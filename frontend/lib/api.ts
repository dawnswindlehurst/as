/**
 * API client for Capivara Bet backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Generic fetch wrapper with error handling.
 */
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API fetch error:", error);
    throw error;
  }
}

/**
 * Game types
 */
export interface Game {
  id: number;
  game: string;
  team1: string;
  team2: string;
  start_time: string;
  tournament?: string;
  best_of: number;
  winner?: string;
  team1_score?: number;
  team2_score?: number;
  finished: boolean;
  is_live: boolean;
  odds?: Odds[];
}

export interface Odds {
  bookmaker: string;
  team1_odds?: number;
  team2_odds?: number;
  timestamp: string;
}

/**
 * Player types
 */
export interface Player {
  player_id: string;
  player_name: string;
  team?: string;
  sport?: string;
}

export interface PlayerGameLog {
  game_id: string;
  game_date: string;
  opponent: string;
  is_home: boolean;
  minutes?: number;
  points?: number;
  rebounds_total?: number;
  assists?: number;
  steals?: number;
  blocks?: number;
}

export interface PlayerPropAnalysis {
  prop_type: string;
  line: number;
  average: number;
  over_rate: number;
  under_rate: number;
  last_5_avg?: number;
  last_10_avg?: number;
  home_avg?: number;
  away_avg?: number;
}

export interface PlayerProps {
  player_id: string;
  player_name: string;
  team: string;
  props: PlayerPropAnalysis[];
  recent_games: PlayerGameLog[];
}

/**
 * Fetch games by date and filters.
 */
export async function getGames(params?: {
  date?: string;
  league?: string;
  game?: string;
}): Promise<Game[]> {
  const searchParams = new URLSearchParams();
  if (params?.date) searchParams.set("date", params.date);
  if (params?.league) searchParams.set("league", params.league);
  if (params?.game) searchParams.set("game", params.game);

  const query = searchParams.toString();
  return fetchAPI<Game[]>(`/api/games${query ? `?${query}` : ""}`);
}

/**
 * Fetch live games.
 */
export async function getLiveGames(game?: string): Promise<Game[]> {
  const searchParams = new URLSearchParams();
  if (game) searchParams.set("game", game);

  const query = searchParams.toString();
  return fetchAPI<Game[]>(`/api/games/live${query ? `?${query}` : ""}`);
}

/**
 * Fetch game by ID.
 */
export async function getGameById(gameId: number): Promise<Game> {
  return fetchAPI<Game>(`/api/games/${gameId}`);
}

/**
 * Search players.
 */
export async function searchPlayers(
  query: string,
  sport: string = "nba"
): Promise<Player[]> {
  const searchParams = new URLSearchParams({ q: query, sport });
  return fetchAPI<Player[]>(`/api/players/search?${searchParams.toString()}`);
}

/**
 * Fetch player game log.
 */
export async function getPlayerGameLog(
  playerId: string,
  limit: number = 10
): Promise<PlayerGameLog[]> {
  const searchParams = new URLSearchParams({ limit: limit.toString() });
  return fetchAPI<PlayerGameLog[]>(
    `/api/players/${playerId}/gamelog?${searchParams.toString()}`
  );
}

/**
 * Fetch player props.
 */
export async function getPlayerProps(playerId: string): Promise<PlayerProps> {
  return fetchAPI<PlayerProps>(`/api/props/${playerId}`);
}

/**
 * Health check.
 */
export async function healthCheck(): Promise<{
  status: string;
  timestamp: string;
  database: string;
  version: string;
}> {
  return fetchAPI("/api/health");
}

/**
 * Stats types
 */
export interface OverviewStats {
  total_matches: number;
  finished_matches: number;
  recent_matches: number;
  breakdown_by_game: Record<string, number>;
}

export interface TeamStats {
  team: string;
  game: string;
  matches_played: number;
  wins: number;
  losses: number;
  win_rate: number;
}

export interface Team {
  team: string;
  game: string;
  matches_played: number;
  wins: number;
  win_rate: number;
}

export interface TeamPlayer {
  player_id: string;
  player_name: string;
  team: string;
  matches_played: number;
  avg_kills: number;
  avg_deaths: number;
  avg_assists: number;
  avg_kd: number;
}

export interface PlayerMatch {
  match_id: string;
  match_date: string | null;
  tournament: string;
  opponent: string;
  won: boolean;
  kills: number | null;
  deaths: number | null;
  assists: number | null;
  kd_ratio: number | null;
  adr: number | null;
  acs: number | null;
  rating: number | null;
  agent: string | null;
  champion: string | null;
  hero: string | null;
}

export interface PlayerStats {
  player_id: string;
  player_name: string;
  team: string;
  total_matches: number;
  averages: {
    kills: number;
    deaths: number;
    assists: number;
    kd_ratio: number;
    adr: number | null;
    acs: number | null;
  };
  recent_matches: PlayerMatch[];
}

export interface RecentResult {
  id: number;
  game: string;
  tournament: string;
  match_date: string | null;
  team1: string;
  team2: string;
  team1_score: number;
  team2_score: number;
  winner: string;
  best_of: number;
}

export interface Tournament {
  tournament: string;
  game: string;
  match_count: number;
  latest_match: string | null;
}

/**
 * Get overview statistics.
 */
export async function getOverview(): Promise<OverviewStats> {
  return fetchAPI<OverviewStats>("/api/stats/overview");
}

/**
 * Get team statistics.
 */
export async function getTeamStats(game?: string): Promise<TeamStats[]> {
  const searchParams = new URLSearchParams();
  if (game) searchParams.set("game", game);

  const query = searchParams.toString();
  return fetchAPI<TeamStats[]>(`/api/stats/teams${query ? `?${query}` : ""}`);
}

/**
 * Get recent match results.
 */
export async function getRecentResults(limit?: number): Promise<RecentResult[]> {
  const searchParams = new URLSearchParams();
  if (limit) searchParams.set("limit", limit.toString());

  const query = searchParams.toString();
  return fetchAPI<RecentResult[]>(`/api/stats/recent-results${query ? `?${query}` : ""}`);
}

/**
 * Get tournaments.
 */
export async function getTournaments(game?: string): Promise<Tournament[]> {
  const searchParams = new URLSearchParams();
  if (game) searchParams.set("game", game);

  const query = searchParams.toString();
  return fetchAPI<Tournament[]>(`/api/stats/tournaments${query ? `?${query}` : ""}`);
}

/**
 * Get teams by game/sport.
 */
export async function getTeamsByGame(game: string): Promise<Team[]> {
  const searchParams = new URLSearchParams({ game });
  return fetchAPI<Team[]>(`/api/teams?${searchParams.toString()}`);
}

/**
 * Get players by team.
 */
export async function getPlayersByTeam(teamName: string): Promise<TeamPlayer[]> {
  return fetchAPI<TeamPlayer[]>(`/api/teams/${encodeURIComponent(teamName)}/players`);
}

/**
 * Get player statistics.
 */
export async function getPlayerStats(playerId: string, limit?: number): Promise<PlayerStats> {
  const searchParams = new URLSearchParams();
  if (limit) searchParams.set("limit", limit.toString());

  const query = searchParams.toString();
  return fetchAPI<PlayerStats>(`/api/players/${encodeURIComponent(playerId)}/stats${query ? `?${query}` : ""}`);
}

/**
 * Value Bets types
 */
export interface ValueBet {
  id: string;
  sport: string;
  game: string;
  league: string;
  start_time: string;
  market: string;
  selection: string;
  odds: number;
  bookmaker: string;
  model_probability: number;
  implied_probability: number;
  edge: number;
  confidence: number;
  expected_value: number;
  kelly_stake: number;
  suggested_stake: number;
  reasoning?: string;
}

export interface ValueBetsSummary {
  total_bets: number;
  by_sport: Record<string, number>;
  avg_edge: number;
  total_suggested_stake: number;
}

/**
 * Get value bets of the day.
 */
export async function getValueBets(params?: {
  sport?: string;
  min_edge?: number;
  min_confidence?: number;
}): Promise<{ value_bets: ValueBet[]; summary: ValueBetsSummary }> {
  const searchParams = new URLSearchParams();
  if (params?.sport) searchParams.set("sport", params.sport);
  if (params?.min_edge !== undefined) searchParams.set("min_edge", params.min_edge.toString());
  if (params?.min_confidence !== undefined) searchParams.set("min_confidence", params.min_confidence.toString());

  const query = searchParams.toString();
  return fetchAPI<{ value_bets: ValueBet[]; summary: ValueBetsSummary }>(
    `/api/value-bets${query ? `?${query}` : ""}`
  );
}

/**
 * Validation types
 */
export interface PeriodInfo {
  start: string;
  end: string;
  days: number;
}

export interface OverallMetrics {
  total_bets: number;
  wins: number;
  losses: number;
  win_rate: number;
  roi: number;
  profit: number;
  total_wagered: number;
  avg_odds: number;
  clv_average: number;
  sharpe_ratio: number;
  max_drawdown: number;
}

export interface SportMetrics {
  sport: string;
  name: string;
  icon: string;
  total_bets: number;
  wins: number;
  win_rate: number;
  roi: number;
  profit: number;
  clv_average: number;
  rank: number;
}

export interface MarketMetrics {
  market: string;
  name: string;
  total_bets: number;
  wins: number;
  win_rate: number;
  roi: number;
  rank: number;
}

export interface EquityPoint {
  date: string;
  bankroll: number;
  profit: number;
}

export interface CalibrationMetrics {
  brier_score: number;
  calibration_error: number;
  overround_beat_rate: number;
}

export interface Insight {
  type: "success" | "warning" | "info" | "danger";
  title: string;
  message: string;
}

export interface ValidationMetrics {
  period: PeriodInfo;
  overall: OverallMetrics;
  by_sport: SportMetrics[];
  by_market: MarketMetrics[];
  equity_curve: EquityPoint[];
  calibration: CalibrationMetrics;
  insights: Insight[];
}

/**
 * Get validation metrics for paper trading.
 */
export async function getValidationMetrics(days?: number): Promise<ValidationMetrics> {
  const searchParams = new URLSearchParams();
  if (days !== undefined) searchParams.set("days", days.toString());

  const query = searchParams.toString();
  return fetchAPI<ValidationMetrics>(`/api/validation/metrics${query ? `?${query}` : ""}`);
}

