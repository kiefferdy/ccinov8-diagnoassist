"""
Authentication and Authorization Exception Classes for DiagnoAssist
Handles user authentication, authorization, and security-related errors
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import DiagnoAssistException


class AuthenticationException(DiagnoAssistException):
    """
    Exception for authentication failures
    """
    
    def __init__(
        self,
        message: str,
        auth_method: Optional[str] = None,
        username: Optional[str] = None,
        failure_reason: Optional[str] = None,
        attempt_count: Optional[int] = None
    ):
        self.auth_method = auth_method  # "password", "token", "oauth", "saml"
        self.username = username
        self.failure_reason = failure_reason
        self.attempt_count = attempt_count
        
        details = {
            "auth_method": auth_method,
            "username": username,
            "failure_reason": failure_reason,
            "attempt_count": attempt_count
        }
        
        # Remove sensitive information from details
        if username:
            details["username"] = username[:3] + "***" if len(username) > 3 else "***"
        
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly authentication error message"""
        if self.failure_reason == "invalid_credentials":
            return "Invalid username or password. Please try again."
        elif self.failure_reason == "account_locked":
            return "Account is locked due to multiple failed login attempts."
        elif self.failure_reason == "account_disabled":
            return "Account is disabled. Please contact your administrator."
        elif self.failure_reason == "expired_password":
            return "Password has expired. Please reset your password."
        elif self.failure_reason == "token_expired":
            return "Session has expired. Please log in again."
        elif self.failure_reason == "token_invalid":
            return "Invalid authentication token. Please log in again."
        else:
            return "Authentication failed. Please check your credentials and try again."


class AuthorizationException(DiagnoAssistException):
    """
    Exception for authorization/permission failures
    """
    
    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        required_role: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
        required_permission: Optional[str] = None,
        user_permissions: Optional[List[str]] = None
    ):
        self.user_id = user_id
        self.resource = resource
        self.action = action
        self.required_role = required_role
        self.user_roles = user_roles or []
        self.required_permission = required_permission
        self.user_permissions = user_permissions or []
        
        details = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "required_role": required_role,
            "user_roles": user_roles,
            "required_permission": required_permission
            # Note: Don't include user_permissions for security
        }
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly authorization error message"""
        if self.action and self.resource:
            return f"You don't have permission to {self.action} {self.resource}."
        elif self.required_role:
            return f"Access denied. This action requires {self.required_role} role."
        elif self.resource:
            return f"You don't have permission to access {self.resource}."
        else:
            return "Access denied. You don't have permission to perform this action."


class TokenException(DiagnoAssistException):
    """
    Exception for token-related errors (JWT, API tokens, etc.)
    """
    
    def __init__(
        self,
        message: str,
        token_type: str,  # "jwt", "api_key", "refresh_token", "access_token"
        token_error: str,  # "expired", "invalid", "malformed", "revoked"
        token_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ):
        self.token_type = token_type
        self.token_error = token_error
        self.token_id = token_id
        self.expires_at = expires_at
        
        details = {
            "token_type": token_type,
            "token_error": token_error,
            "token_id": token_id,
            "expires_at": expires_at.isoformat() if expires_at else None
        }
        
        super().__init__(
            message=message,
            error_code="TOKEN_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly token error message"""
        if self.token_error == "expired":
            return "Your session has expired. Please log in again."
        elif self.token_error == "invalid":
            return "Invalid authentication token. Please log in again."
        elif self.token_error == "malformed":
            return "Authentication token is malformed. Please log in again."
        elif self.token_error == "revoked":
            return "Authentication token has been revoked. Please log in again."
        else:
            return "Authentication token error. Please log in again."


class SessionException(DiagnoAssistException):
    """
    Exception for session management errors
    """
    
    def __init__(
        self,
        message: str,
        session_id: Optional[str] = None,
        session_error: str = "unknown",  # "expired", "invalid", "not_found", "concurrent"
        user_id: Optional[str] = None,
        max_concurrent_sessions: Optional[int] = None
    ):
        self.session_id = session_id
        self.session_error = session_error
        self.user_id = user_id
        self.max_concurrent_sessions = max_concurrent_sessions
        
        details = {
            "session_id": session_id,
            "session_error": session_error,
            "user_id": user_id,
            "max_concurrent_sessions": max_concurrent_sessions
        }
        
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly session error message"""
        if self.session_error == "expired":
            return "Your session has expired. Please log in again."
        elif self.session_error == "invalid":
            return "Invalid session. Please log in again."
        elif self.session_error == "not_found":
            return "Session not found. Please log in again."
        elif self.session_error == "concurrent":
            if self.max_concurrent_sessions:
                return f"Maximum concurrent sessions ({self.max_concurrent_sessions}) exceeded. Please log out from other devices."
            else:
                return "Too many active sessions. Please log out from other devices."
        else:
            return "Session error. Please log in again."


class MFAException(DiagnoAssistException):
    """
    Exception for Multi-Factor Authentication errors
    """
    
    def __init__(
        self,
        message: str,
        mfa_method: str,  # "totp", "sms", "email", "push"
        mfa_error: str,  # "required", "invalid_code", "expired_code", "too_many_attempts"
        user_id: Optional[str] = None,
        attempts_remaining: Optional[int] = None
    ):
        self.mfa_method = mfa_method
        self.mfa_error = mfa_error
        self.user_id = user_id
        self.attempts_remaining = attempts_remaining
        
        details = {
            "mfa_method": mfa_method,
            "mfa_error": mfa_error,
            "user_id": user_id,
            "attempts_remaining": attempts_remaining
        }
        
        super().__init__(
            message=message,
            error_code="MFA_ERROR",
            details=details,
            severity="warning"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly MFA error message"""
        if self.mfa_error == "required":
            return f"Multi-factor authentication required. Please provide your {self.mfa_method.upper()} code."
        elif self.mfa_error == "invalid_code":
            remaining_text = f" ({self.attempts_remaining} attempts remaining)" if self.attempts_remaining else ""
            return f"Invalid {self.mfa_method.upper()} code{remaining_text}."
        elif self.mfa_error == "expired_code":
            return f"The {self.mfa_method.upper()} code has expired. Please request a new one."
        elif self.mfa_error == "too_many_attempts":
            return "Too many failed verification attempts. Please try again later."
        else:
            return f"Multi-factor authentication error with {self.mfa_method.upper()}."


class SecurityPolicyException(DiagnoAssistException):
    """
    Exception for security policy violations
    """
    
    def __init__(
        self,
        message: str,
        policy_type: str,  # "password", "session", "access", "data_retention"
        policy_rule: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        violation_details: Optional[Dict[str, Any]] = None
    ):
        self.policy_type = policy_type
        self.policy_rule = policy_rule
        self.user_id = user_id
        self.resource = resource
        self.violation_details = violation_details or {}
        
        details = {
            "policy_type": policy_type,
            "policy_rule": policy_rule,
            "user_id": user_id,
            "resource": resource,
            "violation_details": violation_details
        }
        
        super().__init__(
            message=message,
            error_code="SECURITY_POLICY_VIOLATION",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly security policy error message"""
        if self.policy_type == "password":
            return "Password does not meet security requirements."
        elif self.policy_type == "session":
            return "Session policy violation. Please log in again."
        elif self.policy_type == "access":
            return "Access policy violation. This action is not allowed."
        elif self.policy_type == "data_retention":
            return "Data retention policy prevents this action."
        else:
            return f"Security policy violation: {self.policy_rule}"


class AuditException(DiagnoAssistException):
    """
    Exception for audit logging and compliance errors
    """
    
    def __init__(
        self,
        message: str,
        audit_event: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        compliance_requirement: Optional[str] = None,
        retention_required: bool = True
    ):
        self.audit_event = audit_event
        self.user_id = user_id
        self.resource_id = resource_id
        self.compliance_requirement = compliance_requirement
        self.retention_required = retention_required
        
        details = {
            "audit_event": audit_event,
            "user_id": user_id,
            "resource_id": resource_id,
            "compliance_requirement": compliance_requirement,
            "retention_required": retention_required
        }
        
        super().__init__(
            message=message,
            error_code="AUDIT_ERROR",
            details=details,
            severity="error"
        )
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly audit error message"""
        if self.compliance_requirement:
            return f"Audit logging required for compliance with {self.compliance_requirement}."
        else:
            return "Audit logging error. This action has been recorded for review."