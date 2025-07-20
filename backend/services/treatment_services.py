from typing import List, Optional, Dict, Any
from repositories.treatment_repository import TreatmentRepository
from repositories.diagnosis_repository import DiagnosisRepository
from services.ai_service import AIService
from schemas.treatment import TreatmentPlanCreate, TreatmentPlanResponse
import logging

logger = logging.getLogger(__name__)

class TreatmentService:
    """
    Service for AI-powered treatment planning and management
    """
    
    def __init__(
        self,
        treatment_repo: TreatmentRepository,
        ai_service: AIService,
        diagnosis_repo: Optional[DiagnosisRepository] = None
    ):
        self.treatment_repo = treatment_repo
        self.ai_service = ai_service
        self.diagnosis_repo = diagnosis_repo
    
    async def generate_treatment_plan(
        self,
        episode_id: str,
        diagnosis_id: str,
        patient_data: Dict[str, Any]
    ) -> TreatmentPlanResponse:
        """
        Generate comprehensive AI-powered treatment plan
        
        Args:
            episode_id: Episode identifier
            diagnosis_id: Diagnosis identifier
            patient_data: Patient information
            
        Returns:
            Treatment plan response
        """
        try:
            # Get diagnosis data
            diagnosis = None
            if self.diagnosis_repo:
                diagnosis = self.diagnosis_repo.get(diagnosis_id)
                if not diagnosis:
                    raise ValueError(f"Diagnosis {diagnosis_id} not found")
            
            # Prepare data for AI treatment generation
            treatment_request = {
                "diagnosis": {
                    "final_diagnosis": diagnosis.final_diagnosis if diagnosis else None,
                    "differential_diagnoses": diagnosis.differential_diagnoses if diagnosis else [],
                    "confidence_scores": diagnosis.confidence_scores if diagnosis else []
                },
                "patient": patient_data,
                "context": "comprehensive_treatment_planning"
            }
            
            # Generate AI treatment recommendations
            ai_treatment = await self.ai_service.generate_treatment_recommendations(
                treatment_request["diagnosis"],
                treatment_request["patient"]
            )
            
            # Create treatment record
            treatment_data = TreatmentPlanCreate(
                episode_id=episode_id,
                diagnosis_id=diagnosis_id,
                treatment_plan=ai_treatment.get("treatment_plan", {}),
                medications=ai_treatment.get("medications", []),
                follow_up_instructions=ai_treatment.get("follow_up_instructions", ""),
                additional_data={
                    "ai_generated": True,
                    "ai_recommendations": ai_treatment,
                    "patient_factors_considered": patient_data
                }
            )
            
            treatment = self.treatment_repo.create(treatment_data)
            
            logger.info(f"Generated treatment plan for episode: {episode_id}")
            return TreatmentPlanResponse.from_orm(treatment)
            
        except Exception as e:
            logger.error(f"Error generating treatment plan: {str(e)}")
            raise
    
    async def check_drug_interactions(
        self, 
        current_medications: List[Dict[str, Any]],
        new_medication: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check for drug interactions and contraindications
        
        Args:
            current_medications: List of current medications
            new_medication: New medication to check
            
        Returns:
            Interaction analysis results
        """
        try:
            # This would integrate with a drug interaction database
            # For now, implementing basic logic
            
            interaction_result = {
                "has_interactions": False,
                "interactions": [],
                "contraindications": [],
                "recommendations": [],
                "severity_levels": {}
            }
            
            # Basic interaction checking logic
            # In production, this would use a proper drug interaction database
            for current_med in current_medications:
                interaction = await self._check_medication_pair(current_med, new_medication)
                if interaction:
                    interaction_result["interactions"].append(interaction)
                    interaction_result["has_interactions"] = True
            
            # Add safety recommendations
            if interaction_result["has_interactions"]:
                interaction_result["recommendations"].append(
                    "Consult with pharmacist before prescribing"
                )
                interaction_result["recommendations"].append(
                    "Monitor patient closely for adverse effects"
                )
            
            return interaction_result
            
        except Exception as e:
            logger.error(f"Error checking drug interactions: {str(e)}")
            raise
    
    async def _check_medication_pair(
        self, 
        med1: Dict[str, Any], 
        med2: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check interaction between two medications"""
        # Simplified interaction checking
        # In production, use proper drug interaction database
        
        known_interactions = {
            ("warfarin", "aspirin"): {
                "severity": "major",
                "description": "Increased bleeding risk",
                "mechanism": "Additive anticoagulant effects"
            },
            ("metformin", "iodinated_contrast"): {
                "severity": "moderate", 
                "description": "Risk of lactic acidosis",
                "mechanism": "Contrast-induced nephrotoxicity"
            }
        }
        
        med1_name = med1.get("name", "").lower()
        med2_name = med2.get("name", "").lower()
        
        # Check both directions
        pair1 = (med1_name, med2_name)
        pair2 = (med2_name, med1_name)
        
        if pair1 in known_interactions:
            return known_interactions[pair1]
        elif pair2 in known_interactions:
            return known_interactions[pair2]
        
        return None