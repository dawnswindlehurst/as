"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.settings import DATABASE_URL, ORACLE_DEPLOYMENT
from database.models import Base
from utils.logger import log

# Import historical models to ensure they're registered
try:
    from database import historical_models
except ImportError:
    pass  # Historical models are optional

# Import scorealarm models to ensure they're registered
try:
    from database import scorealarm_models
except ImportError:
    pass  # Scorealarm models are optional

# Import paper trading models to ensure they're registered
try:
    from database import paper_trading_models
except ImportError:
    pass  # Paper trading models are optional

# Import LoL models to ensure they're registered
try:
    from database import lol_models
except ImportError:
    pass  # LoL models are optional

# Import team and player models to ensure they're registered
try:
    from database import team_models
    from database import player_models
    from database import id_mapping_models
except ImportError:
    pass  # Multi-sport models are optional


# Create engine with Oracle-specific optimizations
if ORACLE_DEPLOYMENT and DATABASE_URL.startswith('postgresql'):
    from config.oracle import DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT, DB_POOL_RECYCLE
    
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_timeout=DB_POOL_TIMEOUT,
        pool_recycle=DB_POOL_RECYCLE,
    )
    log.info(f"Database engine created with Oracle optimizations (pool_size={DB_POOL_SIZE})")
else:
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )
    log.info("Database engine created with default settings")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database - create all tables."""
    log.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    log.info("Database initialized successfully")


def drop_db():
    """Drop all tables - use with caution!"""
    log.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    log.warning("All tables dropped")


@contextmanager
def get_db() -> Session:
    """Get database session context manager.
    
    Usage:
        with get_db() as db:
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        log.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """Get a new database session.
    
    Returns:
        SQLAlchemy Session
    """
    return SessionLocal()
