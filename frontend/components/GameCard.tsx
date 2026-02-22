"use client";

import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Game } from "@/lib/api";
import { formatTime } from "@/lib/utils";
import { getSportIcon, getSportName } from "@/lib/sports";

interface GameCardProps {
  game: Game;
}

export default function GameCard({ game }: GameCardProps) {
  const isLive = game.is_live;
  const hasScore = game.team1_score !== null && game.team2_score !== null;

  return (
    <Card className="hover:bg-slate-700/50 transition-colors">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="text-xs flex items-center gap-1">
              <span>{getSportIcon(game.game)}</span>
              <span>{getSportName(game.game)}</span>
            </Badge>
            {game.tournament && (
              <span className="text-xs text-slate-400 truncate max-w-[200px]">{game.tournament}</span>
            )}
          </div>
          {isLive && (
            <Badge variant="destructive" className="animate-pulse">
              LIVE
            </Badge>
          )}
        </div>

        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-semibold text-white">{game.team1}</span>
            {hasScore && (
              <span className="text-2xl font-bold text-white">
                {game.team1_score}
              </span>
            )}
          </div>
          <div className="flex justify-between items-center">
            <span className="font-semibold text-white">{game.team2}</span>
            {hasScore && (
              <span className="text-2xl font-bold text-white">
                {game.team2_score}
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 pt-3 border-t border-slate-700 flex justify-between items-center text-sm text-slate-400">
          <span>
            {game.finished
              ? "Finalizado"
              : isLive
              ? "Ao vivo"
              : formatTime(game.start_time)}
          </span>
          <span>BO{game.best_of}</span>
        </div>

        {game.odds && game.odds.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-700">
            <div className="flex gap-2 text-xs">
              {game.odds.slice(0, 2).map((odd, idx) => (
                <div key={idx} className="flex-1">
                  <div className="text-slate-400">{odd.bookmaker}</div>
                  <div className="flex gap-1 mt-1">
                    {odd.team1_odds && (
                      <span className="bg-slate-700 px-2 py-1 rounded">
                        {odd.team1_odds.toFixed(2)}
                      </span>
                    )}
                    {odd.team2_odds && (
                      <span className="bg-slate-700 px-2 py-1 rounded">
                        {odd.team2_odds.toFixed(2)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
