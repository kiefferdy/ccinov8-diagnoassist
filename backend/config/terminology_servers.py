from typing import Dict, List, Optional
from dataclasses import dataclass
import httpx
from .settings import get_settings

settings = get_settings()

@dataclass
class TerminologyServer:
    """
    External terminology server configuration
    """
    name: str
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    supported_code_systems: List[str] = None

class TerminologyConfig:
    """
    Configuration for external terminology services
    """
    
    # External FHIR Terminology Servers
    SERVERS = {
        "hl7_tx": TerminologyServer(
            name="HL7 Terminology Server",
            base_url="https://tx.fhir.org/r4",
            supported_code_systems=[
                "http://loinc.org",
                "http://snomed.info/sct",
                "http://hl7.org/fhir/sid/icd-10"
            ]
        ),
        "ontoserver": TerminologyServer(
            name="CSIRO Ontoserver",
            base_url="https://r4.ontoserver.csiro.au/fhir",
            supported_code_systems=[
                "http://snomed.info/sct",
                "http://loinc.org"
            ]
        ),
        "nlm": TerminologyServer(
            name="NLM UMLS Terminology Services",
            base_url="https://uts-ws.nlm.nih.gov/rest",
            api_key=settings.ai_service_api_key,  # Reuse for now
            supported_code_systems=[
                "http://www.nlm.nih.gov/research/umls/rxnorm",
                "http://loinc.org",
                "http://snomed.info/sct"
            ]
        )
    }
    
    # Local Code Systems (for offline operation)
    LOCAL_CODE_SYSTEMS = {
        "diagnoassist_symptoms": f"{settings.fhir_base_url}/CodeSystem/symptoms",
        "diagnoassist_assessments": f"{settings.fhir_base_url}/CodeSystem/assessments",
        "diagnoassist_ai_categories": f"{settings.fhir_base_url}/CodeSystem/ai-categories"
    }
    
    @classmethod
    async def validate_code(
        cls, 
        system: str, 
        code: str, 
        display: Optional[str] = None
    ) -> bool:
        """
        Validate a code against external terminology servers
        """
        for server_name, server in cls.SERVERS.items():
            if system in server.supported_code_systems:
                try:
                    async with httpx.AsyncClient(timeout=server.timeout) as client:
                        # FHIR $validate-code operation
                        params = {
                            "system": system,
                            "code": code
                        }
                        if display:
                            params["display"] = display
                        
                        response = await client.get(
                            f"{server.base_url}/ValueSet/$validate-code",
                            params=params
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            return result.get("parameter", [{}])[0].get("valueBoolean", False)
                            
                except Exception as e:
                    print(f"Error validating code with {server_name}: {e}")
                    continue
        
        return False  # Default to invalid if no server validates
    
    @classmethod
    async def lookup_code(
        cls, 
        system: str, 
        code: str
    ) -> Optional[Dict]:
        """
        Lookup code details from terminology servers
        """
        for server_name, server in cls.SERVERS.items():
            if system in server.supported_code_systems:
                try:
                    async with httpx.AsyncClient(timeout=server.timeout) as client:
                        # FHIR $lookup operation
                        params = {
                            "system": system,
                            "code": code
                        }
                        
                        response = await client.get(
                            f"{server.base_url}/CodeSystem/$lookup",
                            params=params
                        )
                        
                        if response.status_code == 200:
                            return response.json()
                            
                except Exception as e:
                    print(f"Error looking up code with {server_name}: {e}")
                    continue
        
        return None