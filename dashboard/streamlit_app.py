"""Streamlit dashboard main application."""
import streamlit as st
from database.db import init_db
from bookmakers.registry import bookmaker_registry
from games.registry import game_registry

# Page configuration
st.set_page_config(
    page_title="Capivara Bet Esports 2.0",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
@st.cache_resource
def initialize():
    """Initialize application resources."""
    init_db()
    bookmaker_registry.auto_discover()
    game_registry.auto_discover()

initialize()

# Dark mode toggle (stored in session state)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Enhanced Custom CSS with dark mode support
if st.session_state.dark_mode:
    bg_color = "#0e1117"
    text_color = "#fafafa"
    card_bg = "#1e1e1e"
    border_color = "#2e2e2e"
else:
    bg_color = "#ffffff"
    text_color = "#262730"
    card_bg = "#f0f2f6"
    border_color = "#e0e0e0"

st.markdown(f"""
<style>
    .main-header {{
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1E88E5 0%, #00BCD4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }}
    .subtitle {{
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }}
    .metric-card {{
        background-color: {card_bg};
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 0.5rem 0;
        border: 1px solid {border_color};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .success-metric {{
        color: #28a745;
        font-weight: bold;
    }}
    .danger-metric {{
        color: #dc3545;
        font-weight: bold;
    }}
    .sidebar-section {{
        margin: 1rem 0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        background-color: {card_bg};
    }}
    .section-header {{
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1E88E5;
    }}
    /* Improve button styling */
    .stButton>button {{
        border-radius: 0.5rem;
        font-weight: 500;
    }}
    /* Improve metric styling */
    [data-testid="stMetricValue"] {{
        font-size: 1.75rem;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">🎮 Capivara Bet Esports 2.0</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sistema Avançado de Apostas Esportivas com IA e Análise em Tempo Real</p>', unsafe_allow_html=True)

# Sidebar navigation with sections
st.sidebar.title("📊 Dashboard")

# Dark mode toggle in sidebar
dark_mode_toggle = st.sidebar.checkbox("🌙 Modo Escuro", value=st.session_state.dark_mode)
if dark_mode_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_mode_toggle
    st.rerun()

st.sidebar.markdown("---")

# Main section
st.sidebar.markdown("### 📍 Principal")
main_pages = [
    "🏠 Home",
    "🎮 Live Matches",
    "📅 Calendário",
]
main_page = st.sidebar.radio("", main_pages, label_visibility="collapsed")

# Betting section
st.sidebar.markdown("### 💰 Apostas")
betting_pages = [
    "💡 Apostas Sugeridas",
    "✅ Apostas Confirmadas",
    "🔄 Comparador de Odds",
    "💰 Bankroll",
]
betting_page = st.sidebar.radio("", betting_pages, label_visibility="collapsed")

# Analysis section
st.sidebar.markdown("### 📊 Análises")
analysis_pages = [
    "📈 Performance",
    "🎯 Por Confidence",
    "🏦 Por Casa",
    "📊 Calibração",
    "🏆 Rankings",
]
analysis_page = st.sidebar.radio("", analysis_pages, label_visibility="collapsed")

# Metrics section (new)
st.sidebar.markdown("### 📊 Métricas")
metrics_pages = [
    "📊 Dashboard de Métricas",
    "📋 Relatório de Validação",
    "🎯 Análise de Mercados",
]
metrics_page = st.sidebar.radio("", metrics_pages, label_visibility="collapsed")

# System section
st.sidebar.markdown("### ⚙️ Sistema")
system_pages = [
    "📱 Status das APIs",
    "⚙️ Configurações",
]
system_page = st.sidebar.radio("", system_pages, label_visibility="collapsed")

# Determine which page to show
page = None
if main_page and main_page != main_pages[0]:
    page = main_page
elif betting_page and betting_page != betting_pages[0]:
    page = betting_page
elif analysis_page and analysis_page != analysis_pages[0]:
    page = analysis_page
elif metrics_page and metrics_page != metrics_pages[0]:
    page = metrics_page
elif system_page and system_page != system_pages[0]:
    page = system_page
else:
    # Default to first selected
    if main_page == main_pages[0]:
        page = main_page

# Import and display selected page
if page == "🏠 Home":
    from dashboard.pages import home
    home.show()
elif page == "🎮 Live Matches":
    from dashboard.pages import live
    live.show()
elif page == "📅 Calendário":
    from dashboard.pages import calendar
    calendar.show()
elif page == "💡 Apostas Sugeridas":
    from dashboard.pages import suggestions
    suggestions.show()
elif page == "✅ Apostas Confirmadas":
    from dashboard.pages import confirmed
    confirmed.show()
elif page == "🔄 Comparador de Odds":
    from dashboard.pages import odds_compare
    odds_compare.show()
elif page == "💰 Bankroll":
    from dashboard.pages import bankroll
    bankroll.show()
elif page == "📈 Performance":
    from dashboard.pages import performance
    performance.show()
elif page == "🎯 Por Confidence":
    from dashboard.pages import confidence
    confidence.show()
elif page == "🏦 Por Casa":
    from dashboard.pages import bookmakers
    bookmakers.show()
elif page == "📊 Calibração":
    from dashboard.pages import calibration
    calibration.show()
elif page == "🏆 Rankings":
    from dashboard.pages import rankings
    rankings.show()
elif page == "📊 Dashboard de Métricas":
    from dashboard.pages import metrics_dashboard
    metrics_dashboard.show()
elif page == "📋 Relatório de Validação":
    from dashboard.pages import validation_report
    validation_report.show()
elif page == "🎯 Análise de Mercados":
    from dashboard.pages import market_analysis
    market_analysis.show()
elif page == "📱 Status das APIs":
    from dashboard.pages import api_status
    api_status.show()
elif page == "⚙️ Configurações":
    from dashboard.pages import settings
    settings.show()

# Enhanced Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Quick Stats")

# Quick stats (mock data)
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Apostas Hoje", "12", delta="3")
with col2:
    st.metric("ROI 7d", "8.5%", delta="2.1%")

st.sidebar.markdown("---")
st.sidebar.markdown("**Capivara Bet Esports v2.0**")
st.sidebar.markdown("*Dashboard 2.0 - Grande Atualização*")
st.sidebar.success("✅ Sistema Operacional")
st.sidebar.info("💰 Stake Unit: **R$ 100,00**")
