"""Metrics configuration and ranges."""

# Confidence ranges for segmentation
CONFIDENCE_RANGES = [
    (0.55, 0.60, '55-60%'),
    (0.60, 0.65, '60-65%'),
    (0.65, 0.70, '65-70%'),
    (0.70, 0.75, '70-75%'),
    (0.75, 1.00, '75%+'),
]

# Odds ranges for segmentation
ODDS_RANGES = [
    (1.20, 1.50, '1.20-1.50'),
    (1.50, 1.80, '1.50-1.80'),
    (1.80, 2.20, '1.80-2.20'),
    (2.20, 3.00, '2.20-3.00'),
    (3.00, 10.00, '3.00+'),
]

# Edge ranges for segmentation
EDGE_RANGES = [
    (0.03, 0.05, '3-5%'),
    (0.05, 0.08, '5-8%'),
    (0.08, 0.12, '8-12%'),
    (0.12, 1.00, '12%+'),
]

# Metrics thresholds for insights
METRICS_THRESHOLDS = {
    # Performance thresholds
    'excellent_roi': 15.0,  # ROI above this is excellent
    'good_roi': 8.0,  # ROI above this is good
    'poor_roi': -5.0,  # ROI below this is poor
    
    'excellent_winrate': 60.0,  # Win rate above this is excellent
    'good_winrate': 55.0,  # Win rate above this is good
    'poor_winrate': 45.0,  # Win rate below this is poor
    
    # Risk thresholds
    'excellent_sharpe': 2.0,  # Sharpe above this is excellent
    'good_sharpe': 1.0,  # Sharpe above this is good
    'poor_sharpe': 0.0,  # Sharpe below this is poor
    
    'warning_drawdown': 20.0,  # Drawdown above this triggers warning
    'danger_drawdown': 30.0,  # Drawdown above this is dangerous
    
    'high_volatility': 30.0,  # Volatility above this is high
    
    # Calibration thresholds
    'excellent_brier': 0.15,  # Brier below this is excellent
    'good_brier': 0.20,  # Brier below this is good
    'poor_brier': 0.25,  # Brier above this is poor
    
    'excellent_logloss': 0.40,  # Log loss below this is excellent
    'good_logloss': 0.50,  # Log loss below this is good
    'poor_logloss': 0.60,  # Log loss above this is poor
    
    # CLV thresholds
    'excellent_clv': 0.05,  # CLV above this is excellent
    'good_clv': 0.02,  # CLV above this is good
    'poor_clv': -0.02,  # CLV below this is poor
    
    'excellent_clv_rate': 60.0,  # % positive CLV above this is excellent
    'good_clv_rate': 55.0,  # % positive CLV above this is good
    'poor_clv_rate': 45.0,  # % positive CLV below this is poor
}

# Color coding for metrics display
METRIC_COLORS = {
    'excellent': '#00C853',  # Green
    'good': '#2196F3',  # Blue
    'neutral': '#FFC107',  # Yellow/Amber
    'poor': '#F44336',  # Red
    'danger': '#B71C1C',  # Dark Red
}

# Dashboard display settings
DASHBOARD_CONFIG = {
    'refresh_interval': 300,  # seconds (5 minutes)
    'charts_height': 400,
    'tables_page_size': 20,
    'heatmap_color_scale': 'RdYlGn',  # Red-Yellow-Green
    'show_empty_categories': False,
}

# Report export settings
REPORT_CONFIG = {
    'pdf_title': 'Paper Trading Validation Report',
    'pdf_author': 'Capivara Bet Esports',
    'include_charts': True,
    'include_detailed_tables': True,
    'max_markets_in_summary': 10,
}
