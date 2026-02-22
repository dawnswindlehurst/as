"""Performance analysis page."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from betting.analyzer import BetAnalyzer
from validation.metrics import PerformanceMetrics
from utils.helpers import format_currency, format_percentage


def show():
    """Display performance page."""
    st.header("📈 Análise de Performance")
    
    analyzer = BetAnalyzer()
    metrics_calc = PerformanceMetrics()
    
    # Overall stats
    stats = analyzer.get_overall_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Apostas", stats.get("total_bets", 0))
    
    with col2:
        st.metric("Win Rate", format_percentage(stats.get("win_rate", 0)))
    
    with col3:
        st.metric("ROI", format_percentage(stats.get("roi", 0)))
    
    with col4:
        st.metric("Lucro Total", format_currency(stats.get("total_profit", 0)))
    
    st.markdown("---")
    
    # Performance metrics
    st.subheader("📊 Métricas Avançadas")
    
    all_metrics = metrics_calc.get_all_metrics()
    
    if all_metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sharpe Ratio", f"{all_metrics.get('sharpe_ratio', 0):.2f}")
        
        with col2:
            st.metric("Win/Loss Ratio", f"{all_metrics.get('win_loss_ratio', 0):.2f}")
        
        with col3:
            max_dd = all_metrics.get('max_drawdown', 0)
            st.metric("Max Drawdown", format_percentage(max_dd))
    
    st.markdown("---")
    
    # Performance by game
    st.subheader("🎮 Performance por Jogo")
    
    stats_by_game = analyzer.get_stats_by_game()
    
    if stats_by_game:
        game_data = []
        for game, game_stats in stats_by_game.items():
            game_data.append({
                "Jogo": game,
                "Apostas": game_stats.get("total_bets", 0),
                "Win Rate": game_stats.get("win_rate", 0),
                "ROI": game_stats.get("roi", 0),
                "Lucro": game_stats.get("total_profit", 0),
            })
        
        # Bar chart - ROI by game
        fig = px.bar(
            game_data,
            x="Jogo",
            y="ROI",
            title="ROI por Jogo",
            color="ROI",
            color_continuous_scale=["red", "yellow", "green"],
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(game_data, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados suficientes para análise por jogo")
    
    st.markdown("---")
    
    # Performance by confidence range
    st.subheader("🎯 Performance por Confidence Range")
    
    from config.constants import CONFIDENCE_RANGES
    stats_by_confidence = analyzer.get_stats_by_confidence(CONFIDENCE_RANGES)
    
    if stats_by_confidence:
        conf_data = []
        for range_name, conf_stats in stats_by_confidence.items():
            conf_data.append({
                "Range": range_name,
                "Apostas": conf_stats.get("total_bets", 0),
                "Win Rate": conf_stats.get("win_rate", 0),
                "ROI": conf_stats.get("roi", 0),
            })
        
        # Line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[d["Range"] for d in conf_data],
            y=[d["Win Rate"] for d in conf_data],
            mode='lines+markers',
            name='Win Rate',
            line=dict(color='blue'),
        ))
        fig.add_trace(go.Scatter(
            x=[d["Range"] for d in conf_data],
            y=[d["ROI"] for d in conf_data],
            mode='lines+markers',
            name='ROI',
            line=dict(color='green'),
            yaxis='y2',
        ))
        
        fig.update_layout(
            title="Win Rate e ROI por Confidence Range",
            xaxis_title="Confidence Range",
            yaxis_title="Win Rate",
            yaxis2=dict(title="ROI", overlaying='y', side='right'),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados suficientes para análise por confidence")
