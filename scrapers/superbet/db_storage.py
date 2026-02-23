"""
Database storage for Superbet odds.
"""
import asyncio
import asyncpg
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

from .superbet_client import SuperbetEvent, SuperbetMarket
from .sport_mapping import get_sport_name

logger = logging.getLogger(__name__)


class SuperbetDBStorage:
    """Saves Superbet odds to PostgreSQL database."""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL')
        self.pool: Optional[asyncpg.Pool] = None
        
        # Cache de prop types normalizados
        self.prop_type_cache: Dict[str, str] = {}
    
    async def connect(self):
        """Create connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.database_url, min_size=2, max_size=10)
            await self._load_prop_type_cache()
    
    async def close(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def _load_prop_type_cache(self):
        """Load prop type mappings from database."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT superbet_name, normalized_name FROM prop_type_mapping")
            self.prop_type_cache = {r['superbet_name']: r['normalized_name'] for r in rows}
    
    def _normalize_prop_type(self, market_name: str) -> str:
        """Normalize prop type name."""
        if market_name in self.prop_type_cache:
            return self.prop_type_cache[market_name]
        
        # Fallback: extrair tipo básico
        name = market_name.lower()
        if 'pontos' in name and 'rebotes' in name and 'assist' in name:
            return 'pts_reb_ast'
        elif 'pontos' in name and 'rebotes' in name:
            return 'pts_reb'
        elif 'pontos' in name and 'assist' in name:
            return 'pts_ast'
        elif 'rebotes' in name and 'assist' in name:
            return 'reb_ast'
        elif 'pontos' in name:
            return 'points'
        elif 'rebotes' in name:
            return 'rebounds'
        elif 'assist' in name:
            return 'assists'
        elif '3 pontos' in name:
            return 'threes_made'
        elif 'bloqueio' in name or 'toco' in name:
            return 'blocks'
        elif 'roubada' in name:
            return 'steals'
        elif 'duplo' in name:
            return 'double_double'
        elif 'falta' in name:
            return 'fouls'
        elif 'gol' in name:
            return 'goals'
        
        return market_name[:50]
    
    def _extract_period(self, market_name: str) -> str:
        """Extract period from market name."""
        name = market_name.lower()
        if '1º quarto' in name or '1° quarto' in name:
            return '1q'
        elif '2º quarto' in name or '2° quarto' in name:
            return '2q'
        elif '3º quarto' in name or '3° quarto' in name:
            return '3q'
        elif '4º quarto' in name or '4° quarto' in name:
            return '4q'
        elif '1º tempo' in name or '1° tempo' in name or '1º período' in name:
            return '1h'
        elif '2º tempo' in name or '2° tempo' in name or '2º período' in name:
            return '2h'
        return 'full'
    
    async def save_event(self, event: SuperbetEvent, sport_id: int) -> int:
        """Save or update event, return event ID."""
        async with self.pool.acquire() as conn:
            # Upsert event
            event_db_id = await conn.fetchval("""
                INSERT INTO superbet_events (superbet_event_id, sport_id, sport_name, team1, team2, start_time, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                ON CONFLICT (superbet_event_id) DO UPDATE SET
                    team1 = EXCLUDED.team1,
                    team2 = EXCLUDED.team2,
                    start_time = EXCLUDED.start_time,
                    updated_at = NOW()
                RETURNING id
            """, int(event.event_id), sport_id, get_sport_name(sport_id), 
                event.team1, event.team2, event.start_time)
            
            return event_db_id
    
    async def save_main_odds(self, event_db_id: int, markets: List[SuperbetMarket]):
        """Save main odds (moneyline, handicap, totals)."""
        async with self.pool.acquire() as conn:
            for market in markets:
                name = market.market_name.lower()
                
                # Identificar tipo de mercado
                market_type = None
                line = None
                odds_home = None
                odds_away = None
                odds_draw = None
                
                # Moneyline / Vencedor
                if 'vencedor' in name or 'resultado final' in name:
                    if 'total' not in name and 'ambas' not in name:
                        market_type = 'moneyline'
                        for odd in market.odds_list:
                            outcome = odd.outcome_name.lower()
                            if '1' in outcome or 'casa' in outcome:
                                odds_home = odd.odds
                            elif '2' in outcome or 'fora' in outcome or 'visitante' in outcome:
                                odds_away = odd.odds
                            elif 'x' in outcome or 'empate' in outcome:
                                odds_draw = odd.odds
                
                # Handicap
                elif 'handicap' in name and 'jogador' not in name:
                    market_type = 'handicap'
                    for odd in market.odds_list:
                        # Extrair linha do nome
                        try:
                            parts = odd.outcome_name.split()
                            for p in parts:
                                if p.replace('-', '').replace('+', '').replace('.', '').isdigit():
                                    line = float(p)
                                    break
                            
                            if '-' in odd.outcome_name or 'casa' in odd.outcome_name.lower():
                                odds_home = odd.odds
                            else:
                                odds_away = odd.odds
                        except:
                            pass
                
                # Total
                elif 'total de' in name and 'jogador' not in name:
                    if 'pontos' in name or 'gols' in name or 'games' in name:
                        market_type = 'total'
                        for odd in market.odds_list:
                            try:
                                # Extrair linha
                                parts = odd.outcome_name.split()
                                for p in parts:
                                    clean = p.replace(',', '.')
                                    if clean.replace('.', '').isdigit():
                                        line = float(clean)
                                        break
                                
                                if 'mais' in odd.outcome_name.lower() or 'over' in odd.outcome_name.lower():
                                    odds_home = odd.odds  # over
                                elif 'menos' in odd.outcome_name.lower() or 'under' in odd.outcome_name.lower():
                                    odds_away = odd.odds  # under
                            except:
                                pass
                
                # Dupla chance
                elif 'dupla chance' in name:
                    market_type = 'double_chance'
                    for odd in market.odds_list:
                        outcome = odd.outcome_name.upper()
                        if '1X' in outcome:
                            odds_home = odd.odds
                        elif 'X2' in outcome:
                            odds_away = odd.odds
                        elif '12' in outcome:
                            odds_draw = odd.odds
                
                if market_type and (odds_home or odds_away):
                    period = self._extract_period(market.market_name)
                    
                    try:
                        await conn.execute("""
                            INSERT INTO superbet_main_odds (event_id, market_type, period, line, odds_home, odds_away, odds_draw)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT DO NOTHING
                        """, event_db_id, market_type, period, line, odds_home, odds_away, odds_draw)
                    except Exception as e:
                        logger.debug(f"Error saving main odds: {e}")
    
    async def save_player_props(self, event_db_id: int, markets: List[SuperbetMarket]):
        """Save player props."""
        async with self.pool.acquire() as conn:
            for market in markets:
                if 'Jogador -' not in market.market_name and 'Jogador  -' not in market.market_name:
                    continue
                
                prop_type = self._normalize_prop_type(market.market_name)
                period = self._extract_period(market.market_name)
                
                # Processar odds
                players_data = {}
                
                for odd in market.odds_list:
                    try:
                        parts = odd.outcome_name.split(' - ')
                        if len(parts) < 2:
                            continue
                        
                        player = parts[0].strip()
                        line_part = parts[1]
                        
                        if player not in players_data:
                            players_data[player] = {'over': None, 'under': None, 'line': None}
                        
                        if 'Mais de' in line_part:
                            # Extrair linha
                            try:
                                line_str = line_part.split('Mais de ')[1].split()[0].replace(',', '.')
                                line = float(line_str)
                                players_data[player]['line'] = line
                                players_data[player]['over'] = odd.odds
                            except:
                                pass
                        elif 'Menos de' in line_part:
                            players_data[player]['under'] = odd.odds
                    except:
                        pass
                
                # Salvar
                for player, data in players_data.items():
                    if data['line'] is not None:
                        try:
                            await conn.execute("""
                                INSERT INTO superbet_player_props 
                                (event_id, player_name, prop_type, period, line, odds_over, odds_under)
                                VALUES ($1, $2, $3, $4, $5, $6, $7)
                                ON CONFLICT DO NOTHING
                            """, event_db_id, player, prop_type, period, 
                                data['line'], data['over'], data['under'])
                        except Exception as e:
                            logger.debug(f"Error saving player prop: {e}")
    
    async def save_full_event(self, event: SuperbetEvent, sport_id: int):
        """Save event with all odds."""
        if not event.markets:
            return
        
        event_db_id = await self.save_event(event, sport_id)
        await self.save_main_odds(event_db_id, event.markets)
        await self.save_player_props(event_db_id, event.markets)
    
    async def get_stats(self) -> Dict:
        """Get storage statistics."""
        async with self.pool.acquire() as conn:
            events = await conn.fetchval("SELECT COUNT(*) FROM superbet_events")
            main_odds = await conn.fetchval("SELECT COUNT(*) FROM superbet_main_odds")
            player_props = await conn.fetchval("SELECT COUNT(*) FROM superbet_player_props")
            
            return {
                'events': events,
                'main_odds': main_odds,
                'player_props': player_props
            }
