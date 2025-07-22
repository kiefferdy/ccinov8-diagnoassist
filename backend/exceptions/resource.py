"""
Resource Management Exception Classes for DiagnoAssist
Handles resource CRUD operations, permissions, and lifecycle management
"""

from typing import Optional, Dict, Any, List
from .base import DiagnoAssistException


class ResourceNotFoundException(DiagnoAssistException):
    """
    Exception for resource not found errors
    """
    
    def __init__(
        self,
        resource_type: str,
        identifier: str,
        identifier_type: str = "id",
        search_criteria: Optional[Dict[str, Any]] = None
    ):
        self.resource_type = resource_type
        self.identifier = identifier
        self.identifier_type = identifier_type
        self.search_criteria = search_criteria or {}
        
        details = {
            "resource_type": resource_type,
            "identifier": identifier,
            "identifier_type": identifier_type,
            "search_criteria": search_criteria
        }
        
        message = f"{resource_type} with {identifier_type} '{identifier}' not found"
        
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly not found message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        if self.identifier_type == "id":
            return f"The requested {resource_name} was not found."
        else:
            return f"No {resource_name} found with {self.identifier_type} '{self.identifier}'."
    
    def to_fhir_operation_outcome(self) -> Dict[str, Any]:
        """Convert to FHIR OperationOutcome for resource not found"""
        outcome = super().to_fhir_operation_outcome()
        
        # Update severity and code for not found
        outcome["issue"][0]["severity"] = "error"
        outcome["issue"][0]["code"] = "not-found"
        outcome["issue"][0]["details"]["coding"][0]["code"] = "MSG_NO_MATCH"
        outcome["issue"][0]["details"]["text"] = f"No {self.resource_type} resource found with {self.identifier_type} '{self.identifier}'"
        
        return outcome


class ResourceConflictException(DiagnoAssistException):
    """
    Exception for resource conflict errors (HTTP 409)
    Handles creation conflicts, version conflicts, business rule conflicts
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        conflict_type: str = "general",
        conflicting_field: Optional[str] = None,
        conflicting_value: Optional[str] = None,
        existing_resource_id: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.conflict_type = conflict_type  # "duplicate", "version", "state", "business_rule"
        self.conflicting_field = conflicting_field
        self.conflicting_value = conflicting_value
        self.existing_resource_id = existing_resource_id
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "conflict_type": conflict_type,
            "conflicting_field": conflicting_field,
            "conflicting_value": conflicting_value,
            "existing_resource_id": existing_resource_id
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly conflict message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        if self.conflict_type == "duplicate":
            if self.conflicting_field:
                return f"A {resource_name} with this {self.conflicting_field} already exists."
            else:
                return f"This {resource_name} already exists."
        
        elif self.conflict_type == "version":
            return f"The {resource_name} has been modified by another user. Please refresh and try again."
        
        elif self.conflict_type == "state":
            return f"Cannot perform this action due to the current state of the {resource_name}."
        
        elif self.conflict_type == "business_rule":
            return f"This action conflicts with business rules for {resource_name}."
        
        else:
            return f"Conflict detected with {resource_name}. Please review and try again."


class ResourcePermissionException(DiagnoAssistException):
    """
    Exception for resource permission/authorization errors
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        action: str = "access",
        user_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        user_permissions: Optional[List[str]] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action  # "read", "write", "delete", "create", "access"
        self.user_id = user_id
        self.required_permission = required_permission
        self.user_permissions = user_permissions or []
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "user_id": user_id,
            "required_permission": required_permission,
            "user_permissions": user_permissions
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_PERMISSION_DENIED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly permission denied message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        action_messages = {
            "read": f"view this {resource_name}",
            "write": f"modify this {resource_name}",
            "create": f"create {resource_name}s",
            "delete": f"delete this {resource_name}",
            "access": f"access this {resource_name}"
        }
        
        action_text = action_messages.get(self.action, f"{self.action} this {resource_name}")
        return f"You don't have permission to {action_text}."


class ResourceLockedException(DiagnoAssistException):
    """
    Exception for resource locking errors
    Handles cases where resources are locked for editing
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        locked_by: Optional[str] = None,
        lock_reason: Optional[str] = None,
        lock_expires: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.locked_by = locked_by
        self.lock_reason = lock_reason
        self.lock_expires = lock_expires
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "locked_by": locked_by,
            "lock_reason": lock_reason,
            "lock_expires": lock_expires
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_LOCKED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly resource locked message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        if self.locked_by and self.lock_expires:
            return f"This {resource_name} is locked by {self.locked_by} until {self.lock_expires}."
        elif self.locked_by:
            return f"This {resource_name} is currently locked by {self.locked_by}."
        elif self.lock_reason:
            return f"This {resource_name} is locked: {self.lock_reason}."
        else:
            return f"This {resource_name} is currently locked and cannot be modified."


class ResourceStateException(DiagnoAssistException):
    """
    Exception for invalid resource state transitions
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        current_state: str,
        attempted_action: str,
        valid_actions: Optional[List[str]] = None,
        target_state: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.current_state = current_state
        self.attempted_action = attempted_action
        self.valid_actions = valid_actions or []
        self.target_state = target_state
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "current_state": current_state,
            "attempted_action": attempted_action,
            "valid_actions": valid_actions,
            "target_state": target_state
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_STATE_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly state error message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        if self.valid_actions:
            valid_actions_text = ", ".join(self.valid_actions)
            return f"Cannot {self.attempted_action} {resource_name} in {self.current_state} state. Valid actions: {valid_actions_text}."
        else:
            return f"Cannot {self.attempted_action} {resource_name} in {self.current_state} state."


class ResourceQuotaException(DiagnoAssistException):
    """
    Exception for resource quota/limit violations
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        quota_type: str,
        current_count: int,
        quota_limit: int,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.quota_type = quota_type  # "per_user", "per_organization", "per_day", "total"
        self.current_count = current_count
        self.quota_limit = quota_limit
        self.user_id = user_id
        self.organization_id = organization_id
        
        details = {
            "resource_type": resource_type,
            "quota_type": quota_type,
            "current_count": current_count,
            "quota_limit": quota_limit,
            "user_id": user_id,
            "organization_id": organization_id
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_QUOTA_EXCEEDED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly quota exceeded message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        
        quota_messages = {
            "per_user": f"You have reached your limit of {self.quota_limit} {resource_name}s.",
            "per_organization": f"Your organization has reached the limit of {self.quota_limit} {resource_name}s.",
            "per_day": f"Daily limit of {self.quota_limit} {resource_name}s reached.",
            "total": f"System limit of {self.quota_limit} {resource_name}s reached."
        }
        
        return quota_messages.get(
            self.quota_type,
            f"Resource limit exceeded: {self.current_count}/{self.quota_limit} {resource_name}s."
        )


class ResourceDependencyException(DiagnoAssistException):
    """
    Exception for resource dependency violations
    Handles cases where resources have dependencies that prevent certain operations
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        resource_id: str,
        operation: str,
        dependent_resources: List[Dict[str, str]],
        suggestion: Optional[str] = None
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.operation = operation
        self.dependent_resources = dependent_resources
        self.suggestion = suggestion
        
        details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "operation": operation,
            "dependent_resources": dependent_resources,
            "suggestion": suggestion
        }
        
        super().__init__(
            message=message,
            error_code="RESOURCE_DEPENDENCY_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly dependency error message"""
        resource_name = self.resource_type.lower().replace('_', ' ')
        dependent_count = len(self.dependent_resources)
        
        if self.operation == "delete":
            if dependent_count == 1:
                dep = self.dependent_resources[0]
                return f"Cannot delete this {resource_name} because it is referenced by {dep['type']} '{dep['id']}'."
            else:
                return f"Cannot delete this {resource_name} because it is referenced by {dependent_count} other resources."
        
        elif self.operation == "deactivate":
            return f"Cannot deactivate this {resource_name} due to active dependencies."
        
        else:
            return f"Cannot {self.operation} this {resource_name} due to existing dependencies."