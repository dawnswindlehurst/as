"use client";

import { PlayerStats } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";

interface PlayerStatsPanelProps {
  stats: PlayerStats;
  loading?: boolean;
}

export default function PlayerStatsPanel({ stats, loading }: PlayerStatsPanelProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="text-center text-slate-400 py-12">
        Nenhuma estatística disponível
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Player Header */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">{stats.player_name}</h2>
            <p className="text-slate-400 mt-1">{stats.team}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{stats.total_matches}</div>
            <div className="text-sm text-slate-400">Partidas</div>
          </div>
        </div>
      </div>

      {/* Average Stats */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-4">Médias</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="text-center">
            <div className="text-sm text-slate-400">K/D Ratio</div>
            <div className="text-2xl font-bold text-white mt-1">{stats.averages.kd_ratio.toFixed(2)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-slate-400">Kills</div>
            <div className="text-2xl font-bold text-green-400 mt-1">{stats.averages.kills.toFixed(1)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-slate-400">Deaths</div>
            <div className="text-2xl font-bold text-red-400 mt-1">{stats.averages.deaths.toFixed(1)}</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-slate-400">Assists</div>
            <div className="text-2xl font-bold text-blue-400 mt-1">{stats.averages.assists.toFixed(1)}</div>
          </div>
          {stats.averages.adr !== null && (
            <div className="text-center">
              <div className="text-sm text-slate-400">ADR</div>
              <div className="text-2xl font-bold text-orange-400 mt-1">{stats.averages.adr.toFixed(1)}</div>
            </div>
          )}
          {stats.averages.acs !== null && (
            <div className="text-center">
              <div className="text-sm text-slate-400">ACS</div>
              <div className="text-2xl font-bold text-purple-400 mt-1">{stats.averages.acs.toFixed(1)}</div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Matches */}
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h3 className="text-xl font-bold text-white mb-4">Partidas Recentes</h3>
        {stats.recent_matches.length === 0 ? (
          <div className="text-center text-slate-400 py-8">Nenhuma partida recente</div>
        ) : (
          <div className="rounded-md border border-slate-700">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Data</TableHead>
                  <TableHead>Torneio</TableHead>
                  <TableHead>Oponente</TableHead>
                  <TableHead>Resultado</TableHead>
                  <TableHead className="text-center">K</TableHead>
                  <TableHead className="text-center">D</TableHead>
                  <TableHead className="text-center">A</TableHead>
                  <TableHead className="text-center">K/D</TableHead>
                  {stats.recent_matches.some(m => m.adr !== null) && (
                    <TableHead className="text-center">ADR</TableHead>
                  )}
                  {stats.recent_matches.some(m => m.acs !== null) && (
                    <TableHead className="text-center">ACS</TableHead>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {stats.recent_matches.map((match, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="text-slate-300">
                      {match.match_date ? new Date(match.match_date).toLocaleDateString() : "N/A"}
                    </TableCell>
                    <TableCell className="text-slate-300">{match.tournament}</TableCell>
                    <TableCell className="text-white font-medium">{match.opponent}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        match.won ? "bg-green-900/50 text-green-400" : "bg-red-900/50 text-red-400"
                      }`}>
                        {match.won ? "Vitória" : "Derrota"}
                      </span>
                    </TableCell>
                    <TableCell className="text-center text-green-400 font-semibold">{match.kills ?? "-"}</TableCell>
                    <TableCell className="text-center text-red-400 font-semibold">{match.deaths ?? "-"}</TableCell>
                    <TableCell className="text-center text-blue-400 font-semibold">{match.assists ?? "-"}</TableCell>
                    <TableCell className="text-center text-white font-semibold">
                      {match.kd_ratio ? match.kd_ratio.toFixed(2) : "-"}
                    </TableCell>
                    {stats.recent_matches.some(m => m.adr !== null) && (
                      <TableCell className="text-center text-orange-400 font-semibold">
                        {match.adr ? match.adr.toFixed(1) : "-"}
                      </TableCell>
                    )}
                    {stats.recent_matches.some(m => m.acs !== null) && (
                      <TableCell className="text-center text-purple-400 font-semibold">
                        {match.acs ? match.acs.toFixed(1) : "-"}
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
