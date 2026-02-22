"""Chart components for dashboard."""
import plotly.graph_objects as go
import plotly.express as px


def create_roi_chart(data):
    """Create ROI comparison chart.
    
    Args:
        data: List of dictionaries with chart data
        
    Returns:
        Plotly figure
    """
    fig = px.bar(
        data,
        x="category",
        y="roi",
        title="ROI Comparison",
        color="roi",
        color_continuous_scale=["red", "yellow", "green"],
    )
    return fig


def create_equity_curve(equity_data):
    """Create equity curve chart.
    
    Args:
        equity_data: List of equity values over time
        
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=equity_data,
        mode='lines',
        name='Equity',
        line=dict(color='green', width=2),
    ))
    
    fig.update_layout(
        title="Curva de Equity",
        xaxis_title="Aposta #",
        yaxis_title="Lucro Acumulado (R$)",
        hovermode='x',
    )
    
    return fig


def create_win_rate_by_odds(data):
    """Create win rate by odds range chart.
    
    Args:
        data: List of dictionaries with odds ranges and win rates
        
    Returns:
        Plotly figure
    """
    fig = px.line(
        data,
        x="odds_range",
        y="win_rate",
        title="Win Rate por Faixa de Odds",
        markers=True,
    )
    return fig
