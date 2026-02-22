"use client";

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import SportTabs from "@/components/SportTabs";
import TeamCard from "@/components/TeamCard";
import PlayerList from "@/components/PlayerList";
import PlayerStatsPanel from "@/components/PlayerStatsPanel";
import { getTeamsByGame, getPlayersByTeam, getPlayerStats, Team, TeamPlayer, PlayerStats } from "@/lib/api";
import { SPORTS } from "@/lib/sports";

const SPORT_IDS = SPORTS.map(s => s.id);

export default function PropsPage() {
  const [selectedSport, setSelectedSport] = useState<string>("valorant");
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [players, setPlayers] = useState<TeamPlayer[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<TeamPlayer | null>(null);
  const [playerStats, setPlayerStats] = useState<PlayerStats | null>(null);
  const [loadingTeams, setLoadingTeams] = useState(false);
  const [loadingPlayers, setLoadingPlayers] = useState(false);
  const [loadingStats, setLoadingStats] = useState(false);

  // Load teams when sport changes
  useEffect(() => {
    loadTeams(selectedSport);
  }, [selectedSport]);

  const loadTeams = async (sport: string) => {
    try {
      setLoadingTeams(true);
      setTeams([]);
      setSelectedTeam(null);
      setPlayers([]);
      setSelectedPlayer(null);
      setPlayerStats(null);
      
      const teamsData = await getTeamsByGame(sport);
      setTeams(teamsData);
    } catch (error) {
      console.error("Error loading teams:", error);
    } finally {
      setLoadingTeams(false);
    }
  };

  const handleSelectTeam = async (team: Team) => {
    setSelectedTeam(team);
    setSelectedPlayer(null);
    setPlayerStats(null);
    
    try {
      setLoadingPlayers(true);
      const playersData = await getPlayersByTeam(team.team);
      setPlayers(playersData);
    } catch (error) {
      console.error("Error loading players:", error);
      setPlayers([]);
    } finally {
      setLoadingPlayers(false);
    }
  };

  const handleSelectPlayer = async (player: TeamPlayer) => {
    setSelectedPlayer(player);
    
    try {
      setLoadingStats(true);
      const stats = await getPlayerStats(player.player_id);
      setPlayerStats(stats);
    } catch (error) {
      console.error("Error loading player stats:", error);
      setPlayerStats(null);
    } finally {
      setLoadingStats(false);
    }
  };

  const handleBackToTeams = () => {
    setSelectedTeam(null);
    setPlayers([]);
    setSelectedPlayer(null);
    setPlayerStats(null);
  };

  const handleBackToPlayers = () => {
    setSelectedPlayer(null);
    setPlayerStats(null);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Player Props</h1>
        <p className="text-slate-400">Análise hierárquica de props por esporte, time e jogador</p>
      </div>

      {/* Sport Tabs */}
      <div className="mb-8">
        <SportTabs
          sports={SPORT_IDS}
          selectedSport={selectedSport}
          onSelectSport={setSelectedSport}
        />
      </div>

      {/* Teams Grid */}
      {!selectedTeam && (
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">
            Times - {selectedSport.toUpperCase()}
          </h2>
          
          {loadingTeams ? (
            <div className="flex items-center justify-center py-20">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-white"></div>
            </div>
          ) : teams.length === 0 ? (
            <Card>
              <CardContent className="py-12">
                <div className="text-center text-slate-400">
                  <p className="text-lg">Nenhum time encontrado</p>
                  <p className="text-sm mt-2">Não há dados disponíveis para {selectedSport.toUpperCase()}</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {teams.map((team) => (
                <TeamCard
                  key={team.team}
                  team={team}
                  onClick={() => handleSelectTeam(team)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Players List */}
      {selectedTeam && !selectedPlayer && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-white">
              Jogadores - {selectedTeam.team}
            </h2>
            <Button onClick={handleBackToTeams} variant="outline">
              ← Voltar para Times
            </Button>
          </div>
          
          <Card>
            <CardContent className="p-6">
              <PlayerList
                players={players}
                onSelectPlayer={handleSelectPlayer}
                loading={loadingPlayers}
              />
            </CardContent>
          </Card>
        </div>
      )}

      {/* Player Stats */}
      {selectedPlayer && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold text-white">
                Estatísticas - {selectedPlayer.player_name}
              </h2>
              <p className="text-slate-400 mt-1">{selectedTeam?.team}</p>
            </div>
            <Button onClick={handleBackToPlayers} variant="outline">
              ← Voltar para Jogadores
            </Button>
          </div>
          
          {playerStats && (
            <PlayerStatsPanel stats={playerStats} loading={loadingStats} />
          )}
        </div>
      )}
    </div>
  );
}
