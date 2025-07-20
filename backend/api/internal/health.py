from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
import time
from datetime import datetime

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DiagnoAssist API"
    }

@router.get("/health/detailed", summary="Detailed Health Check")
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check including database connectivity
    """
    start_time = time.time()
    
    # Check database
    db_status = "healthy"
    db_latency = 0
    try:
        db_start = time.time()
        db.execute("SELECT 1")
        db_latency = (time.time() - db_start) * 1000  # ms
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    total_time = (time.time() - start_time) * 1000
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "DiagnoAssist API",
        "version": "1.0.0",
        "checks": {
            "database": {
                "status": db_status,
                "latency_ms": round(db_latency, 2)
            }
        },
        "total_latency_ms": round(total_time, 2)
    }