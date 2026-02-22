"""Confidence analysis page."""
import streamlit as st
import plotly.express as px
from analysis.confidence import ConfidenceAnalyzer
from config.constants import CONFIDENCE_RANGES
from utils.helpers import format_percentage, format_currency


def show():
    """Display confidence analysis page."""
    st.header("🎯 Análise por Confidence")
    st.write("Análise de performance em diferentes faixas de confiança do modelo")
    
    analyzer = ConfidenceAnalyzer()
    
    # Analyze by confidence
    analysis = analyzer.analyze_by_confidence()
    
    if not analysis:
        st.info("Sem dados suficientes para análise por confidence")
        return
    
    # Display table
    data = []
    for range_name, stats in analysis.items():
        data.append({
            "Confidence Range": range_name,
            "Total Apostas": stats.get("total_bets", 0),
            "Vitórias": stats.get("won_bets", 0),
            "Derrotas": stats.get("lost_bets", 0),
            "Win Rate": format_percentage(stats.get("win_rate", 0)),
            "Avg Confidence": format_percentage(stats.get("avg_confidence", 0)),
            "Avg Odds": f"{stats.get('avg_odds', 0):.2f}",
            "Avg Edge": format_percentage(stats.get("avg_edge", 0)),
            "ROI": format_percentage(stats.get("roi", 0)),
            "Lucro": format_currency(stats.get("total_profit", 0)),
        })
    
    st.dataframe(data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Win Rate by confidence
        fig = px.bar(
            data,
            x="Confidence Range",
            y="Win Rate",
            title="Win Rate por Confidence Range",
            color="Win Rate",
            color_continuous_scale=["red", "yellow", "green"],
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ROI by confidence
        fig = px.bar(
            data,
            x="Confidence Range",
            y="ROI",
            title="ROI por Confidence Range",
            color="ROI",
            color_continuous_scale=["red", "yellow", "green"],
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Optimal range
    st.subheader("💎 Range Mais Lucrativo")
    optimal = analyzer.get_optimal_confidence_range()
    
    if optimal:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Range", optimal.get("range", "N/A"))
        
        with col2:
            st.metric("ROI", format_percentage(optimal.get("roi", 0)))
        
        with col3:
            st.metric("Win Rate", format_percentage(optimal.get("win_rate", 0)))
        
        with col4:
            st.metric("Total Apostas", optimal.get("total_bets", 0))
        
        st.success(f"A faixa de confidence **{optimal.get('range')}** tem o melhor ROI com {format_percentage(optimal.get('roi', 0))}")
    
    st.markdown("---")
    
    # Insights
    st.subheader("💡 Insights")
    
    st.info("""
    **Como interpretar:**
    - **Win Rate crescente** com confidence indica boa calibração
    - **ROI positivo** em todas as faixas indica edge consistente
    - **Amostras pequenas** (< 20 apostas) podem ter alta variância
    """)
