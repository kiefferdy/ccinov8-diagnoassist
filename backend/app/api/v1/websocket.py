"""
WebSocket API endpoints for DiagnoAssist Backend

Handles real-time WebSocket connections for:
- Encounter collaboration
- AI chat
- System notifications
"""
import json
import logging
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from datetime import datetime

from app.core.websocket_manager import (
    websocket_manager, 
    ConnectionType, 
    MessageType,
    WebSocketConnection
)
from app.models.auth import UserModel
from app.middleware.auth_middleware import get_current_user_websocket
from app.core.exceptions import WebSocketException, NotFoundError
from app.services.encounter_service import encounter_service
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/encounter/{encounter_id}")
async def encounter_websocket(
    websocket: WebSocket,
    encounter_id: str,
    token: str = Query(..., description="JWT token for authentication")
):
    """
    WebSocket endpoint for real-time encounter collaboration
    
    Features:
    - Real-time SOAP section updates
    - User presence indicators
    - Auto-save functionality
    - Collaborative editing
    """
    connection_id = f"encounter_{encounter_id}_{uuid.uuid4().hex[:8]}"
    connection: Optional[WebSocketConnection] = None
    
    try:
        # Authenticate user from token
        user = await get_current_user_websocket(token)
        
        # Verify encounter exists and user has access
        encounter = await encounter_service.get_encounter(encounter_id, user)
        if not encounter:
            await websocket.close(code=4004, reason="Encounter not found")
            return
        
        # Connect WebSocket
        connection = await websocket_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user=user,
            connection_type=ConnectionType.ENCOUNTER,
            resource_id=encounter_id
        )
        
        # Start auto-save for this encounter
        await websocket_manager.start_auto_save(encounter_id, interval_seconds=30)
        
        # Send current encounter state
        await connection.send_message({
            "type": MessageType.ENCOUNTER_UPDATE.value,
            "encounter": encounter.model_dump(),
            "connected_users": websocket_manager.get_resource_users(encounter_id)
        })
        
        # Handle incoming messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_encounter_message(connection, data)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling encounter message: {e}")
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": f"Message handling failed: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"Encounter WebSocket error: {e}")
        if connection:
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"Connection error: {str(e)}"
            })
        else:
            await websocket.close(code=4000, reason=f"Connection failed: {str(e)}")
    
    finally:
        if connection:
            await websocket_manager.disconnect(connection_id)


@router.websocket("/chat/{encounter_id}")
async def chat_websocket(
    websocket: WebSocket,
    encounter_id: str,
    token: str = Query(..., description="JWT token for authentication")
):
    """
    WebSocket endpoint for real-time AI chat
    
    Features:
    - Real-time AI conversation
    - Chat history
    - Typing indicators
    - Context-aware responses
    """
    connection_id = f"chat_{encounter_id}_{uuid.uuid4().hex[:8]}"
    connection: Optional[WebSocketConnection] = None
    
    try:
        # Authenticate user
        user = await get_current_user_websocket(token)
        
        # Verify encounter exists and user has access
        encounter = await encounter_service.get_encounter(encounter_id, user)
        if not encounter:
            await websocket.close(code=4004, reason="Encounter not found")
            return
        
        # Connect WebSocket
        connection = await websocket_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user=user,
            connection_type=ConnectionType.CHAT,
            resource_id=encounter_id
        )
        
        # Send chat history if available
        try:
            # Get existing chat history for this encounter
            chat_history = await ai_service.get_chat_history(f"encounter_{encounter_id}")
            if chat_history:
                await connection.send_message({
                    "type": MessageType.CHAT_HISTORY.value,
                    "history": chat_history.model_dump()
                })
        except Exception as e:
            logger.warning(f"Failed to load chat history: {e}")
        
        # Handle incoming chat messages
        while True:
            try:
                data = await websocket.receive_json()
                await handle_chat_message(connection, encounter_id, data)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling chat message: {e}")
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": f"Chat error: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")
        if connection:
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"Connection error: {str(e)}"
            })
        else:
            await websocket.close(code=4000, reason=f"Connection failed: {str(e)}")
    
    finally:
        if connection:
            await websocket_manager.disconnect(connection_id)


@router.websocket("/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token for authentication")
):
    """
    WebSocket endpoint for system notifications
    
    Features:
    - System-wide notifications
    - User-specific alerts
    - Status updates
    """
    connection_id = f"notifications_{uuid.uuid4().hex[:8]}"
    connection: Optional[WebSocketConnection] = None
    
    try:
        # Authenticate user
        user = await get_current_user_websocket(token)
        
        # Connect WebSocket
        connection = await websocket_manager.connect(
            websocket=websocket,
            connection_id=connection_id,
            user=user,
            connection_type=ConnectionType.NOTIFICATIONS
        )
        
        # Send welcome notification
        await connection.send_message({
            "type": MessageType.NOTIFICATION.value,
            "title": "Connected",
            "message": "You are now connected to real-time notifications",
            "level": "info"
        })
        
        # Handle incoming messages (mainly for ping/pong)
        while True:
            try:
                data = await websocket.receive_json()
                
                if data.get("type") == MessageType.PING.value:
                    await connection.send_message({
                        "type": MessageType.PONG.value,
                        "message": "pong"
                    })
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error handling notification message: {e}")
    
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}")
        if connection:
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"Connection error: {str(e)}"
            })
        else:
            await websocket.close(code=4000, reason=f"Connection failed: {str(e)}")
    
    finally:
        if connection:
            await websocket_manager.disconnect(connection_id)


# Message Handlers

async def handle_encounter_message(connection: WebSocketConnection, data: dict):
    """Handle messages for encounter WebSocket"""
    message_type = data.get("type")
    
    if message_type == MessageType.SOAP_UPDATE.value:
        await handle_soap_update(connection, data)
    
    elif message_type == MessageType.TYPING_START.value:
        await handle_typing_indicator(connection, data, True)
    
    elif message_type == MessageType.TYPING_STOP.value:
        await handle_typing_indicator(connection, data, False)
    
    elif message_type == MessageType.CURSOR_MOVE.value:
        await handle_cursor_move(connection, data)
    
    elif message_type == MessageType.AUTO_SAVE.value:
        await handle_auto_save(connection, data)
    
    elif message_type == MessageType.PING.value:
        await connection.send_message({
            "type": MessageType.PONG.value,
            "message": "pong"
        })
    
    else:
        await connection.send_message({
            "type": MessageType.ERROR.value,
            "error": f"Unknown message type: {message_type}"
        })


async def handle_soap_update(connection: WebSocketConnection, data: dict):
    """Handle SOAP section updates"""
    try:
        encounter_id = connection.resource_id
        soap_section = data.get("section")
        soap_data = data.get("data")
        
        if not soap_section or not soap_data:
            raise ValueError("Missing section or data")
        
        # Broadcast update to other users in the encounter
        await websocket_manager.broadcast_to_resource(
            encounter_id,
            {
                "type": MessageType.SOAP_UPDATE.value,
                "section": soap_section,
                "data": soap_data,
                "user": {
                    "id": connection.user.id,
                    "name": connection.user.name
                },
                "encounter_id": encounter_id
            },
            exclude_connection=connection.connection_id
        )
        
        # Acknowledge the update
        await connection.send_message({
            "type": MessageType.STATUS_UPDATE.value,
            "status": "soap_updated",
            "section": soap_section
        })
        
    except Exception as e:
        await connection.send_message({
            "type": MessageType.ERROR.value,
            "error": f"SOAP update failed: {str(e)}"
        })


async def handle_typing_indicator(connection: WebSocketConnection, data: dict, is_typing: bool):
    """Handle typing indicators"""
    try:
        section = data.get("section", "unknown")
        
        # Broadcast typing status to other users
        await websocket_manager.broadcast_to_resource(
            connection.resource_id,
            {
                "type": MessageType.TYPING_START.value if is_typing else MessageType.TYPING_STOP.value,
                "user": {
                    "id": connection.user.id,
                    "name": connection.user.name
                },
                "section": section,
                "encounter_id": connection.resource_id
            },
            exclude_connection=connection.connection_id
        )
        
    except Exception as e:
        logger.error(f"Typing indicator error: {e}")


async def handle_cursor_move(connection: WebSocketConnection, data: dict):
    """Handle cursor position updates"""
    try:
        section = data.get("section")
        position = data.get("position")
        
        if section and position is not None:
            # Broadcast cursor position to other users
            await websocket_manager.broadcast_to_resource(
                connection.resource_id,
                {
                    "type": MessageType.CURSOR_MOVE.value,
                    "user": {
                        "id": connection.user.id,
                        "name": connection.user.name
                    },
                    "section": section,
                    "position": position,
                    "encounter_id": connection.resource_id
                },
                exclude_connection=connection.connection_id
            )
        
    except Exception as e:
        logger.error(f"Cursor move error: {e}")


async def handle_auto_save(connection: WebSocketConnection, data: dict):
    """Handle auto-save requests"""
    try:
        encounter_id = connection.resource_id
        soap_data = data.get("soap_data")
        
        if soap_data:
            # Here you would save the data to the database
            # For now, just acknowledge the auto-save
            await connection.send_message({
                "type": MessageType.STATUS_UPDATE.value,
                "status": "auto_saved",
                "timestamp": datetime.utcnow().isoformat(),
                "encounter_id": encounter_id
            })
        
    except Exception as e:
        await connection.send_message({
            "type": MessageType.ERROR.value,
            "error": f"Auto-save failed: {str(e)}"
        })


async def handle_chat_message(connection: WebSocketConnection, encounter_id: str, data: dict):
    """Handle AI chat messages"""
    try:
        message_type = data.get("type")
        
        if message_type == MessageType.CHAT_MESSAGE.value:
            user_message = data.get("message")
            if not user_message:
                raise ValueError("Message content is required")
            
            # Send typing indicator
            await connection.send_message({
                "type": MessageType.TYPING_START.value,
                "user": {"id": "ai", "name": "AI Assistant"},
                "message": "AI is thinking..."
            })
            
            try:
                # Get patient and encounter for context
                patient = await encounter_service.get_encounter_patient(encounter_id)
                encounter = await encounter_service.get_encounter(encounter_id, connection.user)
                
                # Create chat request
                from app.models.ai_models import ChatRequest
                chat_request = ChatRequest(
                    message=user_message,
                    encounter_id=encounter_id,
                    conversation_id=f"encounter_{encounter_id}",
                    include_history=True
                )
                
                # Get AI response
                ai_response = await ai_service.chat_with_ai(chat_request, patient, encounter)
                
                # Send AI response
                await connection.send_message({
                    "type": MessageType.CHAT_MESSAGE.value,
                    "message": ai_response.message,
                    "user": {"id": "ai", "name": "AI Assistant"},
                    "conversation_id": ai_response.conversation_id,
                    "suggestions": ai_response.suggestions,
                    "confidence": ai_response.confidence.value
                })
                
            except Exception as ai_error:
                await connection.send_message({
                    "type": MessageType.ERROR.value,
                    "error": f"AI chat failed: {str(ai_error)}"
                })
            
            finally:
                # Stop typing indicator
                await connection.send_message({
                    "type": MessageType.TYPING_STOP.value,
                    "user": {"id": "ai", "name": "AI Assistant"}
                })
        
        elif message_type == MessageType.PING.value:
            await connection.send_message({
                "type": MessageType.PONG.value,
                "message": "pong"
            })
        
        else:
            await connection.send_message({
                "type": MessageType.ERROR.value,
                "error": f"Unknown chat message type: {message_type}"
            })
    
    except Exception as e:
        await connection.send_message({
            "type": MessageType.ERROR.value,
            "error": f"Chat message handling failed: {str(e)}"
        })


# Status endpoints

@router.get("/status")
async def websocket_status(current_user: UserModel = Depends(get_current_user_websocket)):
    """Get WebSocket connection status and statistics"""
    stats = websocket_manager.get_connection_stats()
    
    return {
        "success": True,
        "data": {
            "websocket_status": "operational",
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    }


@router.get("/encounter/{encounter_id}/users")
async def get_encounter_connected_users(
    encounter_id: str,
    current_user: UserModel = Depends(get_current_user_websocket)
):
    """Get users currently connected to an encounter"""
    try:
        # Verify encounter access
        encounter = await encounter_service.get_encounter(encounter_id, current_user)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        
        users = websocket_manager.get_resource_users(encounter_id)
        
        return {
            "success": True,
            "data": {
                "encounter_id": encounter_id,
                "connected_users": users,
                "user_count": len(users)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connected users: {str(e)}")


@router.post("/broadcast/notification")
async def broadcast_notification(
    notification_data: dict,
    current_user: UserModel = Depends(get_current_user_websocket)
):
    """Broadcast a notification to all connected users (Admin only)"""
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        sent_count = await websocket_manager.broadcast_notification(
            {
                "title": notification_data.get("title", "System Notification"),
                "message": notification_data.get("message", ""),
                "level": notification_data.get("level", "info"),
                "sender": current_user.name
            },
            exclude_user=current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "message": "Notification broadcasted successfully",
                "recipients": sent_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to broadcast notification: {str(e)}")