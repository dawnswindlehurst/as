"""Odds comparison table component."""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def render_odds_table(
    events: List[Dict[str, Any]],
    market_type: str = "match_winner",
    highlight_best: bool = True
):
    """
    Render odds comparison table.
    
    Args:
        events: List of event dictionaries with odds
        market_type: Type of market to display
        highlight_best: Whether to highlight best odds
    """
    if not events:
        st.info("Nenhuma odd disponível.")
        return
    
    # Prepare data for table
    rows = []
    for event in events:
        team1 = event.get('team1', 'Team 1')
        team2 = event.get('team2', 'Team 2')
        tournament = event.get('tournament_name', '')
        
        # Find the specified market
        markets = event.get('markets', [])
        target_market = None
        for market in markets:
            if market.get('market_type') == market_type or market.get('market_name') == market_type:
                target_market = market
                break
        
        if target_market:
            odds_list = target_market.get('odds_list', [])
            row = {
                'Partida': f"{team1} vs {team2}",
                'Torneio': tournament,
            }
            
            for odd in odds_list:
                outcome = odd.get('outcome_name', '')
                odds_value = odd.get('odds', 0)
                row[outcome] = odds_value
            
            rows.append(row)
    
    if not rows:
        st.warning("Nenhum mercado encontrado para este tipo.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Style the table
    if highlight_best:
        # Highlight best odds (highest values) in each row
        def highlight_max(row):
            numeric_cols = row.select_dtypes(include=['float64', 'int64'])
            if len(numeric_cols) > 0:
                max_val = numeric_cols.max()
                return ['background-color: #90EE90' if v == max_val and pd.notna(v) else '' 
                        for v in row]
            return ['' for _ in row]
        
        styled_df = df.style.apply(highlight_max, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


def render_value_bets_table(
    bets: List[Dict[str, Any]],
    min_edge: float = 0.03
):
    """
    Render table of value bets (bets with positive expected value).
    
    Args:
        bets: List of bet dictionaries
        min_edge: Minimum edge to display
    """
    if not bets:
        st.info("Nenhuma value bet encontrada.")
        return
    
    # Filter by minimum edge
    value_bets = [bet for bet in bets if bet.get('edge', 0) >= min_edge]
    
    if not value_bets:
        st.warning(f"Nenhuma value bet com edge mínimo de {min_edge*100:.1f}%")
        return
    
    # Prepare data
    rows = []
    for bet in value_bets:
        rows.append({
            'Partida': bet.get('match', ''),
            'Mercado': bet.get('market', ''),
            'Seleção': bet.get('selection', ''),
            'Odds': f"{bet.get('odds', 0):.2f}",
            'Prob. Estimada': f"{bet.get('estimated_prob', 0)*100:.1f}%",
            'Edge': f"{bet.get('edge', 0)*100:.1f}%",
            'Stake Sugerido': f"R$ {bet.get('suggested_stake', 0):.2f}",
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by edge descending
    df = df.sort_values('Edge', ascending=False)
    
    # Style
    st.dataframe(
        df.style.background_gradient(
            subset=['Edge'],
            cmap='Greens'
        ),
        use_container_width=True
    )


def render_arbitrage_table(arbitrage_opportunities: List[Dict[str, Any]]):
    """
    Render arbitrage opportunities table.
    
    Args:
        arbitrage_opportunities: List of arbitrage dictionaries
    """
    if not arbitrage_opportunities:
        st.info("Nenhuma oportunidade de arbitragem encontrada.")
        return
    
    rows = []
    for arb in arbitrage_opportunities:
        rows.append({
            'Partida': arb.get('match', ''),
            'Casa 1': arb.get('bookmaker1', ''),
            'Seleção 1': arb.get('selection1', ''),
            'Odds 1': f"{arb.get('odds1', 0):.2f}",
            'Casa 2': arb.get('bookmaker2', ''),
            'Seleção 2': arb.get('selection2', ''),
            'Odds 2': f"{arb.get('odds2', 0):.2f}",
            'Retorno': f"{arb.get('return_pct', 0):.2f}%",
        })
    
    df = pd.DataFrame(rows)
    
    # Sort by return descending
    df = df.sort_values('Retorno', ascending=False)
    
    st.dataframe(
        df.style.background_gradient(
            subset=['Retorno'],
            cmap='Blues'
        ),
        use_container_width=True
    )


def render_bookmaker_comparison(
    match: Dict[str, Any],
    bookmakers_odds: Dict[str, List[float]]
):
    """
    Render odds comparison across multiple bookmakers for a single match.
    
    Args:
        match: Match information
        bookmakers_odds: Dictionary mapping bookmaker names to list of odds
    """
    team1 = match.get('team1', 'Team 1')
    team2 = match.get('team2', 'Team 2')
    
    st.subheader(f"{team1} vs {team2}")
    
    if not bookmakers_odds:
        st.info("Nenhuma comparação disponível.")
        return
    
    # Create comparison table
    rows = []
    for bookmaker, odds in bookmakers_odds.items():
        row = {'Casa de Apostas': bookmaker}
        
        # Assuming odds are [team1, draw (if applicable), team2]
        if len(odds) >= 2:
            row[team1] = f"{odds[0]:.2f}"
            if len(odds) == 3:
                row['Empate'] = f"{odds[1]:.2f}"
                row[team2] = f"{odds[2]:.2f}"
            else:
                row[team2] = f"{odds[1]:.2f}"
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
