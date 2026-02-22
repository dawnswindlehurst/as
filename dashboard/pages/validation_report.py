"""Validation report page for paper trading results."""
import streamlit as st
from datetime import datetime
from analysis.metrics.aggregator import MetricsAggregator
from analysis.insights import InsightGenerator
from config.paper_trading import PAPER_TRADING_CONFIG, SPORTS, MARKETS
from config.metrics_config import METRICS_THRESHOLDS
from dashboard.components.metrics_table import ranked_table, summary_table
from dashboard.components.insights_panel import insights_by_category, actionable_insights


def show():
    """Display validation report page."""
    st.title("📋 Relatório de Validação - Paper Trading")
    st.markdown("Análise completa dos resultados do período de teste")
    
    # Generate report
    try:
        # Initialize aggregator
        aggregator = MetricsAggregator(
            initial_bankroll=PAPER_TRADING_CONFIG['initial_bankroll']
        )
        
        all_metrics = aggregator.calculate_all()
        
        # Display executive summary
        _display_executive_summary(all_metrics, aggregator)
        
        st.markdown("---")
        
        # Top and bottom performers
        col1, col2 = st.columns(2)
        
        with col1:
            _display_top_markets(aggregator)
        
        with col2:
            _display_bottom_markets(aggregator)
        
        st.markdown("---")
        
        # Detailed analysis by dimension
        _display_detailed_analysis(aggregator)
        
        st.markdown("---")
        
        # Conclusions and recommendations
        _display_conclusions(all_metrics)
        
        st.markdown("---")
        
        # Export options
        _display_export_options()
        
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {str(e)}")
        st.info("Certifique-se de que existem apostas confirmadas no banco de dados.")


def _display_executive_summary(metrics: dict, aggregator: MetricsAggregator):
    """Display executive summary section."""
    st.header("📝 Resumo Executivo")
    
    basic = metrics.get('basic', {})
    risk = metrics.get('risk', {})
    bankroll = metrics.get('bankroll', {})
    metadata = metrics.get('metadata', {})
    
    # Key stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Período de Teste", PAPER_TRADING_CONFIG['duration'])
        st.metric("Total de Apostas", metadata.get('settled_bets', 0))
    
    with col2:
        roi = basic.get('roi', 0)
        roi_color = "normal" if roi >= 0 else "inverse"
        st.metric("ROI Geral", f"{roi:.2f}%", delta_color=roi_color)
        st.metric("Win Rate", f"{basic.get('win_rate', 0):.1f}%")
    
    with col3:
        profit = basic.get('profit', 0)
        st.metric("Lucro/Prejuízo", f"R$ {profit:.2f}")
        st.metric("Sharpe Ratio", f"{risk.get('sharpe_ratio', 0):.2f}")
    
    with col4:
        growth = bankroll.get('bankroll_growth', 0)
        st.metric("Crescimento Bankroll", f"{growth:.1f}%")
        st.metric("Max Drawdown", f"{risk.get('max_drawdown', 0):.1f}%")
    
    st.markdown("")
    
    # Recommendation
    roi = basic.get('roi', 0)
    sharpe = risk.get('sharpe_ratio', 0)
    win_rate = basic.get('win_rate', 0)
    
    if roi >= METRICS_THRESHOLDS['excellent_roi'] and sharpe >= METRICS_THRESHOLDS['excellent_sharpe']:
        st.success("✅ **RECOMENDAÇÃO: APROVAR para operação real**")
        st.markdown("""
        O sistema demonstrou excelente performance durante o paper trading:
        - ROI acima do limiar de excelência
        - Sharpe Ratio indicando bom retorno ajustado ao risco
        - Métricas consistentes indicam edge real
        """)
    elif roi >= METRICS_THRESHOLDS['good_roi'] and sharpe >= METRICS_THRESHOLDS['good_sharpe']:
        st.info("ℹ️ **RECOMENDAÇÃO: APROVAR com cautela**")
        st.markdown("""
        Performance satisfatória, mas recomenda-se:
        - Começar com stakes reduzidos
        - Monitorar métricas de perto
        - Revisar mercados de baixa performance
        """)
    else:
        st.error("❌ **RECOMENDAÇÃO: NÃO APROVAR**")
        st.markdown("""
        Performance abaixo do esperado. Ações necessárias:
        - Revisar modelos preditivos
        - Ajustar critérios de seleção
        - Continuar em paper trading
        """)


def _display_top_markets(aggregator: MetricsAggregator):
    """Display top performing markets."""
    st.subheader("🏆 Top 10 Mercados Mais Lucrativos")
    
    markets = list(MARKETS.keys())
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    # Extract ROI for each market
    market_roi = {}
    for market, metrics in metrics_by_market.items():
        basic = metrics.get('basic', {})
        roi = basic.get('roi', 0)
        bets = basic.get('total_bets', 0)
        
        # Only include markets with at least 5 bets
        if bets >= 5:
            market_roi[market] = roi
    
    if market_roi:
        ranked_table(
            market_roi,
            title="",
            value_label="ROI (%)",
            top_n=10,
            color_scale=True
        )
    else:
        st.info("Dados insuficientes")


def _display_bottom_markets(aggregator: MetricsAggregator):
    """Display worst performing markets."""
    st.subheader("❌ Mercados a Evitar")
    
    markets = list(MARKETS.keys())
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    # Extract ROI for each market
    market_roi = {}
    for market, metrics in metrics_by_market.items():
        basic = metrics.get('basic', {})
        roi = basic.get('roi', 0)
        bets = basic.get('total_bets', 0)
        
        if bets >= 5:
            market_roi[market] = roi
    
    if market_roi:
        # Sort by worst first
        sorted_markets = sorted(market_roi.items(), key=lambda x: x[1])[:5]
        
        st.markdown("**Bottom 5 Mercados (ROI)**")
        for i, (market, roi) in enumerate(sorted_markets, 1):
            color = "🔴" if roi < -5 else "🟡"
            st.markdown(f"{i}. {color} **{market}**: {roi:.2f}%")
            
        st.warning("⚠️ Considerar excluir ou revisar estes mercados")
    else:
        st.info("Dados insuficientes")


def _display_detailed_analysis(aggregator: MetricsAggregator):
    """Display detailed analysis by multiple dimensions."""
    st.header("📊 Análise Detalhada")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Esporte",
        "🎯 Mercado",
        "📊 Confidence",
        "💰 Odds",
        "📈 Resumo"
    ])
    
    # Calculate metrics for all dimensions
    sports = list(SPORTS.keys())
    markets = list(MARKETS.keys())
    
    metrics_by_sport = aggregator.calculate_by_sport(sports)
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    from config.metrics_config import CONFIDENCE_RANGES, ODDS_RANGES
    metrics_by_conf = aggregator.calculate_by_confidence_range(CONFIDENCE_RANGES)
    metrics_by_odds = aggregator.calculate_by_odds_range(ODDS_RANGES)
    
    with tab1:
        if metrics_by_sport:
            from dashboard.components.metrics_table import metrics_table
            metrics_table(metrics_by_sport, sort_by='roi', ascending=False)
        else:
            st.info("Nenhum dado disponível")
    
    with tab2:
        if metrics_by_market:
            from dashboard.components.metrics_table import metrics_table
            metrics_table(metrics_by_market, sort_by='roi', ascending=False, show_top_n=20)
        else:
            st.info("Nenhum dado disponível")
    
    with tab3:
        if metrics_by_conf:
            from dashboard.components.metrics_table import metrics_table
            metrics_table(metrics_by_conf, sort_by='roi', ascending=False)
        else:
            st.info("Nenhum dado disponível")
    
    with tab4:
        if metrics_by_odds:
            from dashboard.components.metrics_table import metrics_table
            metrics_table(metrics_by_odds, sort_by='roi', ascending=False)
        else:
            st.info("Nenhum dado disponível")
    
    with tab5:
        all_metrics = aggregator.calculate_all()
        summary_table(all_metrics)


def _display_conclusions(metrics: dict):
    """Display conclusions and recommendations."""
    st.header("💡 Conclusões e Recomendações")
    
    # Generate insights
    insight_gen = InsightGenerator(metrics)
    insights = insight_gen.generate_all_insights()
    
    # Show actionable insights (high priority only)
    st.subheader("⚡ Ações Prioritárias")
    actionable_insights(insights, priority=1)
    
    st.markdown("")
    
    # Show categorized insights
    st.subheader("📋 Todos os Insights")
    insights_by_category(insights)
    
    st.markdown("")
    
    # General recommendations
    st.subheader("🎯 Recomendações Gerais")
    
    basic = metrics.get('basic', {})
    total_bets = basic.get('total_bets', 0)
    
    recommendations = []
    
    if total_bets < 50:
        recommendations.append("📊 **Amostra pequena**: Continuar coletando dados por mais tempo antes de decisões finais")
    
    if total_bets >= 100:
        recommendations.append("✅ **Amostra adequada**: Métricas têm significância estatística suficiente")
    
    # Add recommendations based on metrics
    roi = basic.get('roi', 0)
    if roi > METRICS_THRESHOLDS['excellent_roi']:
        recommendations.append("🚀 **Performance excelente**: Sistema pronto para operação real")
    
    risk = metrics.get('risk', {})
    max_dd = abs(risk.get('max_drawdown', 0))
    if max_dd > METRICS_THRESHOLDS['warning_drawdown']:
        recommendations.append("⚠️ **Revisar gestão de risco**: Drawdown elevado requer atenção")
    
    clv = metrics.get('clv', {})
    clv_rate = clv.get('clv_positive_rate', 0)
    if clv_rate > 55:
        recommendations.append("💰 **CLV positivo consistente**: Evidência de edge real no mercado")
    
    for rec in recommendations:
        st.markdown(f"- {rec}")


def _display_export_options():
    """Display export options."""
    st.header("📥 Exportar Relatório")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Exportar como PDF", use_container_width=True):
            st.info("Funcionalidade de exportação PDF será implementada em breve")
    
    with col2:
        if st.button("📊 Exportar como Excel", use_container_width=True):
            st.info("Funcionalidade de exportação Excel será implementada em breve")
    
    st.markdown("")
    st.markdown("""
    **O que será incluído no relatório:**
    - ✅ Resumo executivo completo
    - ✅ Todas as métricas e KPIs
    - ✅ Gráficos e visualizações
    - ✅ Insights e recomendações
    - ✅ Análise detalhada por dimensão
    """)


if __name__ == "__main__":
    show()
