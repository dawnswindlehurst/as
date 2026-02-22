"""Metric card component for displaying individual metrics."""
import streamlit as st
from typing import Optional


def metric_card(
    title: str,
    value: any,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    help_text: Optional[str] = None,
    icon: Optional[str] = None
):
    """Display a metric card with optional icon and delta.
    
    Args:
        title: Metric title
        value: Metric value
        delta: Change/comparison value
        delta_color: Color for delta ('normal', 'inverse', 'off')
        help_text: Tooltip help text
        icon: Optional emoji icon to display
    """
    # Format value
    if isinstance(value, float):
        if abs(value) >= 1000:
            formatted_value = f"{value:,.0f}"
        elif abs(value) >= 10:
            formatted_value = f"{value:.1f}"
        else:
            formatted_value = f"{value:.2f}"
    else:
        formatted_value = str(value)
    
    # Display with icon if provided
    display_title = f"{icon} {title}" if icon else title
    
    # Use streamlit metric
    st.metric(
        label=display_title,
        value=formatted_value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def metrics_row(metrics_list: list):
    """Display multiple metrics in a row.
    
    Args:
        metrics_list: List of dictionaries with metric parameters
    """
    if not metrics_list:
        return
    
    cols = st.columns(len(metrics_list))
    
    for col, metric_params in zip(cols, metrics_list):
        with col:
            metric_card(**metric_params)


def metric_card_custom(
    title: str,
    value: any,
    subtitle: Optional[str] = None,
    color: str = "#1E88E5",
    icon: Optional[str] = None
):
    """Display a custom styled metric card.
    
    Args:
        title: Metric title
        value: Metric value
        subtitle: Optional subtitle text
        color: Card accent color
        icon: Optional emoji icon
    """
    # Format value
    if isinstance(value, float):
        if abs(value) >= 1000:
            formatted_value = f"{value:,.0f}"
        elif abs(value) >= 10:
            formatted_value = f"{value:.1f}"
        else:
            formatted_value = f"{value:.2f}"
    else:
        formatted_value = str(value)
    
    icon_display = f'<div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ''
    subtitle_display = f'<div style="font-size: 0.875rem; color: #666; margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ''
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {color}15 0%, {color}05 100%);
        border-left: 4px solid {color};
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 0.5rem 0;
    ">
        {icon_display}
        <div style="font-size: 0.875rem; color: #666; font-weight: 500; margin-bottom: 0.25rem;">
            {title}
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: {color};">
            {formatted_value}
        </div>
        {subtitle_display}
    </div>
    """, unsafe_allow_html=True)


def metrics_grid(metrics_data: dict, columns: int = 3):
    """Display metrics in a grid layout.
    
    Args:
        metrics_data: Dictionary with metric name as key and parameters as value
        columns: Number of columns in the grid
    """
    metrics_list = list(metrics_data.items())
    
    # Create rows
    for i in range(0, len(metrics_list), columns):
        cols = st.columns(columns)
        row_metrics = metrics_list[i:i+columns]
        
        for col, (name, params) in zip(cols, row_metrics):
            with col:
                if isinstance(params, dict):
                    metric_card(**params)
                else:
                    metric_card(title=name, value=params)
