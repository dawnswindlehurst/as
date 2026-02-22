"""Team rankings page - ELO/Glicko rankings by game."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta


def show():
    """Display rankings page."""
    st.header("🏆 Rankings de Times")
    st.markdown("Rankings ELO e Glicko-2 por jogo e região")
    
    # Game selection
    game = st.selectbox(
        "Selecione o Jogo",
        ["CS2", "Dota 2", "Valorant", "League of Legends"],
        key="rankings_game"
    )
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Rankings Atuais", "📈 Evolução", "🌍 Por Região"])
    
    with tab1:
        show_current_rankings(game)
    
    with tab2:
        show_rating_evolution(game)
    
    with tab3:
        show_regional_rankings(game)


def show_current_rankings(game: str):
    """Show current rankings table."""
    st.subheader(f"Rankings de {game}")
    
    # Rating system selector
    rating_system = st.radio(
        "Sistema de Rating",
        ["ELO", "Glicko-2", "Híbrido"],
        horizontal=True
    )
    
    # Mock data (replace with actual database query)
    rankings_data = generate_mock_rankings(game, rating_system)
    
    if rankings_data:
        df = pd.DataFrame(rankings_data)
        
        # Style the dataframe
        st.dataframe(
            df.style.background_gradient(
                subset=['Rating'],
                cmap='RdYlGn'
            ),
            use_container_width=True,
            height=600
        )
        
        # Stats summary
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_rating = df['Rating'].mean()
            st.metric("Rating Médio", f"{avg_rating:.0f}")
        
        with col2:
            top_rating = df['Rating'].max()
            st.metric("Rating Mais Alto", f"{top_rating:.0f}")
        
        with col3:
            total_teams = len(df)
            st.metric("Times Ranqueados", total_teams)
        
        with col4:
            # Calculate rating spread
            rating_spread = df['Rating'].std()
            st.metric("Desvio Padrão", f"{rating_spread:.0f}")
    
    else:
        st.info(f"Sem dados de ranking para {game} ainda.")


def show_rating_evolution(game: str):
    """Show rating evolution over time."""
    st.subheader("Evolução de Rating")
    
    # Team selection
    teams = ["Team Liquid", "NAVI", "FaZe Clan", "Fnatic", "G2 Esports"]
    selected_teams = st.multiselect(
        "Selecione Times",
        teams,
        default=teams[:3]
    )
    
    if not selected_teams:
        st.warning("Selecione pelo menos um time para visualizar.")
        return
    
    # Time period
    period = st.selectbox(
        "Período",
        ["Últimos 30 dias", "Últimos 90 dias", "Últimos 6 meses", "Último ano"]
    )
    
    # Generate mock evolution data
    evolution_data = generate_mock_evolution(selected_teams, period)
    
    # Create line chart
    fig = go.Figure()
    
    for team in selected_teams:
        if team in evolution_data:
            data = evolution_data[team]
            fig.add_trace(go.Scatter(
                x=data['dates'],
                y=data['ratings'],
                mode='lines+markers',
                name=team,
                line=dict(width=2),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title="Evolução de Rating ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Rating",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show recent form
    st.markdown("---")
    st.subheader("📊 Forma Recente")
    
    for team in selected_teams:
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.markdown(f"**{team}**")
        
        with col2:
            # Mock recent results
            form = "W W L W W"  # Win/Loss
            st.markdown(f"`{form}`")
        
        with col3:
            # Rating change
            change = "+45"  # Mock
            color = "green" if "+" in change else "red"
            st.markdown(f"<span style='color: {color};'>{change} pontos</span>", unsafe_allow_html=True)


def show_regional_rankings(game: str):
    """Show rankings by region."""
    st.subheader("Rankings por Região")
    
    # Region selection
    regions = ["América do Norte", "América do Sul", "Europa", "Ásia", "Oceania"]
    selected_region = st.selectbox("Região", regions)
    
    # Top N selector
    top_n = st.slider("Top N Times", min_value=5, max_value=20, value=10)
    
    # Mock data for selected region
    regional_data = generate_mock_regional_rankings(game, selected_region, top_n)
    
    if regional_data:
        df = pd.DataFrame(regional_data)
        
        # Display table
        st.dataframe(
            df.style.background_gradient(
                subset=['Rating'],
                cmap='Greens'
            ),
            use_container_width=True
        )
        
        # Regional comparison chart
        st.markdown("---")
        st.subheader("📊 Comparação Regional")
        
        # Generate data for all regions
        region_averages = {}
        for region in regions:
            # Mock average rating
            region_averages[region] = 1500 + (hash(region) % 300)
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(region_averages.keys()),
                y=list(region_averages.values()),
                marker_color='lightblue'
            )
        ])
        
        fig.update_layout(
            title="Rating Médio por Região",
            xaxis_title="Região",
            yaxis_title="Rating Médio",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info(f"Sem dados de ranking para {selected_region}.")


def generate_mock_rankings(game: str, rating_system: str) -> List[Dict[str, Any]]:
    """Generate mock ranking data."""
    teams = [
        "Team Liquid", "NAVI", "FaZe Clan", "Fnatic", "G2 Esports",
        "Vitality", "Astralis", "NIP", "FURIA", "Cloud9",
        "Team Spirit", "MOUZ", "Heroic", "OG", "Complexity"
    ]
    
    data = []
    base_rating = 1800
    
    for i, team in enumerate(teams):
        rating = base_rating - (i * 30) + (hash(team) % 50)
        data.append({
            'Posição': i + 1,
            'Time': team,
            'Rating': rating,
            'Partidas': 50 + (i * 2),
            'Vitórias': 30 - i,
            'Derrotas': 20 + i,
            'Win Rate': f"{((30-i)/(50+i*2)*100):.1f}%",
            'Forma': "W L W W L"[:(i % 5) * 2 + 3]
        })
    
    return data


def generate_mock_evolution(teams: List[str], period: str) -> Dict[str, Dict]:
    """Generate mock evolution data."""
    # Determine number of data points based on period
    period_map = {
        "Últimos 30 dias": 30,
        "Últimos 90 dias": 90,
        "Últimos 6 meses": 180,
        "Último ano": 365
    }
    days = period_map.get(period, 30)
    
    evolution = {}
    base_date = datetime.now() - timedelta(days=days)
    
    for team in teams:
        dates = [base_date + timedelta(days=i) for i in range(0, days, max(1, days // 20))]
        base_rating = 1600 + (hash(team) % 400)
        
        # Generate ratings with some variation
        ratings = []
        current_rating = base_rating
        for _ in dates:
            change = (hash(str(_) + team) % 100) - 50
            current_rating += change
            ratings.append(current_rating)
        
        evolution[team] = {
            'dates': [d.strftime('%Y-%m-%d') for d in dates],
            'ratings': ratings
        }
    
    return evolution


def generate_mock_regional_rankings(
    game: str,
    region: str,
    top_n: int
) -> List[Dict[str, Any]]:
    """Generate mock regional ranking data."""
    # Regional teams (simplified)
    regional_teams = {
        "América do Norte": ["Team Liquid", "Cloud9", "EG", "NRG", "100 Thieves"],
        "América do Sul": ["FURIA", "MIBR", "Imperial", "paiN Gaming", "Fluxo"],
        "Europa": ["NAVI", "FaZe Clan", "Fnatic", "G2", "Vitality"],
        "Ásia": ["TYLOO", "Lynn Vision", "RARE Atom", "Wings Up", "IHC"],
        "Oceania": ["Grayhound", "Rooster", "ORDER", "Ground Zero", "Vivo Keyd"]
    }
    
    teams = regional_teams.get(region, [])[:top_n]
    
    data = []
    base_rating = 1700
    
    for i, team in enumerate(teams):
        rating = base_rating - (i * 25)
        data.append({
            'Posição': i + 1,
            'Time': team,
            'Rating': rating,
            'País': "Brasil" if region == "América do Sul" else "EUA",
            'Partidas': 45 + i,
            'Win Rate': f"{(65-i*2):.1f}%"
        })
    
    return data
