"""Main metrics dashboard page."""
import streamlit as st
from datetime import datetime, timedelta
from analysis.metrics.aggregator import MetricsAggregator
from analysis.insights import InsightGenerator
from config.paper_trading import PAPER_TRADING_CONFIG, SPORTS, MARKETS
from config.metrics_config import CONFIDENCE_RANGES, ODDS_RANGES
from dashboard.components.metric_card import metrics_row
from dashboard.components.metrics_table import metrics_table, summary_table
from dashboard.components.equity_chart import equity_chart
from dashboard.components.calibration_chart import calibration_curve
from dashboard.components.heatmap import sport_market_heatmap
from dashboard.components.insights_panel import insights_panel, insights_summary


def show():
    """Display metrics dashboard page."""
    st.title("📊 Dashboard de Métricas")
    st.markdown("Sistema completo de métricas para validação de Paper Trading")
    
    # Period selector
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        period = st.selectbox(
            "📅 Período",
            ["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Todo o período"],
            index=3
        )
    
    with col2:
        st.metric(
            "Bankroll Inicial",
            f"R$ {PAPER_TRADING_CONFIG['initial_bankroll']:.2f}"
        )
    
    with col3:
        st.metric(
            "Stake Fixo",
            f"R$ {PAPER_TRADING_CONFIG['stake']:.2f}"
        )
    
    st.markdown("---")
    
    # Calculate date range
    end_date = datetime.now()
    if period == "Hoje":
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "Últimos 7 dias":
        start_date = end_date - timedelta(days=7)
    elif period == "Últimos 30 dias":
        start_date = end_date - timedelta(days=30)
    else:
        start_date = None
    
    # Initialize metrics aggregator
    try:
        aggregator = MetricsAggregator(
            initial_bankroll=PAPER_TRADING_CONFIG['initial_bankroll']
        )
        
        # Filter bets by period if needed
        if start_date:
            filtered_bets = [
                b for b in aggregator.bets 
                if b.created_at >= start_date
            ]
            aggregator = MetricsAggregator(
                bets=filtered_bets,
                initial_bankroll=PAPER_TRADING_CONFIG['initial_bankroll']
            )
        
        # Calculate all metrics
        all_metrics = aggregator.calculate_all()
        
        # Display metrics
        _display_kpis(all_metrics)
        _display_risk_section(all_metrics)
        _display_calibration_section(all_metrics)
        
        # Performance tables
        st.markdown("---")
        st.header("📈 Performance por Dimensão")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎮 Por Esporte",
            "🎯 Por Mercado",
            "📊 Por Confidence",
            "💰 Por Odds"
        ])
        
        with tab1:
            _display_sport_metrics(aggregator)
        
        with tab2:
            _display_market_metrics(aggregator)
        
        with tab3:
            _display_confidence_metrics(aggregator)
        
        with tab4:
            _display_odds_metrics(aggregator)
        
        # Charts section
        st.markdown("---")
        st.header("📉 Visualizações")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Equity curve
            bankroll_metrics = all_metrics.get('bankroll', {})
            equity_data = bankroll_metrics.get('equity_curve', [])
            if equity_data:
                equity_chart(
                    equity_data,
                    initial_bankroll=PAPER_TRADING_CONFIG['initial_bankroll']
                )
        
        with col2:
            # Calibration curve
            cal_metrics = all_metrics.get('calibration', {})
            cal_bins = cal_metrics.get('calibration_bins', [])
            if cal_bins:
                calibration_curve(cal_bins)
        
        # Insights section
        st.markdown("---")
        st.header("💡 Insights e Recomendações")
        
        # Generate insights
        insight_gen = InsightGenerator(all_metrics)
        insights = insight_gen.generate_all_insights()
        
        # Show insights summary
        insights_summary(insights)
        
        st.markdown("")
        
        # Show insights panel
        insights_panel(insights, max_insights=10)
        
    except Exception as e:
        st.error(f"Erro ao carregar métricas: {str(e)}")
        st.info("Certifique-se de que existem apostas confirmadas no banco de dados.")


def _display_kpis(metrics: dict):
    """Display main KPIs."""
    st.subheader("📊 KPIs Principais")
    
    basic = metrics.get('basic', {})
    risk = metrics.get('risk', {})
    clv = metrics.get('clv', {})
    
    kpis = [
        {
            'title': 'Total Apostas',
            'value': basic.get('total_bets', 0),
            'icon': '🎯'
        },
        {
            'title': 'Win Rate',
            'value': f"{basic.get('win_rate', 0):.1f}%",
            'icon': '📈'
        },
        {
            'title': 'ROI',
            'value': f"{basic.get('roi', 0):.2f}%",
            'delta': "Meta: +8%",
            'icon': '💰'
        },
        {
            'title': 'Lucro Total',
            'value': f"R$ {basic.get('profit', 0):.2f}",
            'icon': '💵'
        },
        {
            'title': 'CLV Médio',
            'value': f"{clv.get('clv_average', 0):.3f}",
            'icon': '🎯'
        },
        {
            'title': 'Sharpe Ratio',
            'value': f"{risk.get('sharpe_ratio', 0):.2f}",
            'icon': '📊'
        },
    ]
    
    metrics_row(kpis)


def _display_risk_section(metrics: dict):
    """Display risk metrics section."""
    st.markdown("---")
    st.subheader("⚠️ Métricas de Risco")
    
    risk = metrics.get('risk', {})
    
    risk_metrics = [
        {
            'title': 'Max Drawdown',
            'value': f"{risk.get('max_drawdown', 0):.2f}%",
            'icon': '📉'
        },
        {
            'title': 'Volatilidade',
            'value': f"{risk.get('volatility', 0):.2f}%",
            'icon': '📊'
        },
        {
            'title': 'VaR 95%',
            'value': f"{risk.get('var_95', 0):.2f}%",
            'icon': '⚠️'
        },
        {
            'title': 'Recovery Factor',
            'value': f"{risk.get('recovery_factor', 0):.2f}",
            'icon': '🔄'
        },
    ]
    
    metrics_row(risk_metrics)


def _display_calibration_section(metrics: dict):
    """Display calibration metrics section."""
    st.markdown("---")
    st.subheader("🎯 Métricas de Calibração")
    
    cal = metrics.get('calibration', {})
    
    cal_metrics = [
        {
            'title': 'Brier Score',
            'value': f"{cal.get('brier_score', 0):.4f}",
            'help_text': 'Menor é melhor (0 = perfeito)',
            'icon': '🎯'
        },
        {
            'title': 'Log Loss',
            'value': f"{cal.get('log_loss', 0):.4f}",
            'help_text': 'Menor é melhor',
            'icon': '📉'
        },
        {
            'title': 'Calibration Error',
            'value': f"{cal.get('calibration_error', 0):.4f}",
            'help_text': 'Menor é melhor',
            'icon': '⚖️'
        },
        {
            'title': 'Overround Beat',
            'value': f"{cal.get('overround_beat_rate', 0):.1f}%",
            'help_text': '% de apostas com edge positivo',
            'icon': '💪'
        },
    ]
    
    metrics_row(cal_metrics)


def _display_sport_metrics(aggregator: MetricsAggregator):
    """Display metrics by sport."""
    sports = list(SPORTS.keys())
    metrics_by_sport = aggregator.calculate_by_sport(sports)
    
    if metrics_by_sport:
        metrics_table(
            metrics_by_sport,
            title="Performance por Esporte",
            sort_by='roi',
            ascending=False
        )
    else:
        st.info("Nenhum dado disponível para esportes")


def _display_market_metrics(aggregator: MetricsAggregator):
    """Display metrics by market."""
    markets = list(MARKETS.keys())
    metrics_by_market = aggregator.calculate_by_market(markets)
    
    if metrics_by_market:
        metrics_table(
            metrics_by_market,
            title="Performance por Mercado",
            sort_by='roi',
            ascending=False,
            show_top_n=15
        )
    else:
        st.info("Nenhum dado disponível para mercados")


def _display_confidence_metrics(aggregator: MetricsAggregator):
    """Display metrics by confidence range."""
    metrics_by_conf = aggregator.calculate_by_confidence_range(CONFIDENCE_RANGES)
    
    if metrics_by_conf:
        metrics_table(
            metrics_by_conf,
            title="Performance por Faixa de Confidence",
            sort_by='roi',
            ascending=False
        )
    else:
        st.info("Nenhum dado disponível")


def _display_odds_metrics(aggregator: MetricsAggregator):
    """Display metrics by odds range."""
    metrics_by_odds = aggregator.calculate_by_odds_range(ODDS_RANGES)
    
    if metrics_by_odds:
        metrics_table(
            metrics_by_odds,
            title="Performance por Faixa de Odds",
            sort_by='roi',
            ascending=False
        )
    else:
        st.info("Nenhum dado disponível")


if __name__ == "__main__":
    show()
