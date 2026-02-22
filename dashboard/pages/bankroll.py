"""Bankroll management page - track and manage betting bankroll."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any


def show():
    """Display bankroll management page."""
    st.header("💰 Bankroll Management")
    st.markdown("Controle sua banca e gerencie stakes de forma inteligente")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "📈 Equity Curve",
        "⚙️ Configurações",
        "📉 Drawdown Analysis"
    ])
    
    with tab1:
        show_bankroll_overview()
    
    with tab2:
        show_equity_curve()
    
    with tab3:
        show_bankroll_settings()
    
    with tab4:
        show_drawdown_analysis()


def show_bankroll_overview():
    """Show bankroll overview."""
    st.subheader("Visão Geral da Banca")
    
    # Mock bankroll data
    bankroll_data = get_mock_bankroll_data()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Banca Atual",
            f"R$ {bankroll_data['current_bankroll']:,.2f}",
            delta=f"R$ {bankroll_data['daily_change']:+,.2f}"
        )
    
    with col2:
        st.metric(
            "Banca Inicial",
            f"R$ {bankroll_data['initial_bankroll']:,.2f}",
            delta=None
        )
    
    with col3:
        roi = bankroll_data['roi']
        st.metric(
            "ROI",
            f"{roi:.2f}%",
            delta=f"{roi:.2f}%",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "Stake Unit",
            f"R$ {bankroll_data['unit_size']:.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # Risk metrics
    st.subheader("⚠️ Métricas de Risco")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        max_drawdown = bankroll_data['max_drawdown']
        st.metric(
            "Drawdown Máximo",
            f"{max_drawdown:.2f}%",
            delta=None,
            delta_color="inverse"
        )
        
        # Warning if high
        if max_drawdown > 20:
            st.warning("⚠️ Drawdown acima do recomendado!")
    
    with col2:
        current_drawdown = bankroll_data['current_drawdown']
        st.metric(
            "Drawdown Atual",
            f"{current_drawdown:.2f}%",
            delta=None,
            delta_color="inverse"
        )
    
    with col3:
        risk_of_ruin = bankroll_data['risk_of_ruin']
        st.metric(
            "Risco de Ruína",
            f"{risk_of_ruin:.2f}%",
            delta=None,
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Stake distribution
    st.subheader("📊 Distribuição de Stakes")
    
    stakes_data = generate_stakes_distribution()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=list(stakes_data.keys()),
            values=list(stakes_data.values()),
            hole=0.3
        )
    ])
    
    fig.update_layout(
        title="Stakes por Categoria",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_equity_curve():
    """Show equity curve chart."""
    st.subheader("Curva de Equity")
    st.markdown("Evolução da banca ao longo do tempo")
    
    # Period selector
    period = st.selectbox(
        "Período",
        ["Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Todo período"]
    )
    
    # Generate equity curve data
    equity_data = generate_equity_curve(period)
    
    # Create chart
    fig = go.Figure()
    
    # Equity curve
    fig.add_trace(go.Scatter(
        x=equity_data['dates'],
        y=equity_data['equity'],
        mode='lines',
        name='Equity',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30, 136, 229, 0.1)'
    ))
    
    # Initial bankroll line
    fig.add_hline(
        y=equity_data['equity'][0],
        line_dash="dash",
        line_color="gray",
        annotation_text="Banca Inicial"
    )
    
    fig.update_layout(
        title="Evolução da Banca",
        xaxis_title="Data",
        yaxis_title="Banca (R$)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance summary
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_profit = equity_data['equity'][-1] - equity_data['equity'][0]
        st.metric("Lucro Total", f"R$ {total_profit:,.2f}")
    
    with col2:
        best_day = max(equity_data['daily_changes'])
        st.metric("Melhor Dia", f"R$ {best_day:,.2f}")
    
    with col3:
        worst_day = min(equity_data['daily_changes'])
        st.metric("Pior Dia", f"R$ {worst_day:,.2f}")
    
    with col4:
        avg_daily = sum(equity_data['daily_changes']) / len(equity_data['daily_changes'])
        st.metric("Média Diária", f"R$ {avg_daily:,.2f}")


def show_bankroll_settings():
    """Show bankroll configuration settings."""
    st.subheader("Configurações de Banca")
    
    # Current settings
    st.markdown("### 📝 Configuração Atual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_bankroll = st.number_input(
            "Banca Inicial (R$)",
            min_value=100.0,
            max_value=1000000.0,
            value=10000.0,
            step=100.0
        )
        
        unit_percentage = st.slider(
            "Tamanho da Unit (%)",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        
        max_stake_units = st.slider(
            "Stake Máximo (units)",
            min_value=1,
            max_value=10,
            value=5
        )
    
    with col2:
        kelly_fraction = st.slider(
            "Fração Kelly",
            min_value=0.1,
            max_value=1.0,
            value=0.25,
            step=0.05,
            help="Fração do critério de Kelly a usar (recomendado: 0.25)"
        )
        
        max_daily_risk = st.slider(
            "Risco Máximo Diário (%)",
            min_value=1,
            max_value=10,
            value=5
        )
        
        stop_loss_pct = st.slider(
            "Stop Loss (%)",
            min_value=5,
            max_value=50,
            value=20,
            help="Parar de apostar se a banca cair este percentual"
        )
    
    # Calculate derived values
    unit_size = initial_bankroll * (unit_percentage / 100)
    max_stake = unit_size * max_stake_units
    stop_loss_value = initial_bankroll * (stop_loss_pct / 100)
    
    st.markdown("---")
    st.markdown("### 📊 Valores Calculados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Unit Size:** R$ {unit_size:.2f}")
    
    with col2:
        st.info(f"**Stake Máximo:** R$ {max_stake:.2f}")
    
    with col3:
        st.warning(f"**Stop Loss:** R$ {stop_loss_value:.2f}")
    
    # Save button
    if st.button("💾 Salvar Configurações", type="primary"):
        st.success("✅ Configurações salvas com sucesso!")
        st.info("As novas configurações serão aplicadas nas próximas apostas.")
    
    # Information
    st.markdown("---")
    with st.expander("ℹ️ Sobre as Configurações"):
        st.markdown("""
        **Unit Size**: Valor base da sua aposta. Recomenda-se 1% da banca.
        
        **Fração Kelly**: Fração do Kelly Criterion a usar. 0.25 (Quarter Kelly) 
        é mais conservador e reduz a variância.
        
        **Risco Máximo Diário**: Limite de exposição em um único dia.
        
        **Stop Loss**: Proteção contra sequências negativas. Se a banca cair 
        este percentual, pare de apostar e reavalie sua estratégia.
        """)


def show_drawdown_analysis():
    """Show drawdown analysis."""
    st.subheader("Análise de Drawdown")
    st.markdown("Períodos de perda e recuperação")
    
    # Generate drawdown data
    drawdown_data = generate_drawdown_data()
    
    # Drawdown chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=drawdown_data['dates'],
        y=drawdown_data['drawdown'],
        mode='lines',
        name='Drawdown',
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.3)',
        line=dict(color='#dc3545', width=2)
    ))
    
    fig.update_layout(
        title="Drawdown ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Drawdown (%)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Drawdown periods table
    st.markdown("---")
    st.subheader("📋 Períodos de Drawdown")
    
    periods_data = [
        {
            'Início': '2024-01-10',
            'Fim': '2024-01-15',
            'Duração': '5 dias',
            'Drawdown Máx.': '12.5%',
            'Recuperado': 'Sim'
        },
        {
            'Início': '2024-01-20',
            'Fim': 'Em andamento',
            'Duração': '6 dias',
            'Drawdown Máx.': '5.2%',
            'Recuperado': 'Não'
        },
    ]
    
    df = pd.DataFrame(periods_data)
    st.dataframe(df, use_container_width=True)
    
    # Recovery metrics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tempo Médio de Recuperação", "8.5 dias")
    
    with col2:
        st.metric("Maior Drawdown", "15.3%")
    
    with col3:
        st.metric("Drawdowns Este Mês", "2")


def get_mock_bankroll_data() -> Dict[str, float]:
    """Get mock bankroll data."""
    return {
        'current_bankroll': 11250.00,
        'initial_bankroll': 10000.00,
        'daily_change': 150.00,
        'roi': 12.50,
        'unit_size': 112.50,
        'max_drawdown': 8.5,
        'current_drawdown': 2.3,
        'risk_of_ruin': 0.5,
    }


def generate_stakes_distribution() -> Dict[str, int]:
    """Generate mock stakes distribution."""
    return {
        '1 Unit': 45,
        '2 Units': 30,
        '3 Units': 15,
        '4 Units': 7,
        '5 Units': 3,
    }


def generate_equity_curve(period: str) -> Dict[str, List]:
    """Generate mock equity curve data."""
    period_map = {
        "Últimos 7 dias": 7,
        "Últimos 30 dias": 30,
        "Últimos 90 dias": 90,
        "Todo período": 180
    }
    days = period_map.get(period, 30)
    
    base_date = datetime.now() - timedelta(days=days)
    dates = [base_date + timedelta(days=i) for i in range(days)]
    
    # Generate equity curve with upward trend and some volatility
    equity = [10000]
    daily_changes = []
    
    for _ in range(1, days):
        change = (hash(str(_)) % 400) - 150  # Random daily change
        new_equity = equity[-1] + change
        equity.append(new_equity)
        daily_changes.append(change)
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'equity': equity,
        'daily_changes': daily_changes
    }


def generate_drawdown_data() -> Dict[str, List]:
    """Generate mock drawdown data."""
    days = 30
    base_date = datetime.now() - timedelta(days=days)
    dates = [base_date + timedelta(days=i) for i in range(days)]
    
    # Generate drawdown percentages (always negative or zero)
    drawdown = []
    max_equity = 10000
    current_equity = 10000
    
    for i in range(days):
        change = (hash(str(i)) % 400) - 150
        current_equity += change
        max_equity = max(max_equity, current_equity)
        
        dd = ((current_equity - max_equity) / max_equity * 100) if max_equity > 0 else 0
        drawdown.append(dd)
    
    return {
        'dates': [d.strftime('%Y-%m-%d') for d in dates],
        'drawdown': drawdown
    }
