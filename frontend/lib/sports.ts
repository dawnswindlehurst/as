/**
 * Sports and Esports constants for Capivara Bet
 */

export const SPORTS = [
  // Esports
  { id: 'valorant', name: 'Valorant', icon: '🎯', color: 'red' },
  { id: 'cs2', name: 'CS2', icon: '🔫', color: 'orange' },
  { id: 'lol', name: 'LoL', icon: '⚔️', color: 'blue' },
  { id: 'dota2', name: 'Dota 2', icon: '🏆', color: 'red' },
  // Traditional Sports
  { id: 'nba', name: 'NBA', icon: '🏀', color: 'orange' },
  { id: 'soccer', name: 'Futebol', icon: '⚽', color: 'green' },
  { id: 'tennis', name: 'Tênis', icon: '🎾', color: 'yellow' },
] as const;

export type SportId = typeof SPORTS[number]['id'];

/**
 * Get sport by ID
 */
export function getSportById(id: string) {
  return SPORTS.find(sport => sport.id === id);
}

/**
 * Get sport icon by ID
 */
export function getSportIcon(id: string): string {
  const sport = getSportById(id);
  return sport?.icon || '🎮';
}

/**
 * Get sport name by ID
 */
export function getSportName(id: string): string {
  const sport = getSportById(id);
  return sport?.name || id.toUpperCase();
}

/**
 * Get sport color class by ID (for Tailwind)
 */
export function getSportColorClass(id: string): string {
  const sport = getSportById(id);
  const colorMap: Record<string, string> = {
    red: 'border-red-500 text-red-400',
    orange: 'border-orange-500 text-orange-400',
    blue: 'border-blue-500 text-blue-400',
    green: 'border-green-500 text-green-400',
    yellow: 'border-yellow-500 text-yellow-400',
  };
  return sport?.color ? colorMap[sport.color] : 'border-slate-500 text-slate-400';
}

/**
 * Sport categories
 */
export const ESPORTS = SPORTS.filter(s => ['valorant', 'cs2', 'lol', 'dota2'].includes(s.id));
export const TRADITIONAL_SPORTS = SPORTS.filter(s => ['nba', 'soccer', 'tennis'].includes(s.id));
