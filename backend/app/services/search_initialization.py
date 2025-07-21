"""
Search Service Initialization for DiagnoAssist Backend

Initializes the search service with dependencies and creates search indexes
"""
import logging

from app.services.search_service import SearchService
from app.repositories.search_repository import SearchRepository

logger = logging.getLogger(__name__)


async def initialize_search_service_with_dependencies():
    """Initialize search service with all dependencies"""
    try:
        from app.core.database import get_database
        from app.services.search_service import search_service as global_search_service
        
        # Get database
        db = await get_database()
        
        # Create repository
        search_repository = SearchRepository(db)
        
        # Create service
        search_service_instance = SearchService(search_repository)
        
        # Set global service instance
        import app.services.search_service
        app.services.search_service.search_service = search_service_instance
        
        # Initialize search indexes
        await initialize_search_indexes(db)
        
        logger.info("Search service initialized successfully")
        return search_service_instance
        
    except Exception as e:
        logger.error(f"Failed to initialize search service: {e}")
        raise


async def initialize_search_indexes(db):
    """Initialize search indexes for all collections"""
    try:
        # Create text indexes for full-text search
        
        # Patients collection indexes
        try:
            await db.patients.create_index([
                ("demographics.name", "text"),
                ("demographics.email", "text"),
                ("medical_background.past_medical_history", "text"),
                ("id", "text")
            ], name="patients_text_index")
        except Exception as e:
            logger.debug(f"Patients text index may already exist: {e}")
        
        # Episodes collection indexes
        try:
            await db.episodes.create_index([
                ("chief_complaint", "text"),
                ("category", "text"),
                ("id", "text")
            ], name="episodes_text_index")
        except Exception as e:
            logger.debug(f"Episodes text index may already exist: {e}")
        
        # Encounters collection indexes
        try:
            await db.encounters.create_index([
                ("soap.subjective.chief_complaint", "text"),
                ("soap.assessment.primary_diagnosis", "text"),
                ("id", "text")
            ], name="encounters_text_index")
        except Exception as e:
            logger.debug(f"Encounters text index may already exist: {e}")
        
        # Templates collection indexes
        try:
            await db.templates.create_index([
                ("name", "text"),
                ("description", "text"),
                ("tags", "text")
            ], name="templates_text_index")
        except Exception as e:
            logger.debug(f"Templates text index may already exist: {e}")
        
        # Reports collection indexes
        try:
            await db.reports.create_index([
                ("title", "text"),
                ("description", "text")
            ], name="reports_text_index")
        except Exception as e:
            logger.debug(f"Reports text index may already exist: {e}")
        
        # Users collection indexes
        try:
            await db.users.create_index([
                ("name", "text"),
                ("email", "text")
            ], name="users_text_index")
        except Exception as e:
            logger.debug(f"Users text index may already exist: {e}")
        
        # Create additional indexes for search optimization
        
        # Patients - searchable fields
        await db.patients.create_index("demographics.name")
        await db.patients.create_index("demographics.email")
        await db.patients.create_index("is_active")
        await db.patients.create_index("created_at")
        
        # Episodes - searchable fields
        await db.episodes.create_index("patient_id")
        await db.episodes.create_index("status")
        await db.episodes.create_index("category")
        await db.episodes.create_index("created_at")
        
        # Encounters - searchable fields
        await db.encounters.create_index("patient_id")
        await db.encounters.create_index("episode_id")
        await db.encounters.create_index("type")
        await db.encounters.create_index("status")
        await db.encounters.create_index("created_at")
        
        # Templates - searchable fields
        await db.templates.create_index("owner_id")
        await db.templates.create_index("scope")
        await db.templates.create_index("category")
        await db.templates.create_index("template_type")
        await db.templates.create_index("is_active")
        await db.templates.create_index("is_published")
        await db.templates.create_index("metadata.created_at")
        await db.templates.create_index("metadata.usage_count")
        
        # Reports - searchable fields
        await db.reports.create_index("requested_by")
        await db.reports.create_index("report_type")
        await db.reports.create_index("status")
        await db.reports.create_index("requested_at")
        await db.reports.create_index("shared_with")
        
        # Search-specific collections
        
        # Search history indexes
        await db.search_history.create_index("user_id")
        await db.search_history.create_index("searched_at")
        await db.search_history.create_index([("query", "text")])
        
        # Saved searches indexes
        await db.saved_searches.create_index("created_by")
        await db.saved_searches.create_index("is_public")
        await db.saved_searches.create_index("shared_with")
        await db.saved_searches.create_index("created_at")
        await db.saved_searches.create_index("usage_count")
        
        logger.info("Search indexes initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize search indexes: {e}")
        # Don't raise - allow app to start without perfect indexes