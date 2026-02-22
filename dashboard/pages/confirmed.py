"""Confirmed bets page."""
import streamlit as st
import pandas as pd
from database.db import get_db
from database.models import Bet
from utils.helpers import format_currency, format_percentage, format_odds


def show():
    """Display confirmed bets page."""
    st.header("✅ Apostas Confirmadas")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["Todas", "Pendente", "Ganhas", "Perdidas"]
        )
    
    with col2:
        game_filter = st.selectbox(
            "Jogo",
            ["Todos", "CS2", "LoL", "Dota2", "Valorant"]
        )
    
    with col3:
        bookmaker_filter = st.selectbox(
            "Casa",
            ["Todas", "Pinnacle", "bet365", "Betfair", "Rivalry", "Stake"]
        )
    
    # Get bets
    with get_db() as db:
        query = db.query(Bet).filter(Bet.confirmed == True)
        
        if status_filter != "Todas":
            status_map = {
                "Pendente": "pending",
                "Ganhas": "won",
                "Perdidas": "lost"
            }
            query = query.filter(Bet.status == status_map[status_filter])
        
        if bookmaker_filter != "Todas":
            query = query.filter(Bet.bookmaker == bookmaker_filter)
        
        bets = query.order_by(Bet.created_at.desc()).all()
    
    if not bets:
        st.info("Nenhuma aposta confirmada encontrada")
        return
    
    st.write(f"**Total:** {len(bets)} apostas")
    
    # Convert to DataFrame for display
    data = []
    for bet in bets:
        match = bet.match
        if match:
            data.append({
                "ID": bet.id,
                "Data": bet.created_at.strftime("%d/%m/%Y"),
                "Jogo": match.game,
                "Partida": f"{match.team1} vs {match.team2}",
                "Seleção": bet.selection,
                "Casa": bet.bookmaker,
                "Odds": format_odds(bet.odds),
                "Stake": format_currency(bet.stake),
                "Confidence": format_percentage(bet.confidence),
                "Edge": format_percentage(bet.edge),
                "Status": bet.status.upper(),
                "Resultado": format_currency(bet.profit) if bet.profit is not None else "-",
                "CLV": format_percentage(bet.clv) if bet.clv is not None else "-",
            })
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Summary stats
    st.markdown("---")
    st.subheader("📊 Resumo")
    
    settled_bets = [b for b in bets if b.status in ["won", "lost"]]
    
    if settled_bets:
        won = sum(1 for b in settled_bets if b.status == "won")
        total_profit = sum(b.profit for b in settled_bets if b.profit is not None)
        total_stake = sum(b.stake for b in settled_bets)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Apostas", len(settled_bets))
        
        with col2:
            st.metric("Win Rate", format_percentage(won / len(settled_bets)))
        
        with col3:
            st.metric("Lucro/Prejuízo", format_currency(total_profit))
        
        with col4:
            roi = total_profit / total_stake if total_stake > 0 else 0
            st.metric("ROI", format_percentage(roi))
