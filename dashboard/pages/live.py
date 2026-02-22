"""Live matches page - real-time odds and match status."""

import streamlit as st
import asyncio
from typing import Dict, List, Any
from datetime import datetime

from dashboard.components.live_match_card import render_live_match_card, render_match_list
from scrapers.superbet import SuperbetEsports


def show():
    """Display live matches page."""
    st.header("🎮 Live Matches")
    st.markdown("Partidas ao vivo com odds em tempo real")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        game_filter = st.selectbox(
            "Jogo",
            ["Todos", "CS2", "Dota 2", "Valorant", "League of Legends"],
            key="live_game_filter"
        )
    
    with col2:
        view_mode = st.radio(
            "Visualização",
            ["Cards", "Compacto"],
            horizontal=True,
            key="live_view_mode"
        )
    
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    st.markdown("---")
    
    # Placeholder for auto-refresh
    matches_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Fetch live matches
    with status_placeholder:
        with st.spinner("Carregando partidas ao vivo..."):
            try:
                matches = asyncio.run(fetch_live_matches(game_filter))
            except Exception as e:
                st.error(f"Erro ao carregar partidas: {str(e)}")
                matches = []
    
    # Display matches
    with matches_placeholder.container():
        if matches:
            # Show count
            st.success(f"**{len(matches)}** partidas ao vivo encontradas")
            
            # Filter by game if needed
            if game_filter != "Todos":
                game_map = {
                    "CS2": "Counter-Strike 2",
                    "Dota 2": "Dota 2",
                    "Valorant": "Valorant",
                    "League of Legends": "League of Legends"
                }
                sport_name = game_map.get(game_filter, game_filter)
                matches = [m for m in matches if m.get('sport_name') == sport_name]
            
            # Separate live from upcoming
            live_matches = [m for m in matches if m.get('is_live', False)]
            upcoming_matches = [m for m in matches if not m.get('is_live', False)]
            
            # Display live matches
            if live_matches:
                st.subheader("🔴 Ao Vivo")
                render_match_list(live_matches, compact=(view_mode == "Compacto"))
            
            # Display upcoming matches
            if upcoming_matches:
                st.markdown("---")
                st.subheader("⏰ Próximas Partidas")
                render_match_list(upcoming_matches[:10], compact=(view_mode == "Compacto"))
        else:
            st.info("Nenhuma partida ao vivo no momento.")
            st.markdown("---")
            st.markdown("### 💡 Dica")
            st.markdown(
                "As partidas ao vivo aparecerão aqui automaticamente. "
                "Ative o auto-refresh para atualizar a cada 30 segundos."
            )
    
    # Last update time
    st.caption(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")
    
    # Auto-refresh logic using Streamlit's rerun with time check
    if auto_refresh:
        # Store last refresh time in session state
        if 'last_refresh_time' not in st.session_state:
            st.session_state.last_refresh_time = datetime.now()
        
        # Check if 30 seconds have passed
        time_diff = (datetime.now() - st.session_state.last_refresh_time).total_seconds()
        if time_diff >= 30:
            st.session_state.last_refresh_time = datetime.now()
            st.rerun()


async def fetch_live_matches(game_filter: str) -> List[Dict[str, Any]]:
    """
    Fetch live matches from Superbet API.
    
    Args:
        game_filter: Game to filter by
        
    Returns:
        List of match dictionaries
    """
    async with SuperbetEsports() as esports:
        if game_filter == "CS2":
            matches = await esports.get_cs2_matches(days_ahead=1, include_live=True)
        elif game_filter == "Dota 2":
            matches = await esports.get_dota2_matches(days_ahead=1, include_live=True)
        elif game_filter == "Valorant":
            matches = await esports.get_valorant_matches(days_ahead=1, include_live=True)
        elif game_filter == "League of Legends":
            matches = await esports.get_lol_matches(days_ahead=1, include_live=True)
        else:
            # Fetch all games
            all_matches = await esports.get_all_esports_matches(days_ahead=1, include_live=True)
            matches = []
            for game_matches in all_matches.values():
                matches.extend(game_matches)
        
        # Convert to dictionaries
        return [match.to_dict() for match in matches]
