"""Odds comparison page - compare odds across bookmakers."""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import asyncio

from dashboard.components.odds_table import (
    render_odds_table,
    render_value_bets_table,
    render_arbitrage_table
)
from scrapers.superbet import SuperbetEsports


def show():
    """Display odds comparison page."""
    st.header("🔄 Comparador de Odds")
    st.markdown("Compare odds e identifique value bets automaticamente")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Comparação", "💰 Value Bets", "🔀 Arbitragem"])
    
    with tab1:
        show_odds_comparison()
    
    with tab2:
        show_value_bets()
    
    with tab3:
        show_arbitrage_opportunities()


def show_odds_comparison():
    """Show odds comparison section."""
    st.subheader("Comparação de Odds")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        game = st.selectbox(
            "Jogo",
            ["CS2", "Dota 2", "Valorant", "League of Legends"],
            key="odds_game"
        )
    
    with col2:
        market_type = st.selectbox(
            "Mercado",
            ["match_winner", "map_winner", "total_rounds", "first_blood"],
            key="odds_market"
        )
    
    with col3:
        days_ahead = st.slider(
            "Dias à frente",
            min_value=1,
            max_value=7,
            value=3,
            key="odds_days"
        )
    
    # Fetch and display odds
    if st.button("Buscar Odds", type="primary"):
        with st.spinner("Carregando odds..."):
            try:
                events = asyncio.run(fetch_game_events(game, days_ahead))
                
                if events:
                    st.success(f"**{len(events)}** partidas encontradas")
                    render_odds_table(events, market_type=market_type, highlight_best=True)
                else:
                    st.info("Nenhuma partida encontrada para os critérios selecionados.")
            
            except Exception as e:
                st.error(f"Erro ao buscar odds: {str(e)}")
    else:
        st.info("👆 Selecione os filtros e clique em 'Buscar Odds' para ver as comparações.")


def show_value_bets():
    """Show value bets section."""
    st.subheader("Value Bets")
    st.markdown("Apostas com valor esperado positivo baseado em nossas probabilidades.")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        min_edge = st.slider(
            "Edge Mínimo (%)",
            min_value=1,
            max_value=20,
            value=3,
            key="value_min_edge"
        ) / 100
    
    with col2:
        min_confidence = st.slider(
            "Confiança Mínima (%)",
            min_value=50,
            max_value=90,
            value=55,
            key="value_min_conf"
        ) / 100
    
    # Mock data for demonstration (replace with actual calculation)
    value_bets = generate_mock_value_bets()
    
    if value_bets:
        st.success(f"**{len(value_bets)}** value bets identificadas")
        render_value_bets_table(value_bets, min_edge=min_edge)
        
        # Summary statistics
        st.markdown("---")
        st.subheader("📊 Estatísticas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_edge = sum(bet.get('edge', 0) for bet in value_bets) / len(value_bets)
            st.metric("Edge Médio", f"{avg_edge*100:.1f}%")
        
        with col2:
            total_stake = sum(bet.get('suggested_stake', 0) for bet in value_bets)
            st.metric("Stake Total Sugerido", f"R$ {total_stake:.2f}")
        
        with col3:
            expected_roi = avg_edge
            st.metric("ROI Esperado", f"{expected_roi*100:.1f}%")
    else:
        st.info("Nenhuma value bet identificada no momento.")


def show_arbitrage_opportunities():
    """Show arbitrage opportunities section."""
    st.subheader("Oportunidades de Arbitragem")
    st.markdown("Identifique surebets entre diferentes casas de apostas.")
    
    st.warning(
        "⚠️ **Nota:** Esta funcionalidade requer comparação entre múltiplas casas de apostas. "
        "Atualmente, apenas Superbet está integrada."
    )
    
    # Mock data for demonstration
    arbitrage_opps = []  # Empty for now
    
    if arbitrage_opps:
        render_arbitrage_table(arbitrage_opps)
    else:
        st.info(
            "Nenhuma oportunidade de arbitragem encontrada.\n\n"
            "**Para usar esta funcionalidade:**\n"
            "1. Integre múltiplas casas de apostas\n"
            "2. Compare odds em tempo real\n"
            "3. Identifique discrepâncias que garantam lucro"
        )
    
    # Educational content
    with st.expander("📚 O que é Arbitragem?"):
        st.markdown("""
        **Arbitragem esportiva** (ou surebet) é uma estratégia que garante lucro 
        independente do resultado, aproveitando diferenças nas odds entre casas de apostas.
        
        **Exemplo:**
        - Casa A oferece odds 2.10 para Time 1
        - Casa B oferece odds 2.10 para Time 2
        - Apostando R$100 em cada, você garante lucro de R$10
        
        **Riscos:**
        - Limites de aposta
        - Mudanças rápidas nas odds
        - Restrições das casas de apostas
        """)


async def fetch_game_events(game: str, days_ahead: int) -> List[Dict[str, Any]]:
    """Fetch events for a specific game."""
    async with SuperbetEsports() as esports:
        if game == "CS2":
            matches = await esports.get_cs2_matches(days_ahead=days_ahead)
        elif game == "Dota 2":
            matches = await esports.get_dota2_matches(days_ahead=days_ahead)
        elif game == "Valorant":
            matches = await esports.get_valorant_matches(days_ahead=days_ahead)
        elif game == "League of Legends":
            matches = await esports.get_lol_matches(days_ahead=days_ahead)
        else:
            matches = []
        
        return [match.to_dict() for match in matches]


def generate_mock_value_bets() -> List[Dict[str, Any]]:
    """Generate mock value bets for demonstration."""
    # This would be replaced with actual calculation based on model predictions
    return [
        {
            'match': 'Team Liquid vs NAVI',
            'market': 'Match Winner',
            'selection': 'Team Liquid',
            'odds': 2.10,
            'estimated_prob': 0.55,
            'edge': 0.155,
            'suggested_stake': 125.00,
        },
        {
            'match': 'Fnatic vs G2',
            'market': 'Match Winner',
            'selection': 'Fnatic',
            'odds': 1.85,
            'estimated_prob': 0.60,
            'edge': 0.11,
            'suggested_stake': 100.00,
        },
        {
            'match': 'OG vs Secret',
            'market': 'Match Winner',
            'selection': 'OG',
            'odds': 2.50,
            'estimated_prob': 0.45,
            'edge': 0.125,
            'suggested_stake': 110.00,
        },
    ]
