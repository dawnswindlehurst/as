"""Heatmap component for performance visualization."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional
import numpy as np


def performance_heatmap(
    data: Dict[str, Dict[str, float]],
    title: str = "🔥 Heatmap de Performance",
    metric: str = 'roi',
    height: int = 500,
    color_scale: str = 'RdYlGn'
):
    """Display performance heatmap.
    
    Args:
        data: Nested dict with row_label -> {col_label: value}
        title: Chart title
        metric: Metric name being displayed
        height: Chart height in pixels
        color_scale: Plotly color scale name
    """
    if not data:
        st.info("Nenhum dado disponível para heatmap")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(data).T
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=color_scale,
        text=df.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title=metric.upper()),
        hovertemplate='%{y} × %{x}<br>' + metric.upper() + ': %{z:.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title='',
        yaxis_title='',
        height=height,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def sport_market_heatmap(
    metrics_by_sport: Dict,
    metrics_by_market: Dict,
    metric_name: str = 'roi',
    title: str = "🎮 Esporte × Mercado",
    height: int = 600
):
    """Display sport vs market heatmap.
    
    Args:
        metrics_by_sport: Metrics segmented by sport
        metrics_by_market: Metrics segmented by market
        metric_name: Which metric to display
        title: Chart title
        height: Chart height in pixels
    """
    st.subheader(title)
    
    # Extract available sports and markets
    sports = list(metrics_by_sport.keys())
    markets = list(metrics_by_market.keys())
    
    if not sports or not markets:
        st.info("Dados insuficientes para heatmap")
        return
    
    # Create matrix
    matrix = []
    for sport in sports:
        row = []
        for market in markets:
            # This would need actual data from combined sport+market filtering
            # For now, use average of sport and market metrics
            sport_metric = metrics_by_sport[sport].get('basic', {}).get(metric_name, 0)
            market_metric = metrics_by_market[market].get('basic', {}).get(metric_name, 0)
            row.append((sport_metric + market_metric) / 2)
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=markets,
        y=sports,
        colorscale='RdYlGn',
        text=matrix,
        texttemplate='%{text:.1f}',
        textfont={"size": 9},
        colorbar=dict(title=metric_name.upper() + ' (%)'),
        hovertemplate='%{y} × %{x}<br>' + metric_name.upper() + ': %{z:.2f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title='Mercado',
        yaxis_title='Esporte',
        height=height,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def confidence_odds_heatmap(
    metrics_by_confidence: Dict,
    metrics_by_odds: Dict,
    metric_name: str = 'roi',
    title: str = "📊 Confidence × Odds",
    height: int = 500
):
    """Display confidence range vs odds range heatmap.
    
    Args:
        metrics_by_confidence: Metrics by confidence ranges
        metrics_by_odds: Metrics by odds ranges
        metric_name: Which metric to display
        title: Chart title
        height: Chart height in pixels
    """
    st.subheader(title)
    
    confidence_ranges = list(metrics_by_confidence.keys())
    odds_ranges = list(metrics_by_odds.keys())
    
    if not confidence_ranges or not odds_ranges:
        st.info("Dados insuficientes")
        return
    
    # Create matrix (simplified - would need actual combined filtering)
    matrix = []
    for conf in confidence_ranges:
        row = []
        for odds in odds_ranges:
            conf_metric = metrics_by_confidence[conf].get('basic', {}).get(metric_name, 0)
            odds_metric = metrics_by_odds[odds].get('basic', {}).get(metric_name, 0)
            row.append((conf_metric + odds_metric) / 2)
        matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=odds_ranges,
        y=confidence_ranges,
        colorscale='RdYlGn',
        text=matrix,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title=metric_name.upper() + ' (%)'),
        hovertemplate='Conf: %{y}<br>Odds: %{x}<br>' + metric_name.upper() + ': %{z:.2f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        xaxis_title='Faixa de Odds',
        yaxis_title='Faixa de Confidence',
        height=height,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def correlation_heatmap(
    metrics: Dict,
    variables: List[str],
    title: str = "🔗 Matriz de Correlação",
    height: int = 500
):
    """Display correlation matrix heatmap.
    
    Args:
        metrics: Metrics dictionary
        variables: List of variable names to correlate
        title: Chart title
        height: Chart height in pixels
    """
    st.subheader(title)
    
    # This would need actual bet-level data to calculate correlations
    # For now, show placeholder
    
    st.info("Matriz de correlação requer dados de apostas individuais")
    
    # Example correlation matrix (placeholder)
    example_corr = np.random.rand(len(variables), len(variables))
    np.fill_diagonal(example_corr, 1.0)
    
    fig = go.Figure(data=go.Heatmap(
        z=example_corr,
        x=variables,
        y=variables,
        colorscale='RdBu',
        zmid=0,
        text=example_corr,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title='Correlação'),
        hovertemplate='%{y} × %{x}<br>Corr: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=height,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
