"""
Chat Service for DiagnoAssist Backend

Handles chat functionality including:
- AI chat conversations
- Chat history management
- File sharing in chat
- Chat moderation
- Context management
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum

from app.models.auth import UserModel
from app.models.ai_models import ChatRequest, ChatResponse, ChatHistory, ChatMessage
from app.services.ai_service import ai_service
from app.services.encounter_service import encounter_service
from app.services.patient_service import patient_service
from app.core.websocket_manager import websocket_manager, MessageType
from app.core.exceptions import ValidationException, NotFoundError
from app.core.monitoring import monitoring
from app.core.performance import performance_optimizer

logger = logging.getLogger(__name__)


class ChatType(str, Enum):
    """Types of chat conversations"""
    AI_ASSISTANT = "ai_assistant"
    ENCOUNTER_DISCUSSION = "encounter_discussion"
    SUPPORT = "support"
    GENERAL = "general"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ChatService:
    """Service for managing chat functionality"""
    
    def __init__(self):
        # In-memory chat storage (in production, this would be in a database)
        self.chat_rooms: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> list of chat_room_ids
        self.ai_contexts: Dict[str, Dict[str, Any]] = {}  # chat_id -> context data
        
    async def create_chat_room(
        self,
        room_type: ChatType,
        creator: UserModel,
        name: Optional[str] = None,
        description: Optional[str] = None,
        encounter_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        max_participants: int = 10
    ) -> Dict[str, Any]:
        """
        Create a new chat room
        
        Args:
            room_type: Type of chat room
            creator: User creating the room
            name: Optional room name
            description: Optional room description
            encounter_id: Associated encounter (if applicable)
            patient_id: Associated patient (if applicable)
            max_participants: Maximum number of participants
            
        Returns:
            Chat room information
        """
        try:
            room_id = str(uuid.uuid4())
            
            # Validate encounter/patient access if provided
            if encounter_id:
                encounter = await encounter_service.get_encounter(encounter_id, creator)
                if not encounter:
                    raise ValidationException(f"Access denied to encounter {encounter_id}")
                patient_id = encounter.patient_id
            
            if patient_id:
                patient = await patient_service.get_patient(patient_id, creator)
                if not patient:
                    raise ValidationException(f"Access denied to patient {patient_id}")
            
            # Create room
            room_data = {
                "id": room_id,
                "type": room_type.value,
                "name": name or f"{room_type.value.title()} Chat",
                "description": description,
                "creator_id": creator.id,
                "encounter_id": encounter_id,
                "patient_id": patient_id,
                "participants": [creator.id],
                "max_participants": max_participants,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "is_active": True,
                "message_count": 0,
                "settings": {
                    "ai_enabled": room_type == ChatType.AI_ASSISTANT,
                    "file_sharing_enabled": True,
                    "moderation_enabled": True,
                    "history_retention_days": 30
                }
            }
            
            self.chat_rooms[room_id] = room_data
            
            # Add to user sessions
            if creator.id not in self.user_sessions:
                self.user_sessions[creator.id] = []
            self.user_sessions[creator.id].append(room_id)
            
            # Initialize AI context if AI chat
            if room_type == ChatType.AI_ASSISTANT:
                await self._initialize_ai_context(room_id, encounter_id, patient_id)
            
            logger.info(f"Created chat room {room_id} of type {room_type.value} by {creator.id}")
            
            return {
                "room_id": room_id,
                "room_data": room_data,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to create chat room: {e}")
            raise
    
    async def join_chat_room(
        self,
        room_id: str,
        user: UserModel,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Join a chat room
        
        Args:
            room_id: ID of the chat room
            user: User joining the room
            force: Force join even if room is full
            
        Returns:
            Join result
        """
        try:
            if room_id not in self.chat_rooms:
                raise NotFoundError("Chat room", room_id)
            
            room = self.chat_rooms[room_id]
            
            # Check if room is active
            if not room["is_active"]:
                raise ValidationException("Chat room is not active")
            
            # Check if user is already in room
            if user.id in room["participants"]:
                return {
                    "success": True,
                    "message": "User already in room",
                    "room_data": room
                }
            
            # Check room capacity
            if len(room["participants"]) >= room["max_participants"] and not force:
                raise ValidationException("Chat room is full")
            
            # Validate access permissions
            await self._validate_room_access(room, user)
            
            # Add user to room
            room["participants"].append(user.id)
            room["last_activity"] = datetime.utcnow()
            
            # Add to user sessions
            if user.id not in self.user_sessions:
                self.user_sessions[user.id] = []
            if room_id not in self.user_sessions[user.id]:
                self.user_sessions[user.id].append(room_id)
            
            # Broadcast user joined
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.USER_JOINED.value,
                    "room_id": room_id,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "role": user.role.value
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"User {user.id} joined chat room {room_id}")
            
            return {
                "success": True,
                "message": "Successfully joined chat room",
                "room_data": room
            }
            
        except Exception as e:
            logger.error(f"Failed to join chat room {room_id}: {e}")
            raise
    
    async def leave_chat_room(
        self,
        room_id: str,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Leave a chat room
        
        Args:
            room_id: ID of the chat room
            user: User leaving the room
            
        Returns:
            Leave result
        """
        try:
            if room_id not in self.chat_rooms:
                raise NotFoundError("Chat room", room_id)
            
            room = self.chat_rooms[room_id]
            
            # Remove user from room
            if user.id in room["participants"]:
                room["participants"].remove(user.id)
                room["last_activity"] = datetime.utcnow()
            
            # Remove from user sessions
            if user.id in self.user_sessions and room_id in self.user_sessions[user.id]:
                self.user_sessions[user.id].remove(room_id)
            
            # Broadcast user left
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.USER_LEFT.value,
                    "room_id": room_id,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "role": user.role.value
                    },
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Deactivate room if no participants left (except AI rooms)
            if not room["participants"] and room["type"] != ChatType.AI_ASSISTANT.value:
                room["is_active"] = False
            
            logger.info(f"User {user.id} left chat room {room_id}")
            
            return {
                "success": True,
                "message": "Successfully left chat room"
            }
            
        except Exception as e:
            logger.error(f"Failed to leave chat room {room_id}: {e}")
            raise
    
    async def send_message(
        self,
        room_id: str,
        sender: UserModel,
        content: str,
        message_type: str = "text",
        priority: MessagePriority = MessagePriority.NORMAL,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a message to a chat room
        
        Args:
            room_id: ID of the chat room
            sender: User sending the message
            content: Message content
            message_type: Type of message (text, image, file, system)
            priority: Message priority
            reply_to: ID of message being replied to
            attachments: List of file attachments
            
        Returns:
            Message sending result
        """
        try:
            if room_id not in self.chat_rooms:
                raise NotFoundError("Chat room", room_id)
            
            room = self.chat_rooms[room_id]
            
            # Validate user is in room
            if sender.id not in room["participants"]:
                raise ValidationException("User not in chat room")
            
            # Create message
            message_id = str(uuid.uuid4())
            message = {
                "id": message_id,
                "room_id": room_id,
                "sender_id": sender.id,
                "sender_name": sender.name,
                "sender_role": sender.role.value,
                "content": content,
                "type": message_type,
                "priority": priority.value,
                "reply_to": reply_to,
                "attachments": attachments or [],
                "timestamp": datetime.utcnow(),
                "edited": False,
                "deleted": False
            }
            
            # Update room activity
            room["last_activity"] = datetime.utcnow()
            room["message_count"] += 1
            
            # Broadcast message to room participants
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.CHAT_MESSAGE.value,
                    "message": {
                        **message,
                        "timestamp": message["timestamp"].isoformat()
                    }
                }
            )
            
            # Handle AI response if it's an AI room and not from AI
            if (room["settings"]["ai_enabled"] and 
                room["type"] == ChatType.AI_ASSISTANT.value and 
                sender.id != "ai"):
                
                # Trigger AI response asynchronously
                asyncio.create_task(self._handle_ai_response(room_id, message, room))
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "chat_messages_sent_total",
                labels={
                    "room_type": room["type"],
                    "message_type": message_type,
                    "priority": priority.value
                }
            )
            
            logger.info(f"Message sent to room {room_id} by {sender.id}")
            
            return {
                "success": True,
                "message_id": message_id,
                "timestamp": message["timestamp"].isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send message to room {room_id}: {e}")
            raise
    
    async def get_chat_history(
        self,
        room_id: str,
        user: UserModel,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get chat history for a room
        
        Args:
            room_id: ID of the chat room
            user: User requesting history
            limit: Maximum number of messages
            before: Get messages before this timestamp
            
        Returns:
            Chat history
        """
        try:
            if room_id not in self.chat_rooms:
                raise NotFoundError("Chat room", room_id)
            
            room = self.chat_rooms[room_id]
            
            # Validate user access
            await self._validate_room_access(room, user)
            
            # For now, return AI chat history if it's an AI room
            if room["type"] == ChatType.AI_ASSISTANT.value:
                # Get AI chat history
                conversation_id = f"room_{room_id}"
                ai_history = await ai_service.get_chat_history(conversation_id)
                
                if ai_history:
                    return {
                        "success": True,
                        "room_id": room_id,
                        "messages": [
                            {
                                "id": str(uuid.uuid4()),
                                "content": msg.content,
                                "sender_id": "ai" if msg.role == "assistant" else "user",
                                "sender_name": "AI Assistant" if msg.role == "assistant" else "User",
                                "timestamp": msg.timestamp.isoformat() if hasattr(msg, 'timestamp') else datetime.utcnow().isoformat(),
                                "type": "text"
                            }
                            for msg in ai_history.messages[-limit:]
                        ],
                        "has_more": len(ai_history.messages) > limit
                    }
            
            # Return empty for non-AI rooms (would be database-backed in production)
            return {
                "success": True,
                "room_id": room_id,
                "messages": [],
                "has_more": False
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat history for room {room_id}: {e}")
            raise
    
    async def get_user_chat_rooms(self, user: UserModel) -> List[Dict[str, Any]]:
        """
        Get all chat rooms for a user
        
        Args:
            user: User to get rooms for
            
        Returns:
            List of user's chat rooms
        """
        try:
            user_rooms = []
            
            for room_id, room in self.chat_rooms.items():
                if user.id in room["participants"] and room["is_active"]:
                    # Basic room info without sensitive data
                    room_info = {
                        "id": room_id,
                        "name": room["name"],
                        "type": room["type"],
                        "description": room.get("description"),
                        "participant_count": len(room["participants"]),
                        "last_activity": room["last_activity"].isoformat(),
                        "message_count": room["message_count"],
                        "encounter_id": room.get("encounter_id"),
                        "patient_id": room.get("patient_id")
                    }
                    user_rooms.append(room_info)
            
            # Sort by last activity
            user_rooms.sort(key=lambda x: x["last_activity"], reverse=True)
            
            return user_rooms
            
        except Exception as e:
            logger.error(f"Failed to get chat rooms for user {user.id}: {e}")
            raise
    
    async def _initialize_ai_context(
        self,
        room_id: str,
        encounter_id: Optional[str] = None,
        patient_id: Optional[str] = None
    ):
        """Initialize AI context for a chat room"""
        try:
            context = {
                "room_id": room_id,
                "encounter_id": encounter_id,
                "patient_id": patient_id,
                "initialized_at": datetime.utcnow(),
                "context_data": {}
            }
            
            # Load patient context if available
            if patient_id:
                try:
                    # Get patient summary for AI context
                    context["context_data"]["patient_summary"] = f"Patient ID: {patient_id}"
                except Exception as e:
                    logger.warning(f"Failed to load patient context: {e}")
            
            # Load encounter context if available
            if encounter_id:
                try:
                    # Get encounter summary for AI context
                    context["context_data"]["encounter_summary"] = f"Encounter ID: {encounter_id}"
                except Exception as e:
                    logger.warning(f"Failed to load encounter context: {e}")
            
            self.ai_contexts[room_id] = context
            
        except Exception as e:
            logger.error(f"Failed to initialize AI context for room {room_id}: {e}")
    
    async def _handle_ai_response(self, room_id: str, user_message: Dict[str, Any], room: Dict[str, Any]):
        """Handle AI response generation"""
        try:
            # Send typing indicator
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.TYPING_START.value,
                    "user": {"id": "ai", "name": "AI Assistant"},
                    "room_id": room_id
                }
            )
            
            # Create AI chat request
            conversation_id = f"room_{room_id}"
            chat_request = ChatRequest(
                message=user_message["content"],
                encounter_id=room.get("encounter_id"),
                conversation_id=conversation_id,
                include_history=True
            )
            
            # Get AI response
            patient = None
            encounter = None
            
            if room.get("patient_id"):
                try:
                    # Get patient for context - this would need user context
                    pass  # Skip for now
                except:
                    pass
            
            if room.get("encounter_id"):
                try:
                    # Get encounter for context - this would need user context
                    pass  # Skip for now
                except:
                    pass
            
            ai_response = await ai_service.chat_with_ai(chat_request, patient, encounter)
            
            # Send AI response
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.CHAT_MESSAGE.value,
                    "message": {
                        "id": str(uuid.uuid4()),
                        "room_id": room_id,
                        "sender_id": "ai",
                        "sender_name": "AI Assistant",
                        "sender_role": "assistant",
                        "content": ai_response.message,
                        "type": "text",
                        "priority": "normal",
                        "suggestions": ai_response.suggestions,
                        "confidence": ai_response.confidence.value,
                        "timestamp": datetime.utcnow().isoformat(),
                        "edited": False,
                        "deleted": False
                    }
                }
            )
            
            # Update room activity
            room["last_activity"] = datetime.utcnow()
            room["message_count"] += 1
            
        except Exception as e:
            logger.error(f"Failed to generate AI response for room {room_id}: {e}")
            
            # Send error message
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.ERROR.value,
                    "message": "AI Assistant is currently unavailable",
                    "room_id": room_id
                }
            )
        
        finally:
            # Stop typing indicator
            await websocket_manager.broadcast_to_resource(
                room_id,
                {
                    "type": MessageType.TYPING_STOP.value,
                    "user": {"id": "ai", "name": "AI Assistant"},
                    "room_id": room_id
                }
            )
    
    async def _validate_room_access(self, room: Dict[str, Any], user: UserModel):
        """Validate user access to a chat room"""
        # For encounter-specific rooms, validate encounter access
        if room.get("encounter_id"):
            try:
                encounter = await encounter_service.get_encounter(room["encounter_id"], user)
                if not encounter:
                    raise ValidationException("Access denied to encounter")
            except Exception:
                raise ValidationException("Access denied to encounter")
        
        # For patient-specific rooms, validate patient access
        if room.get("patient_id"):
            try:
                patient = await patient_service.get_patient(room["patient_id"], user)
                if not patient:
                    raise ValidationException("Access denied to patient")
            except Exception:
                raise ValidationException("Access denied to patient")
    
    def get_room_stats(self) -> Dict[str, Any]:
        """Get chat room statistics"""
        active_rooms = sum(1 for room in self.chat_rooms.values() if room["is_active"])
        total_participants = sum(len(room["participants"]) for room in self.chat_rooms.values() if room["is_active"])
        total_messages = sum(room["message_count"] for room in self.chat_rooms.values())
        
        room_types = {}
        for room in self.chat_rooms.values():
            if room["is_active"]:
                room_type = room["type"]
                room_types[room_type] = room_types.get(room_type, 0) + 1
        
        return {
            "total_rooms": len(self.chat_rooms),
            "active_rooms": active_rooms,
            "total_participants": total_participants,
            "total_messages": total_messages,
            "rooms_by_type": room_types,
            "connected_users": len(self.user_sessions)
        }


# Create service instance
chat_service = ChatService()