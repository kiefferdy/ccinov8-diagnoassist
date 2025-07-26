"""
Reports API endpoints for DiagnoAssist Backend

REST endpoints for reporting and analytics:
- Report generation and management
- Analytics queries and dashboards
- Report export and sharing
- Scheduled reports
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path, Response
from fastapi.responses import StreamingResponse
from datetime import datetime, date
from io import BytesIO

from app.models.auth import UserModel, UserRoleEnum
from app.models.reports import (
    ReportModel, ReportRequest, ReportFilter, ReportType, ReportStatus,
    ReportScope, ReportFormat, PatientSummaryReport, EpisodeReport,
    PracticeAnalyticsReport, DashboardConfig, AnalyticsQuery
)
from app.middleware.auth_middleware import get_current_user, require_admin
from app.services.report_service import report_service
from app.core.exceptions import ValidationException, NotFoundError, PermissionDeniedError

logger = logging.getLogger(__name__)

router = APIRouter()


# Report Generation and Management

@router.post("/generate", response_model=dict)
async def generate_report(
    report_request: ReportRequest = Body(..., description="Report generation request"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate a new report
    
    Args:
        report_request: Report generation parameters
        current_user: Authenticated user
        
    Returns:
        Report generation status
    """
    try:
        report = await report_service.generate_report(report_request, current_user)
        
        return {
            "success": True,
            "data": {
                "report_id": report.id,
                "report_type": report.report_type.value,
                "status": report.status.value,
                "estimated_completion": "2-5 minutes",
                "requested_at": report.requested_at.isoformat()
            },
            "message": "Report generation started",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/{report_id}", response_model=dict)
async def get_report(
    report_id: str = Path(..., description="Report ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get report by ID
    
    Args:
        report_id: Report ID
        current_user: Authenticated user
        
    Returns:
        Report data
    """
    try:
        report = await report_service.get_report(report_id, current_user)
        
        return {
            "success": True,
            "data": report.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get report")


@router.get("/", response_model=dict)
async def get_user_reports(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of reports"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get reports for current user
    
    Args:
        limit: Maximum number of reports
        report_type: Filter by report type
        status: Filter by status
        current_user: Authenticated user
        
    Returns:
        List of user reports
    """
    try:
        reports = await report_service.get_user_reports(current_user, limit)
        
        # Apply filters
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        if status:
            reports = [r for r in reports if r.status == status]
        
        return {
            "success": True,
            "data": {
                "reports": [report.model_dump() for report in reports],
                "count": len(reports)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")


@router.delete("/{report_id}", response_model=dict)
async def delete_report(
    report_id: str = Path(..., description="Report ID"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete report
    
    Args:
        report_id: Report ID
        current_user: Authenticated user
        
    Returns:
        Deletion confirmation
    """
    try:
        success = await report_service.delete_report(report_id, current_user)
        
        return {
            "success": success,
            "data": {
                "report_id": report_id,
                "deleted_at": datetime.utcnow().isoformat()
            },
            "message": "Report deleted successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete report")


# Specific Report Types

@router.post("/patient-summary", response_model=dict)
async def generate_patient_summary(
    patient_id: str = Body(..., description="Patient ID"),
    filters: ReportFilter = Body(default_factory=ReportFilter, description="Report filters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate patient summary report
    
    Args:
        patient_id: Patient ID
        filters: Report filters
        current_user: Authenticated user
        
    Returns:
        Patient summary report
    """
    try:
        report = await report_service.generate_patient_summary_report(
            patient_id, filters, current_user
        )
        
        return {
            "success": True,
            "data": report.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate patient summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate patient summary")


@router.post("/episode-report", response_model=dict)
async def generate_episode_report(
    episode_id: str = Body(..., description="Episode ID"),
    filters: ReportFilter = Body(default_factory=ReportFilter, description="Report filters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate episode report
    
    Args:
        episode_id: Episode ID
        filters: Report filters
        current_user: Authenticated user
        
    Returns:
        Episode report
    """
    try:
        report = await report_service.generate_episode_report(
            episode_id, filters, current_user
        )
        
        return {
            "success": True,
            "data": report.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate episode report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate episode report")


@router.post("/practice-analytics", response_model=dict)
async def generate_practice_analytics(
    filters: ReportFilter = Body(..., description="Report filters"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate practice analytics report
    
    Args:
        filters: Report filters
        current_user: Authenticated user
        
    Returns:
        Practice analytics report
    """
    try:
        # Check permissions for practice-wide analytics
        if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
            raise PermissionDeniedError("Insufficient permissions for practice analytics")
        
        report = await report_service.generate_practice_analytics_report(
            filters, current_user
        )
        
        return {
            "success": True,
            "data": report.model_dump(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to generate practice analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate practice analytics")


# Dashboard and Analytics

@router.get("/dashboard/{dashboard_id}", response_model=dict)
async def get_dashboard_data(
    dashboard_id: str = Path(..., description="Dashboard ID"),
    refresh: bool = Query(False, description="Force refresh data"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get dashboard data
    
    Args:
        dashboard_id: Dashboard ID
        refresh: Force refresh data
        current_user: Authenticated user
        
    Returns:
        Dashboard data
    """
    try:
        dashboard_data = await report_service.get_dashboard_data(dashboard_id, current_user)
        
        return {
            "success": True,
            "data": dashboard_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")


@router.post("/analytics/query", response_model=dict)
async def execute_analytics_query(
    query: AnalyticsQuery = Body(..., description="Analytics query"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Execute custom analytics query
    
    Args:
        query: Analytics query
        current_user: Authenticated user
        
    Returns:
        Query results
    """
    try:
        results = await report_service.execute_analytics_query(query, current_user)
        
        return {
            "success": True,
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute analytics query: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute query")


# Report Export and Sharing

@router.get("/{report_id}/export", response_class=StreamingResponse)
async def export_report(
    report_id: str = Path(..., description="Report ID"),
    format: ReportFormat = Query(ReportFormat.PDF, description="Export format"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Export report to specified format
    
    Args:
        report_id: Report ID
        format: Export format
        current_user: Authenticated user
        
    Returns:
        Report file
    """
    try:
        file_data, filename = await report_service.export_report(
            report_id, format.value, current_user
        )
        
        # Determine content type
        content_types = {
            "pdf": "application/pdf",
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json"
        }
        
        content_type = content_types.get(format.value, "application/octet-stream")
        
        return StreamingResponse(
            BytesIO(file_data.getvalue()),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to export report: {e}")
        raise HTTPException(status_code=500, detail="Failed to export report")


@router.post("/{report_id}/share", response_model=dict)
async def share_report(
    report_id: str = Path(..., description="Report ID"),
    share_with_users: List[str] = Body(..., description="User IDs to share with"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Share report with other users
    
    Args:
        report_id: Report ID
        share_with_users: List of user IDs to share with
        current_user: Authenticated user
        
    Returns:
        Sharing confirmation
    """
    try:
        success = await report_service.share_report(
            report_id, share_with_users, current_user
        )
        
        return {
            "success": success,
            "data": {
                "report_id": report_id,
                "shared_with": share_with_users,
                "shared_at": datetime.utcnow().isoformat(),
                "shared_by": current_user.name
            },
            "message": f"Report shared with {len(share_with_users)} users",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to share report: {e}")
        raise HTTPException(status_code=500, detail="Failed to share report")


# Quick Analytics Endpoints

@router.get("/quick/patient-stats", response_model=dict)
async def get_patient_quick_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get quick patient statistics
    
    Args:
        days: Number of days to analyze
        current_user: Authenticated user
        
    Returns:
        Quick patient statistics
    """
    try:
        # Build filters for the time period
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        filters = ReportFilter(
            date_from=start_date,
            date_to=end_date
        )
        
        # Generate quick analytics
        analytics_data = await report_service.report_repository.get_practice_analytics_data(
            filters, current_user
        )
        
        patient_metrics = analytics_data.get("patient_metrics", {})
        encounter_metrics = analytics_data.get("encounter_metrics", {})
        
        return {
            "success": True,
            "data": {
                "period": f"Last {days} days",
                "total_patients": patient_metrics.get("total_patients", 0),
                "new_patients": patient_metrics.get("new_patients", 0),
                "total_encounters": encounter_metrics.get("total_encounters", 0),
                "encounter_types": encounter_metrics.get("encounter_types", {}),
                "generated_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get patient quick stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


@router.get("/quick/clinical-metrics", response_model=dict)
async def get_clinical_quick_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get quick clinical quality metrics
    
    Args:
        days: Number of days to analyze
        current_user: Authenticated user
        
    Returns:
        Quick clinical metrics
    """
    try:
        # Check permissions
        if current_user.role not in [UserRoleEnum.ADMIN, UserRoleEnum.DOCTOR]:
            raise PermissionDeniedError("Insufficient permissions for clinical metrics")
        
        # Build filters
        from datetime import timedelta
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        filters = ReportFilter(
            date_from=start_date,
            date_to=end_date
        )
        
        # Get clinical metrics
        analytics_data = await report_service.report_repository.get_practice_analytics_data(
            filters, current_user
        )
        
        clinical_metrics = analytics_data.get("clinical_metrics", {})
        
        return {
            "success": True,
            "data": {
                "period": f"Last {days} days",
                "clinical_metrics": clinical_metrics.model_dump() if hasattr(clinical_metrics, 'model_dump') else clinical_metrics,
                "quality_indicators": analytics_data.get("quality_metrics", []),
                "generated_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get clinical quick metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get clinical metrics")


# Report Templates

@router.get("/templates", response_model=dict)
async def get_report_templates(
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get available report templates
    
    Args:
        report_type: Filter by report type
        current_user: Authenticated user
        
    Returns:
        List of report templates
    """
    try:
        # This would get actual templates from database
        # For now, return predefined templates
        templates = [
            {
                "id": "patient_summary_standard",
                "name": "Standard Patient Summary",
                "description": "Comprehensive patient summary with medical history, current conditions, and care plans",
                "report_type": "patient_summary",
                "is_system_template": True
            },
            {
                "id": "episode_analysis_standard",
                "name": "Standard Episode Analysis",
                "description": "Detailed episode analysis with outcomes and quality metrics",
                "report_type": "episode_report",
                "is_system_template": True
            },
            {
                "id": "practice_dashboard_monthly",
                "name": "Monthly Practice Dashboard",
                "description": "Monthly practice analytics with key performance indicators",
                "report_type": "practice_analytics",
                "is_system_template": True
            }
        ]
        
        # Apply filter
        if report_type:
            templates = [t for t in templates if t["report_type"] == report_type.value]
        
        return {
            "success": True,
            "data": {
                "templates": templates,
                "count": len(templates)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get report templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


# Admin Endpoints

@router.get("/admin/all", response_model=dict)
async def get_all_reports_admin(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    report_type: Optional[ReportType] = Query(None, description="Filter by report type"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    current_user: UserModel = Depends(require_admin)
):
    """
    Get all reports (Admin only)
    
    Args:
        page: Page number
        limit: Items per page
        report_type: Filter by report type
        status: Filter by status
        current_user: Authenticated admin user
        
    Returns:
        All reports with pagination
    """
    try:
        # This would implement pagination and filtering in repository
        # For now, get user reports as placeholder
        reports = await report_service.get_user_reports(current_user, limit)
        
        return {
            "success": True,
            "data": {
                "reports": [report.model_dump() for report in reports],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": len(reports),
                    "total_pages": 1,
                    "has_next": False,
                    "has_prev": False
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get all reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports")


@router.get("/admin/stats", response_model=dict)
async def get_reporting_stats_admin(
    current_user: UserModel = Depends(require_admin)
):
    """
    Get reporting system statistics (Admin only)
    
    Args:
        current_user: Authenticated admin user
        
    Returns:
        Reporting system statistics
    """
    try:
        # This would get actual stats from database
        stats = {
            "total_reports_generated": 1250,
            "reports_today": 45,
            "average_generation_time": 3.2,
            "most_popular_report_type": "patient_summary",
            "total_exports": 890,
            "unique_report_users": 125,
            "report_types_breakdown": {
                "patient_summary": 450,
                "episode_report": 320,
                "practice_analytics": 280,
                "clinical_quality": 200
            },
            "generation_success_rate": 97.8
        }
        
        return {
            "success": True,
            "data": {
                "reporting_statistics": stats,
                "generated_at": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get reporting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Health Check

@router.get("/health", response_model=dict)
async def reporting_health_check():
    """
    Health check for reporting service
    
    Returns:
        Reporting service health status
    """
    try:
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "report_service": "operational",
                "features": [
                    "report_generation",
                    "analytics_queries",
                    "dashboard_data",
                    "report_export",
                    "report_sharing"
                ],
                "supported_formats": ["pdf", "csv", "excel", "json"],
                "supported_report_types": [rt.value for rt in ReportType]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Reporting health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.utcnow().isoformat()
        }