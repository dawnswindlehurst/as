"""Equity curve chart component."""
import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Optional
import pandas as pd


def equity_chart(
    equity_data: List[Dict],
    title: str = "📈 Curva de Equity",
    initial_bankroll: float = 1000.0,
    show_drawdown: bool = True,
    height: int = 400
):
    """Display equity curve chart.
    
    Args:
        equity_data: List of {'date': datetime, 'bankroll': float} dicts
        title: Chart title
        initial_bankroll: Starting bankroll
        show_drawdown: Show drawdown shaded area
        height: Chart height in pixels
    """
    if not equity_data or len(equity_data) < 2:
        st.info("Dados insuficientes para gráfico de equity")
        return
    
    # Create DataFrame
    df = pd.DataFrame(equity_data)
    
    # Calculate drawdown if requested
    if show_drawdown:
        # Calculate running maximum
        df['peak'] = df['bankroll'].cummax()
        df['drawdown'] = df['bankroll'] - df['peak']
    
    # Create figure
    fig = go.Figure()
    
    # Add equity line
    fig.add_trace(go.Scatter(
        x=df['date'] if 'date' in df.columns else list(range(len(df))),
        y=df['bankroll'],
        mode='lines',
        name='Equity',
        line=dict(color='#1E88E5', width=2.5),
        fill='tonexty',
        fillcolor='rgba(30, 136, 229, 0.1)'
    ))
    
    # Add initial bankroll line
    fig.add_hline(
        y=initial_bankroll,
        line_dash="dash",
        line_color="gray",
        annotation_text="Bankroll Inicial",
        annotation_position="right"
    )
    
    # Add drawdown area if enabled
    if show_drawdown and 'drawdown' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['date'] if 'date' in df.columns else list(range(len(df))),
            y=df['drawdown'],
            mode='lines',
            name='Drawdown',
            line=dict(color='#F44336', width=1),
            fill='tozeroy',
            fillcolor='rgba(244, 67, 54, 0.2)',
            yaxis='y2'
        ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Data' if 'date' in df.columns else 'Apostas',
        yaxis_title='Bankroll (R$)',
        height=height,
        hovermode='x unified',
        showlegend=True,
        template='plotly_white'
    )
    
    # Add second y-axis for drawdown if shown
    if show_drawdown:
        fig.update_layout(
            yaxis2=dict(
                title='Drawdown (R$)',
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    
    st.plotly_chart(fig, use_container_width=True)


def profit_chart(
    bets_data: List[Dict],
    title: str = "💰 Evolução do Lucro",
    show_cumulative: bool = True,
    height: int = 400
):
    """Display profit evolution chart.
    
    Args:
        bets_data: List of bet dictionaries with 'profit' and 'settled_at'
        title: Chart title
        show_cumulative: Show cumulative profit
        height: Chart height in pixels
    """
    if not bets_data:
        st.info("Nenhum dado disponível")
        return
    
    # Sort by date
    sorted_bets = sorted(bets_data, key=lambda x: x.get('settled_at', ''))
    
    # Calculate cumulative profit
    cumulative = []
    total = 0
    for bet in sorted_bets:
        total += bet.get('profit', 0)
        cumulative.append(total)
    
    # Create figure
    fig = go.Figure()
    
    if show_cumulative:
        # Cumulative profit line
        fig.add_trace(go.Scatter(
            x=[bet.get('settled_at', i) for i, bet in enumerate(sorted_bets)],
            y=cumulative,
            mode='lines',
            name='Lucro Acumulado',
            line=dict(color='#00C853', width=2.5),
            fill='tozeroy',
            fillcolor='rgba(0, 200, 83, 0.1)'
        ))
    else:
        # Individual bet profits
        profits = [bet.get('profit', 0) for bet in sorted_bets]
        colors = ['#00C853' if p > 0 else '#F44336' for p in profits]
        
        fig.add_trace(go.Bar(
            x=[bet.get('settled_at', i) for i, bet in enumerate(sorted_bets)],
            y=profits,
            name='Lucro',
            marker_color=colors
        ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Data',
        yaxis_title='Lucro (R$)',
        height=height,
        hovermode='x unified',
        showlegend=True,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def rolling_roi_chart(
    bets_data: List[Dict],
    window: int = 20,
    title: str = "📊 ROI Rolling",
    height: int = 400
):
    """Display rolling ROI chart.
    
    Args:
        bets_data: List of bet dictionaries
        window: Rolling window size
        title: Chart title
        height: Chart height in pixels
    """
    if not bets_data or len(bets_data) < window:
        st.info(f"Dados insuficientes (mínimo {window} apostas)")
        return
    
    # Sort by date
    sorted_bets = sorted(bets_data, key=lambda x: x.get('settled_at', ''))
    
    # Calculate rolling ROI
    rolling_roi = []
    for i in range(window, len(sorted_bets) + 1):
        window_bets = sorted_bets[i-window:i]
        total_stake = sum(b.get('stake', 0) for b in window_bets)
        total_profit = sum(b.get('profit', 0) for b in window_bets)
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        rolling_roi.append(roi)
    
    # Create figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[sorted_bets[i+window-1].get('settled_at', i+window-1) for i in range(len(rolling_roi))],
        y=rolling_roi,
        mode='lines',
        name=f'ROI ({window} apostas)',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='Data',
        yaxis_title='ROI (%)',
        height=height,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
