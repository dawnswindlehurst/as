"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import GameCard from "@/components/GameCard";
import { getSportIcon, SPORTS } from "@/lib/sports";
import { 
  getGames, 
  getLiveGames, 
  getOverview,
  getTeamStats,
  getRecentResults,
  getTournaments,
  Game,
  OverviewStats,
  TeamStats,
  RecentResult,
  Tournament
} from "@/lib/api";

export default function Home() {
  const [todayGames, setTodayGames] = useState<Game[]>([]);
  const [liveGames, setLiveGames] = useState<Game[]>([]);
  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [teamStats, setTeamStats] = useState<TeamStats[]>([]);
  const [recentResults, setRecentResults] = useState<RecentResult[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch today's games
        const today = new Date().toISOString().split("T")[0];
        const games = await getGames({ date: today });
        setTodayGames(games);

        // Fetch live games
        const live = await getLiveGames();
        setLiveGames(live);

        // Fetch stats
        try {
          const overviewData = await getOverview();
          setOverview(overviewData);
          
          const teams = await getTeamStats();
          setTeamStats(teams);
          
          const results = await getRecentResults(10);
          setRecentResults(results);
          
          const tournamentsData = await getTournaments();
          setTournaments(tournamentsData);
        } catch (statsError) {
          console.error("Error fetching stats:", statsError);
        }
      } catch (error) {
        console.error("Error fetching games:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getGameIcon = (game: string) => {
    return getSportIcon(game.toLowerCase());
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">
          Bem-vindo ao Capivara Bet - Sistema de análise de apostas em esports
        </p>
      </div>

      {/* Live Games Section */}
      {liveGames.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-2xl font-bold text-white">Jogos ao Vivo</h2>
            <Badge variant="destructive" className="animate-pulse">
              {liveGames.length} LIVE
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {liveGames.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        </div>
      )}

      {/* Overview Stats */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Visão Geral</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Total de Partidas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {overview?.total_matches || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">
                {overview?.finished_matches || 0} finalizadas
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Últimos 7 dias
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-500">
                {overview?.recent_matches || 0}
              </div>
              <p className="text-xs text-slate-500 mt-1">partidas recentes</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Jogos Hoje
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-500">
                {todayGames.length}
              </div>
              <p className="text-xs text-slate-500 mt-1">agendados</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium text-slate-400">
                Jogos ao Vivo
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">
                {liveGames.length}
              </div>
              <p className="text-xs text-slate-500 mt-1">em andamento</p>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Game Breakdown */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white mb-4">Por Jogo</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {SPORTS.map((sport) => {
            const count = overview?.breakdown_by_game?.[sport.id] || 0;
            return (
              <Card key={sport.id}>
                <CardContent className="py-6">
                  <div className="text-center">
                    <div className="text-4xl mb-2">{sport.icon}</div>
                    <div className="text-2xl font-bold text-white">{count}</div>
                    <p className="text-sm text-slate-400">{sport.name}</p>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Recent Results */}
      {recentResults.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Últimos Resultados</h2>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-slate-700">
                    <tr>
                      <th className="text-left p-4 text-slate-400 font-medium">Jogo</th>
                      <th className="text-left p-4 text-slate-400 font-medium">Torneio</th>
                      <th className="text-left p-4 text-slate-400 font-medium">Partida</th>
                      <th className="text-center p-4 text-slate-400 font-medium">Placar</th>
                      <th className="text-left p-4 text-slate-400 font-medium">Vencedor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentResults.map((result) => (
                      <tr key={result.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="p-4">
                          <Badge variant="outline" className="capitalize">
                            {getGameIcon(result.game)} {result.game}
                          </Badge>
                        </td>
                        <td className="p-4 text-slate-300 text-sm max-w-xs truncate">
                          {result.tournament}
                        </td>
                        <td className="p-4 text-slate-300">
                          <div className="flex flex-col gap-1">
                            <span className={result.winner === result.team1 ? "font-bold text-white" : ""}>
                              {result.team1}
                            </span>
                            <span className={result.winner === result.team2 ? "font-bold text-white" : ""}>
                              {result.team2}
                            </span>
                          </div>
                        </td>
                        <td className="p-4 text-center">
                          <div className="font-bold text-lg text-white">
                            {result.team1_score} - {result.team2_score}
                          </div>
                          <div className="text-xs text-slate-500">BO{result.best_of}</div>
                        </td>
                        <td className="p-4">
                          <Badge variant="default" className="bg-green-600">
                            {result.winner}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Team Rankings */}
      {teamStats.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Ranking de Times</h2>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b border-slate-700">
                    <tr>
                      <th className="text-left p-4 text-slate-400 font-medium">#</th>
                      <th className="text-left p-4 text-slate-400 font-medium">Time</th>
                      <th className="text-left p-4 text-slate-400 font-medium">Jogo</th>
                      <th className="text-center p-4 text-slate-400 font-medium">Partidas</th>
                      <th className="text-center p-4 text-slate-400 font-medium">V-D</th>
                      <th className="text-center p-4 text-slate-400 font-medium">Win Rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {teamStats.slice(0, 15).map((team, index) => (
                      <tr key={`${team.team}-${team.game}`} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="p-4 text-slate-400">{index + 1}</td>
                        <td className="p-4 text-white font-medium">{team.team}</td>
                        <td className="p-4">
                          <Badge variant="outline" className="capitalize">
                            {getGameIcon(team.game)} {team.game}
                          </Badge>
                        </td>
                        <td className="p-4 text-center text-slate-300">{team.matches_played}</td>
                        <td className="p-4 text-center text-slate-300">
                          <span className="text-green-500">{team.wins}</span>-
                          <span className="text-red-500">{team.losses}</span>
                        </td>
                        <td className="p-4 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-24 bg-slate-700 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${team.win_rate}%` }}
                              />
                            </div>
                            <span className="text-white font-bold min-w-[3rem]">
                              {team.win_rate}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tournaments */}
      {tournaments.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Torneios</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tournaments.slice(0, 9).map((tournament) => (
              <Card key={`${tournament.game}-${tournament.tournament}`}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="capitalize">
                      {getGameIcon(tournament.game)} {tournament.game}
                    </Badge>
                    <span className="text-slate-500 text-xs">
                      {tournament.match_count} partidas
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <h3 className="text-white font-medium line-clamp-2">
                    {tournament.tournament}
                  </h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Today's Games */}
      {todayGames.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Jogos de Hoje</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {todayGames.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {loading ? (
        <div className="text-center text-slate-400 py-8">Carregando...</div>
      ) : !overview && todayGames.length === 0 && recentResults.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-slate-400">
            <p className="mb-2">Nenhum dado disponível no momento</p>
            <p className="text-sm">
              Os dados serão exibidos quando as partidas forem carregadas no sistema
            </p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
