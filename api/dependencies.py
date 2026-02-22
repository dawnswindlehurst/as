"""Database dependencies for FastAPI."""
from typing import Generator
from sqlalchemy.orm import Session
from database.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
