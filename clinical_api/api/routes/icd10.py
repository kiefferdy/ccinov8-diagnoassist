"""
ICD-10 related API endpoints
"""

import time
from fastapi import APIRouter, Query, HTTPException

from clinical_api.models.icd10 import ICD10Code, ICD10SearchResponse, CategoriesResponse
from clinical_api.services.icd10_service import ICD10Service
from clinical_api.config import DEFAULT_SEARCH_LIMIT, MAX_SEARCH_LIMIT, MIN_QUERY_LENGTH

router = APIRouter(prefix="/icd10", tags=["ICD-10"])


@router.get("", response_model=ICD10SearchResponse)
async def search_icd10_codes(
    q: str = Query(..., min_length=MIN_QUERY_LENGTH, description="Search query for ICD-10 codes"),
    limit: int = Query(default=DEFAULT_SEARCH_LIMIT, ge=1, le=MAX_SEARCH_LIMIT, description="Maximum number of results")
):
    """
    Search ICD-10 codes by query string
    
    - **q**: Search query (diagnosis name, code, or keywords)
    - **limit**: Maximum number of results to return (1-50)
    
    Returns matching ICD-10 codes with relevance-based ordering.
    """
    start_time = time.time()
    
    try:
        results = ICD10Service.search_codes(q, limit)
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return ICD10SearchResponse(
            codes=results,
            total_results=len(results),
            query=q,
            search_time_ms=round(search_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/{code}", response_model=ICD10Code)
async def get_icd10_code(code: str):
    """
    Get a specific ICD-10 code by exact match
    
    - **code**: The exact ICD-10 code (e.g., "I21.9")
    """
    result = ICD10Service.get_code_by_exact_match(code)
    if not result:
        raise HTTPException(status_code=404, detail=f"ICD-10 code '{code}' not found")
    return result


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """Get all available ICD-10 categories"""
    categories = ICD10Service.get_all_categories()
    return CategoriesResponse(categories=categories)