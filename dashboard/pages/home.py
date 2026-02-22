"""Home page - overview and KPIs."""
import streamlit as st
from betting.analyzer import BetAnalyzer
from betting.tracker import BetTracker
from analysis.streaks import StreakAnalyzer
from utils.helpers import format_currency, format_percentage
from dashboard.components.sparkline import render_metric_with_sparkline, render_mini_chart
import asyncio
from datetime import datetime, timedelta


def show():
    """Display home page."""
    st.header("🏠 Overview & Dashboard")
    
    analyzer = BetAnalyzer()
    tracker = BetTracker()
    streak_analyzer = StreakAnalyzer()
    
    # Get overall stats
    stats = analyzer.get_overall_stats()
    
    # KPIs with sparklines
    st.subheader("📊 Principais Métricas")
    col1, col2, col3, col4 = st.columns(4)
    
    # Generate mock sparkline data (last 7 days)
    # In production, this would come from actual daily data
    bets_sparkline = [45, 48, 52, 49, 53, 51, stats.get("total_bets", 0)]
    winrate_sparkline = [0.52, 0.54, 0.53, 0.55, 0.54, 0.56, stats.get("win_rate", 0)]
    roi_sparkline = [0.08, 0.09, 0.085, 0.095, 0.092, 0.10, stats.get("roi", 0)]
    profit_sparkline = [800, 950, 1100, 1050, 1200, 1150, stats.get("total_profit", 0)]
    
    with col1:
        total_bets = stats.get("total_bets", 0)
        st.metric(
            "Total de Apostas",
            total_bets,
            delta="+3 (hoje)"
        )
        render_mini_chart(bets_sparkline[-7:], chart_type='line', height=80)
    
    with col2:
        win_rate = stats.get("win_rate", 0)
        st.metric(
            "Taxa de Acerto",
            format_percentage(win_rate),
            delta="+2.1%"
        )
        render_mini_chart([w * 100 for w in winrate_sparkline[-7:]], chart_type='line', height=80)
    
    with col3:
        roi = stats.get("roi", 0)
        st.metric(
            "ROI",
            format_percentage(roi),
            delta="+1.2%"
        )
        render_mini_chart([r * 100 for r in roi_sparkline[-7:]], chart_type='line', height=80)
    
    with col4:
        profit = stats.get("total_profit", 0)
        st.metric(
            "Lucro Total",
            format_currency(profit),
            delta=format_currency(150)
        )
        render_mini_chart(profit_sparkline[-7:], chart_type='bar', height=80)
    
    st.markdown("---")
    
    # Performance últimas 24h
    st.subheader("🔥 Performance Últimas 24 Horas")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Apostas", "12", delta="+5")
    
    with col2:
        st.metric("Vitórias", "8", delta="+3")
    
    with col3:
        st.metric("Win Rate", "66.7%", delta="+8.2%")
    
    with col4:
        st.metric("Lucro", "R$ 450,00", delta="+R$ 280,00")
    
    st.markdown("---")
    
    # System alerts
    st.subheader("⚠️ Alertas do Sistema")
    
    # Mock alerts
    alerts = [
        {"type": "success", "message": "✅ 3 value bets identificadas para hoje"},
        {"type": "info", "message": "ℹ️ Próxima partida importante: NAVI vs Team Liquid em 2h"},
        {"type": "warning", "message": "⚠️ API VLR.gg com latência acima do normal (850ms)"},
    ]
    
    for alert in alerts:
        if alert["type"] == "success":
            st.success(alert["message"])
        elif alert["type"] == "info":
            st.info(alert["message"])
        elif alert["type"] == "warning":
            st.warning(alert["message"])
    
    st.markdown("---")
    
    # Upcoming matches section
    st.subheader("⏰ Próximas Partidas (Hoje)")
    
    try:
        # Try to fetch upcoming matches
        from dashboard.components.live_match_card import render_compact_match_card
        
        # Mock upcoming matches (in production, fetch from Superbet API)
        upcoming_matches = generate_mock_upcoming_matches()
        
        if upcoming_matches:
            for match in upcoming_matches[:5]:
                render_compact_match_card(match)
        else:
            st.info("Nenhuma partida programada para hoje.")
    except Exception as e:
        st.info("Carregue a página 'Live Matches' para ver partidas ao vivo.")
    
    st.markdown("---")
    
    # Current streak
    st.subheader("📊 Streak e Estatísticas")
    
    col1, col2, col3 = st.columns(3)
    
    streak_info = streak_analyzer.get_current_streak()
    
    with col1:
        streak_type = streak_info.get("current_streak_type", "N/A")
        streak_count = streak_info.get("current_streak", 0)
        
        if streak_type == "Win":
            st.success(f"**Streak Atual:** {streak_count} vitórias 🔥")
        elif streak_type == "Loss":
            st.error(f"**Streak Atual:** {streak_count} derrotas")
        else:
            st.info(f"**Streak Atual:** N/A")
    
    with col2:
        longest_win = streak_info.get("longest_win_streak", 0)
        st.metric("Maior Streak de Vitórias", longest_win)
    
    with col3:
        longest_loss = streak_info.get("longest_loss_streak", 0)
        st.metric("Maior Streak de Derrotas", longest_loss)
    
    st.markdown("---")
    
    # Pending bets
    st.subheader("⏳ Apostas Pendentes")
    pending = tracker.get_unsettled_bets()
    
    if pending:
        st.warning(f"Você tem **{len(pending)}** apostas aguardando resultado")
        
        # Show recent pending bets
        with st.expander("Ver apostas pendentes"):
            for bet in pending[:5]:
                st.markdown(f"• {bet.get('match', 'N/A')} - {bet.get('market', 'N/A')}")
    else:
        st.success("✅ Nenhuma aposta pendente")
    
    # Recent stats by game
    st.markdown("---")
    st.subheader("🎮 Performance por Jogo")
    
    stats_by_game = analyzer.get_stats_by_game()
    
    if stats_by_game:
        for game, game_stats in stats_by_game.items():
            with st.expander(f"**{game}**"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Apostas", game_stats.get("total_bets", 0))
                
                with col2:
                    st.metric("Win Rate", format_percentage(game_stats.get("win_rate", 0)))
                
                with col3:
                    st.metric("ROI", format_percentage(game_stats.get("roi", 0)))
                
                with col4:
                    st.metric("Lucro", format_currency(game_stats.get("profit", 0)))
    else:
        st.info("Sem dados de apostas por jogo ainda")


def generate_mock_upcoming_matches():
    """Generate mock upcoming matches for demonstration."""
    now = datetime.now()
    
    return [
        {
            'team1': 'NAVI',
            'team2': 'Team Liquid',
            'sport_name': 'CS2',
            'tournament_name': 'IEM Katowice',
            'is_live': False,
            'start_time': (now + timedelta(hours=2)).isoformat(),
            'markets': [
                {
                    'market_name': 'Match Winner',
                    'odds_list': [
                        {'outcome_name': 'NAVI', 'odds': 1.85},
                        {'outcome_name': 'Team Liquid', 'odds': 2.10}
                    ]
                }
            ]
        },
        {
            'team1': 'OG',
            'team2': 'Team Secret',
            'sport_name': 'Dota 2',
            'tournament_name': 'DreamLeague',
            'is_live': False,
            'start_time': (now + timedelta(hours=4)).isoformat(),
            'markets': [
                {
                    'market_name': 'Match Winner',
                    'odds_list': [
                        {'outcome_name': 'OG', 'odds': 2.20},
                        {'outcome_name': 'Team Secret', 'odds': 1.75}
                    ]
                }
            ]
        },
        {
            'team1': 'Fnatic',
            'team2': 'Sentinels',
            'sport_name': 'Valorant',
            'tournament_name': 'VCT Americas',
            'is_live': False,
            'start_time': (now + timedelta(hours=6)).isoformat(),
            'markets': [
                {
                    'market_name': 'Match Winner',
                    'odds_list': [
                        {'outcome_name': 'Fnatic', 'odds': 1.95},
                        {'outcome_name': 'Sentinels', 'odds': 1.95}
                    ]
                }
            ]
        },
    ]
