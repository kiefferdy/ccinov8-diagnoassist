"""
Real-time Service for DiagnoAssist Backend

Handles high-level real-time operations including:
- Auto-save functionality
- Live encounter updates
- Notification broadcasting
- Collaborative editing features
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from app.core.websocket_manager import websocket_manager, ConnectionType, MessageType
from app.models.auth import UserModel
from app.models.encounter import EncounterModel
from app.models.soap import SOAPModel
from app.services.encounter_service import encounter_service
from app.core.exceptions import ValidationException
from app.core.monitoring import monitoring
from app.core.performance import performance_optimizer

logger = logging.getLogger(__name__)


class RealTimeService:
    """Service for managing real-time features"""
    
    def __init__(self):
        # Track auto-save states
        self.auto_save_states: Dict[str, Dict[str, Any]] = {}
        
        # Track typing indicators
        self.typing_indicators: Dict[str, Dict[str, Dict[str, Any]]] = {}
        
        # Track unsaved changes
        self.unsaved_changes: Dict[str, Dict[str, Any]] = {}
        
    async def start_encounter_session(
        self,
        encounter_id: str,
        user: UserModel,
        auto_save_interval: int = 30
    ) -> Dict[str, Any]:
        """
        Start a real-time encounter editing session
        
        Args:
            encounter_id: ID of the encounter
            user: User starting the session
            auto_save_interval: Auto-save interval in seconds
            
        Returns:
            Session information
        """
        try:
            # Verify encounter exists and user has access
            encounter = await encounter_service.get_encounter(encounter_id, user)
            if not encounter:
                raise ValidationException(f"Encounter {encounter_id} not found or access denied")
            
            # Initialize auto-save state
            self.auto_save_states[encounter_id] = {
                "last_save": datetime.utcnow(),
                "pending_changes": {},
                "save_in_progress": False,
                "interval": auto_save_interval
            }
            
            # Initialize typing indicators for this encounter
            if encounter_id not in self.typing_indicators:
                self.typing_indicators[encounter_id] = {}
            
            # Initialize unsaved changes tracking
            if encounter_id not in self.unsaved_changes:
                self.unsaved_changes[encounter_id] = {}
            
            # Start auto-save if not already running
            await websocket_manager.start_auto_save(encounter_id, auto_save_interval)
            
            logger.info(f"Started real-time session for encounter {encounter_id} by user {user.id}")
            
            return {
                "encounter_id": encounter_id,
                "session_started": True,
                "auto_save_interval": auto_save_interval,
                "current_encounter": encounter.model_dump()
            }
            
        except Exception as e:
            logger.error(f"Failed to start encounter session: {e}")
            raise
    
    async def update_soap_section(
        self,
        encounter_id: str,
        section: str,
        field: str,
        value: Any,
        user: UserModel,
        broadcast: bool = True
    ) -> Dict[str, Any]:
        """
        Update a SOAP section field and broadcast to connected users
        
        Args:
            encounter_id: ID of the encounter
            section: SOAP section (subjective, objective, assessment, plan)
            field: Field name within the section
            value: New value for the field
            user: User making the update
            broadcast: Whether to broadcast the update
            
        Returns:
            Update confirmation
        """
        try:
            # Track the change for auto-save
            if encounter_id not in self.unsaved_changes:
                self.unsaved_changes[encounter_id] = {}
            
            if section not in self.unsaved_changes[encounter_id]:
                self.unsaved_changes[encounter_id][section] = {}
            
            self.unsaved_changes[encounter_id][section][field] = {
                "value": value,
                "user_id": user.id,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update auto-save state
            if encounter_id in self.auto_save_states:
                self.auto_save_states[encounter_id]["pending_changes"] = self.unsaved_changes[encounter_id]
            
            # Broadcast update if requested
            if broadcast:
                await websocket_manager.broadcast_to_resource(
                    encounter_id,
                    {
                        "type": MessageType.SOAP_UPDATE.value,
                        "section": section,
                        "field": field,
                        "value": value,
                        "user": {
                            "id": user.id,
                            "name": user.name,
                            "role": user.role.value
                        },
                        "encounter_id": encounter_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "realtime_soap_updates_total",
                labels={"section": section, "field": field}
            )
            
            logger.debug(f"SOAP section updated: {encounter_id}.{section}.{field} by {user.id}")
            
            return {
                "success": True,
                "encounter_id": encounter_id,
                "section": section,
                "field": field,
                "updated_by": user.id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update SOAP section: {e}")
            raise
    
    async def perform_auto_save(
        self,
        encounter_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Perform auto-save for an encounter
        
        Args:
            encounter_id: ID of the encounter
            force: Force save even if no changes
            
        Returns:
            Save result
        """
        try:
            if encounter_id not in self.auto_save_states:
                return {"success": False, "reason": "No auto-save state found"}
            
            auto_save_state = self.auto_save_states[encounter_id]
            
            # Check if save is already in progress
            if auto_save_state["save_in_progress"]:
                return {"success": False, "reason": "Save already in progress"}
            
            # Check if there are pending changes
            pending_changes = auto_save_state.get("pending_changes", {})
            if not pending_changes and not force:
                return {"success": False, "reason": "No changes to save"}
            
            # Mark save in progress
            auto_save_state["save_in_progress"] = True
            
            try:
                # Get current encounter
                encounter = await encounter_service.get_encounter_by_id(encounter_id)
                if not encounter:
                    raise ValidationException(f"Encounter {encounter_id} not found")
                
                # Apply pending changes to encounter
                if pending_changes:
                    encounter = await self._apply_changes_to_encounter(encounter, pending_changes)
                
                # Save to database
                updated_encounter = await encounter_service.update_encounter(encounter_id, encounter)
                
                # Update auto-save state
                auto_save_state["last_save"] = datetime.utcnow()
                auto_save_state["pending_changes"] = {}
                
                # Clear unsaved changes
                if encounter_id in self.unsaved_changes:
                    self.unsaved_changes[encounter_id] = {}
                
                # Broadcast auto-save success
                await websocket_manager.broadcast_to_resource(
                    encounter_id,
                    {
                        "type": MessageType.AUTO_SAVE.value,
                        "status": "success",
                        "encounter_id": encounter_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "message": "Auto-save completed successfully"
                    }
                )
                
                # Record metrics
                monitoring.metrics.increment_counter(
                    "realtime_auto_saves_total",
                    labels={"status": "success"}
                )
                
                logger.info(f"Auto-save completed for encounter {encounter_id}")
                
                return {
                    "success": True,
                    "encounter_id": encounter_id,
                    "saved_at": auto_save_state["last_save"].isoformat(),
                    "changes_applied": bool(pending_changes)
                }
                
            except Exception as save_error:
                # Broadcast auto-save failure
                await websocket_manager.broadcast_to_resource(
                    encounter_id,
                    {
                        "type": MessageType.AUTO_SAVE.value,
                        "status": "error",
                        "encounter_id": encounter_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "error": str(save_error),
                        "message": "Auto-save failed"
                    }
                )
                
                # Record metrics
                monitoring.metrics.increment_counter(
                    "realtime_auto_saves_total",
                    labels={"status": "error"}
                )
                
                logger.error(f"Auto-save failed for encounter {encounter_id}: {save_error}")
                raise
            
            finally:
                # Always clear save in progress flag
                auto_save_state["save_in_progress"] = False
        
        except Exception as e:
            logger.error(f"Auto-save error for encounter {encounter_id}: {e}")
            raise
    
    async def set_typing_indicator(
        self,
        encounter_id: str,
        user: UserModel,
        section: str,
        is_typing: bool
    ) -> bool:
        """
        Set typing indicator for a user in a SOAP section
        
        Args:
            encounter_id: ID of the encounter
            user: User who is typing
            section: SOAP section where user is typing
            is_typing: True if user is typing, False if stopped
            
        Returns:
            Success status
        """
        try:
            # Initialize typing indicators if needed
            if encounter_id not in self.typing_indicators:
                self.typing_indicators[encounter_id] = {}
            
            user_key = f"{user.id}_{section}"
            
            if is_typing:
                # Set typing indicator
                self.typing_indicators[encounter_id][user_key] = {
                    "user_id": user.id,
                    "user_name": user.name,
                    "section": section,
                    "started_at": datetime.utcnow(),
                    "last_activity": datetime.utcnow()
                }
                
                message_type = MessageType.TYPING_START.value
            else:
                # Remove typing indicator
                if user_key in self.typing_indicators[encounter_id]:
                    del self.typing_indicators[encounter_id][user_key]
                
                message_type = MessageType.TYPING_STOP.value
            
            # Broadcast typing indicator
            await websocket_manager.broadcast_to_resource(
                encounter_id,
                {
                    "type": message_type,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "role": user.role.value
                    },
                    "section": section,
                    "encounter_id": encounter_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set typing indicator: {e}")
            return False
    
    async def get_typing_indicators(self, encounter_id: str) -> List[Dict[str, Any]]:
        """
        Get current typing indicators for an encounter
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            List of active typing indicators
        """
        if encounter_id not in self.typing_indicators:
            return []
        
        # Clean up old typing indicators (older than 10 seconds)
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(seconds=10)
        
        active_indicators = []
        expired_keys = []
        
        for key, indicator in self.typing_indicators[encounter_id].items():
            if indicator["last_activity"] < cutoff_time:
                expired_keys.append(key)
            else:
                active_indicators.append({
                    "user_id": indicator["user_id"],
                    "user_name": indicator["user_name"],
                    "section": indicator["section"],
                    "started_at": indicator["started_at"].isoformat()
                })
        
        # Remove expired indicators
        for key in expired_keys:
            del self.typing_indicators[encounter_id][key]
        
        return active_indicators
    
    async def broadcast_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        target_users: Optional[List[str]] = None,
        exclude_users: Optional[List[str]] = None
    ) -> int:
        """
        Broadcast a notification to users
        
        Args:
            title: Notification title
            message: Notification message
            level: Notification level (info, warning, error, success)
            target_users: Specific users to notify (None for all)
            exclude_users: Users to exclude from notification
            
        Returns:
            Number of users notified
        """
        try:
            notification = {
                "title": title,
                "message": message,
                "level": level,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if target_users:
                # Send to specific users
                sent_count = 0
                for user_id in target_users:
                    if exclude_users and user_id in exclude_users:
                        continue
                    count = await websocket_manager.send_to_user(user_id, notification)
                    sent_count += count
                return sent_count
            else:
                # Broadcast to all users
                exclude_user = exclude_users[0] if exclude_users else None
                return await websocket_manager.broadcast_notification(notification, exclude_user)
                
        except Exception as e:
            logger.error(f"Failed to broadcast notification: {e}")
            return 0
    
    async def get_encounter_activity(self, encounter_id: str) -> Dict[str, Any]:
        """
        Get current activity for an encounter
        
        Args:
            encounter_id: ID of the encounter
            
        Returns:
            Encounter activity information
        """
        try:
            connected_users = websocket_manager.get_resource_users(encounter_id)
            typing_indicators = await self.get_typing_indicators(encounter_id)
            
            # Get auto-save status
            auto_save_status = None
            if encounter_id in self.auto_save_states:
                state = self.auto_save_states[encounter_id]
                auto_save_status = {
                    "last_save": state["last_save"].isoformat(),
                    "pending_changes": bool(state.get("pending_changes")),
                    "save_in_progress": state.get("save_in_progress", False),
                    "interval": state.get("interval", 30)
                }
            
            return {
                "encounter_id": encounter_id,
                "connected_users": connected_users,
                "typing_indicators": typing_indicators,
                "auto_save_status": auto_save_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get encounter activity: {e}")
            return {
                "encounter_id": encounter_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_encounter_session(self, encounter_id: str):
        """
        Clean up encounter session data
        
        Args:
            encounter_id: ID of the encounter
        """
        try:
            # Remove auto-save state
            if encounter_id in self.auto_save_states:
                del self.auto_save_states[encounter_id]
            
            # Remove typing indicators
            if encounter_id in self.typing_indicators:
                del self.typing_indicators[encounter_id]
            
            # Remove unsaved changes
            if encounter_id in self.unsaved_changes:
                del self.unsaved_changes[encounter_id]
            
            logger.info(f"Cleaned up session data for encounter {encounter_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup encounter session: {e}")
    
    async def _apply_changes_to_encounter(
        self,
        encounter: EncounterModel,
        changes: Dict[str, Dict[str, Any]]
    ) -> EncounterModel:
        """
        Apply pending changes to an encounter
        
        Args:
            encounter: Current encounter model
            changes: Pending changes to apply
            
        Returns:
            Updated encounter model
        """
        try:
            # Create a copy of the encounter to modify
            encounter_dict = encounter.model_dump()
            
            # Apply changes to each section
            for section, fields in changes.items():
                if section not in encounter_dict.get("soap", {}):
                    continue
                
                for field, change_info in fields.items():
                    if isinstance(change_info, dict) and "value" in change_info:
                        encounter_dict["soap"][section][field] = change_info["value"]
                    else:
                        encounter_dict["soap"][section][field] = change_info
            
            # Update timestamp
            encounter_dict["updated_at"] = datetime.utcnow()
            encounter_dict["workflow"]["last_saved"] = datetime.utcnow()
            
            # Create new encounter model from updated dict
            return EncounterModel(**encounter_dict)
            
        except Exception as e:
            logger.error(f"Failed to apply changes to encounter: {e}")
            raise ValidationException(f"Failed to apply changes: {str(e)}")


# Create service instance
realtime_service = RealTimeService()