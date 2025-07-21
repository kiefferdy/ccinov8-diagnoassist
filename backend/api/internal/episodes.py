"""
Internal Episodes API Router  
Medical episodes and encounters management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/episodes")

# Temporary in-memory storage for demo purposes
episodes_store = {}

@router.post("/", summary="Create Episode")
async def create_episode(episode_data: Dict[str, Any]):
    """
    Create a new medical episode for a patient.
    
    Example request body:
    {
        "patient_id": "uuid-of-patient",
        "chief_complaint": "Chest pain",
        "status": "in-progress",
        "encounter_type": "outpatient",
        "provider_id": "uuid-of-provider"
    }
    """
    try:
        # Generate episode ID
        episode_id = str(uuid.uuid4())
        
        # Create episode record
        episode = {
            "id": episode_id,
            "patient_id": episode_data.get("patient_id"),
            "chief_complaint": episode_data.get("chief_complaint", ""),
            "status": episode_data.get("status", "in-progress"),  # in-progress, completed, cancelled
            "encounter_type": episode_data.get("encounter_type", "outpatient"),  # outpatient, inpatient, emergency
            "provider_id": episode_data.get("provider_id"),
            "start_time": episode_data.get("start_time", datetime.utcnow().isoformat()),
            "end_time": episode_data.get("end_time"),
            "location": episode_data.get("location", ""),
            "priority": episode_data.get("priority", "routine"),  # routine, urgent, emergent
            "notes": episode_data.get("notes", ""),
            "vital_signs": episode_data.get("vital_signs", {}),
            "symptoms": episode_data.get("symptoms", []),
            "assessments": episode_data.get("assessments", []),
            "diagnoses": episode_data.get("diagnoses", []),
            "treatments": episode_data.get("treatments", []),
            "follow_up": episode_data.get("follow_up", {}),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store episode
        episodes_store[episode_id] = episode
        
        return episode
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creating episode: {str(e)}")

@router.get("/{episode_id}", summary="Get Episode")
async def get_episode(episode_id: str):
    """
    Get episode by ID.
    """
    try:
        episode = episodes_store.get(episode_id)
        if not episode:
            raise HTTPException(status_code=404, detail=f"Episode with ID {episode_id} not found")
        
        return episode
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{episode_id}", summary="Update Episode")
async def update_episode(episode_id: str, episode_data: Dict[str, Any]):
    """
    Update existing episode.
    """
    try:
        if episode_id not in episodes_store:
            raise HTTPException(status_code=404, detail=f"Episode with ID {episode_id} not found")
        
        # Get existing episode
        existing_episode = episodes_store[episode_id]
        
        # Update fields
        for key, value in episode_data.items():
            if key not in ["id", "created_at"]:  # Protect immutable fields
                existing_episode[key] = value
        
        existing_episode["updated_at"] = datetime.utcnow().isoformat()
        
        # Store updated episode
        episodes_store[episode_id] = existing_episode
        
        return existing_episode
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}", summary="Get Patient Episodes")
async def get_patient_episodes(
    patient_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """
    Get all episodes for a specific patient.
    """
    try:
        # Filter episodes by patient_id
        patient_episodes = []
        for episode in episodes_store.values():
            if episode.get("patient_id") == patient_id:
                # Apply status filter if provided
                if status is None or episode.get("status") == status:
                    patient_episodes.append(episode)
        
        # Sort by created_at (newest first)
        patient_episodes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        start_idx = skip
        end_idx = start_idx + limit
        paginated_episodes = patient_episodes[start_idx:end_idx]
        
        return {
            "episodes": paginated_episodes,
            "total": len(patient_episodes),
            "patient_id": patient_id,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{episode_id}/summary", summary="Get Episode Summary")
async def get_episode_summary(episode_id: str):
    """
    Get comprehensive episode summary including all related data.
    """
    try:
        episode = episodes_store.get(episode_id)
        if not episode:
            raise HTTPException(status_code=404, detail=f"Episode with ID {episode_id} not found")
        
        # Create comprehensive summary
        summary = {
            "episode": episode,
            "timeline": [
                {
                    "timestamp": episode.get("created_at"),
                    "event": "Episode Created",
                    "description": f"Chief complaint: {episode.get('chief_complaint')}"
                },
                {
                    "timestamp": episode.get("updated_at"),
                    "event": "Last Updated",
                    "description": f"Status: {episode.get('status')}"
                }
            ],
            "clinical_summary": {
                "chief_complaint": episode.get("chief_complaint"),
                "vital_signs": episode.get("vital_signs", {}),
                "symptoms_count": len(episode.get("symptoms", [])),
                "assessments_count": len(episode.get("assessments", [])),
                "diagnoses_count": len(episode.get("diagnoses", [])),
                "treatments_count": len(episode.get("treatments", []))
            },
            "current_status": episode.get("status"),
            "duration": "Calculating..." if not episode.get("end_time") else "Completed"
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{episode_id}/status", summary="Update Episode Status")
async def update_episode_status(episode_id: str, status_data: Dict[str, Any]):
    """
    Update episode status (in-progress, completed, cancelled).
    """
    try:
        if episode_id not in episodes_store:
            raise HTTPException(status_code=404, detail=f"Episode with ID {episode_id} not found")
        
        new_status = status_data.get("status")
        valid_statuses = ["in-progress", "completed", "cancelled"]
        
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        episode = episodes_store[episode_id]
        old_status = episode.get("status")
        episode["status"] = new_status
        episode["updated_at"] = datetime.utcnow().isoformat()
        
        # If marking as completed, set end_time
        if new_status == "completed" and not episode.get("end_time"):
            episode["end_time"] = datetime.utcnow().isoformat()
        
        return {
            "message": f"Episode status updated from '{old_status}' to '{new_status}'",
            "episode_id": episode_id,
            "old_status": old_status,
            "new_status": new_status,
            "updated_at": episode["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", summary="List Episodes")
async def list_episodes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    encounter_type: Optional[str] = Query(None, description="Filter by encounter type")
):
    """
    List episodes with optional filters and pagination.
    """
    try:
        all_episodes = list(episodes_store.values())
        
        # Apply filters
        filtered_episodes = []
        for episode in all_episodes:
            include = True
            
            if status and episode.get("status") != status:
                include = False
            if patient_id and episode.get("patient_id") != patient_id:
                include = False
            if encounter_type and episode.get("encounter_type") != encounter_type:
                include = False
                
            if include:
                filtered_episodes.append(episode)
        
        # Sort by created_at (newest first)
        filtered_episodes.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        start_idx = skip
        end_idx = start_idx + limit
        paginated_episodes = filtered_episodes[start_idx:end_idx]
        
        return {
            "episodes": paginated_episodes,
            "total": len(filtered_episodes),
            "skip": skip,
            "limit": limit,
            "filters": {
                "status": status,
                "patient_id": patient_id,
                "encounter_type": encounter_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))