"""Checkpoint manager for resumable historical data population."""
import json
from pathlib import Path
from datetime import datetime, timezone
from utils.logger import log
from config.settings import DATA_DIR


class CheckpointManager:
    """Gerencia checkpoints para resumir populamento."""
    
    def __init__(self, checkpoint_file: str = "data/populate_checkpoint.json", max_age_hours: int | None = None):
        self.file = Path(checkpoint_file)
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.max_age_hours = max_age_hours
    
    def load(self) -> dict:
        """Carrega checkpoint existente."""
        try:
            if self.file.exists():
                with open(self.file, 'r') as f:
                    data = json.load(f)

                if self._is_stale(data):
                    log.info("♻️ Checkpoint expirado por idade; iniciando novo ciclo")
                    self.clear()
                    return self._empty_checkpoint()

                log.info(f"📂 Checkpoint carregado: {len(data.get('completed_tournaments', []))} torneios já processados")
                return data
        except Exception as e:
            log.warning(f"⚠️ Erro ao carregar checkpoint: {e}")

        return self._empty_checkpoint()

    def _empty_checkpoint(self) -> dict:
        """Retorna estrutura padrão de checkpoint vazio."""
        return {
            "completed_tournaments": [],
            "completed_sports": [],
            "stats": {
                "sports": 0,
                "tournaments": 0,
                "seasons": 0,
                "matches": 0,
                "errors": 0
            },
            "last_updated": None
        }

    def _is_stale(self, data: dict) -> bool:
        """Valida se o checkpoint excedeu a idade máxima permitida."""
        if self.max_age_hours is None:
            return False

        last_updated = data.get("last_updated")
        if not last_updated:
            return False

        try:
            last_updated_dt = datetime.fromisoformat(last_updated)
        except ValueError:
            log.warning("⚠️ Formato de last_updated inválido no checkpoint; mantendo dados")
            return False

        if last_updated_dt.tzinfo is None:
            last_updated_dt = last_updated_dt.replace(tzinfo=timezone.utc)

        age_hours = (datetime.now(timezone.utc) - last_updated_dt).total_seconds() / 3600
        return age_hours >= self.max_age_hours
    
    def save(self, data: dict):
        """Salva checkpoint."""
        data["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def mark_tournament_complete(self, data: dict, tournament_id: int):
        """Marca torneio como completo."""
        if tournament_id not in data["completed_tournaments"]:
            data["completed_tournaments"].append(tournament_id)
            self.save(data)
    
    def mark_sport_complete(self, data: dict, sport_id: int):
        """Marca esporte como completo."""
        if sport_id not in data["completed_sports"]:
            data["completed_sports"].append(sport_id)
            self.save(data)
    
    def is_tournament_done(self, data: dict, tournament_id: int) -> bool:
        """Verifica se torneio já foi processado."""
        return tournament_id in data["completed_tournaments"]
    
    def is_sport_done(self, data: dict, sport_id: int) -> bool:
        """Verifica se esporte já foi processado."""
        return sport_id in data["completed_sports"]
    
    def clear(self):
        """Limpa checkpoint (para recomeçar do zero)."""
        if self.file.exists():
            self.file.unlink()
            log.info("🗑️ Checkpoint limpo")
