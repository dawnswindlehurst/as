"""Live match card component for dashboard."""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, Optional


def render_live_match_card(match: Dict[str, Any]):
    """
    Render a live match card.
    
    Args:
        match: Match data dictionary with teams, odds, status, etc.
    """
    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    sport = match.get('sport_name', 'Unknown')
    tournament = match.get('tournament_name', '')
    is_live = match.get('is_live', False)
    start_time = match.get('start_time')
    
    # Determine status color
    status_color = "#28a745" if is_live else "#6c757d"
    status_text = "🔴 AO VIVO" if is_live else "⏰ Programado"
    
    # Card container
    with st.container():
        # Header with status
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{sport}** - {tournament}")
        with col2:
            st.markdown(
                f'<span style="color: {status_color}; font-weight: bold;">{status_text}</span>',
                unsafe_allow_html=True
            )
        
        # Teams
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"### {team1}")
        
        with col2:
            st.markdown("<div style='text-align: center; padding-top: 10px;'>VS</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"### {team2}")
        
        # Odds if available
        markets = match.get('markets', [])
        if markets:
            st.markdown("**Odds:**")
            for market in markets[:3]:  # Show first 3 markets
                market_name = market.get('market_name', '')
                odds_list = market.get('odds_list', [])
                
                if odds_list:
                    cols = st.columns(len(odds_list))
                    for i, odd in enumerate(odds_list):
                        with cols[i]:
                            outcome = odd.get('outcome_name', '')
                            odds_value = odd.get('odds', 0)
                            st.metric(outcome, f"{odds_value:.2f}")
        
        # Start time
        if start_time and not is_live:
            if isinstance(start_time, str):
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    st.caption(f"⏰ Início: {start_dt.strftime('%d/%m/%Y %H:%M')}")
                except:
                    st.caption(f"⏰ Início: {start_time}")
            else:
                st.caption(f"⏰ Início: {start_time.strftime('%d/%m/%Y %H:%M')}")
        
        st.markdown("---")


def render_compact_match_card(match: Dict[str, Any]):
    """
    Render a compact match card (smaller version).
    
    Args:
        match: Match data dictionary
    """
    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    is_live = match.get('is_live', False)
    
    status_icon = "🔴" if is_live else "⏰"
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"{status_icon} **{team1}** vs **{team2}**")
    
    with col2:
        # Show first market odds if available
        markets = match.get('markets', [])
        if markets and markets[0].get('odds_list'):
            first_odd = markets[0]['odds_list'][0]
            odds_value = first_odd.get('odds', 0)
            st.caption(f"Odds: {odds_value:.2f}")


def render_match_list(matches: list, compact: bool = False):
    """
    Render a list of matches.
    
    Args:
        matches: List of match dictionaries
        compact: Whether to use compact card style
    """
    if not matches:
        st.info("Nenhuma partida encontrada.")
        return
    
    for match in matches:
        if compact:
            render_compact_match_card(match)
        else:
            render_live_match_card(match)
