"""API health status component."""

import streamlit as st
from typing import Dict, Any
from datetime import datetime


def render_api_status(health_results: Dict[str, Dict[str, Any]]):
    """
    Render API health status dashboard.
    
    Args:
        health_results: Dictionary mapping service names to health check results
    """
    if not health_results:
        st.warning("Nenhum resultado de health check disponível.")
        return
    
    # Overall health summary
    total = len(health_results)
    healthy = sum(1 for r in health_results.values() if r.get('is_healthy'))
    health_pct = (healthy / total * 100) if total > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de APIs", total)
    
    with col2:
        st.metric(
            "APIs Saudáveis",
            healthy,
            delta=f"{health_pct:.0f}%",
            delta_color="normal"
        )
    
    with col3:
        status_text = "✅ Operacional" if healthy == total else "⚠️ Degradado"
        status_color = "#28a745" if healthy == total else "#ffc107"
        st.markdown(
            f'<div style="padding: 1rem; background-color: {status_color}20; '
            f'border-left: 4px solid {status_color}; border-radius: 4px;">'
            f'<strong>{status_text}</strong></div>',
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Individual service status
    st.subheader("Status Individual")
    
    for service_name, result in health_results.items():
        is_healthy = result.get('is_healthy', False)
        status_code = result.get('status_code')
        response_time = result.get('response_time_ms')
        error_message = result.get('error_message')
        last_check = result.get('last_check')
        
        # Status indicator
        if is_healthy:
            status_icon = "✅"
            status_color = "#28a745"
            status_text = "Operacional"
        else:
            status_icon = "❌"
            status_color = "#dc3545"
            status_text = "Indisponível"
        
        # Service card
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"{status_icon} **{service_name}**")
            
            with col2:
                st.markdown(
                    f'<span style="color: {status_color};">{status_text}</span>',
                    unsafe_allow_html=True
                )
            
            with col3:
                if status_code:
                    st.caption(f"Status: {status_code}")
                else:
                    st.caption("Status: N/A")
            
            with col4:
                if response_time is not None:
                    # Color code response time
                    if response_time < 200:
                        time_color = "#28a745"
                    elif response_time < 500:
                        time_color = "#ffc107"
                    else:
                        time_color = "#dc3545"
                    
                    st.markdown(
                        f'<span style="color: {time_color};">{response_time:.0f}ms</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("Tempo: N/A")
            
            # Error message if any
            if error_message:
                st.error(f"Erro: {error_message}")
            
            # Last check time
            if last_check:
                try:
                    if isinstance(last_check, str):
                        check_dt = datetime.fromisoformat(last_check)
                    else:
                        check_dt = last_check
                    st.caption(f"Última verificação: {check_dt.strftime('%d/%m/%Y %H:%M:%S')}")
                except:
                    st.caption(f"Última verificação: {last_check}")
            
            st.markdown("---")


def render_api_metrics_summary(metrics: Dict[str, Any]):
    """
    Render summary metrics for API health.
    
    Args:
        metrics: Dictionary with aggregate metrics
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        uptime = metrics.get('uptime_percentage', 0)
        st.metric(
            "Uptime",
            f"{uptime:.1f}%",
            delta=None
        )
    
    with col2:
        avg_response = metrics.get('avg_response_time_ms', 0)
        st.metric(
            "Tempo Médio",
            f"{avg_response:.0f}ms",
            delta=None
        )
    
    with col3:
        total_requests = metrics.get('total_requests', 0)
        st.metric(
            "Requisições (24h)",
            f"{total_requests:,}",
            delta=None
        )
    
    with col4:
        error_rate = metrics.get('error_rate_percentage', 0)
        st.metric(
            "Taxa de Erro",
            f"{error_rate:.2f}%",
            delta=None,
            delta_color="inverse"
        )


def render_api_logs(logs: list, max_entries: int = 10):
    """
    Render recent API error logs.
    
    Args:
        logs: List of log entries
        max_entries: Maximum number of entries to display
    """
    st.subheader("Logs Recentes de Erros")
    
    if not logs:
        st.success("Nenhum erro registrado recentemente.")
        return
    
    # Display most recent logs
    for log in logs[:max_entries]:
        timestamp = log.get('timestamp', '')
        service = log.get('service', 'Unknown')
        message = log.get('message', '')
        level = log.get('level', 'ERROR')
        
        # Color code by level
        level_colors = {
            'ERROR': '#dc3545',
            'WARNING': '#ffc107',
            'INFO': '#17a2b8',
        }
        color = level_colors.get(level, '#6c757d')
        
        st.markdown(
            f'<div style="padding: 0.5rem; margin: 0.5rem 0; '
            f'border-left: 4px solid {color}; background-color: {color}20;">'
            f'<strong>[{level}]</strong> {service} - {timestamp}<br/>'
            f'{message}</div>',
            unsafe_allow_html=True
        )


def render_health_chart(history: list):
    """
    Render a chart showing API health over time.
    
    Args:
        history: List of historical health check results
    """
    import plotly.graph_objects as go
    
    if not history:
        st.info("Sem dados históricos disponíveis.")
        return
    
    # Prepare data
    timestamps = [entry.get('timestamp') for entry in history]
    health_scores = [entry.get('health_percentage', 0) for entry in history]
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=health_scores,
        mode='lines+markers',
        name='Health %',
        line=dict(color='#1E88E5', width=2),
        fill='tozeroy',
        fillcolor='rgba(30, 136, 229, 0.1)'
    ))
    
    # Add threshold line at 95%
    fig.add_hline(
        y=95,
        line_dash="dash",
        line_color="green",
        annotation_text="Target (95%)"
    )
    
    fig.update_layout(
        title="Histórico de Saúde das APIs",
        xaxis_title="Tempo",
        yaxis_title="Saúde (%)",
        yaxis=dict(range=[0, 100]),
        height=300,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
