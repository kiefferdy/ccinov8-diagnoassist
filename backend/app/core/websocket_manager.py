"""
WebSocket Manager for DiagnoAssist Backend

Manages WebSocket connections for real-time features including:
- Encounter collaboration
- AI chat
- Real-time updates
- Status notifications
"""
import asyncio
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

from app.models.auth import UserModel
from app.core.exceptions import WebSocketException

logger = logging.getLogger(__name__)


class ConnectionType(str, Enum):
    """Types of WebSocket connections"""
    ENCOUNTER = "encounter"
    CHAT = "chat"
    NOTIFICATIONS = "notifications"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Types of WebSocket messages"""
    # Encounter messages
    ENCOUNTER_UPDATE = "encounter_update"
    SOAP_UPDATE = "soap_update"
    AUTO_SAVE = "auto_save"
    
    # Collaboration messages
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    CURSOR_MOVE = "cursor_move"
    
    # Chat messages
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    
    # Status messages
    STATUS_UPDATE = "status_update"
    NOTIFICATION = "notification"
    ERROR = "error"
    
    # System messages
    PING = "ping"
    PONG = "pong"
    HEARTBEAT = "heartbeat"


class WebSocketConnection:
    """Represents a single WebSocket connection"""
    
    def __init__(
        self,
        websocket: WebSocket,
        connection_id: str,
        user: UserModel,
        connection_type: ConnectionType,
        resource_id: Optional[str] = None
    ):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user = user
        self.connection_type = connection_type
        self.resource_id = resource_id  # encounter_id, chat_id, etc.
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.is_active = True
        
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message through this connection"""
        try:
            if not self.is_active:
                return False
                
            message["timestamp"] = datetime.utcnow().isoformat()
            await self.websocket.send_json(message)
            self.last_activity = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {self.connection_id}: {e}")
            await self.mark_inactive()
            return False
    
    async def mark_inactive(self):
        """Mark connection as inactive"""
        self.is_active = False
        try:
            await self.websocket.close()
        except:
            pass  # Connection might already be closed


class WebSocketManager:
    """Manages all WebSocket connections and message routing"""
    
    def __init__(self):
        # Active connections by connection_id
        self.connections: Dict[str, WebSocketConnection] = {}
        
        # Connections grouped by resource (encounter_id, chat_id, etc.)
        self.resource_connections: Dict[str, Set[str]] = {}
        
        # User connections
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Connection type groups
        self.type_connections: Dict[ConnectionType, Set[str]] = {
            connection_type: set() for connection_type in ConnectionType
        }
        
        # Auto-save intervals for encounters
        self.auto_save_intervals: Dict[str, asyncio.Task] = {}
        
        # Heartbeat task
        self.heartbeat_task: Optional[asyncio.Task] = None
        
    async def connect(
        self,
        websocket: WebSocket,
        connection_id: str,
        user: UserModel,
        connection_type: ConnectionType,
        resource_id: Optional[str] = None
    ) -> WebSocketConnection:
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            connection = WebSocketConnection(
                websocket=websocket,
                connection_id=connection_id,
                user=user,
                connection_type=connection_type,
                resource_id=resource_id
            )
            
            # Store connection
            self.connections[connection_id] = connection
            
            # Add to resource group
            if resource_id:
                if resource_id not in self.resource_connections:
                    self.resource_connections[resource_id] = set()
                self.resource_connections[resource_id].add(connection_id)
            
            # Add to user group
            if user.id not in self.user_connections:
                self.user_connections[user.id] = set()
            self.user_connections[user.id].add(connection_id)
            
            # Add to type group
            self.type_connections[connection_type].add(connection_id)
            
            logger.info(f"WebSocket connected: {connection_id} ({connection_type.value})")
            
            # Send connection confirmation
            await connection.send_message({
                "type": MessageType.STATUS_UPDATE.value,
                "status": "connected",
                "connection_id": connection_id,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.value
                }
            })
            
            # Notify other users in the same resource
            if resource_id and connection_type == ConnectionType.ENCOUNTER:
                await self.broadcast_to_resource(
                    resource_id,
                    {
                        "type": MessageType.USER_JOINED.value,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "role": user.role.value
                        },
                        "resource_id": resource_id
                    },
                    exclude_connection=connection_id
                )
            
            # Start heartbeat if first connection
            if len(self.connections) == 1 and not self.heartbeat_task:
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            
            return connection
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket {connection_id}: {e}")
            raise WebSocketException(f"Connection failed: {str(e)}")
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        # Notify other users in the same resource
        if connection.resource_id and connection.connection_type == ConnectionType.ENCOUNTER:
            await self.broadcast_to_resource(
                connection.resource_id,
                {
                    "type": MessageType.USER_LEFT.value,
                    "user": {
                        "id": connection.user.id,
                        "name": connection.user.name,
                        "role": connection.user.role.value
                    },
                    "resource_id": connection.resource_id
                },
                exclude_connection=connection_id
            )
        
        # Remove from all groups
        if connection.resource_id:
            if connection.resource_id in self.resource_connections:
                self.resource_connections[connection.resource_id].discard(connection_id)
                if not self.resource_connections[connection.resource_id]:
                    del self.resource_connections[connection.resource_id]
        
        if connection.user.id in self.user_connections:
            self.user_connections[connection.user.id].discard(connection_id)
            if not self.user_connections[connection.user.id]:
                del self.user_connections[connection.user.id]
        
        self.type_connections[connection.connection_type].discard(connection_id)
        
        # Stop auto-save for encounter if this was the last connection
        if (connection.resource_id and 
            connection.connection_type == ConnectionType.ENCOUNTER and
            connection.resource_id not in self.resource_connections):
            await self._stop_auto_save(connection.resource_id)
        
        # Mark connection as inactive and close
        await connection.mark_inactive()
        
        # Remove from connections
        del self.connections[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
        
        # Stop heartbeat if no connections left
        if not self.connections and self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to a specific connection"""
        if connection_id not in self.connections:
            return False
        
        connection = self.connections[connection_id]
        return await connection.send_message(message)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> int:
        """Send message to all connections for a user"""
        if user_id not in self.user_connections:
            return 0
        
        connection_ids = self.user_connections[user_id].copy()
        sent_count = 0
        
        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_resource(
        self,
        resource_id: str,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ) -> int:
        """Broadcast message to all connections for a resource"""
        if resource_id not in self.resource_connections:
            return 0
        
        connection_ids = self.resource_connections[resource_id].copy()
        if exclude_connection:
            connection_ids.discard(exclude_connection)
        
        sent_count = 0
        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_type(
        self,
        connection_type: ConnectionType,
        message: Dict[str, Any],
        exclude_connection: Optional[str] = None
    ) -> int:
        """Broadcast message to all connections of a specific type"""
        connection_ids = self.type_connections[connection_type].copy()
        if exclude_connection:
            connection_ids.discard(exclude_connection)
        
        sent_count = 0
        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_notification(
        self,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ) -> int:
        """Broadcast notification to all users"""
        sent_count = 0
        
        for user_id in self.user_connections:
            if exclude_user and user_id == exclude_user:
                continue
            
            notification_message = {
                **message,
                "type": MessageType.NOTIFICATION.value
            }
            
            count = await self.send_to_user(user_id, notification_message)
            sent_count += count
        
        return sent_count
    
    async def start_auto_save(self, encounter_id: str, interval_seconds: int = 30):
        """Start auto-save for an encounter"""
        if encounter_id in self.auto_save_intervals:
            return  # Already running
        
        async def auto_save_loop():
            while True:
                try:
                    await asyncio.sleep(interval_seconds)
                    
                    # Check if encounter still has active connections
                    if encounter_id not in self.resource_connections:
                        break
                    
                    # Trigger auto-save
                    await self.broadcast_to_resource(
                        encounter_id,
                        {
                            "type": MessageType.AUTO_SAVE.value,
                            "encounter_id": encounter_id,
                            "message": "Auto-saving encounter..."
                        }
                    )
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Auto-save error for encounter {encounter_id}: {e}")
        
        task = asyncio.create_task(auto_save_loop())
        self.auto_save_intervals[encounter_id] = task
        
        logger.info(f"Started auto-save for encounter {encounter_id} (interval: {interval_seconds}s)")
    
    async def _stop_auto_save(self, encounter_id: str):
        """Stop auto-save for an encounter"""
        if encounter_id in self.auto_save_intervals:
            self.auto_save_intervals[encounter_id].cancel()
            del self.auto_save_intervals[encounter_id]
            logger.info(f"Stopped auto-save for encounter {encounter_id}")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to all connections"""
        while True:
            try:
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
                # Clean up inactive connections
                inactive_connections = []
                for connection_id, connection in self.connections.items():
                    if not connection.is_active:
                        inactive_connections.append(connection_id)
                    elif (datetime.utcnow() - connection.last_activity).seconds > 300:  # 5 minutes
                        # Send ping to check if connection is alive
                        success = await connection.send_message({
                            "type": MessageType.PING.value,
                            "message": "heartbeat"
                        })
                        if not success:
                            inactive_connections.append(connection_id)
                
                # Clean up inactive connections
                for connection_id in inactive_connections:
                    await self.disconnect(connection_id)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.connections),
            "connections_by_type": {
                connection_type.value: len(connection_ids)
                for connection_type, connection_ids in self.type_connections.items()
            },
            "active_resources": len(self.resource_connections),
            "connected_users": len(self.user_connections),
            "auto_save_tasks": len(self.auto_save_intervals)
        }
    
    def get_resource_users(self, resource_id: str) -> List[Dict[str, Any]]:
        """Get all users connected to a resource"""
        if resource_id not in self.resource_connections:
            return []
        
        users = []
        for connection_id in self.resource_connections[resource_id]:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                users.append({
                    "id": connection.user.id,
                    "name": connection.user.name,
                    "role": connection.user.role.value,
                    "connected_at": connection.connected_at.isoformat(),
                    "last_activity": connection.last_activity.isoformat()
                })
        
        return users


# Global WebSocket manager instance
websocket_manager = WebSocketManager()