"""
Report Service Initialization for DiagnoAssist Backend

Initializes the report service with dependencies
"""
import logging

from app.services.report_service import ReportService
from app.repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


async def initialize_report_service_with_dependencies():
    """Initialize report service with all dependencies"""
    try:
        from app.core.database import get_database
        from app.services.report_service import report_service as global_report_service
        
        # Get database
        db = await get_database()
        
        # Create repository
        report_repository = ReportRepository(db)
        
        # Create service
        report_service_instance = ReportService(report_repository)
        
        # Set global service instance
        import app.services.report_service
        app.services.report_service.report_service = report_service_instance
        
        logger.info("Report service initialized successfully")
        return report_service_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize report service: {e}")
        raise