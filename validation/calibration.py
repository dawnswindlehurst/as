"""Model calibration validation."""
from typing import Dict
import numpy as np
from database.db import get_db
from database.models import Bet
from models.calibration import ModelCalibration


class CalibrationValidator:
    """Validate model calibration."""
    
    def __init__(self):
        self.calibrator = ModelCalibration()
    
    def validate_calibration(self) -> Dict:
        """Validate model calibration on actual results.
        
        Returns:
            Calibration validation results
        """
        with get_db() as db:
            bets = db.query(Bet).filter(
                Bet.confirmed == True,
                Bet.status.in_(["won", "lost"])
            ).all()
            
            if not bets:
                return {}
            
            y_true = np.array([1 if b.status == "won" else 0 for b in bets])
            y_pred = np.array([b.model_probability for b in bets])
            
            # Calculate calibration metrics
            brier = self.calibrator.calculate_brier_score(y_true, y_pred)
            log_loss = self.calibrator.calculate_log_loss(y_true, y_pred)
            
            # Get calibration curve
            prob_true, prob_pred = self.calibrator.calculate_calibration_curve(
                y_true, y_pred, n_bins=10
            )
            
            return {
                "total_bets": len(bets),
                "brier_score": float(brier),
                "log_loss": float(log_loss),
                "calibration_curve": {
                    "predicted": prob_pred.tolist(),
                    "actual": prob_true.tolist(),
                },
            }
    
    def is_well_calibrated(self, threshold: float = 0.1) -> bool:
        """Check if model is well calibrated.
        
        Args:
            threshold: Maximum acceptable Brier score
            
        Returns:
            True if well calibrated
        """
        validation = self.validate_calibration()
        
        if not validation:
            return False
        
        return validation["brier_score"] < threshold
