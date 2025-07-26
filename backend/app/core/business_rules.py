"""
Business Rules Engine for DiagnoAssist Backend

This module provides a flexible framework for defining and enforcing
business rules across the medical records management system.
"""
import asyncio
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.models.patient import PatientModel
from app.models.encounter import EncounterModel, EncounterStatusEnum
from app.models.episode import EpisodeModel, EpisodeStatusEnum
from app.models.auth import UserModel, UserRoleEnum
from app.models.soap import SOAPModel
from app.core.exceptions import ValidationException, BusinessRuleException

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RuleSeverity(str, Enum):
    """Rule violation severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RuleContext(str, Enum):
    """Context where rules are applied"""
    PATIENT_REGISTRATION = "patient_registration"
    ENCOUNTER_CREATION = "encounter_creation"
    ENCOUNTER_UPDATE = "encounter_update"
    ENCOUNTER_SIGNING = "encounter_signing"
    EPISODE_MANAGEMENT = "episode_management"
    USER_AUTHENTICATION = "user_authentication"
    DATA_MIGRATION = "data_migration"
    FHIR_SYNC = "fhir_sync"


class RuleViolation(BaseModel):
    """Represents a business rule violation"""
    rule_id: str
    rule_name: str
    severity: RuleSeverity
    message: str
    field_path: Optional[str] = None
    suggested_action: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[RuleContext] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class RuleExecutionResult(BaseModel):
    """Result of rule execution"""
    rule_id: str
    passed: bool
    violations: List[RuleViolation] = Field(default_factory=list)
    execution_time_ms: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BusinessRuleEngine:
    """
    Central business rules engine that manages and executes rules
    """
    
    def __init__(self):
        self._rules: Dict[str, 'BusinessRule'] = {}
        self._context_rules: Dict[RuleContext, List[str]] = {}
        self._rule_dependencies: Dict[str, List[str]] = {}
        
    def register_rule(
        self, 
        rule: 'BusinessRule', 
        contexts: List[RuleContext] = None,
        dependencies: List[str] = None
    ):
        """Register a business rule with the engine"""
        self._rules[rule.rule_id] = rule
        
        # Associate rule with contexts
        if contexts:
            for context in contexts:
                if context not in self._context_rules:
                    self._context_rules[context] = []
                self._context_rules[context].append(rule.rule_id)
        
        # Register dependencies
        if dependencies:
            self._rule_dependencies[rule.rule_id] = dependencies
            
        logger.info(f"Registered business rule: {rule.rule_id}")
    
    async def validate(
        self, 
        data: Any, 
        context: RuleContext,
        user: Optional[UserModel] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> List[RuleViolation]:
        """
        Validate data against all rules for a given context
        """
        violations = []
        
        # Get rules for context
        rule_ids = self._context_rules.get(context, [])
        
        # Sort rules by dependencies
        sorted_rule_ids = self._sort_by_dependencies(rule_ids)
        
        # Execute rules
        for rule_id in sorted_rule_ids:
            rule = self._rules[rule_id]
            
            try:
                result = await rule.execute(data, context, user, additional_data)
                violations.extend(result.violations)
                
                # Stop on critical violations if configured
                critical_violations = [v for v in result.violations if v.severity == RuleSeverity.CRITICAL]
                if critical_violations and rule.stop_on_critical:
                    break
                    
            except Exception as e:
                logger.error(f"Error executing rule {rule_id}: {str(e)}")
                violations.append(RuleViolation(
                    rule_id=rule_id,
                    rule_name=rule.name,
                    severity=RuleSeverity.CRITICAL,
                    message=f"Rule execution failed: {str(e)}",
                    context=context
                ))
        
        return violations
    
    async def validate_and_raise(
        self, 
        data: Any, 
        context: RuleContext,
        user: Optional[UserModel] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """
        Validate and raise exception if critical or error violations found
        """
        violations = await self.validate(data, context, user, additional_data)
        
        # Check for critical or error violations
        blocking_violations = [
            v for v in violations 
            if v.severity in [RuleSeverity.CRITICAL, RuleSeverity.ERROR]
        ]
        
        if blocking_violations:
            raise BusinessRuleException(
                message="Business rule violations found",
                violations=blocking_violations
            )
        
        return violations
    
    def _sort_by_dependencies(self, rule_ids: List[str]) -> List[str]:
        """Sort rule IDs by their dependencies"""
        sorted_ids = []
        remaining = set(rule_ids)
        
        while remaining:
            # Find rules with no unresolved dependencies
            ready = []
            for rule_id in remaining:
                dependencies = self._rule_dependencies.get(rule_id, [])
                if all(dep in sorted_ids for dep in dependencies):
                    ready.append(rule_id)
            
            if not ready:
                # Circular dependency or missing dependency
                logger.warning(f"Circular dependency detected in rules: {remaining}")
                ready = list(remaining)  # Add all remaining
            
            sorted_ids.extend(ready)
            remaining -= set(ready)
        
        return sorted_ids
    
    def get_rule(self, rule_id: str) -> Optional['BusinessRule']:
        """Get a specific rule by ID"""
        return self._rules.get(rule_id)
    
    def get_rules_for_context(self, context: RuleContext) -> List['BusinessRule']:
        """Get all rules for a specific context"""
        rule_ids = self._context_rules.get(context, [])
        return [self._rules[rule_id] for rule_id in rule_ids]


class BusinessRule(ABC):
    """
    Abstract base class for business rules
    """
    
    def __init__(
        self, 
        rule_id: str, 
        name: str, 
        description: str,
        stop_on_critical: bool = True
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.stop_on_critical = stop_on_critical
    
    @abstractmethod
    async def execute(
        self, 
        data: Any, 
        context: RuleContext,
        user: Optional[UserModel] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> RuleExecutionResult:
        """Execute the business rule"""
        pass
    
    def create_violation(
        self, 
        severity: RuleSeverity, 
        message: str,
        field_path: Optional[str] = None,
        suggested_action: Optional[str] = None,
        context: Optional[RuleContext] = None,
        **metadata
    ) -> RuleViolation:
        """Helper method to create rule violations"""
        return RuleViolation(
            rule_id=self.rule_id,
            rule_name=self.name,
            severity=severity,
            message=message,
            field_path=field_path,
            suggested_action=suggested_action,
            context=context,
            metadata=metadata
        )


class PatientRegistrationRules:
    """Business rules for patient registration"""
    
    class RequiredDemographicsRule(BusinessRule):
        """Ensure required demographic information is provided"""
        
        def __init__(self):
            super().__init__(
                rule_id="patient.demographics.required",
                name="Required Demographics",
                description="Ensures all required demographic fields are provided"
            )
        
        async def execute(
            self, 
            data: PatientModel, 
            context: RuleContext,
            user: Optional[UserModel] = None,
            additional_data: Optional[Dict[str, Any]] = None
        ) -> RuleExecutionResult:
            start_time = datetime.utcnow()
            violations = []
            
            # Check required fields
            demographics = data.demographics
            
            if not demographics.name or demographics.name.strip() == "":
                violations.append(self.create_violation(
                    RuleSeverity.ERROR,
                    "Patient name is required",
                    field_path="demographics.name",
                    suggested_action="Provide a valid patient name",
                    context=context
                ))
            
            if not demographics.date_of_birth:
                violations.append(self.create_violation(
                    RuleSeverity.ERROR,
                    "Date of birth is required",
                    field_path="demographics.date_of_birth",
                    suggested_action="Provide patient's date of birth",
                    context=context
                ))
            
            if not demographics.gender:
                violations.append(self.create_violation(
                    RuleSeverity.WARNING,
                    "Gender information is recommended",
                    field_path="demographics.gender",
                    suggested_action="Consider adding gender information",
                    context=context
                ))
            
            # Validate contact information
            if not demographics.phone and not demographics.email:
                violations.append(self.create_violation(
                    RuleSeverity.WARNING,
                    "At least one contact method (phone or email) is recommended",
                    field_path="demographics",
                    suggested_action="Add phone number or email address",
                    context=context
                ))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return RuleExecutionResult(
                rule_id=self.rule_id,
                passed=len([v for v in violations if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]]) == 0,
                violations=violations,
                execution_time_ms=execution_time
            )
    
    class AgeValidationRule(BusinessRule):
        """Validate patient age is reasonable"""
        
        def __init__(self):
            super().__init__(
                rule_id="patient.age.validation",
                name="Age Validation",
                description="Ensures patient age is within reasonable bounds"
            )
        
        async def execute(
            self, 
            data: PatientModel, 
            context: RuleContext,
            user: Optional[UserModel] = None,
            additional_data: Optional[Dict[str, Any]] = None
        ) -> RuleExecutionResult:
            start_time = datetime.utcnow()
            violations = []
            
            if data.demographics.date_of_birth:
                try:
                    from datetime import datetime
                    if isinstance(data.demographics.date_of_birth, str):
                        birth_date = datetime.strptime(data.demographics.date_of_birth, "%Y-%m-%d")
                    else:
                        birth_date = data.demographics.date_of_birth
                    
                    age = (datetime.now() - birth_date).days / 365.25
                    
                    if age < 0:
                        violations.append(self.create_violation(
                            RuleSeverity.ERROR,
                            "Date of birth cannot be in the future",
                            field_path="demographics.date_of_birth",
                            suggested_action="Verify and correct the date of birth",
                            context=context,
                            calculated_age=age
                        ))
                    elif age > 150:
                        violations.append(self.create_violation(
                            RuleSeverity.WARNING,
                            f"Unusual age detected: {age:.1f} years",
                            field_path="demographics.date_of_birth",
                            suggested_action="Verify the date of birth is correct",
                            context=context,
                            calculated_age=age
                        ))
                    elif age < 0.1:  # Less than a month old
                        violations.append(self.create_violation(
                            RuleSeverity.INFO,
                            f"Newborn patient: {age:.2f} years old",
                            field_path="demographics.date_of_birth",
                            suggested_action="Ensure appropriate pediatric protocols are followed",
                            context=context,
                            calculated_age=age
                        ))
                
                except (ValueError, TypeError) as e:
                    violations.append(self.create_violation(
                        RuleSeverity.ERROR,
                        f"Invalid date of birth format: {str(e)}",
                        field_path="demographics.date_of_birth",
                        suggested_action="Use YYYY-MM-DD format for date of birth",
                        context=context
                    ))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return RuleExecutionResult(
                rule_id=self.rule_id,
                passed=len([v for v in violations if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]]) == 0,
                violations=violations,
                execution_time_ms=execution_time
            )


class EncounterManagementRules:
    """Business rules for encounter management"""
    
    class EncounterStateTransitionRule(BusinessRule):
        """Validate encounter status transitions"""
        
        def __init__(self):
            super().__init__(
                rule_id="encounter.state.transition",
                name="Encounter State Transition",
                description="Validates allowed encounter status transitions"
            )
            
            # Define allowed transitions
            self.allowed_transitions = {
                EncounterStatusEnum.DRAFT: [EncounterStatusEnum.IN_PROGRESS, EncounterStatusEnum.CANCELLED],
                EncounterStatusEnum.IN_PROGRESS: [EncounterStatusEnum.SIGNED, EncounterStatusEnum.CANCELLED],
                EncounterStatusEnum.SIGNED: [],  # Signed encounters cannot be changed
                EncounterStatusEnum.CANCELLED: []  # Cancelled encounters cannot be changed
            }
        
        async def execute(
            self, 
            data: EncounterModel, 
            context: RuleContext,
            user: Optional[UserModel] = None,
            additional_data: Optional[Dict[str, Any]] = None
        ) -> RuleExecutionResult:
            start_time = datetime.utcnow()
            violations = []
            
            # Get previous status from additional_data
            previous_status = additional_data.get("previous_status") if additional_data else None
            
            if previous_status and previous_status != data.status:
                allowed = self.allowed_transitions.get(previous_status, [])
                
                if data.status not in allowed:
                    violations.append(self.create_violation(
                        RuleSeverity.ERROR,
                        f"Invalid status transition from {previous_status.value} to {data.status.value}",
                        field_path="status",
                        suggested_action=f"Allowed transitions from {previous_status.value}: {[s.value for s in allowed]}",
                        context=context,
                        previous_status=previous_status.value,
                        new_status=data.status.value
                    ))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return RuleExecutionResult(
                rule_id=self.rule_id,
                passed=len(violations) == 0,
                violations=violations,
                execution_time_ms=execution_time
            )
    
    class EncounterCompletenessRule(BusinessRule):
        """Validate encounter is complete before signing"""
        
        def __init__(self):
            super().__init__(
                rule_id="encounter.completeness.signing",
                name="Encounter Completeness for Signing",
                description="Ensures encounter has required documentation before signing"
            )
        
        async def execute(
            self, 
            data: EncounterModel, 
            context: RuleContext,
            user: Optional[UserModel] = None,
            additional_data: Optional[Dict[str, Any]] = None
        ) -> RuleExecutionResult:
            start_time = datetime.utcnow()
            violations = []
            
            # Only apply this rule when signing
            if context != RuleContext.ENCOUNTER_SIGNING:
                return RuleExecutionResult(
                    rule_id=self.rule_id,
                    passed=True,
                    violations=[],
                    execution_time_ms=0
                )
            
            soap = data.soap
            if not soap:
                violations.append(self.create_violation(
                    RuleSeverity.ERROR,
                    "SOAP documentation is required before signing",
                    field_path="soap",
                    suggested_action="Add SOAP documentation",
                    context=context
                ))
                return RuleExecutionResult(
                    rule_id=self.rule_id,
                    passed=False,
                    violations=violations,
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            
            # Check required SOAP sections
            if not soap.subjective or not soap.subjective.chief_complaint:
                violations.append(self.create_violation(
                    RuleSeverity.ERROR,
                    "Chief complaint is required before signing",
                    field_path="soap.subjective.chief_complaint",
                    suggested_action="Add chief complaint in subjective section",
                    context=context
                ))
            
            if not soap.assessment or not soap.assessment.primary_diagnosis:
                violations.append(self.create_violation(
                    RuleSeverity.ERROR,
                    "Primary diagnosis is required before signing",
                    field_path="soap.assessment.primary_diagnosis",
                    suggested_action="Add primary diagnosis in assessment section",
                    context=context
                ))
            
            # Check for plan if needed
            if soap.assessment and soap.assessment.primary_diagnosis:
                if not soap.plan or not soap.plan.treatment_plan:
                    violations.append(self.create_violation(
                        RuleSeverity.WARNING,
                        "Treatment plan is recommended when diagnosis is provided",
                        field_path="soap.plan.treatment_plan",
                        suggested_action="Consider adding treatment plan",
                        context=context
                    ))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return RuleExecutionResult(
                rule_id=self.rule_id,
                passed=len([v for v in violations if v.severity in [RuleSeverity.ERROR, RuleSeverity.CRITICAL]]) == 0,
                violations=violations,
                execution_time_ms=execution_time
            )


class AuthorizationRules:
    """Business rules for authorization and access control"""
    
    class UserRoleEnumPermissionRule(BusinessRule):
        """Validate user permissions for actions"""
        
        def __init__(self):
            super().__init__(
                rule_id="auth.role.permission",
                name="User Role Permission",
                description="Validates user has required permissions for action"
            )
            
            # Define action permissions
            self.action_permissions = {
                "create_patient": [UserRoleEnum.DOCTOR, UserRoleEnum.NURSE, UserRoleEnum.ADMIN],
                "sign_encounter": [UserRoleEnum.DOCTOR],
                "view_encounter": [UserRoleEnum.DOCTOR, UserRoleEnum.NURSE, UserRoleEnum.ADMIN],
                "delete_patient": [UserRoleEnum.ADMIN],
                "manage_users": [UserRoleEnum.ADMIN],
                "view_system_stats": [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]
            }
        
        async def execute(
            self, 
            data: Any, 
            context: RuleContext,
            user: Optional[UserModel] = None,
            additional_data: Optional[Dict[str, Any]] = None
        ) -> RuleExecutionResult:
            start_time = datetime.utcnow()
            violations = []
            
            if not user:
                violations.append(self.create_violation(
                    RuleSeverity.CRITICAL,
                    "User authentication required",
                    suggested_action="Authenticate user before performing action",
                    context=context
                ))
                return RuleExecutionResult(
                    rule_id=self.rule_id,
                    passed=False,
                    violations=violations,
                    execution_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000
                )
            
            # Get requested action from additional_data
            action = additional_data.get("action") if additional_data else None
            
            if action and action in self.action_permissions:
                allowed_roles = self.action_permissions[action]
                
                if user.role not in allowed_roles:
                    violations.append(self.create_violation(
                        RuleSeverity.ERROR,
                        f"User role {user.role.value} not authorized for action: {action}",
                        suggested_action=f"Required roles: {[r.value for r in allowed_roles]}",
                        context=context,
                        user_role=user.role.value,
                        required_roles=[r.value for r in allowed_roles],
                        action=action
                    ))
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return RuleExecutionResult(
                rule_id=self.rule_id,
                passed=len(violations) == 0,
                violations=violations,
                execution_time_ms=execution_time
            )


# Global business rules engine instance
business_rules_engine = BusinessRuleEngine()


def register_default_rules():
    """Register all default business rules"""
    
    # Patient registration rules
    business_rules_engine.register_rule(
        PatientRegistrationRules.RequiredDemographicsRule(),
        contexts=[RuleContext.PATIENT_REGISTRATION]
    )
    
    business_rules_engine.register_rule(
        PatientRegistrationRules.AgeValidationRule(),
        contexts=[RuleContext.PATIENT_REGISTRATION],
        dependencies=["patient.demographics.required"]
    )
    
    # Encounter management rules
    business_rules_engine.register_rule(
        EncounterManagementRules.EncounterStateTransitionRule(),
        contexts=[RuleContext.ENCOUNTER_UPDATE, RuleContext.ENCOUNTER_SIGNING]
    )
    
    business_rules_engine.register_rule(
        EncounterManagementRules.EncounterCompletenessRule(),
        contexts=[RuleContext.ENCOUNTER_SIGNING]
    )
    
    # Authorization rules
    business_rules_engine.register_rule(
        AuthorizationRules.UserRoleEnumPermissionRule(),
        contexts=[
            RuleContext.PATIENT_REGISTRATION,
            RuleContext.ENCOUNTER_CREATION,
            RuleContext.ENCOUNTER_UPDATE,
            RuleContext.ENCOUNTER_SIGNING
        ]
    )
    
    logger.info("Default business rules registered successfully")


# Initialize default rules on module import
register_default_rules()