"""
Business logic for ICD-10 operations
"""

from typing import List, Optional

from clinical_api.models.icd10 import ICD10Code
from clinical_api.database.connection import execute_query
from clinical_api.config import MIN_WORD_LENGTH


class ICD10Service:
    """Service class for ICD-10 code operations"""
    
    @staticmethod
    def search_codes(query: str, limit: int = 10) -> List[ICD10Code]:
        """Search ICD-10 codes by query string"""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.lower().strip()
        results = []
        
        # 1. Exact code match (highest priority)
        exact_matches = execute_query(
            "SELECT code, description, category FROM icd10_codes WHERE LOWER(code) = ? LIMIT 3",
            (query,)
        )
        results.extend(exact_matches)
        
        if len(results) < limit:
            # 2. Code starts with query
            code_matches = execute_query(
                """SELECT code, description, category FROM icd10_codes 
                   WHERE LOWER(code) LIKE ? AND LOWER(code) != ? 
                   ORDER BY LENGTH(code) LIMIT ?""",
                (f"{query}%", query, limit - len(results))
            )
            results.extend(code_matches)
        
        if len(results) < limit:
            # 3. Description contains query words (tokenized search)
            description_matches = ICD10Service._search_by_description(
                query, limit - len(results), [r[0] for r in results]
            )
            results.extend(description_matches)
        
        # Convert to ICD10Code objects and remove duplicates
        unique_codes = {}
        for code, description, category in results:
            if code not in unique_codes:
                unique_codes[code] = ICD10Code(
                    code=code,
                    description=description,
                    category=category
                )
        
        return list(unique_codes.values())[:limit]
    
    @staticmethod
    def _search_by_description(query: str, limit: int, exclude_codes: List[str]) -> List[tuple]:
        """Search by description with word tokenization"""
        query_words = [word for word in query.split() if len(word) >= MIN_WORD_LENGTH]
        
        if not query_words:
            return []
        
        like_conditions = []
        params = []
        
        for word in query_words:
            like_conditions.append("search_terms LIKE ?")
            params.append(f"%{word}%")
        
        # Exclude already found results
        exclude_clause = ""
        if exclude_codes:
            exclude_clause = f"AND code NOT IN ({','.join(['?' for _ in exclude_codes])})"
            params.extend(exclude_codes)
        
        sql = f"""
            SELECT code, description, category FROM icd10_codes 
            WHERE ({' AND '.join(like_conditions)}) {exclude_clause}
            ORDER BY 
                CASE 
                    WHEN LOWER(description) LIKE ? THEN 1
                    WHEN LOWER(description) LIKE ? THEN 2
                    ELSE 3
                END,
                LENGTH(description)
            LIMIT ?
        """
        params.extend([f"{query}%", f"%{query}%", limit])
        
        return execute_query(sql, params)
    
    @staticmethod
    def get_code_by_exact_match(code: str) -> Optional[ICD10Code]:
        """Get a specific ICD-10 code by exact match"""
        result = execute_query(
            "SELECT code, description, category FROM icd10_codes WHERE UPPER(code) = UPPER(?)",
            (code,)
        )
        
        if result:
            row = result[0]
            return ICD10Code(
                code=row[0],
                description=row[1],
                category=row[2]
            )
        return None
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all available ICD-10 categories"""
        result = execute_query(
            "SELECT DISTINCT category FROM icd10_codes WHERE category IS NOT NULL ORDER BY category"
        )
        return [row[0] for row in result]