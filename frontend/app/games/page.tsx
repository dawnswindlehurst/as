"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import GameCard from "@/components/GameCard";
import { getGames, Game } from "@/lib/api";
import { SPORTS, getSportById } from "@/lib/sports";

export default function GamesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGame, setSelectedGame] = useState<string | null>(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const today = new Date().toISOString().split("T")[0];
        const fetchedGames = await getGames({ 
          date: today,
          game: selectedGame || undefined 
        });
        setGames(fetchedGames);
      } catch (error) {
        console.error("Error fetching games:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, [selectedGame]);

  const gameTypes = SPORTS.map(s => s.id);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Jogos</h1>
        <p className="text-slate-400">Visualize todos os jogos disponíveis</p>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-2 flex-wrap">
        <Badge
          variant={selectedGame === null ? "default" : "outline"}
          className="cursor-pointer px-4 py-2"
          onClick={() => setSelectedGame(null)}
        >
          Todos
        </Badge>
        {gameTypes.map((type) => {
          const sport = getSportById(type);
          return (
            <Badge
              key={type}
              variant={selectedGame === type ? "default" : "outline"}
              className="cursor-pointer px-4 py-2 flex items-center gap-1"
              onClick={() => setSelectedGame(type)}
            >
              <span>{sport?.icon}</span>
              <span>{sport?.name || type.toUpperCase()}</span>
            </Badge>
          );
        })}
      </div>

      {/* Games Grid */}
      {loading ? (
        <div className="text-center text-slate-400 py-8">Carregando...</div>
      ) : games.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-slate-400">
            Nenhum jogo encontrado
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {games.map((game) => (
            <GameCard key={game.id} game={game} />
          ))}
        </div>
      )}
    </div>
  );
}
