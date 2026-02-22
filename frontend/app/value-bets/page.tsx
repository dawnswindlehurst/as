"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { getValueBets, ValueBet, ValueBetsSummary } from "@/lib/api";

// Sport icons mapping
const SPORT_ICONS: Record<string, string> = {
  nba: "🏀",
  soccer: "⚽",
  tennis: "🎾",
  valorant: "🎯",
  cs2: "🔫",
  lol: "⚔️",
  dota2: "🏆",
};

// Sport display names
const SPORT_NAMES: Record<string, string> = {
  nba: "NBA",
  soccer: "Futebol",
  tennis: "Tênis",
  valorant: "Valorant",
  cs2: "CS2",
  lol: "LoL",
  dota2: "Dota 2",
};

export default function ValueBetsPage() {
  const [valueBets, setValueBets] = useState<ValueBet[]>([]);
  const [summary, setSummary] = useState<ValueBetsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSport, setSelectedSport] = useState<string>("all");
  const [minEdge, setMinEdge] = useState<number>(3);
  const [minConfidence, setMinConfidence] = useState<number>(55);

  useEffect(() => {
    const fetchValueBets = async () => {
      try {
        setLoading(true);
        const data = await getValueBets({
          sport: selectedSport === "all" ? undefined : selectedSport,
          min_edge: minEdge,
          min_confidence: minConfidence,
        });
        setValueBets(data.value_bets);
        setSummary(data.summary);
      } catch (error) {
        console.error("Error fetching value bets:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchValueBets();
  }, [selectedSport, minEdge, minConfidence]);

  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getEdgeBadgeVariant = (edge: number) => {
    if (edge >= 5) return "default"; // green
    return "secondary"; // yellow
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          Value Bets do Dia
        </h1>
        <p className="text-slate-400">
          {new Date().toLocaleDateString("pt-BR", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="text-slate-400 text-sm mb-1">Total de Bets</div>
              <div className="text-3xl font-bold text-white">
                {summary.total_bets}
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="text-slate-400 text-sm mb-1">Edge Médio</div>
              <div className="text-3xl font-bold text-green-400">
                {summary.avg_edge.toFixed(1)}%
              </div>
            </CardContent>
          </Card>
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-6">
              <div className="text-slate-400 text-sm mb-1">
                Stake Total Sugerido
              </div>
              <div className="text-3xl font-bold text-white">
                R$ {summary.total_suggested_stake.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex flex-wrap gap-2">
          <Badge
            variant={selectedSport === "all" ? "default" : "outline"}
            className="cursor-pointer"
            onClick={() => setSelectedSport("all")}
          >
            Todos
          </Badge>
          {Object.entries(SPORT_NAMES).map(([key, name]) => (
            <Badge
              key={key}
              variant={selectedSport === key ? "default" : "outline"}
              className="cursor-pointer"
              onClick={() => setSelectedSport(key)}
            >
              {SPORT_ICONS[key]} {name}
            </Badge>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm text-slate-400">
              Edge Mínimo: {minEdge}%
            </label>
            <input
              type="range"
              min="3"
              max="15"
              step="0.5"
              value={minEdge}
              onChange={(e) => setMinEdge(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-400">
              Confidence Mínimo: {minConfidence}%
            </label>
            <input
              type="range"
              min="55"
              max="80"
              step="1"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="text-slate-400">Carregando value bets...</div>
        </div>
      )}

      {/* Empty State */}
      {!loading && valueBets.length === 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-12 text-center">
            <div className="text-slate-400 text-lg mb-2">
              Nenhuma value bet encontrada
            </div>
            <div className="text-slate-500 text-sm">
              Tente ajustar os filtros de edge e confidence
            </div>
          </CardContent>
        </Card>
      )}

      {/* Value Bets List */}
      {!loading && valueBets.length > 0 && (
        <div className="space-y-4">
          {valueBets.map((bet) => (
            <Card
              key={bet.id}
              className="bg-slate-800 border-slate-700 hover:border-blue-500 transition-colors"
            >
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  {/* Left Side - Game Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-3xl">{SPORT_ICONS[bet.sport]}</span>
                      <div>
                        <h3 className="text-xl font-semibold text-white">
                          {bet.game}
                        </h3>
                        <div className="text-sm text-slate-400">
                          {bet.league} • {formatTime(bet.start_time)}
                        </div>
                      </div>
                    </div>
                    <div className="mt-3 space-y-1">
                      <div className="text-sm text-slate-300">
                        <span className="font-medium">Mercado:</span>{" "}
                        {bet.market}
                      </div>
                      <div className="text-sm text-slate-300">
                        <span className="font-medium">Seleção:</span>{" "}
                        <span className="text-white font-semibold">
                          {bet.selection}
                        </span>
                      </div>
                      <div className="text-sm text-slate-300">
                        <span className="font-medium">Odds:</span> {bet.odds}{" "}
                        <span className="text-slate-400">({bet.bookmaker})</span>
                      </div>
                      {bet.reasoning && (
                        <div className="text-sm text-slate-400 italic mt-2">
                          💡 {bet.reasoning}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Side - Stats & Action */}
                  <div className="flex flex-col items-end gap-3 min-w-[200px]">
                    <div className="flex gap-2">
                      <Badge
                        variant={getEdgeBadgeVariant(bet.edge)}
                        className="text-base font-bold"
                      >
                        Edge: {bet.edge.toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-sm text-slate-400">
                        Confidence: {bet.confidence}%
                      </div>
                      <div className="text-sm text-green-400">
                        EV: +{(bet.expected_value * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-slate-400">
                        Kelly: {(bet.kelly_stake * 100).toFixed(0)}%
                      </div>
                      <div className="text-lg font-bold text-white mt-2">
                        Stake: R$ {bet.suggested_stake.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
