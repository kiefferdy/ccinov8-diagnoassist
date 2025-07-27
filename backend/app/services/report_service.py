"""
Report Service for DiagnoAssist Backend

Handles business logic for reports and analytics including:
- Report generation and data aggregation
- Analytics processing and insights
- Dashboard data preparation
- Report export and sharing
"""
import logging
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
import json
from io import BytesIO

from app.models.reports import (
    ReportModel, ReportRequest, ReportFilter, ReportType, ReportStatus,
    PatientSummaryReport, EpisodeReport, PracticeAnalyticsReport,
    DashboardConfig, ReportTemplate, ReportSchedule, AnalyticsQuery,
    PatientDemographics, ClinicalMetrics, FinancialMetrics, UtilizationMetrics
)
from app.models.auth import UserModel, UserRoleEnum
from app.repositories.report_repository import ReportRepository
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError
# Simplified for core functionality - removed enterprise monitoring/performance systems

logger = logging.getLogger(__name__)


class ReportService:
    """Service for report generation and analytics"""
    
    def __init__(self, report_repository: ReportRepository):
        self.report_repository = report_repository
        self._generation_queue = asyncio.Queue()
        self._processing_reports = set()
    
    # Report Generation
    
    async def generate_report(
        self,
        report_request: ReportRequest,
        user: UserModel
    ) -> ReportModel:
        """
        Generate a report based on request
        
        Args:
            report_request: Report generation request
            user: User requesting the report
            
        Returns:
            Generated report model
        """
        try:
            # Validate request
            await self._validate_report_request(report_request, user)
            
            # Create report entry
            report = await self.report_repository.create_report(report_request, user)
            
            # Start background generation
            asyncio.create_task(self._generate_report_background(report.id, report_request, user))
            
            # Log report request
            logger.debug(f"Report requested - type: {report_request.report_type.value}, format: {report_request.report_format.value}")
            
            logger.info(f"Started report generation {report.id} for user {user.id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    async def get_report(
        self,
        report_id: str,
        user: UserModel
    ) -> ReportModel:
        """
        Get report by ID with permission check
        
        Args:
            report_id: Report ID
            user: User requesting the report
            
        Returns:
            Report if found and accessible
        """
        try:
            report = await self.report_repository.get_by_id(report_id)
            if not report:
                raise NotFoundError("Report not found")
            
            # Check permissions
            if not await self._has_report_access(report, user):
                raise PermissionDeniedError("Access denied to report")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to get report {report_id}: {e}")
            raise
    
    async def get_user_reports(
        self,
        user: UserModel,
        limit: int = 50
    ) -> List[ReportModel]:
        """
        Get reports for user
        
        Args:
            user: User requesting reports
            limit: Maximum number of reports
            
        Returns:
            List of user reports
        """
        try:
            return await self.report_repository.get_user_reports(user, limit)
            
        except Exception as e:
            logger.error(f"Failed to get user reports: {e}")
            raise
    
    async def delete_report(
        self,
        report_id: str,
        user: UserModel
    ) -> bool:
        """
        Delete report
        
        Args:
            report_id: Report ID
            user: User deleting the report
            
        Returns:
            Success status
        """
        try:
            report = await self.get_report(report_id, user)
            
            # Check delete permissions
            if report.requested_by != user.id and user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError("No permission to delete report")
            
            # Delete report
            success = await self.report_repository.delete(report_id)
            
            if success:
                logger.info(f"Deleted report {report_id} by user {user.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {e}")
            raise
    
    # Specific Report Types
    
    async def generate_patient_summary_report(
        self,
        patient_id: str,
        filters: ReportFilter,
        user: UserModel
    ) -> PatientSummaryReport:
        """
        Generate patient summary report
        
        Args:
            patient_id: Patient ID
            filters: Report filters
            user: User generating report
            
        Returns:
            Patient summary report
        """
        try:
            # Get aggregated patient data
            patient_data = await self.report_repository.get_patient_summary_data(patient_id, filters)
            
            # Process data into report format
            report = await self._process_patient_summary_data(patient_data, user)
            
            logger.info(f"Generated patient summary report for {patient_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate patient summary report: {e}")
            raise
    
    async def generate_episode_report(
        self,
        episode_id: str,
        filters: ReportFilter,
        user: UserModel
    ) -> EpisodeReport:
        """
        Generate episode report
        
        Args:
            episode_id: Episode ID
            filters: Report filters
            user: User generating report
            
        Returns:
            Episode report
        """
        try:
            # Get aggregated episode data
            episode_data = await self.report_repository.get_episode_report_data(episode_id, filters)
            
            # Process data into report format
            report = await self._process_episode_data(episode_data, user)
            
            logger.info(f"Generated episode report for {episode_id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate episode report: {e}")
            raise
    
    async def generate_practice_analytics_report(
        self,
        filters: ReportFilter,
        user: UserModel
    ) -> PracticeAnalyticsReport:
        """
        Generate practice analytics report
        
        Args:
            filters: Report filters
            user: User generating report
            
        Returns:
            Practice analytics report
        """
        try:
            # Get aggregated practice data
            analytics_data = await self.report_repository.get_practice_analytics_data(filters, user)
            
            # Process data into report format
            report = await self._process_practice_analytics_data(analytics_data, filters, user)
            
            # Generate insights and recommendations
            report.key_insights = await self._generate_practice_insights(analytics_data)
            report.recommendations = await self._generate_practice_recommendations(analytics_data)
            
            logger.info(f"Generated practice analytics report for user {user.id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate practice analytics report: {e}")
            raise
    
    # Dashboard Services
    
    async def get_dashboard_data(
        self,
        dashboard_id: str,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Get dashboard data
        
        Args:
            dashboard_id: Dashboard ID
            user: User requesting dashboard data
            
        Returns:
            Dashboard data
        """
        try:
            # Get dashboard configuration
            dashboard_config = await self._get_dashboard_config(dashboard_id, user)
            
            # Get data for all widgets
            dashboard_data = await self.report_repository.get_dashboard_data(dashboard_config, user)
            
            return {
                "dashboard_id": dashboard_id,
                "name": dashboard_config.name,
                "widgets": dashboard_data,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def execute_analytics_query(
        self,
        query: AnalyticsQuery,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Execute custom analytics query
        
        Args:
            query: Analytics query
            user: User executing query
            
        Returns:
            Query results
        """
        try:
            # Validate query permissions
            if not await self._has_query_permissions(query, user):
                raise PermissionDeniedError("Insufficient permissions for query")
            
            # Execute query
            results = await self.report_repository.get_analytics_query_result(query, user)
            
            # Add metadata
            results["executed_by"] = user.id
            results["executed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Executed analytics query '{query.query_name}' for user {user.id}")
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute analytics query: {e}")
            raise
    
    # Report Export and Sharing
    
    async def export_report(
        self,
        report_id: str,
        export_format: str,
        user: UserModel
    ) -> Tuple[BytesIO, str]:
        """
        Export report to specified format
        
        Args:
            report_id: Report ID
            export_format: Export format (pdf, csv, excel, etc.)
            user: User exporting report
            
        Returns:
            Tuple of (file_data, filename)
        """
        try:
            # Get report
            report = await self.get_report(report_id, user)
            
            # Generate export based on format
            if export_format.lower() == "pdf":
                file_data, filename = await self._export_to_pdf(report)
            elif export_format.lower() == "csv":
                file_data, filename = await self._export_to_csv(report)
            elif export_format.lower() == "excel":
                file_data, filename = await self._export_to_excel(report)
            elif export_format.lower() == "json":
                file_data, filename = await self._export_to_json(report)
            else:
                raise ValidationException(f"Unsupported export format: {export_format}")
            
            # Update download count
            await self._update_download_count(report_id)
            
            logger.info(f"Exported report {report_id} as {export_format} for user {user.id}")
            return file_data, filename
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            raise
    
    async def share_report(
        self,
        report_id: str,
        share_with_users: List[str],
        user: UserModel
    ) -> bool:
        """
        Share report with other users
        
        Args:
            report_id: Report ID
            share_with_users: List of user IDs to share with
            user: User sharing the report
            
        Returns:
            Success status
        """
        try:
            # Get report and check permissions
            report = await self.get_report(report_id, user)
            
            if report.requested_by != user.id and user.role != UserRoleEnum.ADMIN:
                raise PermissionDeniedError("No permission to share report")
            
            # Update shared users
            current_shared = set(report.shared_with)
            new_shared = current_shared.union(set(share_with_users))
            
            success = await self.report_repository.update(
                report_id,
                {"shared_with": list(new_shared)}
            )
            
            if success:
                logger.info(f"Shared report {report_id} with {len(share_with_users)} users")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to share report: {e}")
            raise
    
    # Background Processing
    
    async def _generate_report_background(
        self,
        report_id: str,
        report_request: ReportRequest,
        user: UserModel
    ):
        """
        Background task for report generation
        
        Args:
            report_id: Report ID
            report_request: Report request
            user: User who requested report
        """
        try:
            # Mark as generating
            await self.report_repository.update_report_status(
                report_id, ReportStatus.GENERATING
            )
            
            start_time = datetime.utcnow()
            
            # Generate report based on type
            if report_request.report_type == ReportType.PATIENT_SUMMARY:
                await self._generate_patient_summary_background(report_id, report_request, user)
            elif report_request.report_type == ReportType.EPISODE_REPORT:
                await self._generate_episode_background(report_id, report_request, user)
            elif report_request.report_type == ReportType.PRACTICE_ANALYTICS:
                await self._generate_practice_analytics_background(report_id, report_request, user)
            else:
                raise ValidationException(f"Unsupported report type: {report_request.report_type}")
            
            # Calculate generation time
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Mark as completed
            await self.report_repository.update_report_status(
                report_id, ReportStatus.COMPLETED
            )
            
            # Update generation time
            await self.report_repository.update(
                report_id,
                {"generation_time_seconds": generation_time}
            )
            
            # Log generation metrics
            logger.debug(f"Report generation complete - type: {report_request.report_type.value}, duration: {generation_time:.2f}s")
            
            logger.info(f"Completed report generation {report_id} in {generation_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to generate report {report_id}: {e}")
            
            # Mark as failed
            await self.report_repository.update_report_status(
                report_id, ReportStatus.FAILED, str(e)
            )
    
    # Private helper methods
    
    async def _validate_report_request(self, request: ReportRequest, user: UserModel):
        """Validate report request"""
        
        # Check date range
        if request.filters.date_from and request.filters.date_to:
            if request.filters.date_from > request.filters.date_to:
                raise ValidationException("Invalid date range")
        
        # Check permissions for scope
        if request.scope.value in ["organization", "system"] and user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
            raise PermissionDeniedError("Insufficient permissions for report scope")
    
    async def _has_report_access(self, report: ReportModel, user: UserModel) -> bool:
        """Check if user has access to report"""
        if report.requested_by == user.id:
            return True
        
        if user.id in report.shared_with:
            return True
        
        if user.role == UserRoleEnum.ADMIN:
            return True
        
        if report.is_public:
            return True
        
        return False
    
    async def _has_query_permissions(self, query: AnalyticsQuery, user: UserModel) -> bool:
        """Check if user has permissions to execute query"""
        if query.created_by == user.id:
            return True
        
        if user.id in query.allowed_users:
            return True
        
        if user.role == UserRoleEnum.ADMIN:
            return True
        
        return False
    
    async def _process_patient_summary_data(
        self,
        patient_data: Dict[str, Any],
        user: UserModel
    ) -> PatientSummaryReport:
        """Process raw patient data into summary report"""
        
        patient = patient_data["patient"]
        
        # Build demographics
        demographics = PatientDemographics(
            age=self._calculate_age(patient.get("demographics", {}).get("date_of_birth")),
            gender=patient.get("demographics", {}).get("gender"),
            # Add other demographic fields as available
        )
        
        # Create summary report
        report = PatientSummaryReport(
            patient_id=patient["id"],
            patient_name=patient.get("demographics", {}).get("name", ""),
            demographics=demographics,
            medical_history_summary=patient.get("medical_background", {}).get("past_medical_history", ""),
            active_conditions=patient_data.get("active_conditions", []),
            current_medications=patient_data.get("current_medications", []),
            recent_encounters=self._format_encounters_for_summary(patient_data.get("encounters", [])),
            upcoming_appointments=patient_data.get("upcoming_appointments", []),
            care_plans=patient_data.get("care_plans", []),
            lab_results_summary=patient_data.get("recent_lab_results", []),
            vital_signs_trends=patient_data.get("vital_signs_trends", []),
            clinical_alerts=await self._generate_clinical_alerts(patient_data),
            care_team=patient_data.get("care_team", []),
            generated_by=user.id
        )
        
        return report
    
    async def _process_episode_data(
        self,
        episode_data: Dict[str, Any],
        user: UserModel
    ) -> EpisodeReport:
        """Process raw episode data into episode report"""
        
        episode = episode_data["episode"]
        patient = episode_data["patient"]
        encounters = episode_data["encounters"]
        
        # Create episode report
        report = EpisodeReport(
            episode_id=episode["id"],
            patient_id=episode["patient_id"],
            episode_title=episode.get("chief_complaint", ""),
            start_date=episode.get("created_at").date() if episode.get("created_at") else date.today(),
            status=episode.get("status", ""),
            category=episode.get("category", ""),
            chief_complaint=episode.get("chief_complaint", ""),
            treatment_summary=episode.get("treatment_summary", ""),
            total_encounters=len(encounters),
            encounter_types_breakdown=episode_data.get("encounter_types", {}),
            encounters=self._format_encounters_for_episode(encounters),
            procedures_performed=episode_data.get("procedures", []),
            medications_prescribed=episode_data.get("medications", []),
            lab_tests_ordered=episode_data.get("lab_tests", []),
            imaging_studies=episode_data.get("imaging_studies", []),
            clinical_outcomes_achieved=await self._extract_clinical_outcomes(episode_data),
            total_cost=episode_data.get("cost_analysis", {}).get("total_cost"),
            generated_by=user.id
        )
        
        return report
    
    async def _process_practice_analytics_data(
        self,
        analytics_data: Dict[str, Any],
        filters: ReportFilter,
        user: UserModel
    ) -> PracticeAnalyticsReport:
        """Process raw analytics data into practice report"""
        
        # Create practice analytics report
        report = PracticeAnalyticsReport(
            practice_name="DiagnoAssist Practice",  # This would come from settings
            report_period=self._format_report_period(filters),
            period_start=filters.date_from or date.today() - timedelta(days=30),
            period_end=filters.date_to or date.today(),
            total_patients=analytics_data.get("patient_metrics", {}).get("total_patients", 0),
            new_patients=analytics_data.get("patient_metrics", {}).get("new_patients", 0),
            total_encounters=analytics_data.get("encounter_metrics", {}).get("total_encounters", 0),
            encounters_by_type=analytics_data.get("encounter_metrics", {}).get("encounter_types", {}),
            clinical_metrics=analytics_data.get("clinical_metrics", ClinicalMetrics()),
            financial_metrics=analytics_data.get("financial_metrics", FinancialMetrics()),
            utilization_metrics=analytics_data.get("utilization_metrics", UtilizationMetrics()),
            top_diagnoses=analytics_data.get("diagnostic_trends", []),
            medication_trends=analytics_data.get("medication_trends", []),
            quality_measures=analytics_data.get("quality_metrics", []),
            clinical_outcomes=analytics_data.get("outcome_analysis", []),
            provider_metrics=analytics_data.get("provider_metrics", []),
            generated_by=user.id
        )
        
        return report
    
    def _calculate_age(self, date_of_birth: Optional[str]) -> Optional[int]:
        """Calculate age from date of birth"""
        if not date_of_birth:
            return None
        
        try:
            from datetime import datetime
            dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            today = datetime.now(dob.tzinfo)
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except:
            return None
    
    def _format_encounters_for_summary(self, encounters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format encounters for patient summary"""
        return [{
            "id": enc.get("id"),
            "date": enc.get("created_at"),
            "type": enc.get("type"),
            "status": enc.get("status"),
            "chief_complaint": enc.get("soap", {}).get("subjective", {}).get("chief_complaint", "")
        } for enc in encounters[:10]]  # Last 10 encounters
    
    def _format_encounters_for_episode(self, encounters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format encounters for episode report"""
        return [{
            "id": enc.get("id"),
            "date": enc.get("created_at"),
            "type": enc.get("type"),
            "status": enc.get("status"),
            "provider": enc.get("provider", {}),
            "summary": self._generate_encounter_summary(enc)
        } for enc in encounters]
    
    def _generate_encounter_summary(self, encounter: Dict[str, Any]) -> str:
        """Generate summary for encounter"""
        soap = encounter.get("soap", {})
        assessment = soap.get("assessment", {}).get("primary_diagnosis", "")
        return assessment if assessment else "Assessment pending"
    
    async def _generate_clinical_alerts(self, patient_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate clinical alerts for patient"""
        alerts = []
        
        # Check for medication interactions
        medications = patient_data.get("current_medications", [])
        if len(medications) > 5:
            alerts.append({
                "type": "medication_alert",
                "severity": "medium",
                "message": "Patient is on multiple medications - review for interactions"
            })
        
        # Check for missing preventive care
        # This would be more sophisticated in a real implementation
        alerts.append({
            "type": "preventive_care",
            "severity": "low",
            "message": "Annual wellness visit due"
        })
        
        return alerts
    
    async def _extract_clinical_outcomes(self, episode_data: Dict[str, Any]) -> List[str]:
        """Extract clinical outcomes from episode data"""
        # This would analyze the episode data to determine outcomes
        return ["Symptom resolution", "Patient education completed"]
    
    def _format_report_period(self, filters: ReportFilter) -> str:
        """Format report period string"""
        if filters.date_from and filters.date_to:
            return f"{filters.date_from} to {filters.date_to}"
        elif filters.date_from:
            return f"From {filters.date_from}"
        elif filters.date_to:
            return f"Until {filters.date_to}"
        else:
            return "Last 30 days"
    
    async def _generate_practice_insights(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate insights from practice analytics"""
        insights = []
        
        # Patient volume insights
        patient_metrics = analytics_data.get("patient_metrics", {})
        total_patients = patient_metrics.get("total_patients", 0)
        new_patients = patient_metrics.get("new_patients", 0)
        
        if new_patients > 0:
            growth_rate = (new_patients / total_patients) * 100 if total_patients > 0 else 0
            insights.append(f"Patient base grew by {growth_rate:.1f}% this period")
        
        # Clinical quality insights
        clinical_metrics = analytics_data.get("clinical_metrics", {})
        if hasattr(clinical_metrics, 'patient_satisfaction_score') and clinical_metrics.patient_satisfaction_score:
            if clinical_metrics.patient_satisfaction_score >= 4.0:
                insights.append("Patient satisfaction scores are above average")
            else:
                insights.append("Patient satisfaction scores need improvement")
        
        return insights
    
    async def _generate_practice_recommendations(self, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations from practice analytics"""
        recommendations = []
        
        # Utilization recommendations
        utilization_metrics = analytics_data.get("utilization_metrics", {})
        if hasattr(utilization_metrics, 'appointment_no_show_rate') and utilization_metrics.appointment_no_show_rate:
            if utilization_metrics.appointment_no_show_rate > 10:
                recommendations.append("Consider implementing appointment reminder system to reduce no-show rate")
        
        # Quality recommendations
        recommendations.append("Continue monitoring clinical quality indicators")
        recommendations.append("Regular staff training on documentation best practices")
        
        return recommendations
    
    # Export helper methods
    
    async def _export_to_pdf(self, report: ReportModel) -> Tuple[BytesIO, str]:
        """Export report to PDF"""
        # This would use a PDF generation library like ReportLab
        pdf_content = f"Report: {report.title}\nGenerated: {report.generated_at}"
        
        buffer = BytesIO()
        buffer.write(pdf_content.encode())
        buffer.seek(0)
        
        filename = f"report_{report.id}.pdf"
        return buffer, filename
    
    async def _export_to_csv(self, report: ReportModel) -> Tuple[BytesIO, str]:
        """Export report to CSV"""
        # This would extract tabular data and create CSV
        csv_content = "Report Type,Generated Date,Status\n"
        csv_content += f"{report.report_type},{report.generated_at},{report.status}"
        
        buffer = BytesIO()
        buffer.write(csv_content.encode())
        buffer.seek(0)
        
        filename = f"report_{report.id}.csv"
        return buffer, filename
    
    async def _export_to_excel(self, report: ReportModel) -> Tuple[BytesIO, str]:
        """Export report to Excel"""
        # This would use openpyxl or similar library
        buffer = BytesIO()
        filename = f"report_{report.id}.xlsx"
        return buffer, filename
    
    async def _export_to_json(self, report: ReportModel) -> Tuple[BytesIO, str]:
        """Export report to JSON"""
        json_content = report.model_dump_json(indent=2)
        
        buffer = BytesIO()
        buffer.write(json_content.encode())
        buffer.seek(0)
        
        filename = f"report_{report.id}.json"
        return buffer, filename
    
    async def _update_download_count(self, report_id: str):
        """Update report download count"""
        try:
            await self.report_repository.update(
                report_id,
                {"$inc": {"download_count": 1}}
            )
        except Exception as e:
            logger.error(f"Failed to update download count: {e}")
    
    async def _get_dashboard_config(self, dashboard_id: str, user: UserModel) -> DashboardConfig:
        """Get dashboard configuration"""
        # This would retrieve dashboard config from database
        # For now, return a default config
        return DashboardConfig(
            id=dashboard_id,
            name="Default Dashboard",
            owner_id=user.id,
            widgets=[]
        )
    
    # Background generation methods
    
    async def _generate_patient_summary_background(
        self,
        report_id: str,
        request: ReportRequest,
        user: UserModel
    ):
        """Generate patient summary report in background"""
        # This would implement the actual patient summary generation
        pass
    
    async def _generate_episode_background(
        self,
        report_id: str,
        request: ReportRequest,
        user: UserModel
    ):
        """Generate episode report in background"""
        # This would implement the actual episode report generation
        pass
    
    async def _generate_practice_analytics_background(
        self,
        report_id: str,
        request: ReportRequest,
        user: UserModel
    ):
        """Generate practice analytics report in background"""
        # This would implement the actual practice analytics generation
        pass


# Service instance (to be initialized with dependencies)
report_service = None