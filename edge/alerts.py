"""Alert system for betting opportunities."""
from typing import List, Dict
from utils.logger import log


class AlertSystem:
    """Alert system for high-value opportunities."""
    
    def __init__(self, telegram_enabled: bool = False):
        self.telegram_enabled = telegram_enabled
        self.alert_thresholds = {
            "high_confidence": 0.70,
            "high_edge": 0.10,
            "excellent_edge": 0.15,
        }
    
    def check_alerts(self, opportunities: List[Dict]) -> List[Dict]:
        """Check opportunities for alert conditions.
        
        Args:
            opportunities: List of opportunities
            
        Returns:
            List of opportunities that triggered alerts
        """
        alerts = []
        
        for opp in opportunities:
            alert_type = self._classify_alert(opp)
            if alert_type:
                alerts.append({
                    **opp,
                    "alert_type": alert_type,
                })
        
        if alerts:
            log.info(f"Generated {len(alerts)} alerts")
            
            if self.telegram_enabled:
                self._send_telegram_alerts(alerts)
        
        return alerts
    
    def _classify_alert(self, opportunity: Dict) -> str:
        """Classify alert type.
        
        Args:
            opportunity: Opportunity dictionary
            
        Returns:
            Alert type or empty string
        """
        confidence = opportunity.get("model_probability", 0)
        edge = opportunity.get("edge", 0)
        
        if edge >= self.alert_thresholds["excellent_edge"]:
            return "excellent_edge"
        elif edge >= self.alert_thresholds["high_edge"]:
            return "high_edge"
        elif confidence >= self.alert_thresholds["high_confidence"] and edge >= 0.05:
            return "high_confidence"
        
        return ""
    
    def _send_telegram_alerts(self, alerts: List[Dict]):
        """Send alerts via Telegram.
        
        Args:
            alerts: List of alerts
        """
        # TODO: Implement Telegram integration
        log.info(f"Would send {len(alerts)} alerts via Telegram")
