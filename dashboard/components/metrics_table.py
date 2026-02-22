"""Metrics table component for displaying segmented data."""
import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


def metrics_table(
    data: Dict[str, Dict],
    title: Optional[str] = None,
    sort_by: str = 'roi',
    ascending: bool = False,
    show_top_n: Optional[int] = None,
    highlight_best: bool = True
):
    """Display a table of metrics segmented by dimension.
    
    Args:
        data: Dictionary with segment name as key and metrics dict as value
        title: Optional table title
        sort_by: Column to sort by
        ascending: Sort order
        show_top_n: Show only top N rows
        highlight_best: Highlight best performing rows
    """
    if not data:
        st.info("Nenhum dado disponível")
        return
    
    if title:
        st.subheader(title)
    
    # Convert to DataFrame
    rows = []
    for segment_name, metrics in data.items():
        row = {'Segmento': segment_name}
        
        # Extract basic metrics if available
        if 'basic' in metrics:
            basic = metrics['basic']
            row.update({
                'Apostas': basic.get('total_bets', 0),
                'Win Rate (%)': basic.get('win_rate', 0),
                'ROI (%)': basic.get('roi', 0),
                'Lucro (R$)': basic.get('profit', 0),
                'Yield/Bet (R$)': basic.get('yield_per_bet', 0),
            })
        
        # Extract risk metrics if available
        if 'risk' in metrics:
            risk = metrics['risk']
            row.update({
                'Sharpe': risk.get('sharpe_ratio', 0),
                'Max DD (%)': risk.get('max_drawdown', 0),
            })
        
        # Extract CLV if available
        if 'clv' in metrics:
            clv = metrics['clv']
            row.update({
                'CLV Médio': clv.get('clv_average', 0),
                'CLV+ (%)': clv.get('clv_positive_rate', 0),
            })
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Sort
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=ascending)
    
    # Show top N
    if show_top_n:
        df = df.head(show_top_n)
    
    # Format columns
    if 'Win Rate (%)' in df.columns:
        df['Win Rate (%)'] = df['Win Rate (%)'].apply(lambda x: f"{x:.1f}%")
    if 'ROI (%)' in df.columns:
        df['ROI (%)'] = df['ROI (%)'].apply(lambda x: f"{x:.1f}%")
    if 'Lucro (R$)' in df.columns:
        df['Lucro (R$)'] = df['Lucro (R$)'].apply(lambda x: f"R$ {x:.2f}")
    if 'Yield/Bet (R$)' in df.columns:
        df['Yield/Bet (R$)'] = df['Yield/Bet (R$)'].apply(lambda x: f"R$ {x:.2f}")
    if 'Sharpe' in df.columns:
        df['Sharpe'] = df['Sharpe'].apply(lambda x: f"{x:.2f}")
    if 'Max DD (%)' in df.columns:
        df['Max DD (%)'] = df['Max DD (%)'].apply(lambda x: f"{x:.1f}%")
    if 'CLV Médio' in df.columns:
        df['CLV Médio'] = df['CLV Médio'].apply(lambda x: f"{x:.4f}")
    if 'CLV+ (%)' in df.columns:
        df['CLV+ (%)'] = df['CLV+ (%)'].apply(lambda x: f"{x:.1f}%")
    
    # Display table
    st.dataframe(df, use_container_width=True, hide_index=True)


def comparison_table(
    data: List[Dict],
    columns: List[str],
    title: Optional[str] = None
):
    """Display a comparison table with custom columns.
    
    Args:
        data: List of dictionaries with row data
        columns: List of column names to display
        title: Optional table title
    """
    if not data:
        st.info("Nenhum dado disponível")
        return
    
    if title:
        st.subheader(title)
    
    df = pd.DataFrame(data)
    
    # Filter to requested columns
    available_cols = [col for col in columns if col in df.columns]
    if available_cols:
        df = df[available_cols]
    
    st.dataframe(df, use_container_width=True, hide_index=True)


def ranked_table(
    data: Dict[str, float],
    title: str,
    value_label: str = "Valor",
    top_n: int = 10,
    show_rank: bool = True,
    color_scale: bool = True
):
    """Display a ranked table (top performers).
    
    Args:
        data: Dictionary with item name and value
        title: Table title
        value_label: Label for value column
        top_n: Number of top items to show
        show_rank: Show rank column
        color_scale: Apply color gradient
    """
    if not data:
        st.info("Nenhum dado disponível")
        return
    
    st.subheader(title)
    
    # Sort by value
    sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    # Create DataFrame
    rows = []
    for i, (name, value) in enumerate(sorted_items, 1):
        row = {}
        if show_rank:
            # Add medal emojis for top 3
            if i == 1:
                row['Rank'] = '🥇'
            elif i == 2:
                row['Rank'] = '🥈'
            elif i == 3:
                row['Rank'] = '🥉'
            else:
                row['Rank'] = f'{i}°'
        
        row['Item'] = name
        row[value_label] = value
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Apply styling if color_scale
    if color_scale:
        # Convert to styled dataframe
        st.dataframe(
            df.style.background_gradient(
                subset=[value_label],
                cmap='RdYlGn'
            ),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def summary_table(metrics: Dict, sections: List[str] = None):
    """Display a summary table of all metrics.
    
    Args:
        metrics: Complete metrics dictionary
        sections: List of metric sections to include (None = all)
    """
    st.subheader("📊 Resumo de Métricas")
    
    if sections is None:
        sections = ['basic', 'risk', 'calibration', 'clv', 'streaks', 'bankroll']
    
    rows = []
    
    # Basic metrics
    if 'basic' in sections and 'basic' in metrics:
        basic = metrics['basic']
        rows.extend([
            {'Categoria': 'Performance', 'Métrica': 'Total de Apostas', 'Valor': basic.get('total_bets', 0)},
            {'Categoria': 'Performance', 'Métrica': 'Win Rate', 'Valor': f"{basic.get('win_rate', 0):.1f}%"},
            {'Categoria': 'Performance', 'Métrica': 'ROI', 'Valor': f"{basic.get('roi', 0):.2f}%"},
            {'Categoria': 'Performance', 'Métrica': 'Lucro Total', 'Valor': f"R$ {basic.get('profit', 0):.2f}"},
        ])
    
    # Risk metrics
    if 'risk' in sections and 'risk' in metrics:
        risk = metrics['risk']
        rows.extend([
            {'Categoria': 'Risco', 'Métrica': 'Sharpe Ratio', 'Valor': f"{risk.get('sharpe_ratio', 0):.3f}"},
            {'Categoria': 'Risco', 'Métrica': 'Max Drawdown', 'Valor': f"{risk.get('max_drawdown', 0):.2f}%"},
            {'Categoria': 'Risco', 'Métrica': 'Volatilidade', 'Valor': f"{risk.get('volatility', 0):.2f}%"},
        ])
    
    # Calibration metrics
    if 'calibration' in sections and 'calibration' in metrics:
        cal = metrics['calibration']
        rows.extend([
            {'Categoria': 'Calibração', 'Métrica': 'Brier Score', 'Valor': f"{cal.get('brier_score', 0):.4f}"},
            {'Categoria': 'Calibração', 'Métrica': 'Log Loss', 'Valor': f"{cal.get('log_loss', 0):.4f}"},
        ])
    
    # CLV metrics
    if 'clv' in sections and 'clv' in metrics:
        clv = metrics['clv']
        rows.extend([
            {'Categoria': 'CLV', 'Métrica': 'CLV Médio', 'Valor': f"{clv.get('clv_average', 0):.4f}"},
            {'Categoria': 'CLV', 'Métrica': 'Taxa CLV+', 'Valor': f"{clv.get('clv_positive_rate', 0):.1f}%"},
        ])
    
    # Bankroll metrics
    if 'bankroll' in sections and 'bankroll' in metrics:
        bank = metrics['bankroll']
        rows.extend([
            {'Categoria': 'Bankroll', 'Métrica': 'Crescimento', 'Valor': f"{bank.get('bankroll_growth', 0):.2f}%"},
            {'Categoria': 'Bankroll', 'Métrica': 'Unidades Ganhas', 'Valor': f"{bank.get('units_won', 0):.2f}"},
        ])
    
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma métrica disponível")
