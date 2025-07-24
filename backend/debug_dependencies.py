#!/usr/bin/env python3
"""
Diagnostic script to investigate FastAPI dependency injection issue
"""

from fastapi import FastAPI, Depends
from api.dependencies import get_service_manager, get_repository_manager, get_database_session
import inspect

app = FastAPI()

@app.get("/debug/services")
async def debug_services(services = Depends(get_service_manager)):
    """Debug endpoint to investigate dependency injection"""
    
    debug_info = {}
    
    # Basic info about the services object
    debug_info["services_type"] = str(type(services))
    debug_info["services_str"] = str(services)
    debug_info["services_dir"] = [attr for attr in dir(services) if not attr.startswith('_')]
    
    # Check the patient attribute specifically
    debug_info["patient_attr_type"] = str(type(services.patient))
    debug_info["patient_attr_str"] = str(services.patient)
    
    # Check if it's a property
    patient_attr = getattr(type(services), 'patient', None)
    debug_info["patient_class_attr_type"] = str(type(patient_attr))
    debug_info["is_property"] = isinstance(patient_attr, property)
    
    # Try to access the property directly from the class
    if isinstance(patient_attr, property):
        debug_info["property_fget"] = str(patient_attr.fget)
        try:
            # Try calling the property getter manually
            actual_service = patient_attr.fget(services)
            debug_info["manual_property_call_type"] = str(type(actual_service))
            debug_info["manual_property_call_str"] = str(actual_service)
            debug_info["manual_call_has_create_patient"] = hasattr(actual_service, 'create_patient')
        except Exception as e:
            debug_info["manual_property_call_error"] = str(e)
    
    # Check the internal _services dict
    if hasattr(services, '_services'):
        debug_info["_services_keys"] = list(services._services.keys())
        if 'patient' in services._services:
            debug_info["_services_patient_type"] = str(type(services._services['patient']))
            debug_info["_services_patient_has_create"] = hasattr(services._services['patient'], 'create_patient')
    
    return debug_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)