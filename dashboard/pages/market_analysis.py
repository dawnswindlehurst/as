"""Market analysis page for detailed market performance."""
import streamlit as st
from analysis.metrics.aggregator import MetricsAggregator
from config.paper_trading import MARKETS, SPORTS
from dashboard.components.metrics_table import metrics_table, comparison_table
from dashboard.components.equity_chart import equity_chart, profit_chart
from dashboard.components.heatmap import performance_heatmap
from dashboard.components.metric_card import metrics_grid


def show():
    """Display market analysis page."""
    st.title("🎯 Análise Detalhada por Mercado")
    st.markdown("Análise profunda de performance em diferentes mercados de apostas")
    
    try:
        # Initialize aggregator
        aggregator = MetricsAggregator()
        
        # Market selector
        st.sidebar.subheader("⚙️ Filtros")
        
        selected_markets = st.sidebar.multiselect(
            "Selecionar Mercados",
            options=list(MARKETS.keys()),
            default=list(MARKETS.keys())[:5]
        )
        
        selected_sports = st.sidebar.multiselect(
            "Selecionar Esportes",
            options=list(SPORTS.keys()),
            default=list(SPORTS.keys())
        )
        
        min_bets = st.sidebar.slider(
            "Mínimo de Apostas",
            min_value=1,
            max_value=50,
            value=5,
            help="Mostrar apenas mercados com pelo menos N apostas"
        )
        
        st.markdown("---")
        
        # Overview section
        _display_market_overview(aggregator, selected_markets, min_bets)
        
        st.markdown("---")
        
        # Comparison section
        _display_market_comparison(aggregator, selected_markets, min_bets)
        
        st.markdown("---")
        
        # Deep dive on specific market
        _display_market_deep_dive(aggregator, selected_markets)
        
        st.markdown("---")
        
        # Sport × Market analysis
        _display_sport_market_analysis(aggregator, selected_sports, selected_markets)
        
    except Exception as e:
        st.error(f"Erro ao carregar análise: {str(e)}")
        st.info("Certifique-se de que existem apostas confirmadas.")


def _display_market_overview(aggregator: MetricsAggregator, markets: list, min_bets: int):
    """Display market overview section."""
    st.header("📊 Visão Geral dos Mercados")
    
    # Calculate metrics for all markets
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    # Filter by minimum bets
    filtered_metrics = {
        market: metrics
        for market, metrics in metrics_by_market.items()
        if metrics.get('basic', {}).get('total_bets', 0) >= min_bets
    }
    
    if not filtered_metrics:
        st.warning(f"Nenhum mercado com pelo menos {min_bets} apostas")
        return
    
    # Summary cards
    total_markets = len(filtered_metrics)
    profitable_markets = sum(
        1 for m in filtered_metrics.values()
        if m.get('basic', {}).get('roi', 0) > 0
    )
    
    best_market = max(
        filtered_metrics.items(),
        key=lambda x: x[1].get('basic', {}).get('roi', 0)
    )
    
    worst_market = min(
        filtered_metrics.items(),
        key=lambda x: x[1].get('basic', {}).get('roi', 0)
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Mercados", total_markets)
    
    with col2:
        st.metric(
            "Mercados Lucrativos",
            f"{profitable_markets}/{total_markets}",
            f"{profitable_markets/total_markets*100:.0f}%" if total_markets > 0 else "0%"
        )
    
    with col3:
        best_roi = best_market[1].get('basic', {}).get('roi', 0)
        st.metric("Melhor ROI", f"{best_roi:.1f}%", best_market[0])
    
    with col4:
        worst_roi = worst_market[1].get('basic', {}).get('roi', 0)
        st.metric("Pior ROI", f"{worst_roi:.1f}%", worst_market[0])
    
    st.markdown("")
    
    # Full table
    metrics_table(
        filtered_metrics,
        title="Performance Completa",
        sort_by='roi',
        ascending=False
    )


def _display_market_comparison(aggregator: MetricsAggregator, markets: list, min_bets: int):
    """Display market comparison section."""
    st.header("⚖️ Comparação de Mercados")
    
    # Calculate metrics
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    # Filter by minimum bets
    filtered_metrics = {
        market: metrics
        for market, metrics in metrics_by_market.items()
        if metrics.get('basic', {}).get('total_bets', 0) >= min_bets
    }
    
    if len(filtered_metrics) < 2:
        st.info("Selecione pelo menos 2 mercados para comparação")
        return
    
    # Create comparison data
    comparison_data = []
    
    for market, metrics in filtered_metrics.items():
        basic = metrics.get('basic', {})
        risk = metrics.get('risk', {})
        clv = metrics.get('clv', {})
        
        comparison_data.append({
            'Mercado': MARKETS.get(market, market),
            'Apostas': basic.get('total_bets', 0),
            'Win Rate (%)': f"{basic.get('win_rate', 0):.1f}",
            'ROI (%)': f"{basic.get('roi', 0):.2f}",
            'Sharpe': f"{risk.get('sharpe_ratio', 0):.2f}",
            'Max DD (%)': f"{risk.get('max_drawdown', 0):.1f}",
            'CLV Médio': f"{clv.get('clv_average', 0):.4f}",
        })
    
    comparison_table(
        comparison_data,
        columns=['Mercado', 'Apostas', 'Win Rate (%)', 'ROI (%)', 'Sharpe', 'Max DD (%)', 'CLV Médio'],
        title=""
    )
    
    # Best practices per metric
    st.subheader("🏆 Melhores por Métrica")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        best_roi = max(filtered_metrics.items(), key=lambda x: x[1].get('basic', {}).get('roi', 0))
        st.markdown(f"**Melhor ROI:** {MARKETS.get(best_roi[0], best_roi[0])}")
        st.markdown(f"*{best_roi[1].get('basic', {}).get('roi', 0):.2f}%*")
    
    with col2:
        best_sharpe = max(filtered_metrics.items(), key=lambda x: x[1].get('risk', {}).get('sharpe_ratio', 0))
        st.markdown(f"**Melhor Sharpe:** {MARKETS.get(best_sharpe[0], best_sharpe[0])}")
        st.markdown(f"*{best_sharpe[1].get('risk', {}).get('sharpe_ratio', 0):.2f}*")
    
    with col3:
        best_clv = max(filtered_metrics.items(), key=lambda x: x[1].get('clv', {}).get('clv_average', 0))
        st.markdown(f"**Melhor CLV:** {MARKETS.get(best_clv[0], best_clv[0])}")
        st.markdown(f"*{best_clv[1].get('clv', {}).get('clv_average', 0):.4f}*")


def _display_market_deep_dive(aggregator: MetricsAggregator, markets: list):
    """Display deep dive analysis for a specific market."""
    st.header("🔍 Análise Detalhada de Mercado")
    
    # Market selector for deep dive
    selected_market = st.selectbox(
        "Selecione um mercado para análise detalhada:",
        options=markets,
        format_func=lambda x: MARKETS.get(x, x)
    )
    
    if not selected_market:
        return
    
    # Filter bets for this market
    market_bets = [b for b in aggregator.bets if b.market_type == selected_market]
    
    if not market_bets:
        st.info(f"Nenhuma aposta encontrada para {MARKETS.get(selected_market, selected_market)}")
        return
    
    # Create aggregator for this market only
    market_aggregator = MetricsAggregator(bets=market_bets)
    market_metrics = market_aggregator.calculate_all()
    
    # Display metrics
    st.subheader(f"📊 Métricas: {MARKETS.get(selected_market, selected_market)}")
    
    basic = market_metrics.get('basic', {})
    risk = market_metrics.get('risk', {})
    cal = market_metrics.get('calibration', {})
    clv = market_metrics.get('clv', {})
    
    # Metrics grid
    metrics_data = {
        'Total Apostas': {'title': 'Total Apostas', 'value': basic.get('total_bets', 0), 'icon': '🎯'},
        'Win Rate': {'title': 'Win Rate', 'value': f"{basic.get('win_rate', 0):.1f}%", 'icon': '📈'},
        'ROI': {'title': 'ROI', 'value': f"{basic.get('roi', 0):.2f}%", 'icon': '💰'},
        'Lucro': {'title': 'Lucro Total', 'value': f"R$ {basic.get('profit', 0):.2f}", 'icon': '💵'},
        'Sharpe': {'title': 'Sharpe Ratio', 'value': f"{risk.get('sharpe_ratio', 0):.2f}", 'icon': '📊'},
        'Drawdown': {'title': 'Max Drawdown', 'value': f"{risk.get('max_drawdown', 0):.1f}%", 'icon': '📉'},
        'Brier': {'title': 'Brier Score', 'value': f"{cal.get('brier_score', 0):.4f}", 'icon': '🎯'},
        'CLV': {'title': 'CLV Médio', 'value': f"{clv.get('clv_average', 0):.4f}", 'icon': '💎'},
    }
    
    metrics_grid(metrics_data, columns=4)
    
    st.markdown("")
    
    # Charts for this market
    col1, col2 = st.columns(2)
    
    with col1:
        # Equity curve for this market
        equity_data = market_metrics.get('bankroll', {}).get('equity_curve', [])
        if equity_data and len(equity_data) > 1:
            equity_chart(
                equity_data,
                title=f"📈 Equity - {MARKETS.get(selected_market, selected_market)}"
            )
    
    with col2:
        # Profit evolution
        bets_data = [
            {
                'profit': b.profit if b.profit else 0,
                'settled_at': b.settled_at
            }
            for b in market_bets
            if b.status in ['won', 'lost'] and b.settled_at
        ]
        
        if bets_data:
            profit_chart(bets_data, title=f"💰 Evolução - {MARKETS.get(selected_market, selected_market)}")


def _display_sport_market_analysis(aggregator: MetricsAggregator, sports: list, markets: list):
    """Display sport × market analysis."""
    st.header("🎮 Análise Esporte × Mercado")
    
    if not sports or not markets:
        st.info("Selecione esportes e mercados para análise combinada")
        return
    
    # Calculate metrics by both dimensions
    metrics_by_sport = aggregator.calculate_by_sport(sports)
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    if not metrics_by_sport or not metrics_by_market:
        st.info("Dados insuficientes para análise combinada")
        return
    
    # Metric selector
    metric_to_show = st.selectbox(
        "Métrica a visualizar:",
        options=['ROI (%)', 'Win Rate (%)', 'Sharpe Ratio', 'CLV Médio'],
        index=0
    )
    
    # Map metric name to key
    metric_map = {
        'ROI (%)': ('basic', 'roi'),
        'Win Rate (%)': ('basic', 'win_rate'),
        'Sharpe Ratio': ('risk', 'sharpe_ratio'),
        'CLV Médio': ('clv', 'clv_average'),
    }
    
    section, key = metric_map[metric_to_show]
    
    # Create heatmap data
    heatmap_data = {}
    for sport in sports:
        heatmap_data[sport] = {}
        for market in markets:
            # Get metrics for this sport
            sport_metric = metrics_by_sport.get(sport, {}).get(section, {}).get(key, 0)
            # Get metrics for this market
            market_metric = metrics_by_market.get(market, {}).get(section, {}).get(key, 0)
            # Average (simplified - would need actual combined filtering)
            heatmap_data[sport][market] = (sport_metric + market_metric) / 2
    
    # Display heatmap
    performance_heatmap(
        heatmap_data,
        title=f"🔥 Heatmap: {metric_to_show}",
        metric=metric_to_show.lower()
    )
    
    # Interpretation
    with st.expander("ℹ️ Como Interpretar"):
        st.markdown("""
        **Este heatmap mostra a performance combinada de esporte × mercado:**
        
        - 🟢 **Verde**: Performance alta - continuar focando nestas combinações
        - 🟡 **Amarelo**: Performance média - monitorar
        - 🔴 **Vermelho**: Performance baixa - evitar ou revisar estratégia
        
        **Nota:** Valores são médias simplificadas. Para análise exata, filtrar apostas por ambas dimensões.
        """)


if __name__ == "__main__":
    show()
