"""
Collaboration API endpoints for DiagnoAssist Backend

REST endpoints for collaborative editing:
- Session management
- Operation handling
- Cursor tracking
- Lock management
"""
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from datetime import datetime

from app.models.auth import UserModel
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.collaboration_service import collaboration_service
from app.services.encounter_service import encounter_service
from app.core.exceptions import ValidationException, NotFoundError, ConflictException

logger = logging.getLogger(__name__)

router = APIRouter()


# Session Management

@router.post("/sessions/{encounter_id}/start")
async def start_collaborative_session(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Start a collaborative editing session for an encounter
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Collaborative session information
    """
    try:
        # Get encounter and validate access
        encounter = await encounter_service.get_encounter(encounter_id, current_user)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        
        # Get initial document state
        initial_document = encounter.soap.model_dump() if encounter.soap else {}
        
        # Start session
        session = await collaboration_service.start_collaborative_session(
            encounter_id, current_user, initial_document
        )
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "session_active": True,
                "version": session.version,
                "participants": list(session.participants.values()),
                "document_state": session.document_state
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start collaborative session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start collaborative session")


@router.post("/sessions/{encounter_id}/join")
async def join_collaborative_session(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Join an existing collaborative session
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Session information
    """
    try:
        # Validate encounter access
        encounter = await encounter_service.get_encounter(encounter_id, current_user)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        
        # Join session
        session = await collaboration_service.join_session(encounter_id, current_user)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "session_active": True,
                "version": session.version,
                "participants": list(session.participants.values()),
                "document_state": session.document_state
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to join collaborative session: {e}")
        raise HTTPException(status_code=500, detail="Failed to join collaborative session")


@router.post("/sessions/{encounter_id}/leave")
async def leave_collaborative_session(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Leave a collaborative session
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Leave confirmation
    """
    try:
        success = await collaboration_service.leave_session(encounter_id, current_user)
        
        return {
            "success": success,
            "data": {
                "encounter_id": encounter_id,
                "message": "Left collaborative session successfully" if success else "Failed to leave session"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to leave collaborative session: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave collaborative session")


@router.get("/sessions/{encounter_id}/state")
async def get_session_state(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current collaborative session state
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        Session state
    """
    try:
        state = await collaboration_service.get_session_state(encounter_id, current_user)
        
        return {
            "success": True,
            "data": state,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get session state: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session state")


# Operation Management

@router.post("/sessions/{encounter_id}/operations")
async def apply_operation(
    encounter_id: str,
    operation: Dict[str, Any] = Body(..., description="Operation to apply"),
    client_version: int = Body(..., description="Client's document version"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Apply an operation to the collaborative document
    
    Args:
        encounter_id: ID of the encounter
        operation: Operation to apply
        client_version: Client's document version
        current_user: Authenticated user
        
    Returns:
        Operation result
    """
    try:
        result = await collaboration_service.apply_operation(
            encounter_id, current_user, operation, client_version
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to apply operation: {e}")
        raise HTTPException(status_code=500, detail="Failed to apply operation")


# Cursor Management

@router.post("/sessions/{encounter_id}/cursor")
async def update_cursor_position(
    encounter_id: str,
    section: str = Body(..., description="SOAP section"),
    position: int = Body(..., description="Cursor position"),
    selection_start: Optional[int] = Body(None, description="Selection start"),
    selection_end: Optional[int] = Body(None, description="Selection end"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update user's cursor position
    
    Args:
        encounter_id: ID of the encounter
        section: SOAP section
        position: Cursor position
        selection_start: Selection start position
        selection_end: Selection end position
        current_user: Authenticated user
        
    Returns:
        Update confirmation
    """
    try:
        await collaboration_service.update_cursor_position(
            encounter_id, current_user, section, position, selection_start, selection_end
        )
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "section": section,
                "position": position,
                "message": "Cursor position updated"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update cursor position: {e}")
        raise HTTPException(status_code=500, detail="Failed to update cursor position")


# Lock Management

@router.post("/sessions/{encounter_id}/locks/{section}")
async def acquire_section_lock(
    encounter_id: str,
    section: str,
    lock_type: str = Body("write", description="Type of lock (read, write)"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Acquire a lock on a SOAP section for exclusive editing
    
    Args:
        encounter_id: ID of the encounter
        section: SOAP section to lock
        lock_type: Type of lock (read, write)
        current_user: Authenticated user
        
    Returns:
        Lock acquisition result
    """
    try:
        success = await collaboration_service.acquire_section_lock(
            encounter_id, current_user, section, lock_type
        )
        
        if success:
            return {
                "success": True,
                "data": {
                    "encounter_id": encounter_id,
                    "section": section,
                    "lock_type": lock_type,
                    "message": "Section locked successfully"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=409, detail="Section is already locked by another user")
        
    except Exception as e:
        logger.error(f"Failed to acquire section lock: {e}")
        raise HTTPException(status_code=500, detail="Failed to acquire section lock")


@router.delete("/sessions/{encounter_id}/locks/{section}")
async def release_section_lock(
    encounter_id: str,
    section: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Release a lock on a SOAP section
    
    Args:
        encounter_id: ID of the encounter
        section: SOAP section to unlock
        current_user: Authenticated user
        
    Returns:
        Lock release result
    """
    try:
        success = await collaboration_service.release_section_lock(
            encounter_id, current_user, section
        )
        
        return {
            "success": success,
            "data": {
                "encounter_id": encounter_id,
                "section": section,
                "message": "Section unlocked successfully" if success else "Failed to release lock"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to release section lock: {e}")
        raise HTTPException(status_code=500, detail="Failed to release section lock")


# Utility Endpoints

@router.get("/sessions/{encounter_id}/participants")
async def get_session_participants(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get participants in a collaborative session
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        List of participants
    """
    try:
        state = await collaboration_service.get_session_state(encounter_id, current_user)
        
        if not state.get("active"):
            return {
                "success": True,
                "data": {
                    "participants": [],
                    "count": 0,
                    "session_active": False
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "data": {
                "participants": state.get("participants", []),
                "count": len(state.get("participants", [])),
                "session_active": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get session participants: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session participants")


@router.get("/sessions/{encounter_id}/history")
async def get_change_history(
    encounter_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of changes"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get change history for a collaborative session
    
    Args:
        encounter_id: ID of the encounter
        limit: Maximum number of changes to return
        current_user: Authenticated user
        
    Returns:
        Change history
    """
    try:
        state = await collaboration_service.get_session_state(encounter_id, current_user)
        
        if not state.get("active"):
            return {
                "success": True,
                "data": {
                    "changes": [],
                    "count": 0,
                    "session_active": False
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # For now, return empty history (would be implemented with proper storage)
        return {
            "success": True,
            "data": {
                "changes": [],
                "count": 0,
                "session_active": True,
                "message": "Change history feature coming soon"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get change history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get change history")


# Admin Endpoints

@router.get("/admin/stats")
async def get_collaboration_stats(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get collaboration statistics (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Collaboration statistics
    """
    try:
        stats = collaboration_service.get_collaboration_stats()
        
        return {
            "success": True,
            "data": {
                "collaboration_statistics": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get collaboration statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collaboration statistics")


@router.post("/admin/sessions/{encounter_id}/force-end")
async def force_end_session(
    encounter_id: str,
    reason: str = Body(..., description="Reason for force ending"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Force end a collaborative session (Admin only)
    
    Args:
        encounter_id: ID of the encounter
        reason: Reason for force ending
        current_user: Authenticated admin user
        
    Returns:
        Force end result
    """
    try:
        # End session by removing all participants
        if encounter_id in collaboration_service.sessions:
            session = collaboration_service.sessions[encounter_id]
            participants = list(session.participants.keys())
            
            # Remove all participants (this will end the session)
            for user_id in participants:
                # Create a mock user object for cleanup
                class MockUser:
                    def __init__(self, user_id):
                        self.id = user_id
                
                await collaboration_service.leave_session(encounter_id, MockUser(user_id))
            
            logger.info(f"Admin {current_user.id} force-ended collaborative session for encounter {encounter_id}: {reason}")
            
            return {
                "success": True,
                "data": {
                    "encounter_id": encounter_id,
                    "message": "Session force-ended successfully",
                    "reason": reason,
                    "ended_by": current_user.name
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "success": True,
                "data": {
                    "encounter_id": encounter_id,
                    "message": "No active session to end"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Failed to force end session: {e}")
        raise HTTPException(status_code=500, detail="Failed to force end session")


# Health Check

@router.get("/health")
async def collaboration_health_check():
    """
    Health check for collaboration service
    
    Returns:
        Collaboration service health status
    """
    try:
        stats = collaboration_service.get_collaboration_stats()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "collaboration_service": "operational",
                "active_sessions": stats["active_sessions"],
                "total_participants": stats["total_participants"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Collaboration health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }