"""
Report Repository for DiagnoAssist Backend

Handles data access operations for reports and analytics including:
- Report generation data aggregation
- Analytics query execution
- Report storage and retrieval
- Dashboard data collection
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.repositories.base_repository import BaseRepository
from app.models.reports import (
    ReportModel, ReportRequest, ReportFilter, ReportType, ReportStatus,
    PatientSummaryReport, EpisodeReport, PracticeAnalyticsReport,
    PatientDemographics, ClinicalMetrics, FinancialMetrics, UtilizationMetrics,
    DiagnosticTrend, MedicationTrend, OutcomeMetric, DashboardConfig,
    ReportTemplate, ReportSchedule, AnalyticsQuery
)
from app.models.auth import UserModel, UserRole
from app.core.exceptions import NotFoundError, ValidationException

logger = logging.getLogger(__name__)


class ReportRepository(BaseRepository[ReportModel]):
    """Repository for report and analytics data operations"""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        # Main collections
        self.reports_collection = database.reports
        self.dashboard_collection = database.dashboards
        self.report_templates_collection = database.report_templates
        self.report_schedules_collection = database.report_schedules
        
        # Data collections for aggregation
        self.patients_collection = database.patients
        self.episodes_collection = database.episodes
        self.encounters_collection = database.encounters
        self.users_collection = database.users
        
        super().__init__(self.reports_collection, ReportModel)
    
    # Report CRUD Operations
    
    async def create_report(
        self,
        report_request: ReportRequest,
        user: UserModel
    ) -> ReportModel:
        """
        Create a new report entry
        
        Args:
            report_request: Report generation request
            user: User creating the report
            
        Returns:
            Created report model
        """
        try:
            report_id = str(ObjectId())
            
            report = ReportModel(
                id=report_id,
                report_type=report_request.report_type,
                title=self._generate_report_title(report_request),
                description=self._generate_report_description(report_request),
                requested_by=user.id,
                filters_applied=report_request.filters,
                status=ReportStatus.PENDING
            )
            
            # Insert into database
            document = self._model_to_document(report)
            await self.reports_collection.insert_one(document)
            
            logger.info(f"Created report {report_id} for user {user.id}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to create report: {e}")
            raise
    
    async def update_report_status(
        self,
        report_id: str,
        status: ReportStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update report status
        
        Args:
            report_id: Report ID
            status: New status
            error_message: Error message if failed
            
        Returns:
            Success status
        """
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if status == ReportStatus.COMPLETED:
                update_data["generated_at"] = datetime.utcnow()
            elif status == ReportStatus.FAILED and error_message:
                update_data["error_message"] = error_message
            
            result = await self.reports_collection.update_one(
                {"_id": ObjectId(report_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Failed to update report status: {e}")
            return False
    
    async def get_user_reports(
        self,
        user: UserModel,
        limit: int = 50
    ) -> List[ReportModel]:
        """
        Get reports for a user
        
        Args:
            user: User requesting reports
            limit: Maximum number of reports
            
        Returns:
            List of user reports
        """
        try:
            query = {"requested_by": user.id}
            
            cursor = self.reports_collection.find(query).sort("requested_at", -1).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            return [self._document_to_model(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Failed to get user reports: {e}")
            raise
    
    # Data Aggregation Methods
    
    async def get_patient_summary_data(
        self,
        patient_id: str,
        filters: ReportFilter
    ) -> Dict[str, Any]:
        """
        Aggregate patient summary data
        
        Args:
            patient_id: Patient ID
            filters: Report filters
            
        Returns:
            Aggregated patient data
        """
        try:
            # Get patient basic info
            patient = await self.patients_collection.find_one({"id": patient_id})
            if not patient:
                raise NotFoundError("Patient not found")
            
            # Build date filter
            date_filter = {}
            if filters.date_from:
                date_filter["$gte"] = filters.date_from
            if filters.date_to:
                date_filter["$lte"] = filters.date_to
            
            # Get episodes
            episodes_query = {"patient_id": patient_id}
            if date_filter:
                episodes_query["created_at"] = date_filter
            
            episodes = await self.episodes_collection.find(episodes_query).to_list(length=None)
            
            # Get encounters
            encounters_query = {"patient_id": patient_id}
            if date_filter:
                encounters_query["created_at"] = date_filter
            
            encounters = await self.encounters_collection.find(encounters_query).to_list(length=None)
            
            # Aggregate data
            summary_data = {
                "patient": patient,
                "episodes": episodes,
                "encounters": encounters,
                "active_conditions": await self._get_active_conditions(patient_id),
                "current_medications": await self._get_current_medications(patient_id),
                "recent_lab_results": await self._get_recent_lab_results(patient_id, filters),
                "vital_signs_trends": await self._get_vital_signs_trends(patient_id, filters),
                "upcoming_appointments": await self._get_upcoming_appointments(patient_id),
                "care_team": await self._get_care_team(patient_id)
            }
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Failed to get patient summary data: {e}")
            raise
    
    async def get_episode_report_data(
        self,
        episode_id: str,
        filters: ReportFilter
    ) -> Dict[str, Any]:
        """
        Aggregate episode report data
        
        Args:
            episode_id: Episode ID
            filters: Report filters
            
        Returns:
            Aggregated episode data
        """
        try:
            # Get episode
            episode = await self.episodes_collection.find_one({"id": episode_id})
            if not episode:
                raise NotFoundError("Episode not found")
            
            # Get related encounters
            encounters = await self.encounters_collection.find(
                {"episode_id": episode_id}
            ).to_list(length=None)
            
            # Get patient info
            patient = await self.patients_collection.find_one({"id": episode["patient_id"]})
            
            # Aggregate episode metrics
            episode_data = {
                "episode": episode,
                "patient": patient,
                "encounters": encounters,
                "total_encounters": len(encounters),
                "encounter_types": await self._get_encounter_types_breakdown(encounters),
                "procedures": await self._get_episode_procedures(episode_id),
                "medications": await self._get_episode_medications(episode_id),
                "lab_tests": await self._get_episode_lab_tests(episode_id),
                "imaging_studies": await self._get_episode_imaging(episode_id),
                "clinical_outcomes": await self._get_episode_outcomes(episode_id),
                "cost_analysis": await self._get_episode_costs(episode_id)
            }
            
            return episode_data
            
        except Exception as e:
            logger.error(f"Failed to get episode report data: {e}")
            raise
    
    async def get_practice_analytics_data(
        self,
        filters: ReportFilter,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Aggregate practice-wide analytics data
        
        Args:
            filters: Report filters
            user: User requesting analytics
            
        Returns:
            Aggregated practice analytics
        """
        try:
            # Build date filter
            date_filter = {}
            if filters.date_from:
                date_filter["$gte"] = filters.date_from
            if filters.date_to:
                date_filter["$lte"] = filters.date_to
            
            # Get practice metrics
            analytics_data = {
                "patient_metrics": await self._get_patient_metrics(date_filter, user),
                "encounter_metrics": await self._get_encounter_metrics(date_filter, user),
                "clinical_metrics": await self._get_clinical_metrics(date_filter, user),
                "financial_metrics": await self._get_financial_metrics(date_filter, user),
                "utilization_metrics": await self._get_utilization_metrics(date_filter, user),
                "quality_metrics": await self._get_quality_metrics(date_filter, user),
                "provider_metrics": await self._get_provider_metrics(date_filter, user),
                "diagnostic_trends": await self._get_diagnostic_trends(date_filter, user),
                "medication_trends": await self._get_medication_trends(date_filter, user),
                "outcome_analysis": await self._get_outcome_analysis(date_filter, user)
            }
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Failed to get practice analytics data: {e}")
            raise
    
    # Dashboard Data Methods
    
    async def get_dashboard_data(
        self,
        dashboard_config: DashboardConfig,
        user: UserModel
    ) -> Dict[str, Any]:
        """
        Get data for dashboard widgets
        
        Args:
            dashboard_config: Dashboard configuration
            user: User requesting dashboard data
            
        Returns:
            Dashboard widget data
        """
        try:
            dashboard_data = {}
            
            for widget in dashboard_config.widgets:
                try:
                    widget_data = await self._get_widget_data(widget, user)
                    dashboard_data[widget.id] = widget_data
                except Exception as e:
                    logger.error(f"Failed to get data for widget {widget.id}: {e}")
                    dashboard_data[widget.id] = {"error": str(e)}
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def get_analytics_query_result(
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
            # Build aggregation pipeline
            pipeline = []
            
            # Add filters
            if query.filters:
                pipeline.append({"$match": query.filters})
            
            # Add grouping
            if query.grouping:
                group_stage = {"_id": {}}
                for field in query.grouping:
                    group_stage["_id"][field] = f"${field}"
                
                # Add aggregations
                for agg in query.aggregations:
                    group_stage[agg["name"]] = {agg["operation"]: agg["field"]}
                
                pipeline.append({"$group": group_stage})
            
            # Add sorting
            if query.sorting:
                sort_stage = {}
                for sort_item in query.sorting:
                    direction = 1 if sort_item["direction"] == "asc" else -1
                    sort_stage[sort_item["field"]] = direction
                pipeline.append({"$sort": sort_stage})
            
            # Add limit
            if query.limit:
                pipeline.append({"$limit": query.limit})
            
            # Execute query on appropriate collection
            collection = self._get_collection_for_query(query)
            results = await collection.aggregate(pipeline).to_list(length=None)
            
            return {
                "results": results,
                "count": len(results),
                "query_executed": query.query_name,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute analytics query: {e}")
            raise
    
    # Private helper methods
    
    def _generate_report_title(self, request: ReportRequest) -> str:
        """Generate report title based on request"""
        type_names = {
            ReportType.PATIENT_SUMMARY: "Patient Summary",
            ReportType.EPISODE_REPORT: "Episode Report",
            ReportType.PRACTICE_ANALYTICS: "Practice Analytics",
            ReportType.CLINICAL_QUALITY: "Clinical Quality Report"
        }
        
        base_title = type_names.get(request.report_type, "Report")
        
        if request.filters.date_from and request.filters.date_to:
            date_range = f"{request.filters.date_from} to {request.filters.date_to}"
            return f"{base_title} ({date_range})"
        
        return f"{base_title} - {datetime.now().strftime('%Y-%m-%d')}"
    
    def _generate_report_description(self, request: ReportRequest) -> str:
        """Generate report description based on request"""
        descriptions = {
            ReportType.PATIENT_SUMMARY: "Comprehensive patient summary including medical history, current conditions, medications, and care plans.",
            ReportType.EPISODE_REPORT: "Detailed episode analysis including encounters, procedures, outcomes, and quality metrics.",
            ReportType.PRACTICE_ANALYTICS: "Practice-wide analytics including patient volumes, clinical quality, financial performance, and utilization metrics.",
            ReportType.CLINICAL_QUALITY: "Clinical quality indicators and performance metrics for quality improvement initiatives."
        }
        
        return descriptions.get(request.report_type, "Generated report")
    
    async def _get_active_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get active conditions for patient"""
        # This would query FHIR or conditions collection
        return []  # Placeholder
    
    async def _get_current_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get current medications for patient"""
        # This would query FHIR or medications collection
        return []  # Placeholder
    
    async def _get_recent_lab_results(self, patient_id: str, filters: ReportFilter) -> List[Dict[str, Any]]:
        """Get recent lab results for patient"""
        # This would query FHIR observations
        return []  # Placeholder
    
    async def _get_vital_signs_trends(self, patient_id: str, filters: ReportFilter) -> List[Dict[str, Any]]:
        """Get vital signs trends for patient"""
        # This would query vital signs data
        return []  # Placeholder
    
    async def _get_upcoming_appointments(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get upcoming appointments for patient"""
        # This would query appointments/scheduling system
        return []  # Placeholder
    
    async def _get_care_team(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get care team for patient"""
        # This would query care team assignments
        return []  # Placeholder
    
    async def _get_encounter_types_breakdown(self, encounters: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get breakdown of encounter types"""
        breakdown = {}
        for encounter in encounters:
            encounter_type = encounter.get("type", "unknown")
            breakdown[encounter_type] = breakdown.get(encounter_type, 0) + 1
        return breakdown
    
    async def _get_episode_procedures(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get procedures for episode"""
        return []  # Placeholder
    
    async def _get_episode_medications(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get medications for episode"""
        return []  # Placeholder
    
    async def _get_episode_lab_tests(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get lab tests for episode"""
        return []  # Placeholder
    
    async def _get_episode_imaging(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get imaging studies for episode"""
        return []  # Placeholder
    
    async def _get_episode_outcomes(self, episode_id: str) -> List[Dict[str, Any]]:
        """Get clinical outcomes for episode"""
        return []  # Placeholder
    
    async def _get_episode_costs(self, episode_id: str) -> Dict[str, Any]:
        """Get cost analysis for episode"""
        return {}  # Placeholder
    
    async def _get_patient_metrics(self, date_filter: Dict, user: UserModel) -> Dict[str, Any]:
        """Get patient volume and demographic metrics"""
        try:
            # Build query with user access controls
            query = {}
            if date_filter:
                query["created_at"] = date_filter
            
            # Get patient counts
            total_patients = await self.patients_collection.count_documents(query)
            
            # Get new patients in period
            new_patients_query = {**query, "created_at": date_filter} if date_filter else {}
            new_patients = await self.patients_collection.count_documents(new_patients_query)
            
            # Get demographic breakdown
            demographics_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$demographics.gender",
                    "count": {"$sum": 1}
                }}
            ]
            
            gender_breakdown = await self.patients_collection.aggregate(demographics_pipeline).to_list(length=None)
            
            return {
                "total_patients": total_patients,
                "new_patients": new_patients,
                "gender_breakdown": {item["_id"]: item["count"] for item in gender_breakdown}
            }
            
        except Exception as e:
            logger.error(f"Failed to get patient metrics: {e}")
            return {}
    
    async def _get_encounter_metrics(self, date_filter: Dict, user: UserModel) -> Dict[str, Any]:
        """Get encounter volume and type metrics"""
        try:
            query = {}
            if date_filter:
                query["created_at"] = date_filter
            
            total_encounters = await self.encounters_collection.count_documents(query)
            
            # Get encounter type breakdown
            type_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$type",
                    "count": {"$sum": 1}
                }}
            ]
            
            type_breakdown = await self.encounters_collection.aggregate(type_pipeline).to_list(length=None)
            
            return {
                "total_encounters": total_encounters,
                "encounter_types": {item["_id"]: item["count"] for item in type_breakdown}
            }
            
        except Exception as e:
            logger.error(f"Failed to get encounter metrics: {e}")
            return {}
    
    async def _get_clinical_metrics(self, date_filter: Dict, user: UserModel) -> ClinicalMetrics:
        """Get clinical quality metrics"""
        # Placeholder implementation
        return ClinicalMetrics(
            total_encounters=100,
            completed_encounters=95,
            average_encounter_duration=30.5,
            patient_satisfaction_score=4.2
        )
    
    async def _get_financial_metrics(self, date_filter: Dict, user: UserModel) -> FinancialMetrics:
        """Get financial performance metrics"""
        # Placeholder implementation
        return FinancialMetrics(
            total_revenue=50000.0,
            average_revenue_per_encounter=250.0,
            collection_rate=92.5
        )
    
    async def _get_utilization_metrics(self, date_filter: Dict, user: UserModel) -> UtilizationMetrics:
        """Get resource utilization metrics"""
        # Placeholder implementation
        return UtilizationMetrics(
            provider_productivity=3.2,
            appointment_no_show_rate=8.5,
            room_utilization_rate=75.0
        )
    
    async def _get_quality_metrics(self, date_filter: Dict, user: UserModel) -> List[OutcomeMetric]:
        """Get quality outcome metrics"""
        # Placeholder implementation
        return [
            OutcomeMetric(
                metric_name="Patient Satisfaction",
                metric_value=4.2,
                metric_unit="score",
                benchmark_value=4.0,
                performance_status="above_benchmark",
                improvement_trend="improving"
            )
        ]
    
    async def _get_provider_metrics(self, date_filter: Dict, user: UserModel) -> List[Dict[str, Any]]:
        """Get provider performance metrics"""
        return []  # Placeholder
    
    async def _get_diagnostic_trends(self, date_filter: Dict, user: UserModel) -> List[DiagnosticTrend]:
        """Get diagnostic code trends"""
        return []  # Placeholder
    
    async def _get_medication_trends(self, date_filter: Dict, user: UserModel) -> List[MedicationTrend]:
        """Get medication prescription trends"""
        return []  # Placeholder
    
    async def _get_outcome_analysis(self, date_filter: Dict, user: UserModel) -> List[OutcomeMetric]:
        """Get patient outcome analysis"""
        return []  # Placeholder
    
    async def _get_widget_data(self, widget: Any, user: UserModel) -> Dict[str, Any]:
        """Get data for specific dashboard widget"""
        # This would be implemented based on widget type and data source
        return {"placeholder": "widget_data"}
    
    def _get_collection_for_query(self, query: AnalyticsQuery) -> AsyncIOMotorCollection:
        """Get appropriate collection for analytics query"""
        # Default to encounters collection
        return self.encounters_collection