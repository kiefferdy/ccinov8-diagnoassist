"""
Chat API endpoints for DiagnoAssist Backend

REST endpoints for chat functionality:
- Chat room management
- Chat history
- File sharing
- Chat statistics
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from datetime import datetime

from app.models.auth import UserModel
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.chat_service import chat_service, ChatType, MessagePriority
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)

router = APIRouter()


# Chat Room Management

@router.post("/rooms")
async def create_chat_room(
    room_type: ChatType,
    name: Optional[str] = None,
    description: Optional[str] = None,
    encounter_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    max_participants: int = Query(10, ge=2, le=50),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new chat room
    
    Args:
        room_type: Type of chat room
        name: Optional room name
        description: Optional room description
        encounter_id: Associated encounter ID
        patient_id: Associated patient ID
        max_participants: Maximum number of participants (2-50)
        current_user: Authenticated user
        
    Returns:
        Created chat room information
    """
    try:
        result = await chat_service.create_chat_room(
            room_type=room_type,
            creator=current_user,
            name=name,
            description=description,
            encounter_id=encounter_id,
            patient_id=patient_id,
            max_participants=max_participants
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create chat room: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat room")


@router.get("/rooms")
async def get_user_chat_rooms(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all chat rooms for the current user
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of user's chat rooms
    """
    try:
        rooms = await chat_service.get_user_chat_rooms(current_user)
        
        return {
            "success": True,
            "data": {
                "rooms": rooms,
                "count": len(rooms)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user chat rooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat rooms")


@router.post("/rooms/{room_id}/join")
async def join_chat_room(
    room_id: str,
    force: bool = Query(False, description="Force join even if room is full"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Join a chat room
    
    Args:
        room_id: ID of the chat room
        force: Force join even if room is full
        current_user: Authenticated user
        
    Returns:
        Join result
    """
    try:
        result = await chat_service.join_chat_room(
            room_id=room_id,
            user=current_user,
            force=force
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to join chat room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to join chat room")


@router.post("/rooms/{room_id}/leave")
async def leave_chat_room(
    room_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Leave a chat room
    
    Args:
        room_id: ID of the chat room
        current_user: Authenticated user
        
    Returns:
        Leave result
    """
    try:
        result = await chat_service.leave_chat_room(
            room_id=room_id,
            user=current_user
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to leave chat room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to leave chat room")


# Message Management

@router.post("/rooms/{room_id}/messages")
async def send_message(
    room_id: str,
    content: str = Body(..., description="Message content"),
    message_type: str = Body("text", description="Message type"),
    priority: MessagePriority = Body(MessagePriority.NORMAL, description="Message priority"),
    reply_to: Optional[str] = Body(None, description="ID of message being replied to"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Send a message to a chat room
    
    Args:
        room_id: ID of the chat room
        content: Message content
        message_type: Type of message (text, image, file, system)
        priority: Message priority
        reply_to: ID of message being replied to
        current_user: Authenticated user
        
    Returns:
        Message sending result
    """
    try:
        result = await chat_service.send_message(
            room_id=room_id,
            sender=current_user,
            content=content,
            message_type=message_type,
            priority=priority,
            reply_to=reply_to
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to send message to room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")


@router.get("/rooms/{room_id}/history")
async def get_chat_history(
    room_id: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of messages"),
    before: Optional[str] = Query(None, description="Get messages before this timestamp (ISO format)"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get chat history for a room
    
    Args:
        room_id: ID of the chat room
        limit: Maximum number of messages (1-200)
        before: Get messages before this timestamp
        current_user: Authenticated user
        
    Returns:
        Chat history
    """
    try:
        before_datetime = None
        if before:
            try:
                before_datetime = datetime.fromisoformat(before.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")
        
        result = await chat_service.get_chat_history(
            room_id=room_id,
            user=current_user,
            limit=limit,
            before=before_datetime
        )
        
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get chat history for room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat history")


# AI Chat Specific Endpoints

@router.post("/ai/quick-chat")
async def ai_quick_chat(
    message: str = Body(..., description="Message to send to AI"),
    encounter_id: Optional[str] = Body(None, description="Associated encounter ID"),
    include_context: bool = Body(True, description="Include encounter/patient context"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Quick AI chat without creating a persistent room
    
    Args:
        message: Message to send to AI
        encounter_id: Associated encounter ID for context
        include_context: Whether to include encounter/patient context
        current_user: Authenticated user
        
    Returns:
        AI response
    """
    try:
        from app.services.ai_service import ai_service
        from app.models.ai_models import ChatRequest
        
        # Create temporary conversation ID
        conversation_id = f"quick_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        chat_request = ChatRequest(
            message=message,
            encounter_id=encounter_id if include_context else None,
            conversation_id=conversation_id,
            include_history=False  # No history for quick chat
        )
        
        # Get patient and encounter context if needed
        patient = None
        encounter = None
        
        if include_context and encounter_id:
            try:
                from app.services.encounter_service import encounter_service
                encounter = await encounter_service.get_encounter(encounter_id, current_user)
                if encounter:
                    from app.services.patient_service import patient_service
                    patient = await patient_service.get_patient(encounter.patient_id, current_user)
            except Exception as e:
                logger.warning(f"Failed to load context: {e}")
        
        # Get AI response
        ai_response = await ai_service.chat_with_ai(chat_request, patient, encounter)
        
        return {
            "success": True,
            "data": {
                "message": ai_response.message,
                "confidence": ai_response.confidence.value,
                "suggestions": ai_response.suggestions,
                "conversation_id": ai_response.conversation_id
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI quick chat failed: {e}")
        raise HTTPException(status_code=500, detail="AI chat failed")


@router.get("/ai/encounter/{encounter_id}")
async def get_ai_chat_for_encounter(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get or create AI chat room for a specific encounter
    
    Args:
        encounter_id: ID of the encounter
        current_user: Authenticated user
        
    Returns:
        AI chat room information
    """
    try:
        # Check if AI chat room already exists for this encounter
        user_rooms = await chat_service.get_user_chat_rooms(current_user)
        existing_room = None
        
        for room in user_rooms:
            if (room["type"] == ChatType.AI_ASSISTANT.value and 
                room.get("encounter_id") == encounter_id):
                existing_room = room
                break
        
        if existing_room:
            return {
                "success": True,
                "data": {
                    "room": existing_room,
                    "existed": True
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Create new AI chat room for encounter
        result = await chat_service.create_chat_room(
            room_type=ChatType.AI_ASSISTANT,
            creator=current_user,
            name=f"AI Assistant - Encounter {encounter_id[:8]}",
            description="AI clinical assistant for this encounter",
            encounter_id=encounter_id
        )
        
        return {
            "success": True,
            "data": {
                "room": result["room_data"],
                "existed": False
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get AI chat for encounter {encounter_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI chat")


# Admin Endpoints

@router.get("/admin/stats")
async def get_chat_statistics(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get chat system statistics (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Chat system statistics
    """
    try:
        stats = chat_service.get_room_stats()
        
        return {
            "success": True,
            "data": {
                "chat_statistics": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat statistics")


@router.delete("/admin/rooms/{room_id}")
async def delete_chat_room(
    room_id: str,
    reason: str = Body(..., description="Reason for deletion"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Delete a chat room (Admin only)
    
    Args:
        room_id: ID of the chat room
        reason: Reason for deletion
        current_user: Authenticated admin user
        
    Returns:
        Deletion result
    """
    try:
        # For now, just mark as inactive (in production, implement proper deletion)
        if room_id in chat_service.chat_rooms:
            chat_service.chat_rooms[room_id]["is_active"] = False
            chat_service.chat_rooms[room_id]["deleted_at"] = datetime.utcnow()
            chat_service.chat_rooms[room_id]["deleted_by"] = current_user.id
            chat_service.chat_rooms[room_id]["deletion_reason"] = reason
            
            return {
                "success": True,
                "data": {
                    "room_id": room_id,
                    "message": "Chat room deleted successfully"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Chat room not found")
        
    except Exception as e:
        logger.error(f"Failed to delete chat room {room_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat room")


# Health Check

@router.get("/health")
async def chat_health_check():
    """
    Health check for chat service
    
    Returns:
        Chat service health status
    """
    try:
        stats = chat_service.get_room_stats()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "chat_service": "operational",
                "active_rooms": stats["active_rooms"],
                "connected_users": stats["connected_users"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }