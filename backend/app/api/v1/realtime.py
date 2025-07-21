"""
Real-time API endpoints for DiagnoAssist Backend

REST endpoints to complement WebSocket functionality for:
- Managing real-time sessions
- Getting connection status
- Triggering auto-save
- Managing notifications
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

from app.models.auth import UserModel
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.realtime_service import realtime_service
from app.core.websocket_manager import websocket_manager
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/session/start/{encounter_id}")
async def start_realtime_session(
    encounter_id: str,
    auto_save_interval: int = Query(30, ge=10, le=300, description="Auto-save interval in seconds"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Start a real-time editing session for an encounter
    
    Args:
        encounter_id: ID of the encounter
        auto_save_interval: Auto-save interval in seconds (10-300)
        current_user: Authenticated user
        
    Returns:
        Session information
    """
    try:
        session_info = await realtime_service.start_encounter_session(
            encounter_id, current_user, auto_save_interval
        )
        
        return {
            "success": True,
            "data": session_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start real-time session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/encounter/{encounter_id}/soap/update")
async def update_soap_realtime(
    encounter_id: str,
    section: str,
    field: str,
    value: str,
    broadcast: bool = Query(True, description="Broadcast update to connected users"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a SOAP section field in real-time
    
    Args:
        encounter_id: ID of the encounter
        section: SOAP section (subjective, objective, assessment, plan)
        field: Field name within the section
        value: New value for the field
        broadcast: Whether to broadcast the update
        current_user: Authenticated user
        
    Returns:
        Update confirmation
    """
    try:
        update_result = await realtime_service.update_soap_section(
            encounter_id, section, field, value, current_user, broadcast
        )
        
        return {
            "success": True,
            "data": update_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update SOAP section: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update SOAP: {str(e)}")


@router.post("/encounter/{encounter_id}/auto-save")
async def trigger_auto_save(
    encounter_id: str,
    force: bool = Query(False, description="Force save even if no changes"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Manually trigger auto-save for an encounter
    
    Args:
        encounter_id: ID of the encounter
        force: Force save even if no changes
        current_user: Authenticated user
        
    Returns:
        Save result
    """
    try:
        save_result = await realtime_service.perform_auto_save(encounter_id, force)
        
        if not save_result["success"]:
            return {
                "success": False,
                "message": save_result.get("reason", "Auto-save not performed"),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "data": save_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger auto-save: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-save failed: {str(e)}")


@router.get("/encounter/{encounter_id}/activity")
async def get_encounter_activity(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current activity for an encounter
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Encounter activity information
    """
    try:
        activity_info = await realtime_service.get_encounter_activity(encounter_id)
        
        return {
            "success": True,
            "data": activity_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get encounter activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activity: {str(e)}")


@router.post("/encounter/{encounter_id}/typing")
async def set_typing_indicator(
    encounter_id: str,
    section: str,
    is_typing: bool,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Set typing indicator for a user in a SOAP section
    
    Args:
        encounter_id: ID of the encounter
        section: SOAP section where user is typing
        is_typing: True if user is typing, False if stopped
        current_user: Authenticated user
        
    Returns:
        Success status
    """
    try:
        success = await realtime_service.set_typing_indicator(
            encounter_id, current_user, section, is_typing
        )
        
        return {
            "success": success,
            "data": {
                "encounter_id": encounter_id,
                "section": section,
                "is_typing": is_typing,
                "user_id": current_user.id
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to set typing indicator: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set typing indicator: {str(e)}")


@router.get("/encounter/{encounter_id}/typing")
async def get_typing_indicators(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current typing indicators for an encounter
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        List of active typing indicators
    """
    try:
        typing_indicators = await realtime_service.get_typing_indicators(encounter_id)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "typing_indicators": typing_indicators
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get typing indicators: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get typing indicators: {str(e)}")


@router.post("/notifications/broadcast")
async def broadcast_notification(
    title: str,
    message: str,
    level: str = Query("info", regex="^(info|warning|error|success)$"),
    target_users: Optional[List[str]] = None,
    current_user: UserModel = Depends(require_admin)
):
    """
    Broadcast a notification to users (Admin only)
    
    Args:
        title: Notification title
        message: Notification message
        level: Notification level (info, warning, error, success)
        target_users: Specific users to notify (None for all)
        current_user: Authenticated admin user
        
    Returns:
        Broadcast result
    """
    try:
        sent_count = await realtime_service.broadcast_notification(
            title, message, level, target_users, [current_user.id]
        )
        
        return {
            "success": True,
            "data": {
                "title": title,
                "message": message,
                "level": level,
                "recipients": sent_count,
                "sender": current_user.name
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to broadcast notification: {str(e)}")


@router.get("/connections/stats")
async def get_connection_stats(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get WebSocket connection statistics
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Connection statistics
    """
    try:
        stats = websocket_manager.get_connection_stats()
        
        return {
            "success": True,
            "data": {
                "websocket_statistics": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get connection stats: {str(e)}")


@router.get("/encounter/{encounter_id}/connections")
async def get_encounter_connections(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get users currently connected to an encounter
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        List of connected users
    """
    try:
        connected_users = websocket_manager.get_resource_users(encounter_id)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "connected_users": connected_users,
                "connection_count": len(connected_users)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get encounter connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get connections: {str(e)}")


@router.delete("/session/cleanup/{encounter_id}")
async def cleanup_encounter_session(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Clean up encounter session data
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Cleanup confirmation
    """
    try:
        await realtime_service.cleanup_encounter_session(encounter_id)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "message": "Session data cleaned up successfully"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup encounter session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup session: {str(e)}")


# Health check for real-time services
@router.get("/health")
async def realtime_health_check():
    """
    Health check for real-time services
    
    Returns:
        Real-time service health status
    """
    try:
        stats = websocket_manager.get_connection_stats()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "websocket_manager": "operational",
                "realtime_service": "operational",
                "active_connections": stats["total_connections"],
                "active_resources": stats["active_resources"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Real-time health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }