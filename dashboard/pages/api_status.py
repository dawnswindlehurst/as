"""API status page - health monitoring for all APIs."""

import streamlit as st
import asyncio
from datetime import datetime

from dashboard.components.api_health import (
    render_api_status,
    render_api_metrics_summary,
    render_api_logs,
    render_health_chart
)
from utils.api_health import quick_health_check


def show():
    """Display API status page."""
    st.header("📱 Status das APIs")
    st.markdown("Monitoramento de saúde e performance das integrações")
    
    # Refresh button
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Atualizar Status", type="primary"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (60s)", value=False)
    
    st.markdown("---")
    
    # Fetch health status
    with st.spinner("Verificando status das APIs..."):
        try:
            health_results = asyncio.run(quick_health_check())
            
            # Convert to dict format
            health_dict = {
                name: result.to_dict() if hasattr(result, 'to_dict') else result
                for name, result in health_results.items()
            }
            
            # Render status
            render_api_status(health_dict)
            
        except Exception as e:
            st.error(f"Erro ao verificar status das APIs: {str(e)}")
            st.info("Algumas APIs podem estar temporariamente indisponíveis.")
    
    st.markdown("---")
    
    # Metrics summary (mock data for now)
    st.subheader("📊 Métricas Agregadas (Últimas 24h)")
    
    mock_metrics = {
        'uptime_percentage': 99.2,
        'avg_response_time_ms': 245,
        'total_requests': 15420,
        'error_rate_percentage': 0.8,
    }
    
    render_api_metrics_summary(mock_metrics)
    
    st.markdown("---")
    
    # Error logs (mock data)
    st.subheader("🚨 Logs Recentes")
    
    mock_logs = [
        {
            'timestamp': '2024-01-26 16:45:23',
            'service': 'VLR.gg',
            'level': 'WARNING',
            'message': 'Rate limit approaching (80% of quota used)',
        },
        {
            'timestamp': '2024-01-26 15:30:12',
            'service': 'OpenDota',
            'level': 'INFO',
            'message': 'API response time increased to 450ms',
        },
    ]
    
    render_api_logs(mock_logs, max_entries=5)
    
    st.markdown("---")
    
    # Historical health chart (mock data)
    st.subheader("📈 Histórico de Saúde")
    
    mock_history = [
        {'timestamp': '00:00', 'health_percentage': 100},
        {'timestamp': '04:00', 'health_percentage': 100},
        {'timestamp': '08:00', 'health_percentage': 98},
        {'timestamp': '12:00', 'health_percentage': 97},
        {'timestamp': '16:00', 'health_percentage': 99},
        {'timestamp': '20:00', 'health_percentage': 100},
    ]
    
    render_health_chart(mock_history)
    
    # API details
    st.markdown("---")
    with st.expander("ℹ️ Detalhes das APIs"):
        st.markdown("""
        ### APIs Integradas
        
        **VLR.gg**
        - Fonte: Dados de Valorant
        - Endpoint: https://www.vlr.gg
        - Método: Web scraping
        
        **HLTV**
        - Fonte: Dados de CS:GO/CS2
        - Endpoint: https://www.hltv.org
        - Método: Web scraping
        
        **OpenDota**
        - Fonte: Dados de Dota 2
        - Endpoint: https://api.opendota.com/api
        - Método: REST API
        
        **Superbet**
        - Fonte: Odds de apostas
        - Endpoint: https://production-superbet-offer-br.freetls.fastly.net
        - Método: REST API
        
        ### Limites de Taxa
        
        - **VLR.gg**: ~30 requisições/minuto
        - **HLTV**: ~20 requisições/minuto
        - **OpenDota**: 60 requisições/minuto (sem chave)
        - **Superbet**: Sem limite conhecido
        
        ### Tempo de Resposta Esperado
        
        - **Ótimo**: < 200ms
        - **Aceitável**: 200-500ms
        - **Lento**: 500-1000ms
        - **Crítico**: > 1000ms
        """)
    
    # Auto-refresh logic using Streamlit's rerun with time check
    if auto_refresh:
        # Store last refresh time in session state
        if 'api_status_last_refresh' not in st.session_state:
            st.session_state.api_status_last_refresh = datetime.now()
        
        # Check if 60 seconds have passed
        time_diff = (datetime.now() - st.session_state.api_status_last_refresh).total_seconds()
        if time_diff >= 60:
            st.session_state.api_status_last_refresh = datetime.now()
            st.rerun()
    
    # Last update
    st.caption(f"Última verificação: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
