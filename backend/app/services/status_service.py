"""
Status Service for DiagnoAssist Backend

Handles real-time status updates and notifications including:
- System status notifications
- User presence and availability
- Application announcements
- Medical alerts and critical notifications
- Workflow status updates
- Performance monitoring alerts
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from app.models.auth import UserModel, UserRole
from app.core.websocket_manager import websocket_manager, MessageType, ConnectionType
from app.core.exceptions import ValidationException
from app.core.monitoring import monitoring

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


@dataclass
class StatusNotification:
    """Represents a status notification"""
    id: str
    type: StatusType
    level: StatusLevel
    title: str
    message: str
    target_users: Optional[List[str]] = None
    target_roles: Optional[List[UserRole]] = None
    broadcast_all: bool = False
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    acknowledged_by: Set[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
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
        if self.status in [UserStatus.OFFLINE, UserStatus.BUSY, UserStatus.IN_SURGERY]:
            return False
        
        if self.available_until and datetime.utcnow() > self.available_until:
            return False
        
        return True


class StatusService:
    """Service for managing real-time status updates"""
    
    def __init__(self):
        # Active notifications
        self.active_notifications: Dict[str, StatusNotification] = {}
        
        # User presence tracking
        self.user_presence: Dict[str, UserPresence] = {}
        
        # System status
        self.system_status = {
            "overall_health": "healthy",
            "services": {
                "database": "healthy",
                "fhir_server": "healthy",
                "ai_service": "healthy",
                "websocket": "healthy"
            },
            "maintenance_mode": False,
            "last_updated": datetime.utcnow()
        }
        
        # Performance metrics for alerts
        self.performance_thresholds = {
            "response_time_ms": 1000,
            "error_rate_percent": 5.0,
            "cpu_usage_percent": 80.0,
            "memory_usage_percent": 85.0,
            "database_connection_percent": 90.0
        }
        
        # Start background tasks
        self._start_background_tasks()
    
    async def create_notification(
        self,
        notification_type: StatusType,
        level: StatusLevel,
        title: str,
        message: str,
        target_users: Optional[List[str]] = None,
        target_roles: Optional[List[UserRole]] = None,
        broadcast_all: bool = False,
        expires_in_minutes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StatusNotification:
        """
        Create and broadcast a status notification
        
        Args:
            notification_type: Type of notification
            level: Notification level
            title: Notification title
            message: Notification message
            target_users: Specific users to notify
            target_roles: Specific roles to notify
            broadcast_all: Broadcast to all users
            expires_in_minutes: Expiration time in minutes
            metadata: Additional metadata
            
        Returns:
            Created notification
        """
        try:
            notification_id = str(uuid.uuid4())
            
            expires_at = None
            if expires_in_minutes:
                expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
            
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
            
            # Broadcast notification
            await self._broadcast_notification(notification)
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "status_notifications_created_total",
                labels={
                    "type": notification_type.value,
                    "level": level.value
                }
            )
            
            logger.info(f"Created status notification: {title} ({level.value})")
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            raise
    
    async def update_user_presence(
        self,
        user: UserModel,
        status: UserStatus,
        activity: Optional[str] = None,
        location: Optional[str] = None,
        available_until: Optional[datetime] = None,
        auto_reply_message: Optional[str] = None
    ) -> UserPresence:
        """
        Update user presence information
        
        Args:
            user: User updating presence
            status: New status
            activity: Current activity
            location: Current location
            available_until: Available until timestamp
            auto_reply_message: Auto-reply message
            
        Returns:
            Updated presence information
        """
        try:
            presence = UserPresence(
                user_id=user.id,
                status=status,
                last_seen=datetime.utcnow(),
                current_activity=activity,
                location=location,
                available_until=available_until,
                auto_reply_message=auto_reply_message
            )
            
            old_status = None
            if user.id in self.user_presence:
                old_status = self.user_presence[user.id].status
            
            self.user_presence[user.id] = presence
            
            # Broadcast presence update if status changed
            if old_status != status:
                await self._broadcast_presence_update(user, presence)
            
            logger.debug(f"Updated presence for user {user.id}: {status.value}")
            
            return presence
            
        except Exception as e:
            logger.error(f"Failed to update user presence: {e}")
            raise
    
    async def acknowledge_notification(
        self,
        notification_id: str,
        user: UserModel
    ) -> bool:
        """
        Acknowledge a notification
        
        Args:
            notification_id: ID of the notification
            user: User acknowledging the notification
            
        Returns:
            Success status
        """
        try:
            if notification_id not in self.active_notifications:
                return False
            
            notification = self.active_notifications[notification_id]
            notification.acknowledged_by.add(user.id)
            
            # Broadcast acknowledgment
            await websocket_manager.broadcast_notification({
                "type": "notification_acknowledged",
                "notification_id": notification_id,
                "acknowledged_by": user.name,
                "acknowledged_at": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge notification: {e}")
            return False
    
    async def dismiss_notification(
        self,
        notification_id: str,
        user: UserModel
    ) -> bool:
        """
        Dismiss a notification for a user
        
        Args:
            notification_id: ID of the notification
            user: User dismissing the notification
            
        Returns:
            Success status
        """
        try:
            if notification_id not in self.active_notifications:
                return False
            
            # For now, just acknowledge it (in production, track dismissals separately)
            return await self.acknowledge_notification(notification_id, user)
            
        except Exception as e:
            logger.error(f"Failed to dismiss notification: {e}")
            return False
    
    async def create_medical_alert(
        self,
        patient_id: str,
        encounter_id: Optional[str],
        alert_type: str,
        severity: StatusLevel,
        description: str,
        target_roles: Optional[List[UserRole]] = None
    ) -> StatusNotification:
        """
        Create a medical alert notification
        
        Args:
            patient_id: ID of the patient
            encounter_id: ID of the encounter (if applicable)
            alert_type: Type of medical alert
            severity: Alert severity
            description: Alert description
            target_roles: Roles to notify
            
        Returns:
            Created alert notification
        """
        try:
            title = f"Medical Alert: {alert_type}"
            
            metadata = {
                "patient_id": patient_id,
                "encounter_id": encounter_id,
                "alert_type": alert_type,
                "requires_immediate_attention": severity == StatusLevel.CRITICAL
            }
            
            notification = await self.create_notification(
                notification_type=StatusType.MEDICAL_ALERT,
                level=severity,
                title=title,
                message=description,
                target_roles=target_roles or [UserRole.DOCTOR, UserRole.NURSE],
                expires_in_minutes=60,  # Medical alerts expire in 1 hour
                metadata=metadata
            )
            
            # Log medical alert
            logger.warning(f"Medical alert created: {alert_type} for patient {patient_id}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create medical alert: {e}")
            raise
    
    async def create_workflow_status(
        self,
        workflow_type: str,
        status: str,
        entity_id: str,
        description: str,
        user: Optional[UserModel] = None
    ) -> StatusNotification:
        """
        Create a workflow status notification
        
        Args:
            workflow_type: Type of workflow (encounter_signing, fhir_sync, etc.)
            status: Workflow status (started, completed, failed)
            entity_id: ID of the entity being processed
            description: Status description
            user: User who triggered the workflow
            
        Returns:
            Created notification
        """
        try:
            level = StatusLevel.INFO
            if status == "failed":
                level = StatusLevel.ERROR
            elif status == "completed":
                level = StatusLevel.SUCCESS
            
            title = f"Workflow {status.title()}: {workflow_type.replace('_', ' ').title()}"
            
            metadata = {
                "workflow_type": workflow_type,
                "status": status,
                "entity_id": entity_id,
                "triggered_by": user.id if user else None
            }
            
            target_users = [user.id] if user else None
            
            notification = await self.create_notification(
                notification_type=StatusType.WORKFLOW,
                level=level,
                title=title,
                message=description,
                target_users=target_users,
                expires_in_minutes=30,
                metadata=metadata
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Failed to create workflow status: {e}")
            raise
    
    async def update_system_status(
        self,
        service: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Update system service status
        
        Args:
            service: Service name
            status: Service status (healthy, warning, error)
            details: Additional status details
        """
        try:
            old_status = self.system_status["services"].get(service, "unknown")
            self.system_status["services"][service] = status
            self.system_status["last_updated"] = datetime.utcnow()
            
            # Update overall health
            self._update_overall_health()
            
            # Create notification if status changed to error
            if old_status != status and status == "error":
                await self.create_notification(
                    notification_type=StatusType.SYSTEM,
                    level=StatusLevel.ERROR,
                    title=f"Service Error: {service}",
                    message=f"Service {service} is experiencing issues",
                    broadcast_all=True,
                    expires_in_minutes=60,
                    metadata={"service": service, "details": details or {}}
                )
            
            # Broadcast system status update
            await websocket_manager.broadcast_notification({
                "type": "system_status_update",
                "service": service,
                "status": status,
                "overall_health": self.system_status["overall_health"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
    
    def get_user_presence(self, user_id: str) -> Optional[UserPresence]:
        """Get user presence information"""
        return self.user_presence.get(user_id)
    
    def get_online_users(self) -> List[Dict[str, Any]]:
        """Get list of online users"""
        online_users = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=5)  # Consider offline after 5 minutes
        
        for user_id, presence in self.user_presence.items():
            if (presence.status != UserStatus.OFFLINE and 
                presence.last_seen > cutoff_time):
                online_users.append({
                    "user_id": user_id,
                    "status": presence.status.value,
                    "activity": presence.current_activity,
                    "location": presence.location,
                    "last_seen": presence.last_seen.isoformat(),
                    "available": presence.is_available()
                })
        
        return online_users
    
    def get_active_notifications(self, user: UserModel) -> List[Dict[str, Any]]:
        """Get active notifications for a user"""
        notifications = []
        current_time = datetime.utcnow()
        
        for notification in self.active_notifications.values():
            # Check if notification is expired
            if notification.expires_at and current_time > notification.expires_at:
                continue
            
            # Check if user should receive this notification
            if self._should_user_receive_notification(notification, user):
                notifications.append({
                    "id": notification.id,
                    "type": notification.type.value,
                    "level": notification.level.value,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                    "expires_at": notification.expires_at.isoformat() if notification.expires_at else None,
                    "acknowledged": user.id in notification.acknowledged_by,
                    "metadata": notification.metadata
                })
        
        return notifications
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            **self.system_status,
            "last_updated": self.system_status["last_updated"].isoformat()
        }
    
    # Private helper methods
    
    async def _broadcast_notification(self, notification: StatusNotification):
        """Broadcast notification to appropriate users"""
        try:
            notification_data = {
                "type": MessageType.NOTIFICATION.value,
                "notification": {
                    "id": notification.id,
                    "type": notification.type.value,
                    "level": notification.level.value,
                    "title": notification.title,
                    "message": notification.message,
                    "created_at": notification.created_at.isoformat(),
                    "expires_at": notification.expires_at.isoformat() if notification.expires_at else None,
                    "metadata": notification.metadata
                }
            }
            
            if notification.broadcast_all:
                await websocket_manager.broadcast_notification(notification_data)
            elif notification.target_users:
                for user_id in notification.target_users:
                    await websocket_manager.send_to_user(user_id, notification_data)
            elif notification.target_roles:
                # For role-based notifications, we'd need to query users by role
                # For now, broadcast to all (in production, implement role-based targeting)
                await websocket_manager.broadcast_notification(notification_data)
            
        except Exception as e:
            logger.error(f"Failed to broadcast notification: {e}")
    
    async def _broadcast_presence_update(self, user: UserModel, presence: UserPresence):
        """Broadcast user presence update"""
        try:
            presence_data = {
                "type": MessageType.STATUS_UPDATE.value,
                "status_type": "user_presence",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "status": presence.status.value,
                    "activity": presence.current_activity,
                    "location": presence.location,
                    "last_seen": presence.last_seen.isoformat(),
                    "available": presence.is_available()
                }
            }
            
            await websocket_manager.broadcast_notification(presence_data)
            
        except Exception as e:
            logger.error(f"Failed to broadcast presence update: {e}")
    
    def _should_user_receive_notification(self, notification: StatusNotification, user: UserModel) -> bool:
        """Check if user should receive a notification"""
        if notification.broadcast_all:
            return True
        
        if notification.target_users and user.id in notification.target_users:
            return True
        
        if notification.target_roles and user.role in notification.target_roles:
            return True
        
        return False
    
    def _update_overall_health(self):
        """Update overall system health based on service statuses"""
        services = self.system_status["services"]
        
        if any(status == "error" for status in services.values()):
            self.system_status["overall_health"] = "error"
        elif any(status == "warning" for status in services.values()):
            self.system_status["overall_health"] = "warning"
        else:
            self.system_status["overall_health"] = "healthy"
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Cleanup expired notifications every 5 minutes
        asyncio.create_task(self._cleanup_expired_notifications())
        
        # Update user presence every minute
        asyncio.create_task(self._update_offline_users())
    
    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications"""
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                current_time = datetime.utcnow()
                expired_ids = []
                
                for notification_id, notification in self.active_notifications.items():
                    if notification.expires_at and current_time > notification.expires_at:
                        expired_ids.append(notification_id)
                
                for notification_id in expired_ids:
                    del self.active_notifications[notification_id]
                
                if expired_ids:
                    logger.info(f"Cleaned up {len(expired_ids)} expired notifications")
                
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
    
    async def _update_offline_users(self):
        """Update users to offline status if they haven't been seen recently"""
        while True:
            try:
                await asyncio.sleep(60)  # 1 minute
                
                cutoff_time = datetime.utcnow() - timedelta(minutes=5)
                
                for user_id, presence in self.user_presence.items():
                    if (presence.status != UserStatus.OFFLINE and 
                        presence.last_seen < cutoff_time):
                        
                        # Update to offline
                        presence.status = UserStatus.OFFLINE
                        
                        # Broadcast presence update
                        class MockUser:
                            def __init__(self, user_id):
                                self.id = user_id
                                self.name = f"User {user_id}"
                        
                        await self._broadcast_presence_update(MockUser(user_id), presence)
                
            except Exception as e:
                logger.error(f"Error updating offline users: {e}")


# Create service instance
status_service = StatusService()