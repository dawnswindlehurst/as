"""Event calendar page - tournament schedule view."""

import streamlit as st
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any

from dashboard.components.calendar_view import (
    render_calendar_view,
    render_event_timeline,
    render_tournament_list
)
from scrapers.superbet import SuperbetEsports, SuperbetClient


def show():
    """Display calendar page."""
    st.header("📅 Calendário de Eventos")
    st.markdown("Visualize torneios e partidas programadas")
    
    # View mode selection
    view_mode = st.radio(
        "Modo de Visualização",
        ["Timeline (7 dias)", "Calendário Mensal", "Lista de Torneios"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        game_filter = st.selectbox(
            "Filtrar por Jogo",
            ["Todos", "CS2", "Dota 2", "Valorant", "League of Legends"]
        )
    
    with col2:
        if view_mode == "Calendário Mensal":
            # Month/Year selector
            year = st.selectbox(
                "Ano",
                [2024, 2025, 2026],
                index=1
            )
            month = st.selectbox(
                "Mês",
                list(range(1, 13)),
                index=datetime.now().month - 1,
                format_func=lambda x: datetime(2000, x, 1).strftime('%B')
            )
        elif view_mode == "Lista de Torneios":
            tier_filter = st.selectbox(
                "Tier",
                ["Todos", "S", "A", "B", "C"]
            )
    
    st.markdown("---")
    
    # Fetch data
    with st.spinner("Carregando eventos..."):
        try:
            if view_mode == "Lista de Torneios":
                tournaments = asyncio.run(fetch_tournaments(game_filter))
                tier = None if tier_filter == "Todos" else tier_filter
                render_tournament_list(tournaments, tier_filter=tier)
            else:
                events = asyncio.run(fetch_events(game_filter, days_ahead=30))
                
                if view_mode == "Timeline (7 dias)":
                    render_event_timeline(events, days_ahead=7)
                elif view_mode == "Calendário Mensal":
                    game_name = None if game_filter == "Todos" else map_game_filter(game_filter)
                    render_calendar_view(events, year, month, game_filter=game_name)
        
        except Exception as e:
            st.error(f"Erro ao carregar eventos: {str(e)}")
            st.info("Verifique sua conexão com a internet e tente novamente.")
    
    # Legend for calendar view
    if view_mode == "Calendário Mensal":
        st.markdown("---")
        st.markdown("### 📝 Legenda")
        st.markdown(
            "- Cada dia mostra até 3 eventos\n"
            "- Use os filtros para refinar sua visualização\n"
            "- Clique em um evento para mais detalhes (em breve)"
        )


async def fetch_events(game_filter: str, days_ahead: int = 7) -> List[Dict[str, Any]]:
    """
    Fetch events from Superbet API.
    
    Args:
        game_filter: Game to filter by
        days_ahead: Number of days to look ahead
        
    Returns:
        List of event dictionaries
    """
    async with SuperbetEsports() as esports:
        if game_filter == "CS2":
            matches = await esports.get_cs2_matches(days_ahead=days_ahead)
        elif game_filter == "Dota 2":
            matches = await esports.get_dota2_matches(days_ahead=days_ahead)
        elif game_filter == "Valorant":
            matches = await esports.get_valorant_matches(days_ahead=days_ahead)
        elif game_filter == "League of Legends":
            matches = await esports.get_lol_matches(days_ahead=days_ahead)
        else:
            # Fetch all games
            all_matches = await esports.get_all_esports_matches(days_ahead=days_ahead)
            matches = []
            for game_matches in all_matches.values():
                matches.extend(game_matches)
        
        return [match.to_dict() for match in matches]


async def fetch_tournaments(game_filter: str) -> List[Dict[str, Any]]:
    """
    Fetch tournaments from Superbet API.
    
    Args:
        game_filter: Game to filter by
        
    Returns:
        List of tournament dictionaries
    """
    async with SuperbetClient() as client:
        if game_filter == "Todos":
            tournaments = await client.get_tournaments()
        else:
            sport_id = get_sport_id(game_filter)
            tournaments = await client.get_tournaments(sport_id=sport_id)
        
        return [tournament.to_dict() for tournament in tournaments]


def get_sport_id(game_filter: str) -> int:
    """Map game filter to sport ID."""
    game_map = {
        "CS2": 55,
        "Dota 2": 54,
        "Valorant": 153,
        "League of Legends": 39,
    }
    return game_map.get(game_filter, 0)


def map_game_filter(game_filter: str) -> str:
    """Map filter name to sport name."""
    game_map = {
        "CS2": "Counter-Strike 2",
        "Dota 2": "Dota 2",
        "Valorant": "Valorant",
        "League of Legends": "League of Legends"
    }
    return game_map.get(game_filter, game_filter)
