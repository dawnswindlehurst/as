"""Table components for dashboard."""
import pandas as pd


def format_bets_table(bets):
    """Format bets for table display.
    
    Args:
        bets: List of Bet objects
        
    Returns:
        Pandas DataFrame
    """
    data = []
    
    for bet in bets:
        match = bet.match
        if match:
            data.append({
                "ID": bet.id,
                "Jogo": match.game,
                "Partida": f"{match.team1} vs {match.team2}",
                "Casa": bet.bookmaker,
                "Odds": f"{bet.odds:.2f}",
                "Stake": f"R$ {bet.stake:.2f}",
                "Status": bet.status.upper(),
                "Lucro": f"R$ {bet.profit:.2f}" if bet.profit is not None else "-",
            })
    
    return pd.DataFrame(data)


def format_stats_table(stats_dict):
    """Format statistics dictionary for table display.
    
    Args:
        stats_dict: Dictionary of statistics
        
    Returns:
        Pandas DataFrame
    """
    data = []
    
    for key, value in stats_dict.items():
        data.append({
            "Métrica": key,
            "Valor": value,
        })
    
    return pd.DataFrame(data)
