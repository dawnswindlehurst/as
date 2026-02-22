"""Bookmakers analysis page."""
import streamlit as st
import plotly.express as px
from analysis.bookmakers import BookmakerAnalyzer
from utils.helpers import format_percentage, format_currency


def show():
    """Display bookmakers analysis page."""
    st.header("🏦 Análise por Casa de Apostas")
    
    analyzer = BookmakerAnalyzer()
    
    # Analyze by bookmaker
    analysis = analyzer.analyze_by_bookmaker()
    
    if not analysis:
        st.info("Sem dados suficientes para análise por casa")
        return
    
    # Display table
    data = []
    for bookmaker, stats in analysis.items():
        data.append({
            "Casa": bookmaker,
            "Total Apostas": stats.get("total_bets", 0),
            "Vitórias": stats.get("won_bets", 0),
            "Win Rate": format_percentage(stats.get("win_rate", 0)),
            "Avg Odds": f"{stats.get('avg_odds', 0):.2f}",
            "Avg Edge": format_percentage(stats.get("avg_edge", 0)),
            "Avg CLV": format_percentage(stats.get("avg_clv", 0)),
            "ROI": format_percentage(stats.get("roi", 0)),
            "Lucro": format_currency(stats.get("total_profit", 0)),
        })
    
    st.dataframe(data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # ROI comparison
        fig = px.bar(
            data,
            x="Casa",
            y="ROI",
            title="ROI por Casa de Apostas",
            color="ROI",
            color_continuous_scale=["red", "yellow", "green"],
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CLV comparison
        fig = px.bar(
            data,
            x="Casa",
            y="Avg CLV",
            title="CLV Médio por Casa",
            color="Avg CLV",
            color_continuous_scale=["red", "yellow", "green"],
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Best bookmaker by game
    st.subheader("🎮 Melhor Casa por Jogo")
    
    games = ["CS2", "LoL", "Dota2", "Valorant"]
    
    for game in games:
        best_bm = analyzer.get_best_bookmaker_by_game(game)
        
        if best_bm:
            with st.expander(f"**{game}**"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Melhor Casa", best_bm.get("best_bookmaker", "N/A"))
                
                with col2:
                    st.metric("ROI", format_percentage(best_bm.get("roi", 0)))
                
                with col3:
                    st.metric("Total Apostas", best_bm.get("total_bets", 0))
    
    st.markdown("---")
    
    # Insights
    st.subheader("💡 Insights")
    
    st.info("""
    **Como interpretar:**
    - **CLV positivo** indica que você está conseguindo odds melhores que o fechamento
    - **ROI varia** entre casas - foque nas mais lucrativas
    - **Sharp bookmakers** (Pinnacle) geralmente têm margens menores
    """)
