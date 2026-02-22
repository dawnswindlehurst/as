#!/usr/bin/env python3
"""
Runner para populamento histórico.

Uso:
    python run_populate_historical.py           # Continua de onde parou
    python run_populate_historical.py --fresh   # Recomeça do zero
    python run_populate_historical.py --status  # Mostra status do checkpoint
"""

import asyncio
import argparse
from jobs.populate_historical import HistoricalPopulateJob
from utils.checkpoint import CheckpointManager
from utils.logger import log


def show_status():
    """Mostra status do checkpoint."""
    checkpoint = CheckpointManager()
    data = checkpoint.load()
    
    print("\n📊 STATUS DO POPULAMENTO")
    print("="*40)
    print(f"Esportes completos: {len(data['completed_sports'])}")
    print(f"Torneios completos: {len(data['completed_tournaments'])}")
    print(f"Stats: {data['stats']}")
    print(f"Última atualização: {data['last_updated']}")
    print("="*40)


def main():
    parser = argparse.ArgumentParser(description="Populamento histórico Scorealarm")
    parser.add_argument("--fresh", action="store_true", help="Recomeça do zero")
    parser.add_argument("--status", action="store_true", help="Mostra status")
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.fresh:
        checkpoint = CheckpointManager()
        checkpoint.clear()
        log.info("🔄 Recomeçando do zero...")
    
    log.info("🚀 Iniciando populamento histórico...")
    log.info("💡 Pressione Ctrl+C para interromper (progresso será salvo)")
    
    job = HistoricalPopulateJob()
    asyncio.run(job.run())


if __name__ == "__main__":
    main()
