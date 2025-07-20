from typing import Dict, Any, Optional
from fhir.resources.bundle import Bundle
from fhir.resources.operationoutcome import OperationOutcome
import logging

logger = logging.getLogger(__name__)

class FHIRInteropService:
    """
    Service for FHIR interoperability operations (Bundles, validation, etc.)
    """
    
    def __init__(self):
        pass
    
    async def process_bundle(self, bundle_data: Dict[str, Any]) -> Bundle:
        """
        Process FHIR Bundle (transaction or batch)
        
        Args:
            bundle_data: FHIR Bundle data
            
        Returns:
            Processed FHIR Bundle
        """
        try:
            # Validate bundle
            bundle = Bundle(**bundle_data)
            
            if bundle.type == "transaction":
                return await self._process_transaction_bundle(bundle)
            elif bundle.type == "batch":
                return await self._process_batch_bundle(bundle)
            else:
                raise ValueError(f"Unsupported bundle type: {bundle.type}")
                
        except Exception as e:
            logger.error(f"Error processing FHIR Bundle: {str(e)}")
            raise
    
    async def validate_bundle(self, bundle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate FHIR Bundle without processing
        
        Args:
            bundle_data: FHIR Bundle data
            
        Returns:
            Validation results
        """
        try:
            validation_result = {
                "valid": True,
                "issues": [],
                "warnings": []
            }
            
            # Basic bundle validation
            try:
                bundle = Bundle(**bundle_data)
            except Exception as e:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Bundle validation failed: {str(e)}")
                return validation_result
            
            # Validate bundle type
            if bundle.type not in ["document", "message", "transaction", "transaction-response", 
                                  "batch", "batch-response", "history", "searchset", "collection"]:
                validation_result["issues"].append(f"Invalid bundle type: {bundle.type}")
                validation_result["valid"] = False
            
            # Validate entries
            if bundle.entry:
                for i, entry in enumerate(bundle.entry):
                    entry_issues = await self._validate_bundle_entry(entry, i)
                    validation_result["issues"].extend(entry_issues)
            
            # Set overall validity
            validation_result["valid"] = len(validation_result["issues"]) == 0
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating FHIR Bundle: {str(e)}")
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    async def _process_transaction_bundle(self, bundle: Bundle) -> Bundle:
        """Process transaction bundle (all-or-nothing)"""
        # TODO: Implement transaction processing
        # For now, return the same bundle
        response_bundle = Bundle()
        response_bundle.type = "transaction-response"
        response_bundle.entry = []
        
        return response_bundle
    
    async def _process_batch_bundle(self, bundle: Bundle) -> Bundle:
        """Process batch bundle (independent operations)"""
        # TODO: Implement batch processing
        # For now, return the same bundle
        response_bundle = Bundle()
        response_bundle.type = "batch-response"
        response_bundle.entry = []
        
        return response_bundle
    
    async def _validate_bundle_entry(self, entry: Dict[str, Any], index: int) -> list:
        """Validate individual bundle entry"""
        issues = []
        
        # Check if entry has required fields
        if "resource" not in entry and "request" not in entry:
            issues.append(f"Entry {index}: Missing both resource and request")
        
        # Validate resource if present
        if "resource" in entry:
            resource = entry["resource"]
            if "resourceType" not in resource:
                issues.append(f"Entry {index}: Resource missing resourceType")
        
        return issues