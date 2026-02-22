"""Filter components for dashboard."""
import streamlit as st


def create_date_filter():
    """Create date range filter.
    
    Returns:
        Tuple of (start_date, end_date)
    """
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Data Início")
    
    with col2:
        end_date = st.date_input("Data Fim")
    
    return start_date, end_date


def create_game_filter():
    """Create game filter.
    
    Returns:
        Selected game or "Todos"
    """
    games = ["Todos", "CS2", "LoL", "Dota2", "Valorant"]
    return st.selectbox("Jogo", games)


def create_bookmaker_filter():
    """Create bookmaker filter.
    
    Returns:
        Selected bookmaker or "Todas"
    """
    bookmakers = [
        "Todas",
        "Pinnacle",
        "bet365",
        "Betfair",
        "Rivalry",
        "Stake",
        "Cloudbet",
    ]
    return st.selectbox("Casa de Apostas", bookmakers)


def create_status_filter():
    """Create bet status filter.
    
    Returns:
        Selected status or "Todas"
    """
    statuses = ["Todas", "Pendente", "Ganhas", "Perdidas", "Void"]
    return st.selectbox("Status", statuses)
