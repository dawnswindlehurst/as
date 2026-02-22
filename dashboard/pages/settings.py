"""Settings page."""
import streamlit as st
from config.settings import (
    MIN_CONFIDENCE, MIN_EDGE, MAX_EDGE, KELLY_FRACTION,
    PAPER_TRADING_STAKE, PAPER_TRADING_CURRENCY
)
from config.telegram import telegram_config


def show():
    """Display settings page."""
    st.header("⚙️ Configurações")
    
    # Betting parameters
    st.subheader("💰 Parâmetros de Apostas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Stake Padrão (R$)",
            value=PAPER_TRADING_STAKE,
            min_value=10.0,
            max_value=1000.0,
            step=10.0,
            disabled=True,
            help="Valor fixo para paper trading"
        )
        
        st.number_input(
            "Confidence Mínima",
            value=MIN_CONFIDENCE,
            min_value=0.50,
            max_value=0.95,
            step=0.05,
            format="%.2f",
            disabled=True,
            help="Probabilidade mínima do modelo para considerar aposta"
        )
    
    with col2:
        st.number_input(
            "Edge Mínima",
            value=MIN_EDGE,
            min_value=0.01,
            max_value=0.20,
            step=0.01,
            format="%.2f",
            disabled=True,
            help="Edge mínima para considerar aposta"
        )
        
        st.number_input(
            "Kelly Fraction",
            value=KELLY_FRACTION,
            min_value=0.10,
            max_value=1.00,
            step=0.05,
            format="%.2f",
            disabled=True,
            help="Fração do Kelly para sizing"
        )
    
    st.markdown("---")
    
    # Telegram settings
    st.subheader("📱 Telegram")
    
    telegram_enabled = telegram_config.is_enabled()
    
    if telegram_enabled:
        st.success("✅ Telegram configurado e ativo")
        
        # Notification preferences
        st.write("**Preferências de Notificação:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("Oportunidades de Apostas", value=True, disabled=True)
            st.checkbox("Resultados de Apostas", value=True, disabled=True)
        
        with col2:
            st.checkbox("Relatório Diário", value=True, disabled=True)
            st.checkbox("Alertas Especiais", value=True, disabled=True)
    else:
        st.warning("⚠️ Telegram não configurado")
        st.info("Configure as variáveis TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no arquivo .env")
    
    st.markdown("---")
    
    # Filters
    st.subheader("🎮 Filtros de Jogos")
    
    games = ["CS2", "LoL", "Dota2", "Valorant"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for game in games[:2]:
            st.checkbox(game, value=True, disabled=True)
    
    with col2:
        for game in games[2:]:
            st.checkbox(game, value=True, disabled=True)
    
    st.markdown("---")
    
    # Bookmakers
    st.subheader("🏦 Casas de Apostas Ativas")
    
    st.write("**Tradicionais:**")
    traditional = ["Pinnacle", "bet365", "Betfair", "Rivalry"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for bm in traditional[:2]:
            st.checkbox(bm, value=True, disabled=True, key=f"trad_{bm}")
    
    with col2:
        for bm in traditional[2:]:
            st.checkbox(bm, value=True, disabled=True, key=f"trad_{bm}")
    
    st.write("**Crypto:**")
    crypto = ["Stake", "Cloudbet", "Thunderpick", "Roobet"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        for bm in crypto[:2]:
            st.checkbox(bm, value=True, disabled=True, key=f"crypto_{bm}")
    
    with col2:
        for bm in crypto[2:]:
            st.checkbox(bm, value=True, disabled=True, key=f"crypto_{bm}")
    
    st.markdown("---")
    
    st.info("""
    **Modo Paper Trading Ativo**
    
    Todas as apostas são simuladas. Nenhum dinheiro real é apostado.
    As configurações acima são fixas durante o período de teste.
    """)
