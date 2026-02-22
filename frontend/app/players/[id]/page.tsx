"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import PlayerProps from "@/components/PlayerProps";
import StatsChart from "@/components/StatsChart";
import { getPlayerProps, getPlayerGameLog, PlayerProps as PlayerPropsType, PlayerGameLog } from "@/lib/api";

export default function PlayerDetailPage() {
  const params = useParams();
  const playerId = params.id as string;
  
  const [player, setPlayer] = useState<PlayerPropsType | null>(null);
  const [gameLog, setGameLog] = useState<PlayerGameLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlayer = async () => {
      try {
        setLoading(true);
        const [props, log] = await Promise.all([
          getPlayerProps(playerId),
          getPlayerGameLog(playerId, 20),
        ]);
        setPlayer(props);
        setGameLog(log);
      } catch (error) {
        console.error("Error fetching player:", error);
      } finally {
        setLoading(false);
      }
    };

    if (playerId) {
      fetchPlayer();
    }
  }, [playerId]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-slate-400 py-8">Carregando...</div>
      </div>
    );
  }

  if (!player) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="py-8 text-center text-slate-400">
            Jogador não encontrado
          </CardContent>
        </Card>
      </div>
    );
  }

  const pointsData = gameLog.slice(0, 10).reverse().map(g => g.points || 0);
  const reboundsData = gameLog.slice(0, 10).reverse().map(g => g.rebounds_total || 0);
  const assistsData = gameLog.slice(0, 10).reverse().map(g => g.assists || 0);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">{player.player_name}</h1>
        <p className="text-slate-400">{player.team}</p>
      </div>

      {/* Props Analysis */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Análise de Props</CardTitle>
        </CardHeader>
        <CardContent>
          <PlayerProps props={player.props} />
        </CardContent>
      </Card>

      {/* Stats Charts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatsChart 
          title="Pontos (Últimos 10 Jogos)" 
          data={pointsData}
          labels={gameLog.slice(0, 10).reverse().map(g => g.game_date.slice(5, 10))}
        />
        <StatsChart 
          title="Rebotes (Últimos 10 Jogos)" 
          data={reboundsData}
          labels={gameLog.slice(0, 10).reverse().map(g => g.game_date.slice(5, 10))}
        />
        <StatsChart 
          title="Assistências (Últimos 10 Jogos)" 
          data={assistsData}
          labels={gameLog.slice(0, 10).reverse().map(g => g.game_date.slice(5, 10))}
        />
      </div>

      {/* Game Log */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Jogos</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {gameLog.map((game, idx) => (
              <div
                key={idx}
                className="p-3 bg-slate-700 rounded-md flex justify-between items-center"
              >
                <div>
                  <div className="font-medium text-white">
                    {game.is_home ? "vs" : "@"} {game.opponent}
                  </div>
                  <div className="text-sm text-slate-400">{game.game_date}</div>
                </div>
                <div className="text-right">
                  <div className="text-white">
                    {game.points}pts / {game.rebounds_total}reb / {game.assists}ast
                  </div>
                  <div className="text-sm text-slate-400">{game.minutes} min</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
