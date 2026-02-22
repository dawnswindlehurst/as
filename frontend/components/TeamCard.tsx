"use client";

import { Team } from "@/lib/api";

interface TeamCardProps {
  team: Team;
  onClick: () => void;
}

const sportColors: Record<string, string> = {
  valorant: "border-red-500 hover:border-red-400",
  cs2: "border-orange-500 hover:border-orange-400",
  lol: "border-blue-500 hover:border-blue-400",
  dota2: "border-red-700 hover:border-red-600",
  nba: "border-purple-500 hover:border-purple-400",
};

export default function TeamCard({ team, onClick }: TeamCardProps) {
  const colorClass = sportColors[team.game] || "border-slate-600 hover:border-slate-500";
  
  return (
    <div
      onClick={onClick}
      className={`
        bg-slate-800 rounded-lg p-6 border-2 ${colorClass}
        cursor-pointer transition-all duration-200
        hover:bg-slate-700 hover:scale-105 hover:shadow-lg
      `}
    >
      <div className="flex flex-col items-center text-center space-y-3">
        {/* Team Logo Placeholder */}
        <div className="w-16 h-16 bg-slate-700 rounded-full flex items-center justify-center">
          <span className="text-2xl font-bold text-white">
            {team.team.substring(0, 2).toUpperCase()}
          </span>
        </div>
        
        {/* Team Name */}
        <h3 className="text-lg font-bold text-white line-clamp-2">
          {team.team}
        </h3>
        
        {/* Stats */}
        <div className="w-full pt-3 border-t border-slate-700 space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Partidas</span>
            <span className="text-white font-semibold">{team.matches_played}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Vitórias</span>
            <span className="text-white font-semibold">{team.wins}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-400">Win Rate</span>
            <span className={`font-semibold ${team.win_rate >= 50 ? "text-green-400" : "text-red-400"}`}>
              {team.win_rate}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
