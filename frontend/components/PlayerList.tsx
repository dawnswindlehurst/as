"use client";

import { TeamPlayer } from "@/lib/api";

interface PlayerListProps {
  players: TeamPlayer[];
  onSelectPlayer: (player: TeamPlayer) => void;
  loading?: boolean;
}

export default function PlayerList({ players, onSelectPlayer, loading }: PlayerListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!players || players.length === 0) {
    return (
      <div className="text-center text-slate-400 py-12">
        <p className="text-lg">Nenhum jogador encontrado</p>
        <p className="text-sm mt-2">Este time ainda não possui estatísticas de jogadores</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {players.map((player) => (
        <div
          key={player.player_id}
          onClick={() => onSelectPlayer(player)}
          className="bg-slate-800 rounded-lg p-4 hover:bg-slate-700 cursor-pointer transition-all duration-200 border border-slate-700 hover:border-slate-600"
        >
          <div className="flex items-center justify-between">
            {/* Player Info */}
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-white">{player.player_name}</h4>
              <p className="text-sm text-slate-400">{player.matches_played} partidas</p>
            </div>
            
            {/* Player Stats */}
            <div className="flex gap-6 text-sm">
              <div className="text-center">
                <div className="text-slate-400">K/D</div>
                <div className="text-white font-semibold">{player.avg_kd.toFixed(2)}</div>
              </div>
              <div className="text-center">
                <div className="text-slate-400">Kills</div>
                <div className="text-white font-semibold">{player.avg_kills.toFixed(1)}</div>
              </div>
              <div className="text-center">
                <div className="text-slate-400">Deaths</div>
                <div className="text-white font-semibold">{player.avg_deaths.toFixed(1)}</div>
              </div>
              <div className="text-center">
                <div className="text-slate-400">Assists</div>
                <div className="text-white font-semibold">{player.avg_assists.toFixed(1)}</div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
