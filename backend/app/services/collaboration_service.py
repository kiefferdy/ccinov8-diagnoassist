"""
Collaboration Service for DiagnoAssist Backend

Handles collaborative editing features including:
- Real-time collaborative SOAP editing
- Operational transformation for conflict resolution
- User presence and cursor tracking
- Change history and version control
- Merge conflict resolution
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

from app.models.auth import UserModel
from app.models.encounter import EncounterModel
from app.core.websocket_manager import websocket_manager, MessageType
from app.core.exceptions import ValidationException, ConflictException
from app.core.monitoring import monitoring

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    """Types of collaborative operations"""
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    FORMAT = "format"


class ChangeType(str, Enum):
    """Types of changes for history tracking"""
    TEXT_EDIT = "text_edit"
    SECTION_UPDATE = "section_update"
    STATUS_CHANGE = "status_change"
    USER_ACTION = "user_action"


@dataclass
class Operation:
    """Represents a single operation in operational transformation"""
    type: OperationType
    length: int = 0
    text: str = ""
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class Delta:
    """Represents a set of operations (delta) for operational transformation"""
    operations: List[Operation]
    
    def apply_to_text(self, text: str) -> str:
        """Apply this delta to a text string"""
        result = ""
        text_index = 0
        
        for op in self.operations:
            if op.type == OperationType.RETAIN:
                result += text[text_index:text_index + op.length]
                text_index += op.length
            elif op.type == OperationType.INSERT:
                result += op.text
            elif op.type == OperationType.DELETE:
                text_index += op.length
        
        # Append any remaining text
        result += text[text_index:]
        return result


@dataclass
class CollaborativeSession:
    """Represents a collaborative editing session"""
    encounter_id: str
    participants: Dict[str, Dict[str, Any]]  # user_id -> user info
    document_state: Dict[str, Any]  # Current SOAP document state
    operations_log: List[Dict[str, Any]]  # History of all operations
    version: int
    last_activity: datetime
    change_history: List[Dict[str, Any]]
    locks: Dict[str, Dict[str, Any]]  # Section locks
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = {}
        if self.document_state is None:
            self.document_state = {}
        if self.operations_log is None:
            self.operations_log = []
        if self.change_history is None:
            self.change_history = []
        if self.locks is None:
            self.locks = {}


class CollaborationService:
    """Service for managing collaborative editing"""
    
    def __init__(self):
        # Active collaborative sessions
        self.sessions: Dict[str, CollaborativeSession] = {}
        
        # User cursors and selections
        self.user_cursors: Dict[str, Dict[str, Any]] = {}  # encounter_id -> {user_id -> cursor_info}
        
        # Operational transformation state
        self.pending_operations: Dict[str, List[Dict[str, Any]]] = {}  # encounter_id -> operations
        
        # Change conflict resolution
        self.conflict_resolution_strategies = {
            "last_writer_wins": self._resolve_last_writer_wins,
            "merge_changes": self._resolve_merge_changes,
            "manual_review": self._resolve_manual_review
        }
    
    async def start_collaborative_session(
        self,
        encounter_id: str,
        user: UserModel,
        initial_document: Dict[str, Any]
    ) -> CollaborativeSession:
        """
        Start a collaborative editing session for an encounter
        
        Args:
            encounter_id: ID of the encounter
            user: User starting the session
            initial_document: Initial SOAP document state
            
        Returns:
            Collaborative session
        """
        try:
            if encounter_id in self.sessions:
                # Join existing session
                session = self.sessions[encounter_id]
                await self._add_participant(session, user)
            else:
                # Create new session
                session = CollaborativeSession(
                    encounter_id=encounter_id,
                    participants={},
                    document_state=initial_document,
                    operations_log=[],
                    version=1,
                    last_activity=datetime.utcnow(),
                    change_history=[],
                    locks={}
                )
                
                await self._add_participant(session, user)
                self.sessions[encounter_id] = session
                
                # Initialize user cursors
                if encounter_id not in self.user_cursors:
                    self.user_cursors[encounter_id] = {}
            
            # Broadcast session start
            await self._broadcast_session_update(encounter_id, "session_started", {
                "participants": list(session.participants.values()),
                "version": session.version
            })
            
            logger.info(f"Started collaborative session for encounter {encounter_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to start collaborative session: {e}")
            raise
    
    async def join_session(
        self,
        encounter_id: str,
        user: UserModel
    ) -> CollaborativeSession:
        """
        Join an existing collaborative session
        
        Args:
            encounter_id: ID of the encounter
            user: User joining the session
            
        Returns:
            Collaborative session
        """
        try:
            if encounter_id not in self.sessions:
                raise ValidationException(f"No collaborative session found for encounter {encounter_id}")
            
            session = self.sessions[encounter_id]
            await self._add_participant(session, user)
            
            # Initialize user cursor
            if encounter_id not in self.user_cursors:
                self.user_cursors[encounter_id] = {}
            
            # Broadcast user joined
            await self._broadcast_session_update(encounter_id, "user_joined", {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": user.role.value
                },
                "participants": list(session.participants.values())
            })
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to join collaborative session: {e}")
            raise
    
    async def leave_session(
        self,
        encounter_id: str,
        user: UserModel
    ) -> bool:
        """
        Leave a collaborative session
        
        Args:
            encounter_id: ID of the encounter
            user: User leaving the session
            
        Returns:
            Success status
        """
        try:
            if encounter_id not in self.sessions:
                return True
            
            session = self.sessions[encounter_id]
            
            # Remove participant
            if user.id in session.participants:
                del session.participants[user.id]
            
            # Remove user cursor
            if encounter_id in self.user_cursors and user.id in self.user_cursors[encounter_id]:
                del self.user_cursors[encounter_id][user.id]
            
            # Release any locks held by user
            await self._release_user_locks(session, user.id)
            
            # End session if no participants left
            if not session.participants:
                await self._end_session(encounter_id)
            else:
                # Broadcast user left
                await self._broadcast_session_update(encounter_id, "user_left", {
                    "user": {
                        "id": user.id,
                        "name": user.name
                    },
                    "participants": list(session.participants.values())
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to leave collaborative session: {e}")
            return False
    
    async def apply_operation(
        self,
        encounter_id: str,
        user: UserModel,
        operation: Dict[str, Any],
        client_version: int
    ) -> Dict[str, Any]:
        """
        Apply an operation to the collaborative document
        
        Args:
            encounter_id: ID of the encounter
            user: User applying the operation
            operation: Operation to apply
            client_version: Client's document version
            
        Returns:
            Operation result with transformed operations if needed
        """
        try:
            if encounter_id not in self.sessions:
                raise ValidationException(f"No collaborative session found for encounter {encounter_id}")
            
            session = self.sessions[encounter_id]
            
            # Validate user is participant
            if user.id not in session.participants:
                raise ValidationException("User not in collaborative session")
            
            # Handle version conflicts using operational transformation
            if client_version < session.version:
                # Transform operation against newer operations
                transformed_op = await self._transform_operation(
                    session, operation, client_version
                )
            else:
                transformed_op = operation
            
            # Apply operation to document
            await self._apply_operation_to_document(session, transformed_op, user)
            
            # Increment version
            session.version += 1
            session.last_activity = datetime.utcnow()
            
            # Log operation
            session.operations_log.append({
                "operation": transformed_op,
                "user_id": user.id,
                "timestamp": datetime.utcnow().isoformat(),
                "version": session.version
            })
            
            # Broadcast operation to other participants
            await self._broadcast_operation(encounter_id, transformed_op, user, session.version)
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "collaboration_operations_total",
                labels={
                    "operation_type": operation.get("type", "unknown"),
                    "section": operation.get("section", "unknown")
                }
            )
            
            return {
                "success": True,
                "version": session.version,
                "transformed_operation": transformed_op
            }
            
        except Exception as e:
            logger.error(f"Failed to apply operation: {e}")
            raise
    
    async def update_cursor_position(
        self,
        encounter_id: str,
        user: UserModel,
        section: str,
        position: int,
        selection_start: Optional[int] = None,
        selection_end: Optional[int] = None
    ):
        """
        Update user's cursor position
        
        Args:
            encounter_id: ID of the encounter
            user: User updating cursor
            section: SOAP section
            position: Cursor position
            selection_start: Selection start position
            selection_end: Selection end position
        """
        try:
            if encounter_id not in self.user_cursors:
                self.user_cursors[encounter_id] = {}
            
            cursor_info = {
                "user_id": user.id,
                "user_name": user.name,
                "user_color": self._get_user_color(user.id),
                "section": section,
                "position": position,
                "selection_start": selection_start,
                "selection_end": selection_end,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.user_cursors[encounter_id][user.id] = cursor_info
            
            # Broadcast cursor update
            await websocket_manager.broadcast_to_resource(
                encounter_id,
                {
                    "type": MessageType.CURSOR_MOVE.value,
                    "cursor": cursor_info,
                    "encounter_id": encounter_id
                },
                exclude_connection=f"encounter_{encounter_id}_{user.id}"
            )
            
        except Exception as e:
            logger.error(f"Failed to update cursor position: {e}")
    
    async def acquire_section_lock(
        self,
        encounter_id: str,
        user: UserModel,
        section: str,
        lock_type: str = "write"
    ) -> bool:
        """
        Acquire a lock on a SOAP section for exclusive editing
        
        Args:
            encounter_id: ID of the encounter
            user: User acquiring the lock
            section: SOAP section to lock
            lock_type: Type of lock (read, write)
            
        Returns:
            Success status
        """
        try:
            if encounter_id not in self.sessions:
                return False
            
            session = self.sessions[encounter_id]
            
            # Check if section is already locked
            if section in session.locks:
                existing_lock = session.locks[section]
                if existing_lock["user_id"] != user.id:
                    return False  # Already locked by another user
            
            # Acquire lock
            session.locks[section] = {
                "user_id": user.id,
                "user_name": user.name,
                "lock_type": lock_type,
                "acquired_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(minutes=10)  # 10-minute timeout
            }
            
            # Broadcast lock acquired
            await self._broadcast_session_update(encounter_id, "section_locked", {
                "section": section,
                "user": {
                    "id": user.id,
                    "name": user.name
                },
                "lock_type": lock_type
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire section lock: {e}")
            return False
    
    async def release_section_lock(
        self,
        encounter_id: str,
        user: UserModel,
        section: str
    ) -> bool:
        """
        Release a lock on a SOAP section
        
        Args:
            encounter_id: ID of the encounter
            user: User releasing the lock
            section: SOAP section to unlock
            
        Returns:
            Success status
        """
        try:
            if encounter_id not in self.sessions:
                return False
            
            session = self.sessions[encounter_id]
            
            # Check if user owns the lock
            if section not in session.locks:
                return True  # No lock to release
            
            lock = session.locks[section]
            if lock["user_id"] != user.id:
                return False  # User doesn't own the lock
            
            # Release lock
            del session.locks[section]
            
            # Broadcast lock released
            await self._broadcast_session_update(encounter_id, "section_unlocked", {
                "section": section,
                "user": {
                    "id": user.id,
                    "name": user.name
                }
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to release section lock: {e}")
            return False
    
    async def get_session_state(
        self,
        encounter_id: str,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Get current collaborative session state
        
        Args:
            encounter_id: ID of the encounter
            user: User requesting state
            
        Returns:
            Session state
        """
        try:
            if encounter_id not in self.sessions:
                return {
                    "active": False,
                    "message": "No active collaborative session"
                }
            
            session = self.sessions[encounter_id]
            
            # Get user cursors
            cursors = []
            if encounter_id in self.user_cursors:
                for cursor_info in self.user_cursors[encounter_id].values():
                    if cursor_info["user_id"] != user.id:  # Exclude own cursor
                        cursors.append(cursor_info)
            
            return {
                "active": True,
                "encounter_id": encounter_id,
                "version": session.version,
                "participants": list(session.participants.values()),
                "document_state": session.document_state,
                "cursors": cursors,
                "locks": session.locks,
                "last_activity": session.last_activity.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get session state: {e}")
            return {"active": False, "error": str(e)}
    
    # Private helper methods
    
    async def _add_participant(self, session: CollaborativeSession, user: UserModel):
        """Add a participant to the session"""
        session.participants[user.id] = {
            "id": user.id,
            "name": user.name,
            "role": user.role.value,
            "joined_at": datetime.utcnow().isoformat(),
            "color": self._get_user_color(user.id)
        }
    
    async def _end_session(self, encounter_id: str):
        """End a collaborative session"""
        try:
            if encounter_id in self.sessions:
                session = self.sessions[encounter_id]
                
                # Log session end
                logger.info(f"Ending collaborative session for encounter {encounter_id}")
                
                # Clean up
                del self.sessions[encounter_id]
                
                if encounter_id in self.user_cursors:
                    del self.user_cursors[encounter_id]
                
                if encounter_id in self.pending_operations:
                    del self.pending_operations[encounter_id]
        
        except Exception as e:
            logger.error(f"Failed to end session: {e}")
    
    async def _transform_operation(
        self,
        session: CollaborativeSession,
        operation: Dict[str, Any],
        client_version: int
    ) -> Dict[str, Any]:
        """Transform operation using operational transformation"""
        # Simplified OT - in production, implement full operational transformation
        # For now, just return the operation as-is
        return operation
    
    async def _apply_operation_to_document(
        self,
        session: CollaborativeSession,
        operation: Dict[str, Any],
        user: UserModel
    ):
        """Apply operation to the collaborative document"""
        try:
            section = operation.get("section")
            field = operation.get("field")
            value = operation.get("value")
            
            if section and field:
                if section not in session.document_state:
                    session.document_state[section] = {}
                
                session.document_state[section][field] = value
                
                # Add to change history
                session.change_history.append({
                    "type": ChangeType.TEXT_EDIT.value,
                    "section": section,
                    "field": field,
                    "old_value": session.document_state[section].get(field, ""),
                    "new_value": value,
                    "user_id": user.id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": session.version + 1
                })
        
        except Exception as e:
            logger.error(f"Failed to apply operation to document: {e}")
            raise
    
    async def _broadcast_operation(
        self,
        encounter_id: str,
        operation: Dict[str, Any],
        user: UserModel,
        version: int
    ):
        """Broadcast operation to other participants"""
        await websocket_manager.broadcast_to_resource(
            encounter_id,
            {
                "type": MessageType.SOAP_UPDATE.value,
                "operation": operation,
                "user": {
                    "id": user.id,
                    "name": user.name
                },
                "version": version,
                "encounter_id": encounter_id
            },
            exclude_connection=f"encounter_{encounter_id}_{user.id}"
        )
    
    async def _broadcast_session_update(
        self,
        encounter_id: str,
        update_type: str,
        data: Dict[str, Any]
    ):
        """Broadcast session update to all participants"""
        await websocket_manager.broadcast_to_resource(
            encounter_id,
            {
                "type": MessageType.STATUS_UPDATE.value,
                "update_type": update_type,
                "data": data,
                "encounter_id": encounter_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def _release_user_locks(self, session: CollaborativeSession, user_id: str):
        """Release all locks held by a user"""
        locks_to_release = []
        for section, lock in session.locks.items():
            if lock["user_id"] == user_id:
                locks_to_release.append(section)
        
        for section in locks_to_release:
            del session.locks[section]
    
    def _get_user_color(self, user_id: str) -> str:
        """Get a consistent color for a user"""
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
            "#F7DC6F", "#BB8FCE", "#85C1E9", "#F8C471", "#82E0AA"
        ]
        
        # Use hash of user_id to get consistent color
        color_index = hash(user_id) % len(colors)
        return colors[color_index]
    
    # Conflict resolution strategies
    
    async def _resolve_last_writer_wins(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts using last writer wins strategy"""
        if not conflicts:
            return {}
        
        # Return the latest change
        latest_conflict = max(conflicts, key=lambda x: x.get("timestamp", ""))
        return latest_conflict.get("operation", {})
    
    async def _resolve_merge_changes(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicts by merging changes"""
        # Simplified merge - in production, implement sophisticated merging
        merged_result = {}
        
        for conflict in conflicts:
            operation = conflict.get("operation", {})
            merged_result.update(operation)
        
        return merged_result
    
    async def _resolve_manual_review(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mark conflicts for manual review"""
        return {
            "requires_manual_review": True,
            "conflicts": conflicts,
            "resolution_needed": True
        }
    
    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        active_sessions = len(self.sessions)
        total_participants = sum(len(session.participants) for session in self.sessions.values())
        total_operations = sum(len(session.operations_log) for session in self.sessions.values())
        
        return {
            "active_sessions": active_sessions,
            "total_participants": total_participants,
            "total_operations": total_operations,
            "sessions_by_encounter": {
                encounter_id: {
                    "participants": len(session.participants),
                    "version": session.version,
                    "last_activity": session.last_activity.isoformat()
                }
                for encounter_id, session in self.sessions.items()
            }
        }


# Create service instance
collaboration_service = CollaborationService()