"""
Status Service for DiagnoAssist Backend (Simplified)

Handles basic status functionality:
- System status information
- User presence tracking (simplified)
- Basic application status
- Medical alerts (simplified logging)
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from app.models.auth import UserModel, UserRoleEnum
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class StatusType(str, Enum):
    """Types of status updates"""
    SYSTEM = "system"
    USER_PRESENCE = "user_presence"
    APPLICATION = "application"
    MEDICAL_ALERT = "medical_alert"
    WORKFLOW = "workflow"
    PERFORMANCE = "performance"
    MAINTENANCE = "maintenance"
    SECURITY = "security"


class StatusLevel(str, Enum):
    """Status notification levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class UserStatus(str, Enum):
    """User presence status"""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"
    IN_CALL = "in_call"
    IN_SURGERY = "in_surgery"
    ON_BREAK = "on_break"


# Legacy enums for compatibility
class MessageType(str, Enum):
    """Message types (legacy compatibility)"""
    STATUS_UPDATE = "status_update"
    NOTIFICATION = "notification"
    ALERT = "alert"


class ConnectionType(str, Enum):
    """Connection types (legacy compatibility)"""
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class StatusNotification:
    """Represents a status notification"""
    id: str
    type: StatusType
    level: StatusLevel
    title: str
    message: str
    target_users: Optional[List[str]] = None
    target_roles: Optional[List[UserRoleEnum]] = None
    broadcast_all: bool = False
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    acknowledged_by: Optional[set] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.acknowledged_by is None:
            self.acknowledged_by = set()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UserPresence:
    """Represents a user's presence information"""
    user_id: str
    status: UserStatus
    last_seen: datetime
    current_activity: Optional[str] = None
    location: Optional[str] = None
    available_until: Optional[datetime] = None
    auto_reply_message: Optional[str] = None
    
    def is_available(self) -> bool:
        """Check if user is available"""
        return self.status not in [UserStatus.OFFLINE, UserStatus.BUSY, UserStatus.IN_SURGERY]


class StatusService:
    """Simplified service for managing status updates"""
    
    def __init__(self):
        # Active notifications (in-memory storage)
        self.active_notifications: Dict[str, StatusNotification] = {}
        
        # User presence tracking
        self.user_presence: Dict[str, UserPresence] = {}
        
        # System status
        self.system_status = {
            "overall_health": "healthy",
            "services": {
                "database": "healthy",
                "fhir_server": "healthy",
                "ai_service": "healthy"
            },
            "maintenance_mode": False,
            "last_updated": datetime.now()
        }
    
    async def create_notification(
        self,
        notification_type: StatusType,
        level: StatusLevel,
        title: str,
        message: str,
        target_users: Optional[List[str]] = None,
        target_roles: Optional[List[UserRoleEnum]] = None,
        broadcast_all: bool = False,
        expires_in_minutes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StatusNotification:
        """Create a status notification (simplified - logs instead of real-time broadcast)"""
        try:
            import uuid
            notification_id = str(uuid.uuid4())
            
            expires_at = None
            if expires_in_minutes:
                from datetime import timedelta
                expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
            
            notification = StatusNotification(
                id=notification_id,
                type=notification_type,
                level=level,
                title=title,
                message=message,
                target_users=target_users,
                target_roles=target_roles,
                broadcast_all=broadcast_all,
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            # Store notification
            self.active_notifications[notification_id] = notification
            
            # Log notification (simplified - no real-time broadcast)
            logger.info(f"Status notification created: {title} - {message} (Level: {level.value})")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise ValidationException(f"Failed to create notification: {str(e)}")
    
    async def update_user_presence(
        self,
        user_id: str,
        status: UserStatus,
        activity: Optional[str] = None,
        location: Optional[str] = None
    ) -> UserPresence:
        """Update user presence status"""
        try:
            presence = UserPresence(
                user_id=user_id,
                status=status,
                last_seen=datetime.now(),
                current_activity=activity,
                location=location
            )
            
            self.user_presence[user_id] = presence
            
            logger.debug(f"User {user_id} presence updated to {status.value}")
            
            return presence
            
        except Exception as e:
            logger.error(f"Error updating user presence: {e}")
            raise ValidationException(f"Failed to update user presence: {str(e)}")
    
    async def get_user_presence(self, user_id: str) -> Optional[UserPresence]:
        """Get user presence status"""
        return self.user_presence.get(user_id)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        self.system_status["last_updated"] = datetime.now()
        return self.system_status.copy()
    
    async def acknowledge_notification(self, notification_id: str, user_id: str) -> bool:
        """Acknowledge a notification"""
        try:
            if notification_id in self.active_notifications:
                notification = self.active_notifications[notification_id]
                notification.acknowledged_by.add(user_id)
                logger.debug(f"Notification {notification_id} acknowledged by user {user_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging notification: {e}")
            return False
    
    async def get_user_notifications(self, user_id: str) -> List[StatusNotification]:
        """Get notifications for a specific user"""
        try:
            user_notifications = []
            for notification in self.active_notifications.values():
                if (notification.broadcast_all or 
                    (notification.target_users and user_id in notification.target_users)):
                    user_notifications.append(notification)
            
            return user_notifications
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []
    
    async def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications"""
        try:
            now = datetime.now()
            expired_ids = []
            
            for notification_id, notification in self.active_notifications.items():
                if notification.expires_at and notification.expires_at < now:
                    expired_ids.append(notification_id)
            
            for notification_id in expired_ids:
                del self.active_notifications[notification_id]
            
            if expired_ids:
                logger.info(f"Cleaned up {len(expired_ids)} expired notifications")
            
            return len(expired_ids)
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
            return 0
    
    async def broadcast_medical_alert(
        self,
        title: str,
        message: str,
        severity: StatusLevel,
        target_roles: Optional[List[UserRoleEnum]] = None
    ) -> StatusNotification:
        """Broadcast a medical alert (simplified logging)"""
        try:
            # Default to medical staff if no roles specified
            if not target_roles:
                target_roles = [UserRoleEnum.DOCTOR, UserRoleEnum.NURSE]
            
            return await self.create_notification(
                notification_type=StatusType.MEDICAL_ALERT,
                level=severity,
                title=title,
                message=message,
                target_roles=target_roles,
                expires_in_minutes=60  # Medical alerts expire in 1 hour
            )
            
        except Exception as e:
            logger.error(f"Error broadcasting medical alert: {e}")
            raise ValidationException(f"Failed to broadcast medical alert: {str(e)}")


# Create global service instance
status_service = StatusService()