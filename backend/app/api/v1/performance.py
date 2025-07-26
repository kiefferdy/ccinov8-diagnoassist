"""
Performance Monitoring API endpoints for DiagnoAssist Backend

Provides endpoints for monitoring and managing performance optimization:
- Performance health checks
- Performance metrics and statistics
- Performance test execution
- Cache management
"""
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query

from app.models.auth import UserModel, UserRoleEnum
from app.middleware.auth_middleware import get_current_user, require_admin
from app.core.performance_integration import performance_integrator, get_performance_health_check
from app.core.performance import performance_optimizer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=dict)
async def performance_health_check():
    """
    Get comprehensive performance system health status
    
    Returns:
        Performance health information including system status, metrics, and recommendations
    """
    try:
        health_data = await get_performance_health_check()
        
        return {
            "success": True,
            "data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        }


@router.get("/stats", response_model=dict)
async def get_performance_stats(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get detailed performance statistics
    
    Args:
        current_user: Authenticated user (requires doctor or admin role)
        
    Returns:
        Detailed performance statistics and metrics
    """
    try:
        # Check permissions
        if current_user.role not in [UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN]:
            raise HTTPException(
                status_code=403, 
                detail="Insufficient permissions for performance statistics"
            )
        
        # Get comprehensive performance data
        performance_summary = await performance_optimizer.get_performance_summary()
        integration_status = performance_integrator.get_integration_status()
        
        return {
            "success": True,
            "data": {
                "performance_summary": performance_summary,
                "integration_status": integration_status,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance statistics")


@router.post("/test", response_model=dict)
async def run_performance_tests(
    current_user: UserModel = Depends(require_admin)
):
    """
    Run comprehensive performance tests (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Performance test results with pass/fail status and recommendations
    """
    try:
        logger.info(f"Performance tests initiated by user: {current_user.id}")
        
        # Run performance tests
        test_results = await performance_integrator.run_performance_tests()
        
        return {
            "success": True,
            "data": test_results,
            "message": f"Performance tests completed with status: {test_results['overall_status']}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance tests failed: {e}")
        raise HTTPException(status_code=500, detail="Performance tests failed")


@router.get("/cache", response_model=dict)
async def get_cache_statistics(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get cache performance statistics
    
    Args:
        current_user: Authenticated user (requires doctor or admin role)
        
    Returns:
        Cache statistics and performance metrics
    """
    try:
        # Check permissions
        if current_user.role not in [UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for cache statistics"
            )
        
        # Get cache statistics
        cache_stats = performance_optimizer.memory_cache.get_stats()
        query_stats = performance_optimizer.query_optimizer.get_query_stats_summary()
        
        return {
            "success": True,
            "data": {
                "cache_statistics": cache_stats,
                "query_statistics": query_stats,
                "cache_health": {
                    "operational": True,
                    "entries_count": cache_stats.get("total_entries", 0),
                    "utilization_percent": cache_stats.get("usage_percent", 0)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cache statistics")


@router.post("/cache/clear", response_model=dict)
async def clear_cache(
    cache_type: str = Query("all", description="Type of cache to clear: 'memory', 'query', or 'all'"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Clear system caches (Admin only)
    
    Args:
        cache_type: Type of cache to clear
        current_user: Authenticated admin user
        
    Returns:
        Cache clearing status and confirmation
    """
    try:
        logger.info(f"Cache clearing initiated by admin: {current_user.id}, type: {cache_type}")
        
        cleared_caches = []
        
        if cache_type in ["memory", "all"]:
            performance_optimizer.memory_cache.clear()
            cleared_caches.append("memory_cache")
        
        if cache_type in ["query", "all"]:
            performance_optimizer.query_optimizer.query_cache.clear()
            cleared_caches.append("query_cache")
        
        return {
            "success": True,
            "data": {
                "cleared_caches": cleared_caches,
                "cache_type": cache_type,
                "cleared_at": datetime.utcnow().isoformat()
            },
            "message": f"Successfully cleared {len(cleared_caches)} cache(s)",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear caches")


@router.get("/queries/slow", response_model=dict)
async def get_slow_queries(
    threshold_ms: float = Query(500, ge=100, le=10000, description="Threshold in milliseconds"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get slow query analysis (Admin only)
    
    Args:
        threshold_ms: Query execution time threshold in milliseconds
        current_user: Authenticated admin user
        
    Returns:
        List of slow queries with execution statistics
    """
    try:
        slow_queries = performance_optimizer.query_optimizer.get_slow_queries(threshold_ms)
        
        return {
            "success": True,
            "data": {
                "slow_queries": slow_queries,
                "threshold_ms": threshold_ms,
                "query_count": len(slow_queries),
                "analysis_timestamp": datetime.utcnow().isoformat()
            },
            "message": f"Found {len(slow_queries)} slow queries above {threshold_ms}ms threshold",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Slow query analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze slow queries")


@router.get("/batch", response_model=dict)
async def get_batch_processing_stats(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get batch processing statistics
    
    Args:
        current_user: Authenticated user (requires doctor or admin role)
        
    Returns:
        Batch processing statistics and queue status
    """
    try:
        # Check permissions
        if current_user.role not in [UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for batch processing statistics"
            )
        
        # Get batch processing statistics
        batch_stats = performance_optimizer.batch_processor.get_batch_stats()
        
        return {
            "success": True,
            "data": {
                "batch_statistics": batch_stats,
                "processing_health": {
                    "active_batches": len(batch_stats),
                    "total_pending_items": sum(
                        batch_info.get("pending_items", 0) 
                        for batch_info in batch_stats.values()
                    )
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get batch processing stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve batch processing statistics")


@router.post("/optimize", response_model=dict)
async def trigger_optimization(
    current_user: UserModel = Depends(require_admin)
):
    """
    Trigger manual performance optimization (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Optimization results and status
    """
    try:
        logger.info(f"Manual performance optimization triggered by admin: {current_user.id}")
        
        # Trigger optimization actions
        optimization_actions = []
        
        # Force flush all batch processors
        await performance_optimizer.batch_processor.flush_all()
        optimization_actions.append("batch_flush_completed")
        
        # Clean up expired cache entries
        performance_optimizer.memory_cache._cleanup_expired_entries()
        optimization_actions.append("cache_cleanup_completed")
        
        # Get updated performance statistics
        updated_stats = await performance_optimizer.get_performance_summary()
        
        return {
            "success": True,
            "data": {
                "optimization_actions": optimization_actions,
                "updated_performance_stats": updated_stats,
                "optimization_timestamp": datetime.utcnow().isoformat()
            },
            "message": f"Performance optimization completed: {len(optimization_actions)} actions performed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance optimization failed: {e}")
        raise HTTPException(status_code=500, detail="Performance optimization failed")


@router.get("/recommendations", response_model=dict)
async def get_performance_recommendations(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get performance improvement recommendations
    
    Args:
        current_user: Authenticated user (requires doctor or admin role)
        
    Returns:
        Performance recommendations based on current system analysis
    """
    try:
        # Check permissions
        if current_user.role not in [UserRoleEnum.DOCTOR, UserRoleEnum.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for performance recommendations"
            )
        
        # Run performance tests to get recommendations
        test_results = await performance_integrator.run_performance_tests()
        
        return {
            "success": True,
            "data": {
                "recommendations": test_results.get("recommendations", []),
                "overall_status": test_results.get("overall_status", "unknown"),
                "test_summary": {
                    "total_tests": len(test_results.get("tests", {})),
                    "test_results": test_results.get("tests", {})
                },
                "generated_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate performance recommendations")