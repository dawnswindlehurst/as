"""Health check routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from api.dependencies import get_db
from datetime import datetime
from database.models import CollectionStatus, Match, Bet

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns system status and database connectivity.
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """
    Get system metrics including collection statistics.
    
    Returns detailed metrics about data collection and system health.
    """
    try:
        # Collection statistics
        total_collections = db.query(func.count(CollectionStatus.id)).scalar() or 0
        
        completed_collections = db.query(func.count(CollectionStatus.id)).filter(
            CollectionStatus.status == "completed"
        ).scalar() or 0
        
        running_collections = db.query(func.count(CollectionStatus.id)).filter(
            CollectionStatus.status == "running"
        ).scalar() or 0
        
        failed_collections = db.query(func.count(CollectionStatus.id)).filter(
            CollectionStatus.status == "failed"
        ).scalar() or 0
        
        # Get last collection info
        last_collection = db.query(CollectionStatus).order_by(
            CollectionStatus.updated_at.desc()
        ).first()
        
        last_collection_info = None
        if last_collection:
            last_collection_info = {
                "type": last_collection.collection_type,
                "source": last_collection.source,
                "status": last_collection.status,
                "started_at": last_collection.started_at.isoformat() if last_collection.started_at else None,
                "completed_at": last_collection.completed_at.isoformat() if last_collection.completed_at else None,
                "processed_items": last_collection.processed_items,
                "total_items": last_collection.total_items,
            }
        
        # Database statistics
        total_matches = db.query(func.count(Match.id)).scalar() or 0
        total_bets = db.query(func.count(Bet.id)).scalar() or 0
        pending_bets = db.query(func.count(Bet.id)).filter(
            Bet.status == "pending"
        ).scalar() or 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "collection": {
                "total": total_collections,
                "completed": completed_collections,
                "running": running_collections,
                "failed": failed_collections,
                "last_collection": last_collection_info
            },
            "database": {
                "total_matches": total_matches,
                "total_bets": total_bets,
                "pending_bets": pending_bets
            },
            "status": "healthy"
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }


@router.get("/collection/status")
async def get_collection_status(db: Session = Depends(get_db)):
    """
    Get current collection status.
    
    Returns status of all collection tasks.
    """
    try:
        collections = db.query(CollectionStatus).order_by(
            CollectionStatus.updated_at.desc()
        ).limit(20).all()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "collections": [
                {
                    "id": c.id,
                    "type": c.collection_type,
                    "source": c.source,
                    "game": c.game,
                    "status": c.status,
                    "progress": f"{c.processed_items}/{c.total_items}" if c.total_items else "0/0",
                    "started_at": c.started_at.isoformat() if c.started_at else None,
                    "completed_at": c.completed_at.isoformat() if c.completed_at else None,
                    "error": c.error_message
                }
                for c in collections
            ]
        }
    except Exception as e:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }
