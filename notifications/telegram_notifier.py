"""Enhanced Telegram notifier for value bets and traditional sports."""
from typing import Dict, List, Optional, Any
from notifications.bot import telegram_bot
from utils.logger import log


class TelegramNotifier:
    """Enhanced notifier for value bets across all sports.
    
    Extends the base Telegram bot with specialized notifications
    for NBA, soccer, tennis, and esports value bets.
    """
    
    def __init__(self):
        """Initialize the notifier."""
        self.bot = telegram_bot
    
    def send_value_bet_alert(self, bet_info: Dict[str, Any]) -> bool:
        """Send value bet alert.
        
        Args:
            bet_info: Dictionary with bet information
                - sport: Sport name
                - event_name: Event description
                - bet_type: Type of bet
                - selection: What to bet on
                - our_odds: Our calculated fair odds
                - bookmaker_odds: Bookmaker's odds
                - edge: Edge percentage
                - confidence: Confidence level
                - bookmaker: Bookmaker name
                - stake: Suggested stake
                
        Returns:
            True if sent successfully
        """
        message = self._format_value_bet(bet_info)
        return self.bot.send_message(message)
    
    def _format_value_bet(self, bet: Dict[str, Any]) -> str:
        """Format value bet as message."""
        sport_emoji = self._get_sport_emoji(bet.get("sport", ""))
        
        edge = bet.get("edge", 0) * 100
        confidence = bet.get("confidence", 0) * 100
        
        return f"""
{sport_emoji} *VALUE BET ALERT*

*Sport:* {bet.get('sport', 'Unknown').upper()}
*Event:* {bet.get('event_name', 'TBA')}

*Market:* {bet.get('bet_type', 'Unknown')}
*Selection:* {bet.get('selection', '')}

📊 *Analysis:*
*Our Fair Odds:* {bet.get('our_odds', 0):.2f}
*Bookmaker Odds:* {bet.get('bookmaker_odds', 0):.2f}
*Edge:* {edge:.2f}%
*Confidence:* {confidence:.1f}%

💰 *Bet Details:*
*Bookmaker:* {bet.get('bookmaker', 'Unknown')}
*Suggested Stake:* R$ {bet.get('stake', 100):.2f}
*Potential Profit:* R$ {bet.get('stake', 100) * (bet.get('bookmaker_odds', 1) - 1):.2f}
"""
    
    def send_nba_player_prop_alert(self, prop_info: Dict[str, Any]) -> bool:
        """Send NBA player prop value bet alert.
        
        Args:
            prop_info: Player prop information
            
        Returns:
            True if sent successfully
        """
        message = f"""
🏀 *NBA PLAYER PROP VALUE*

*Player:* {prop_info.get('player_name', '')} ({prop_info.get('team', '')})
*Matchup:* {prop_info.get('matchup', '')}

*Prop:* {prop_info.get('prop_type', '')}
*Line:* {prop_info.get('line', 0)} {prop_info.get('selection', '')}

📊 *Stats:*
*Season Avg:* {prop_info.get('season_avg', 0):.1f}
*Last 5 Games:* {prop_info.get('last5_avg', 0):.1f}
*vs Opponent:* {prop_info.get('vs_opponent_avg', 0):.1f}

💰 *Bet:*
*Odds:* {prop_info.get('odds', 0):.2f}
*Edge:* {prop_info.get('edge', 0) * 100:.2f}%
*Stake:* R$ {prop_info.get('stake', 100):.2f}
"""
        return self.bot.send_message(message)
    
    def send_soccer_btts_alert(self, match_info: Dict[str, Any]) -> bool:
        """Send soccer BTTS (Both Teams To Score) alert.
        
        Args:
            match_info: Match information
            
        Returns:
            True if sent successfully
        """
        message = f"""
⚽ *SOCCER BTTS VALUE*

*League:* {match_info.get('league', '')}
*Match:* {match_info.get('home_team', '')} vs {match_info.get('away_team', '')}

*Selection:* Both Teams To Score - {match_info.get('selection', 'YES')}

📊 *Analysis:*
*Home Goals/Game:* {match_info.get('home_avg_goals', 0):.2f}
*Away Goals/Game:* {match_info.get('away_avg_goals', 0):.2f}
*Home BTTS %:* {match_info.get('home_btts_pct', 0):.1%}
*Away BTTS %:* {match_info.get('away_btts_pct', 0):.1%}

💰 *Bet:*
*Odds:* {match_info.get('odds', 0):.2f}
*Edge:* {match_info.get('edge', 0) * 100:.2f}%
*Stake:* R$ {match_info.get('stake', 100):.2f}
"""
        return self.bot.send_message(message)
    
    def send_tennis_total_games_alert(self, match_info: Dict[str, Any]) -> bool:
        """Send tennis total games over/under alert.
        
        Args:
            match_info: Match information
            
        Returns:
            True if sent successfully
        """
        message = f"""
🎾 *TENNIS TOTAL GAMES VALUE*

*Tournament:* {match_info.get('tournament', '')}
*Match:* {match_info.get('player1', '')} vs {match_info.get('player2', '')}

*Selection:* Total Games {match_info.get('selection', '')} {match_info.get('line', 0)}

📊 *Analysis:*
*P1 Avg Games:* {match_info.get('p1_avg_games', 0):.1f}
*P2 Avg Games:* {match_info.get('p2_avg_games', 0):.1f}
*H2H Avg:* {match_info.get('h2h_avg_games', 0):.1f}
*Surface:* {match_info.get('surface', 'Unknown')}

💰 *Bet:*
*Odds:* {match_info.get('odds', 0):.2f}
*Edge:* {match_info.get('edge', 0) * 100:.2f}%
*Stake:* R$ {match_info.get('stake', 100):.2f}
"""
        return self.bot.send_message(message)
    
    def send_multi_sport_summary(self, opportunities: List[Dict[str, Any]]) -> bool:
        """Send summary of value bets across multiple sports.
        
        Args:
            opportunities: List of value bet opportunities
            
        Returns:
            True if sent successfully
        """
        if not opportunities:
            return False
        
        # Group by sport
        by_sport = {}
        for opp in opportunities:
            sport = opp.get("sport", "unknown")
            if sport not in by_sport:
                by_sport[sport] = []
            by_sport[sport].append(opp)
        
        message = "📈 *VALUE BETS SUMMARY*\n\n"
        
        for sport, opps in by_sport.items():
            emoji = self._get_sport_emoji(sport)
            message += f"{emoji} *{sport.upper()}:* {len(opps)} opportunities\n"
        
        message += f"\n*Total Opportunities:* {len(opportunities)}\n"
        message += f"*Total Edge:* {sum(o.get('edge', 0) for o in opportunities) * 100:.2f}%\n"
        
        # Top 3 by edge
        top_opps = sorted(opportunities, key=lambda x: x.get("edge", 0), reverse=True)[:3]
        
        message += "\n🔥 *Top 3 by Edge:*\n"
        for i, opp in enumerate(top_opps, 1):
            message += f"\n{i}. {opp.get('event_name', 'TBA')}\n"
            message += f"   Edge: {opp.get('edge', 0) * 100:.2f}% @ {opp.get('bookmaker_odds', 0):.2f}\n"
        
        return self.bot.send_message(message)
    
    def send_bet_result(self, bet_result: Dict[str, Any]) -> bool:
        """Send bet result notification.
        
        Args:
            bet_result: Bet result information
            
        Returns:
            True if sent successfully
        """
        sport_emoji = self._get_sport_emoji(bet_result.get("sport", ""))
        status = bet_result.get("status", "unknown")
        
        if status == "won":
            status_emoji = "✅"
            title = "BET WON"
        elif status == "lost":
            status_emoji = "❌"
            title = "BET LOST"
        else:
            status_emoji = "⚪"
            title = "BET SETTLED"
        
        pnl = bet_result.get("pnl", 0)
        pnl_sign = "+" if pnl >= 0 else ""
        
        message = f"""
{sport_emoji} {status_emoji} *{title}*

*Event:* {bet_result.get('event_name', '')}
*Selection:* {bet_result.get('selection', '')}

💰 *Result:*
*Stake:* R$ {bet_result.get('stake', 0):.2f}
*Odds:* {bet_result.get('odds', 0):.2f}
*P&L:* {pnl_sign}R$ {pnl:.2f}

*Original Edge:* {bet_result.get('edge', 0) * 100:.2f}%
"""
        return self.bot.send_message(message)
    
    def send_daily_report(self, stats: Dict[str, Any]) -> bool:
        """Send comprehensive daily report.
        
        Args:
            stats: Daily statistics
            
        Returns:
            True if sent successfully
        """
        total_pnl = stats.get("total_pnl", 0)
        pnl_sign = "+" if total_pnl >= 0 else ""
        pnl_emoji = "📈" if total_pnl >= 0 else "📉"
        
        message = f"""
📊 *DAILY BETTING REPORT*
{pnl_emoji} *{pnl_sign}R$ {total_pnl:.2f}*

*Today's Performance:*
• Bets Placed: {stats.get('bets_placed', 0)}
• Settled: {stats.get('bets_settled', 0)}
• Won: {stats.get('won', 0)} | Lost: {stats.get('lost', 0)}
• Win Rate: {stats.get('win_rate', 0):.1f}%

*Financial:*
• Total Staked: R$ {stats.get('total_staked', 0):.2f}
• ROI: {stats.get('roi', 0):.2f}%

*By Sport:*
"""
        
        for sport, sport_stats in stats.get("by_sport", {}).items():
            emoji = self._get_sport_emoji(sport)
            message += f"{emoji} {sport.upper()}: {sport_stats.get('pnl', 0):+.2f}\n"
        
        message += f"""
*Overall Stats:*
• Total Bets: {stats.get('overall_bets', 0)}
• Overall P&L: R$ {stats.get('overall_pnl', 0):.2f}
• Overall ROI: {stats.get('overall_roi', 0):.2f}%
"""
        
        return self.bot.send_message(message)
    
    def _get_sport_emoji(self, sport: str) -> str:
        """Get emoji for a sport."""
        emojis = {
            "nba": "🏀",
            "basketball": "🏀",
            "soccer": "⚽",
            "football": "⚽",
            "tennis": "🎾",
            "cs2": "🎯",
            "csgo": "🎯",
            "dota2": "⚔️",
            "dota": "⚔️",
            "lol": "🗡️",
            "valorant": "🔫",
        }
        return emojis.get(sport.lower(), "🎮")


# Global notifier instance
telegram_notifier = TelegramNotifier()
