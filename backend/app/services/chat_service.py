"""
Chat Service for DiagnoAssist Backend (Simplified)

Handles core AI chat functionality:
- AI chat conversations
- Chat history management  
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
from app.core.exceptions import ValidationException, NotFoundError

logger = logging.getLogger(__name__)


class ChatType(str, Enum):
    """Types of chat conversations"""
    AI_ASSISTANT = "ai_assistant"
    CLINICAL_CONSULTATION = "clinical_consultation"
    GENERAL = "general"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ChatService:
    """Service for managing AI chat conversations"""
    
    def __init__(self):
        # In-memory storage for chat sessions (in production, use database)
        self.chat_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, List[str]] = {}
        self.message_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def start_chat_session(
        self, 
        user: UserModel,
        chat_type: ChatType = ChatType.AI_ASSISTANT,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start a new AI chat session"""
        try:
            session_id = str(uuid.uuid4())
            
            session_data = {
                "session_id": session_id,
                "chat_type": chat_type.value,
                "user_id": user.id,
                "user_name": user.name,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "context": context or {},
                "message_count": 0,
                "is_active": True
            }
            
            self.chat_sessions[session_id] = session_data
            self.message_history[session_id] = []
            
            # Track user sessions
            if user.id not in self.user_sessions:
                self.user_sessions[user.id] = []
            self.user_sessions[user.id].append(session_id)
            
            logger.info(f"Started new chat session {session_id} for user {user.id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "message": "Chat session started successfully",
                "initial_message": "Hello! I'm your AI medical assistant. How can I help you today?"
            }
            
        except Exception as e:
            logger.error(f"Error starting chat session: {e}")
            raise ValidationException(f"Failed to start chat session: {str(e)}")
    
    async def send_message(
        self,
        session_id: str,
        user: UserModel,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a message in a chat session and get AI response"""
        try:
            if session_id not in self.chat_sessions:
                raise NotFoundError("Chat session", session_id)
            
            session = self.chat_sessions[session_id]
            
            # Verify user owns this session
            if session["user_id"] != user.id:
                raise ValidationException("User does not have access to this chat session")
            
            if not session["is_active"]:
                raise ValidationException("Chat session is not active")
            
            message_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Store user message
            user_message = {
                "id": message_id,
                "type": "user",
                "content": content,
                "sender_id": user.id,
                "sender_name": user.name,
                "timestamp": timestamp,
                "context": context or {}
            }
            
            self.message_history[session_id].append(user_message)
            
            # Get AI response
            ai_response_content = await self._generate_ai_response(
                session_id, content, session["context"], context
            )
            
            # Store AI response
            ai_message_id = str(uuid.uuid4())
            ai_message = {
                "id": ai_message_id,
                "type": "ai",
                "content": ai_response_content,
                "sender_id": "ai_assistant",
                "sender_name": "AI Medical Assistant",
                "timestamp": datetime.utcnow(),
                "context": {"ai_generated": True}
            }
            
            self.message_history[session_id].append(ai_message)
            
            # Update session
            session["last_activity"] = datetime.utcnow()
            session["message_count"] += 2  # User message + AI response
            
            logger.info(f"Processed message in session {session_id}")
            
            return {
                "success": True,
                "user_message": user_message,
                "ai_response": ai_message,
                "session_info": {
                    "session_id": session_id,
                    "message_count": session["message_count"],
                    "last_activity": session["last_activity"].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def _generate_ai_response(
        self,
        session_id: str,
        user_message: str,
        session_context: Dict[str, Any],
        message_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response to user message"""
        try:
            # Build context from chat history
            chat_history = self.message_history.get(session_id, [])
            
            # Create chat request
            chat_request = ChatRequest(
                message=user_message,
                context={
                    **session_context,
                    **(message_context or {}),
                    "chat_session_id": session_id,
                    "previous_messages": chat_history[-10:]  # Last 10 messages for context
                }
            )
            
            # Get AI response
            ai_response = await ai_service.chat_with_ai(chat_request)
            
            return ai_response.content
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    async def get_chat_history(
        self,
        session_id: str,
        user: UserModel,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get chat history for a session"""
        try:
            if session_id not in self.chat_sessions:
                raise NotFoundError("Chat session", session_id)
            
            session = self.chat_sessions[session_id]
            
            # Verify user owns this session
            if session["user_id"] != user.id:
                raise ValidationException("User does not have access to this chat session")
            
            messages = self.message_history.get(session_id, [])
            
            # Apply pagination
            total_messages = len(messages)
            paginated_messages = messages[offset:offset + limit]
            
            return {
                "success": True,
                "session_id": session_id,
                "messages": paginated_messages,
                "pagination": {
                    "total": total_messages,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_messages
                },
                "session_info": session
            }
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise
    
    async def get_user_sessions(
        self,
        user: UserModel,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """Get all chat sessions for a user"""
        try:
            user_session_ids = self.user_sessions.get(user.id, [])
            
            sessions = []
            for session_id in user_session_ids:
                if session_id in self.chat_sessions:
                    session = self.chat_sessions[session_id]
                    
                    if active_only and not session.get("is_active", False):
                        continue
                    
                    # Add message count
                    session_data = session.copy()
                    session_data["total_messages"] = len(self.message_history.get(session_id, []))
                    
                    sessions.append(session_data)
            
            # Sort by last activity
            sessions.sort(key=lambda x: x["last_activity"], reverse=True)
            
            return {
                "success": True,
                "user_id": user.id,
                "sessions": sessions,
                "total_sessions": len(sessions)
            }
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            raise
    
    async def end_chat_session(
        self,
        session_id: str,
        user: UserModel
    ) -> Dict[str, Any]:
        """End a chat session"""
        try:
            if session_id not in self.chat_sessions:
                raise NotFoundError("Chat session", session_id)
            
            session = self.chat_sessions[session_id]
            
            # Verify user owns this session
            if session["user_id"] != user.id:
                raise ValidationException("User does not have access to this chat session")
            
            # Mark session as inactive
            session["is_active"] = False
            session["ended_at"] = datetime.utcnow()
            
            logger.info(f"Ended chat session {session_id}")
            
            return {
                "success": True,
                "message": "Chat session ended successfully",
                "session_summary": {
                    "session_id": session_id,
                    "duration_minutes": (session["ended_at"] - session["created_at"]).total_seconds() / 60,
                    "total_messages": session["message_count"],
                    "ended_at": session["ended_at"].isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error ending chat session: {e}")
            raise
    
    async def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Clean up old inactive sessions"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cleaned_sessions = []
            
            for session_id, session in list(self.chat_sessions.items()):
                if session["last_activity"] < cutoff_time:
                    # Remove from all tracking
                    del self.chat_sessions[session_id]
                    if session_id in self.message_history:
                        del self.message_history[session_id]
                    
                    # Remove from user sessions
                    user_id = session["user_id"]
                    if user_id in self.user_sessions:
                        self.user_sessions[user_id] = [
                            sid for sid in self.user_sessions[user_id] if sid != session_id
                        ]
                    
                    cleaned_sessions.append(session_id)
            
            logger.info(f"Cleaned up {len(cleaned_sessions)} inactive chat sessions")
            
            return {
                "cleaned_sessions": len(cleaned_sessions),
                "remaining_sessions": len(self.chat_sessions)
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
            return {"error": str(e)}


# Global chat service instance
chat_service = ChatService()