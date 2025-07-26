"""
Template Service for DiagnoAssist Backend

Handles business logic for templates including:
- Template creation, management, and validation
- Template application to encounters
- Template search and recommendations
- Template usage analytics and optimization
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import json

from app.models.template import (
    TemplateModel, TemplateCreateRequest, TemplateUpdateRequest,
    TemplateSearchRequest, TemplateApplicationRequest, AppliedTemplateInfo,
    TemplateUsageStats, TemplateValidationResult, TemplateType, TemplateScope,
    TemplateCategory, TemplateField, TemplateSection
)
from app.models.auth import UserModel, UserRoleEnum
from app.models.encounter import EncounterModel
from app.models.soap import SOAPModel
from app.repositories.template_repository import TemplateRepository
from app.services.encounter_service import EncounterService
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError
from app.core.business_rules import business_rules_engine
from app.core.monitoring import monitoring

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for template management and operations"""
    
    def __init__(
        self,
        template_repository: TemplateRepository,
        encounter_service: EncounterService
    ):
        self.template_repository = template_repository
        self.encounter_service = encounter_service
    
    # Template CRUD Operations
    
    async def create_template(
        self,
        template_data: TemplateCreateRequest,
        user: UserModel
    ) -> TemplateModel:
        """
        Create a new template with validation
        
        Args:
            template_data: Template creation data
            user: User creating the template
            
        Returns:
            Created template
        """
        try:
            # Validate template data
            validation_result = await self.validate_template_structure(template_data.sections)
            if not validation_result.is_valid:
                raise ValidationException(f"Template validation failed: {', '.join(validation_result.errors)}")
            
            # Check permissions for scope
            if template_data.scope in [TemplateScope.ORGANIZATION, TemplateScope.PUBLIC]:
                if user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
                    raise PermissionDeniedError("Insufficient permissions for template scope")
            
            # Generate keywords for search
            keywords = await self._generate_template_keywords(template_data)
            template_data.keywords = keywords
            
            # Create template
            template = await self.template_repository.create_template(template_data, user)
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "templates_created_total",
                labels={
                    "type": template_data.template_type.value,
                    "category": template_data.category.value,
                    "scope": template_data.scope.value
                }
            )
            
            logger.info(f"Created template {template.id} by user {user.id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise
    
    async def get_template(
        self,
        template_id: str,
        user: UserModel
    ) -> TemplateModel:
        """
        Get template by ID with permission check
        
        Args:
            template_id: Template ID
            user: User requesting the template
            
        Returns:
            Template if found and accessible
        """
        try:
            template = await self.template_repository.get_template_by_id(template_id, user)
            if not template:
                raise NotFoundError("Template not found")
            
            return template
            
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            raise
    
    async def update_template(
        self,
        template_id: str,
        update_data: TemplateUpdateRequest,
        user: UserModel
    ) -> TemplateModel:
        """
        Update template with validation
        
        Args:
            template_id: Template ID
            update_data: Update data
            user: User updating the template
            
        Returns:
            Updated template
        """
        try:
            # Validate sections if provided
            if update_data.sections:
                validation_result = await self.validate_template_structure(update_data.sections)
                if not validation_result.is_valid:
                    raise ValidationException(f"Template validation failed: {', '.join(validation_result.errors)}")
            
            # Update keywords if content changed
            if update_data.sections or update_data.name or update_data.description:
                keywords = await self._generate_template_keywords_from_update(update_data)
                if keywords:
                    update_data.keywords = keywords
            
            # Update template
            template = await self.template_repository.update_template(template_id, update_data, user)
            
            logger.info(f"Updated template {template_id} by user {user.id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            raise
    
    async def delete_template(
        self,
        template_id: str,
        user: UserModel
    ) -> bool:
        """
        Delete template
        
        Args:
            template_id: Template ID
            user: User deleting the template
            
        Returns:
            Success status
        """
        try:
            success = await self.template_repository.delete_template(template_id, user)
            
            if success:
                logger.info(f"Deleted template {template_id} by user {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            raise
    
    # Template Search and Discovery
    
    async def search_templates(
        self,
        search_request: TemplateSearchRequest,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Search templates with filtering and pagination
        
        Args:
            search_request: Search parameters
            user: User performing the search
            
        Returns:
            Search results with pagination
        """
        try:
            results = await self.template_repository.search_templates(search_request, user)
            
            # Add usage recommendations
            for template in results["templates"]:
                template_dict = template.model_dump()
                template_dict["recommendation_score"] = await self._calculate_recommendation_score(
                    template, user
                )
                
            return results
            
        except Exception as e:
            logger.error(f"Failed to search templates: {e}")
            raise
    
    async def get_recommended_templates(
        self,
        user: UserModel,
        encounter_type: Optional[str] = None,
        category: Optional[TemplateCategory] = None,
        limit: int = 10
    ) -> List[TemplateModel]:
        """
        Get recommended templates for user
        
        Args:
            user: User requesting recommendations
            encounter_type: Encounter type filter
            category: Category filter
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended templates
        """
        try:
            # Get user's accessible templates
            templates = await self.template_repository.get_user_templates(
                user, category=category, limit=limit * 2
            )
            
            # Filter by encounter type if specified
            if encounter_type:
                templates = [
                    t for t in templates 
                    if not t.encounter_types or encounter_type in t.encounter_types
                ]
            
            # Calculate recommendation scores
            scored_templates = []
            for template in templates:
                score = await self._calculate_recommendation_score(template, user)
                scored_templates.append((template, score))
            
            # Sort by score and return top results
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            
            return [template for template, score in scored_templates[:limit]]
            
        except Exception as e:
            logger.error(f"Failed to get recommended templates: {e}")
            raise
    
    async def get_popular_templates(
        self,
        user: UserModel,
        category: Optional[TemplateCategory] = None,
        limit: int = 10
    ) -> List[TemplateModel]:
        """
        Get popular templates
        
        Args:
            user: User requesting templates
            category: Category filter
            limit: Maximum number of templates
            
        Returns:
            List of popular templates
        """
        try:
            return await self.template_repository.get_popular_templates(
                user, category=category, limit=limit
            )
            
        except Exception as e:
            logger.error(f"Failed to get popular templates: {e}")
            raise
    
    # Template Application
    
    async def apply_template_to_encounter(
        self,
        application_request: TemplateApplicationRequest,
        user: UserModel
    ) -> Tuple[EncounterModel, AppliedTemplateInfo]:
        """
        Apply template to encounter
        
        Args:
            application_request: Template application request
            user: User applying the template
            
        Returns:
            Updated encounter and application info
        """
        try:
            # Get template and encounter
            template = await self.get_template(application_request.template_id, user)
            encounter = await self.encounter_service.get_encounter(
                application_request.encounter_id, user
            )
            
            if not encounter:
                raise NotFoundError("Encounter not found")
            
            # Check if encounter can be modified
            if encounter.status == "signed":
                raise ValidationException("Cannot modify signed encounter")
            
            # Apply template based on merge strategy
            updated_encounter = await self._apply_template_to_encounter_data(
                template, encounter, application_request, user
            )
            
            # Update encounter
            from app.models.encounter import EncounterUpdateRequest
            update_request = EncounterUpdateRequest(
                soap=updated_encounter.soap,
                applied_templates=updated_encounter.applied_templates
            )
            
            final_encounter = await self.encounter_service.update_encounter(
                application_request.encounter_id, update_request, user
            )
            
            # Record template usage
            await self.template_repository.record_template_usage(
                application_request.template_id, user, application_request.encounter_id
            )
            
            # Create application info
            applied_sections = application_request.apply_sections or [
                section.section for section in template.sections
            ]
            
            application_info = AppliedTemplateInfo(
                template_id=template.id,
                template_name=template.name,
                applied_at=datetime.utcnow(),
                applied_by=user.id,
                applied_sections=applied_sections,
                field_modifications=application_request.field_overrides
            )
            
            # Record metrics
            monitoring.metrics.increment_counter(
                "templates_applied_total",
                labels={
                    "template_type": template.template_type.value,
                    "merge_strategy": application_request.merge_strategy
                }
            )
            
            logger.info(f"Applied template {template.id} to encounter {encounter.id}")
            return final_encounter, application_info
            
        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            raise
    
    async def get_applicable_templates(
        self,
        encounter_id: str,
        user: UserModel
    ) -> List[TemplateModel]:
        """
        Get templates applicable to specific encounter
        
        Args:
            encounter_id: Encounter ID
            user: User requesting templates
            
        Returns:
            List of applicable templates
        """
        try:
            # Get encounter
            encounter = await self.encounter_service.get_encounter(encounter_id, user)
            if not encounter:
                raise NotFoundError("Encounter not found")
            
            # Get recommended templates based on encounter context
            templates = await self.get_recommended_templates(
                user,
                encounter_type=encounter.type,
                limit=20
            )
            
            # Filter based on encounter-specific criteria
            applicable_templates = []
            for template in templates:
                if await self._is_template_applicable_to_encounter(template, encounter):
                    applicable_templates.append(template)
            
            return applicable_templates
            
        except Exception as e:
            logger.error(f"Failed to get applicable templates: {e}")
            raise
    
    # Template Analytics
    
    async def get_template_usage_stats(
        self,
        template_id: str,
        user: UserModel
    ) -> TemplateUsageStats:
        """
        Get template usage statistics
        
        Args:
            template_id: Template ID
            user: User requesting stats
            
        Returns:
            Usage statistics
        """
        try:
            return await self.template_repository.get_template_usage_stats(template_id, user)
            
        except Exception as e:
            logger.error(f"Failed to get template usage stats: {e}")
            raise
    
    async def rate_template(
        self,
        template_id: str,
        rating: float,
        user: UserModel
    ) -> bool:
        """
        Rate a template
        
        Args:
            template_id: Template ID
            rating: Rating value (1-5)
            user: User rating the template
            
        Returns:
            Success status
        """
        try:
            return await self.template_repository.rate_template(template_id, user, rating)
            
        except Exception as e:
            logger.error(f"Failed to rate template: {e}")
            raise
    
    # Template Validation
    
    async def validate_template_structure(
        self,
        sections: List[TemplateSection]
    ) -> TemplateValidationResult:
        """
        Validate template structure and content
        
        Args:
            sections: Template sections to validate
            
        Returns:
            Validation result
        """
        try:
            errors = []
            warnings = []
            suggestions = []
            
            # Check basic structure
            if not sections:
                errors.append("Template must have at least one section")
                return TemplateValidationResult(is_valid=False, errors=errors)
            
            # Validate sections
            section_names = set()
            for section in sections:
                # Check for duplicate sections
                if section.section in section_names:
                    errors.append(f"Duplicate section: {section.section}")
                section_names.add(section.section)
                
                # Validate fields
                if not section.fields:
                    warnings.append(f"Section '{section.section}' has no fields")
                
                field_ids = set()
                for field in section.fields:
                    # Check for duplicate field IDs
                    if field.id in field_ids:
                        errors.append(f"Duplicate field ID: {field.id}")
                    field_ids.add(field.id)
                    
                    # Validate field structure
                    field_validation = await self._validate_template_field(field)
                    errors.extend(field_validation.get("errors", []))
                    warnings.extend(field_validation.get("warnings", []))
                    suggestions.extend(field_validation.get("suggestions", []))
            
            # Clinical quality checks
            clinical_score = await self._calculate_clinical_quality_score(sections)
            
            # Generate suggestions for improvement
            improvement_suggestions = await self._generate_improvement_suggestions(sections)
            suggestions.extend(improvement_suggestions)
            
            is_valid = len(errors) == 0
            
            return TemplateValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                clinical_quality_score=clinical_score
            )
            
        except Exception as e:
            logger.error(f"Failed to validate template structure: {e}")
            return TemplateValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    # Private helper methods
    
    async def _generate_template_keywords(self, template_data: TemplateCreateRequest) -> List[str]:
        """Generate keywords for template search"""
        keywords = []
        
        # Add name and description words
        if template_data.name:
            keywords.extend(template_data.name.lower().split())
        if template_data.description:
            keywords.extend(template_data.description.lower().split())
        
        # Add field labels and help text
        for section in template_data.sections:
            for field in section.fields:
                keywords.extend(field.label.lower().split())
                if field.help_text:
                    keywords.extend(field.help_text.lower().split())
        
        # Add tags and category
        keywords.extend(template_data.tags)
        keywords.append(template_data.category.value)
        keywords.append(template_data.template_type.value)
        
        # Remove duplicates and common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [k for k in set(keywords) if k not in common_words and len(k) > 2]
        
        return keywords
    
    async def _generate_template_keywords_from_update(self, update_data: TemplateUpdateRequest) -> Optional[List[str]]:
        """Generate keywords from update data"""
        if not any([update_data.name, update_data.description, update_data.sections]):
            return None
        
        keywords = []
        
        if update_data.name:
            keywords.extend(update_data.name.lower().split())
        if update_data.description:
            keywords.extend(update_data.description.lower().split())
        
        if update_data.sections:
            for section in update_data.sections:
                for field in section.fields:
                    keywords.extend(field.label.lower().split())
                    if field.help_text:
                        keywords.extend(field.help_text.lower().split())
        
        # Remove duplicates and common words
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [k for k in set(keywords) if k not in common_words and len(k) > 2]
        
        return keywords if keywords else None
    
    async def _calculate_recommendation_score(self, template: TemplateModel, user: UserModel) -> float:
        """Calculate recommendation score for template"""
        score = 0.0
        
        # Base score from rating
        if template.metadata.rating:
            score += template.metadata.rating * 20  # 0-100 scale
        else:
            score += 50  # Default for unrated templates
        
        # Usage frequency bonus
        if template.metadata.usage_count > 0:
            score += min(template.metadata.usage_count * 2, 30)
        
        # User-specific factors
        if template.owner_id == user.id:
            score += 10  # Slight bonus for own templates
        
        # Recent usage bonus
        if template.metadata.last_used:
            days_since_use = (datetime.utcnow() - template.metadata.last_used).days
            if days_since_use < 7:
                score += 10
            elif days_since_use < 30:
                score += 5
        
        # Scope preference
        if template.scope == TemplateScope.ORGANIZATION:
            score += 5
        
        return min(score, 100.0)
    
    async def _apply_template_to_encounter_data(
        self,
        template: TemplateModel,
        encounter: EncounterModel,
        application_request: TemplateApplicationRequest,
        user: UserModel
    ) -> EncounterModel:
        """Apply template data to encounter"""
        
        # Initialize SOAP if not exists
        if not encounter.soap:
            from app.models.soap import SOAPModel, SubjectiveSection, ObjectiveSection, AssessmentSection, PlanSection
            encounter.soap = SOAPModel(
                subjective=SubjectiveSection(),
                objective=ObjectiveSection(),
                assessment=AssessmentSection(),
                plan=PlanSection()
            )
        
        # Get sections to apply
        sections_to_apply = application_request.apply_sections or [
            section.section for section in template.sections
        ]
        
        # Apply template sections
        for template_section in template.sections:
            if template_section.section not in sections_to_apply:
                continue
            
            # Apply fields based on merge strategy
            await self._apply_section_to_encounter(
                template_section,
                encounter,
                application_request.merge_strategy,
                application_request.field_overrides or {}
            )
        
        # Add to applied templates
        if not encounter.applied_templates:
            encounter.applied_templates = []
        
        applied_info = AppliedTemplateInfo(
            template_id=template.id,
            template_name=template.name,
            applied_at=datetime.utcnow(),
            applied_by=user.id,
            applied_sections=sections_to_apply,
            field_modifications=application_request.field_overrides
        )
        
        encounter.applied_templates.append(applied_info)
        
        return encounter
    
    async def _apply_section_to_encounter(
        self,
        template_section: TemplateSection,
        encounter: EncounterModel,
        merge_strategy: str,
        field_overrides: Dict[str, Any]
    ):
        """Apply template section to encounter SOAP data"""
        
        section_name = template_section.section
        soap_section = getattr(encounter.soap, section_name, None)
        
        if not soap_section:
            return
        
        for field in template_section.fields:
            field_value = field_overrides.get(field.id, field.default_value)
            
            if field_value is not None:
                # Apply value based on merge strategy
                if merge_strategy == "replace":
                    setattr(soap_section, field.id, field_value)
                elif merge_strategy == "merge":
                    existing_value = getattr(soap_section, field.id, None)
                    if not existing_value:
                        setattr(soap_section, field.id, field_value)
                elif merge_strategy == "append":
                    existing_value = getattr(soap_section, field.id, None)
                    if existing_value:
                        combined_value = f"{existing_value}\n{field_value}"
                        setattr(soap_section, field.id, combined_value)
                    else:
                        setattr(soap_section, field.id, field_value)
    
    async def _is_template_applicable_to_encounter(
        self,
        template: TemplateModel,
        encounter: EncounterModel
    ) -> bool:
        """Check if template is applicable to encounter"""
        
        # Check encounter type compatibility
        if template.encounter_types and encounter.type not in template.encounter_types:
            return False
        
        # Check if already applied
        if encounter.applied_templates:
            applied_template_ids = [at.template_id for at in encounter.applied_templates]
            if template.id in applied_template_ids:
                return False
        
        # Add additional applicability checks as needed
        return True
    
    async def _validate_template_field(self, field: TemplateField) -> Dict[str, List[str]]:
        """Validate individual template field"""
        errors = []
        warnings = []
        suggestions = []
        
        # Check required properties
        if not field.label:
            errors.append(f"Field {field.id} missing label")
        
        # Validate field-specific rules
        if field.field_type in ["select", "multiselect", "radio"] and not field.options:
            errors.append(f"Field {field.id} requires options for type {field.field_type}")
        
        # Check validation rules
        if field.validation_rules:
            for rule, value in field.validation_rules.items():
                if rule == "pattern" and not isinstance(value, str):
                    errors.append(f"Pattern rule must be string for field {field.id}")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }
    
    async def _calculate_clinical_quality_score(self, sections: List[TemplateSection]) -> float:
        """Calculate clinical quality score for template"""
        score = 0.0
        total_checks = 0
        
        # Check for essential SOAP sections
        section_names = {section.section for section in sections}
        essential_sections = {"subjective", "objective", "assessment", "plan"}
        
        for essential in essential_sections:
            total_checks += 1
            if essential in section_names:
                score += 25.0
        
        # Check field completeness
        for section in sections:
            if section.fields:
                total_checks += 1
                score += 10.0
                
                # Check for clinical fields
                clinical_fields = [f for f in section.fields if f.clinical_context]
                if clinical_fields:
                    score += 5.0
        
        return min(score, 100.0)
    
    async def _generate_improvement_suggestions(self, sections: List[TemplateSection]) -> List[str]:
        """Generate suggestions for template improvement"""
        suggestions = []
        
        section_names = {section.section for section in sections}
        
        # Check for missing SOAP sections
        essential_sections = {"subjective", "objective", "assessment", "plan"}
        missing_sections = essential_sections - section_names
        
        if missing_sections:
            suggestions.append(f"Consider adding missing SOAP sections: {', '.join(missing_sections)}")
        
        # Check for empty sections
        empty_sections = [s.section for s in sections if not s.fields]
        if empty_sections:
            suggestions.append(f"Add fields to empty sections: {', '.join(empty_sections)}")
        
        # Suggest clinical coding
        sections_without_codes = [
            s.section for s in sections 
            if s.fields and not any(f.icd_10_codes or f.cpt_codes for f in s.fields)
        ]
        if sections_without_codes:
            suggestions.append("Consider adding ICD-10 or CPT codes to improve clinical accuracy")
        
        return suggestions


# Create service instance (to be initialized with dependencies)
template_service = None