"""
Status API endpoints for DiagnoAssist Backend

REST endpoints for real-time status management:
- System status monitoring
- User presence management
- Notification management
- Medical alerts
- Workflow status updates
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from datetime import datetime

from app.models.auth import UserModel, UserRole
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.status_service import (
    status_service, StatusType, StatusLevel, UserStatus
)
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

router = APIRouter()


# Notification Management

@router.post("/notifications")
async def create_notification(
    notification_type: StatusType = Body(..., description="Type of notification"),
    level: StatusLevel = Body(..., description="Notification level"),
    title: str = Body(..., description="Notification title"),
    message: str = Body(..., description="Notification message"),
    target_users: Optional[List[str]] = Body(None, description="Specific users to notify"),
    target_roles: Optional[List[UserRole]] = Body(None, description="Specific roles to notify"),
    broadcast_all: bool = Body(False, description="Broadcast to all users"),
    expires_in_minutes: Optional[int] = Body(None, description="Expiration time in minutes"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Create a status notification (Admin only)
    
    Args:
        notification_type: Type of notification
        level: Notification level
        title: Notification title
        message: Notification message
        target_users: Specific users to notify
        target_roles: Specific roles to notify
        broadcast_all: Broadcast to all users
        expires_in_minutes: Expiration time in minutes
        current_user: Authenticated admin user
        
    Returns:
        Created notification
    """
    try:
        notification = await status_service.create_notification(
            notification_type=notification_type,
            level=level,
            title=title,
            message=message,
            target_users=target_users,
            target_roles=target_roles,
            broadcast_all=broadcast_all,
            expires_in_minutes=expires_in_minutes,
            metadata={"created_by": current_user.id}
        )
        
        return {
            "success": True,
            "data": {
                "notification_id": notification.id,
                "title": notification.title,
                "level": notification.level.value,
                "created_at": notification.created_at.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to create notification")


@router.get("/notifications")
async def get_user_notifications(
    include_acknowledged: bool = Query(False, description="Include acknowledged notifications"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get notifications for the current user
    
    Args:
        include_acknowledged: Include acknowledged notifications
        current_user: Authenticated user
        
    Returns:
        List of user notifications
    """
    try:
        notifications = status_service.get_active_notifications(current_user)
        
        if not include_acknowledged:
            notifications = [n for n in notifications if not n.get("acknowledged")]
        
        return {
            "success": True,
            "data": {
                "notifications": notifications,
                "count": len(notifications),
                "unread_count": len([n for n in notifications if not n.get("acknowledged")])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")


@router.post("/notifications/{notification_id}/acknowledge")
async def acknowledge_notification(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Acknowledge a notification
    
    Args:
        notification_id: ID of the notification
        current_user: Authenticated user
        
    Returns:
        Acknowledgment confirmation
    """
    try:
        success = await status_service.acknowledge_notification(notification_id, current_user)
        
        if success:
            return {
                "success": True,
                "data": {
                    "notification_id": notification_id,
                    "acknowledged_by": current_user.name,
                    "acknowledged_at": datetime.utcnow().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
        
    except Exception as e:
        logger.error(f"Failed to acknowledge notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge notification")


@router.post("/notifications/{notification_id}/dismiss")
async def dismiss_notification(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Dismiss a notification
    
    Args:
        notification_id: ID of the notification
        current_user: Authenticated user
        
    Returns:
        Dismissal confirmation
    """
    try:
        success = await status_service.dismiss_notification(notification_id, current_user)
        
        if success:
            return {
                "success": True,
                "data": {
                    "notification_id": notification_id,
                    "dismissed_by": current_user.name,
                    "dismissed_at": datetime.utcnow().isoformat()
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
        
    except Exception as e:
        logger.error(f"Failed to dismiss notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to dismiss notification")


# User Presence Management

@router.post("/presence")
async def update_user_presence(
    status: UserStatus = Body(..., description="User status"),
    activity: Optional[str] = Body(None, description="Current activity"),
    location: Optional[str] = Body(None, description="Current location"),
    available_until: Optional[str] = Body(None, description="Available until (ISO format)"),
    auto_reply_message: Optional[str] = Body(None, description="Auto-reply message"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update user presence status
    
    Args:
        status: User status
        activity: Current activity
        location: Current location
        available_until: Available until timestamp
        auto_reply_message: Auto-reply message
        current_user: Authenticated user
        
    Returns:
        Updated presence information
    """
    try:
        available_until_dt = None
        if available_until:
            try:
                available_until_dt = datetime.fromisoformat(available_until.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid timestamp format")
        
        presence = await status_service.update_user_presence(
            user=current_user,
            status=status,
            activity=activity,
            location=location,
            available_until=available_until_dt,
            auto_reply_message=auto_reply_message
        )
        
        return {
            "success": True,
            "data": {
                "user_id": presence.user_id,
                "status": presence.status.value,
                "activity": presence.current_activity,
                "location": presence.location,
                "last_seen": presence.last_seen.isoformat(),
                "available": presence.is_available(),
                "auto_reply_message": presence.auto_reply_message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update user presence: {e}")
        raise HTTPException(status_code=500, detail="Failed to update presence")


@router.get("/presence")
async def get_online_users(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get list of online users
    
    Args:
        current_user: Authenticated user
        
    Returns:
        List of online users
    """
    try:
        online_users = status_service.get_online_users()
        
        return {
            "success": True,
            "data": {
                "online_users": online_users,
                "count": len(online_users)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get online users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get online users")


@router.get("/presence/{user_id}")
async def get_user_presence(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get presence information for a specific user
    
    Args:
        user_id: ID of the user
        current_user: Authenticated user
        
    Returns:
        User presence information
    """
    try:
        presence = status_service.get_user_presence(user_id)
        
        if not presence:
            return {
                "success": True,
                "data": {
                    "user_id": user_id,
                    "status": "offline",
                    "available": False,
                    "message": "User presence not found"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        
        return {
            "success": True,
            "data": {
                "user_id": presence.user_id,
                "status": presence.status.value,
                "activity": presence.current_activity,
                "location": presence.location,
                "last_seen": presence.last_seen.isoformat(),
                "available": presence.is_available(),
                "auto_reply_message": presence.auto_reply_message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user presence: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user presence")


# Medical Alerts

@router.post("/alerts/medical")
async def create_medical_alert(
    patient_id: str = Body(..., description="Patient ID"),
    alert_type: str = Body(..., description="Type of medical alert"),
    severity: StatusLevel = Body(..., description="Alert severity"),
    description: str = Body(..., description="Alert description"),
    encounter_id: Optional[str] = Body(None, description="Encounter ID"),
    target_roles: Optional[List[UserRole]] = Body(None, description="Roles to notify"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a medical alert notification
    
    Args:
        patient_id: ID of the patient
        alert_type: Type of medical alert
        severity: Alert severity
        description: Alert description
        encounter_id: ID of the encounter (if applicable)
        target_roles: Roles to notify
        current_user: Authenticated user
        
    Returns:
        Created medical alert
    """
    try:
        alert = await status_service.create_medical_alert(
            patient_id=patient_id,
            encounter_id=encounter_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            target_roles=target_roles
        )
        
        return {
            "success": True,
            "data": {
                "alert_id": alert.id,
                "alert_type": alert_type,
                "severity": severity.value,
                "patient_id": patient_id,
                "created_at": alert.created_at.isoformat(),
                "created_by": current_user.name
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create medical alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to create medical alert")


# Workflow Status

@router.post("/workflow")
async def create_workflow_status(
    workflow_type: str = Body(..., description="Type of workflow"),
    status: str = Body(..., description="Workflow status"),
    entity_id: str = Body(..., description="Entity ID"),
    description: str = Body(..., description="Status description"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a workflow status notification
    
    Args:
        workflow_type: Type of workflow
        status: Workflow status
        entity_id: Entity ID
        description: Status description
        current_user: Authenticated user
        
    Returns:
        Created workflow status
    """
    try:
        notification = await status_service.create_workflow_status(
            workflow_type=workflow_type,
            status=status,
            entity_id=entity_id,
            description=description,
            user=current_user
        )
        
        return {
            "success": True,
            "data": {
                "notification_id": notification.id,
                "workflow_type": workflow_type,
                "status": status,
                "entity_id": entity_id,
                "created_at": notification.created_at.isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow status: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workflow status")


# System Status

@router.get("/system")
async def get_system_status(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get current system status
    
    Args:
        current_user: Authenticated user
        
    Returns:
        System status information
    """
    try:
        system_status = status_service.get_system_status()
        
        return {
            "success": True,
            "data": system_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


@router.post("/system/{service}")
async def update_system_status(
    service: str,
    status: str = Body(..., description="Service status"),
    details: Optional[dict] = Body(None, description="Additional details"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Update system service status (Admin only)
    
    Args:
        service: Service name
        status: Service status
        details: Additional details
        current_user: Authenticated admin user
        
    Returns:
        Status update confirmation
    """
    try:
        await status_service.update_system_status(service, status, details)
        
        return {
            "success": True,
            "data": {
                "service": service,
                "status": status,
                "updated_by": current_user.name,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to update system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update system status")


# Maintenance Mode

@router.post("/maintenance")
async def enable_maintenance_mode(
    message: str = Body(..., description="Maintenance message"),
    estimated_duration: Optional[int] = Body(None, description="Estimated duration in minutes"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Enable maintenance mode (Admin only)
    
    Args:
        message: Maintenance message
        estimated_duration: Estimated duration in minutes
        current_user: Authenticated admin user
        
    Returns:
        Maintenance mode confirmation
    """
    try:
        # Update system status
        await status_service.update_system_status("maintenance", "active", {
            "message": message,
            "estimated_duration": estimated_duration,
            "started_by": current_user.id
        })
        
        # Create maintenance notification
        await status_service.create_notification(
            notification_type=StatusType.MAINTENANCE,
            level=StatusLevel.WARNING,
            title="System Maintenance",
            message=f"System maintenance is in progress. {message}",
            broadcast_all=True,
            expires_in_minutes=estimated_duration if estimated_duration else 120
        )
        
        return {
            "success": True,
            "data": {
                "maintenance_enabled": True,
                "message": message,
                "estimated_duration": estimated_duration,
                "started_by": current_user.name,
                "started_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to enable maintenance mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable maintenance mode")


@router.delete("/maintenance")
async def disable_maintenance_mode(
    current_user: UserModel = Depends(require_admin)
):
    """
    Disable maintenance mode (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Maintenance mode disabled confirmation
    """
    try:
        # Update system status
        await status_service.update_system_status("maintenance", "inactive")
        
        # Create maintenance complete notification
        await status_service.create_notification(
            notification_type=StatusType.MAINTENANCE,
            level=StatusLevel.SUCCESS,
            title="Maintenance Complete",
            message="System maintenance has been completed. All services are now operational.",
            broadcast_all=True,
            expires_in_minutes=30
        )
        
        return {
            "success": True,
            "data": {
                "maintenance_enabled": False,
                "completed_by": current_user.name,
                "completed_at": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to disable maintenance mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable maintenance mode")


# Health Check

@router.get("/health")
async def status_health_check():
    """
    Health check for status service
    
    Returns:
        Status service health information
    """
    try:
        system_status = status_service.get_system_status()
        online_users = status_service.get_online_users()
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "status_service": "operational",
                "system_health": system_status["overall_health"],
                "online_users": len(online_users),
                "active_notifications": len(status_service.active_notifications)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Status health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }