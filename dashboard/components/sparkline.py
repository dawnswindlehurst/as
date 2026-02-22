"""Sparkline chart component for KPIs."""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Optional


def render_sparkline(
    data: List[float],
    width: int = 150,
    height: int = 50,
    color: str = "#1E88E5",
    show_trend: bool = True
):
    """
    Render a sparkline chart (small inline chart).
    
    Args:
        data: List of numeric values
        width: Chart width in pixels
        height: Chart height in pixels
        color: Line color
        show_trend: Whether to show trend indicator
    """
    if not data or len(data) < 2:
        return
    
    # Create sparkline
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba(30, 136, 229, 0.1)',
        hoverinfo='y'
    ))
    
    # Update layout for minimal appearance
    fig.update_layout(
        showlegend=False,
        height=height,
        width=width,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False
        ),
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False})
    
    # Show trend indicator
    if show_trend and len(data) >= 2:
        trend = data[-1] - data[0]
        trend_pct = (trend / data[0] * 100) if data[0] != 0 else 0
        
        if trend > 0:
            st.markdown(f'<span style="color: #28a745;">↑ +{trend_pct:.1f}%</span>', unsafe_allow_html=True)
        elif trend < 0:
            st.markdown(f'<span style="color: #dc3545;">↓ {trend_pct:.1f}%</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span style="color: #6c757d;">→ 0%</span>', unsafe_allow_html=True)


def render_metric_with_sparkline(
    label: str,
    value: str,
    sparkline_data: List[float],
    delta: Optional[str] = None,
    delta_color: str = "normal"
):
    """
    Render a metric card with embedded sparkline.
    
    Args:
        label: Metric label
        value: Current metric value
        sparkline_data: Historical data for sparkline
        delta: Change indicator text
        delta_color: Color for delta (normal, inverse, off)
    """
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.metric(
            label=label,
            value=value,
            delta=delta,
            delta_color=delta_color
        )
    
    with col2:
        if sparkline_data:
            render_sparkline(sparkline_data, width=100, height=40, show_trend=False)


def render_mini_chart(
    data: List[float],
    labels: Optional[List[str]] = None,
    chart_type: str = 'line',
    height: int = 100
):
    """
    Render a small chart (larger than sparkline but still compact).
    
    Args:
        data: Numeric data
        labels: X-axis labels
        chart_type: 'line' or 'bar'
        height: Chart height in pixels
    """
    if not data:
        return
    
    fig = go.Figure()
    
    x_values = labels if labels else list(range(len(data)))
    
    if chart_type == 'line':
        fig.add_trace(go.Scatter(
            x=x_values,
            y=data,
            mode='lines+markers',
            line=dict(color='#1E88E5', width=2),
            marker=dict(size=6)
        ))
    elif chart_type == 'bar':
        fig.add_trace(go.Bar(
            x=x_values,
            y=data,
            marker_color='#1E88E5'
        ))
    
    fig.update_layout(
        showlegend=False,
        height=height,
        margin=dict(l=30, r=10, t=10, b=30),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_trend_indicator(
    current: float,
    previous: float,
    format_as_percentage: bool = False,
    show_value: bool = True
):
    """
    Render a simple trend indicator comparing two values.
    
    Args:
        current: Current value
        previous: Previous value
        format_as_percentage: Whether to format as percentage
        show_value: Whether to show the actual change value
    """
    if previous == 0:
        return
    
    change = current - previous
    change_pct = (change / previous * 100)
    
    if change > 0:
        icon = "↑"
        color = "#28a745"
    elif change < 0:
        icon = "↓"
        color = "#dc3545"
    else:
        icon = "→"
        color = "#6c757d"
    
    if show_value:
        if format_as_percentage:
            text = f"{icon} {abs(change_pct):.1f}%"
        else:
            text = f"{icon} {abs(change):.2f} ({abs(change_pct):.1f}%)"
    else:
        text = f"{icon} {abs(change_pct):.1f}%"
    
    st.markdown(f'<span style="color: {color}; font-weight: bold;">{text}</span>', unsafe_allow_html=True)
