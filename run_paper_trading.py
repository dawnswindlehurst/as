#!/usr/bin/env python3
"""Script CLI para rodar Paper Trading."""
import asyncio
import time
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import schedule
from jobs.paper_trading_job import PaperTradingJob
from database.db import get_db_session, init_db
from utils.logger import logger as log, setup_logger


async def run_job():
    """Executa um ciclo do job."""
    db = get_db_session()
    try:
        job = PaperTradingJob(db)
        await job.run()
    except Exception as e:
        log.error(f"Erro ao executar job: {e}")
    finally:
        db.close()


def run_once():
    """Roda o job uma vez."""
    log.info("=" * 60)
    log.info("Executando Paper Trading Job (once)")
    log.info("=" * 60)
    asyncio.run(run_job())


def run_scheduled(interval_minutes: int = 30):
    """Roda o job em schedule."""
    log.info("=" * 60)
    log.info(f"Iniciando Paper Trading Job (a cada {interval_minutes} minutos)")
    log.info("=" * 60)
    
    # Rodar a cada N minutos
    schedule.every(interval_minutes).minutes.do(lambda: asyncio.run(run_job()))
    
    # Rodar imediatamente
    asyncio.run(run_job())
    
    # Loop
    log.info("Scheduler ativo. Pressione Ctrl+C para sair.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("Scheduler interrompido pelo usuário")


def main():
    """Main entry point."""
    # Setup logger
    setup_logger()
    
    # Garantir que o banco existe
    try:
        init_db()
    except Exception as e:
        log.warning(f"Aviso ao inicializar DB (pode ser normal): {e}")
    
    # Parse args
    import argparse
    parser = argparse.ArgumentParser(description="Paper Trading Job")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Executar uma vez e sair"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Intervalo em minutos para execução scheduled (default: 30)"
    )
    
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_scheduled(args.interval)


if __name__ == "__main__":
    main()
