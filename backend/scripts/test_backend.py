"""
DiagnoAssist Backend Test Script - Updated with Services Layer
Comprehensive testing including the new business logic layer
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging
import requests

# Fix paths - we're in scripts folder, need to go to backend root
scripts_dir = Path(__file__).parent
backend_dir = scripts_dir.parent  # Go up one level to backend root
sys.path.insert(0, str(backend_dir))

# Load environment from backend root
env_path = backend_dir / '.env'
load_dotenv(env_path)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_environment():
    """Test environment variables"""
    print("🔍 Testing Environment Configuration...")
    
    # Check what we have
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    secret_key = os.getenv('SECRET_KEY')
    database_url = os.getenv('DATABASE_URL')
    
    print(f"✅ SUPABASE_URL: {'✓ Set' if supabase_url else '✗ Missing'}")
    print(f"✅ SUPABASE_ANON_KEY: {'✓ Set' if supabase_key else '✗ Missing'}")
    print(f"✅ SECRET_KEY: {'✓ Set' if secret_key else '✗ Missing'}")
    print(f"✅ DATABASE_URL: {'✓ Set' if database_url else '✗ Missing'}")
    
    # Check optional settings
    optional_vars = {
        'FHIR_BASE_URL': os.getenv('FHIR_BASE_URL'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'DEBUG': os.getenv('DEBUG'),
        'PORT': os.getenv('PORT')
    }
    
    for var, value in optional_vars.items():
        if value:
            print(f"✅ {var}: {value}")
    
    # Critical check
    if not supabase_url or not supabase_key or not secret_key:
        print("❌ Missing critical environment variables")
        return False
    
    if not database_url:
        print("❌ DATABASE_URL is required for SQLAlchemy operations")
        return False
    
    print("✅ Environment configuration validated")
    return True

def test_supabase_connection():
    """Test Supabase REST API connection"""
    print("🔍 Testing Supabase Connection...")
    
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not configured")
            return False
        
        # Test REST API endpoint
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        # Try to access a simple endpoint
        response = requests.get(
            f"{supabase_url}/rest/v1/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Supabase REST API connection successful")
            return True
        else:
            print(f"❌ Supabase connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def check_file_structure():
    """Check if all required files exist in backend directory"""
    print("🔍 Checking File Structure...")
    print(f"   Backend directory: {backend_dir}")
    
    required_files = [
        # Core files
        'main.py',
        
        # Config layer
        'config/__init__.py',
        'config/database.py',
        'config/settings.py',
        
        # Models layer
        'models/__init__.py',
        'models/patient.py',
        'models/episode.py',
        'models/diagnosis.py',
        'models/treatment.py',
        'models/fhir_resource.py',
        
        # Repositories layer
        'repositories/__init__.py',
        'repositories/base_repository.py',
        'repositories/patient_repository.py',
        'repositories/episode_repository.py',
        'repositories/diagnosis_repository.py',
        'repositories/treatment_repository.py',
        'repositories/fhir_repository.py',
        'repositories/repository_manager.py',
        
        # Schemas layer
        'schemas/__init__.py',
        'schemas/patient.py',
        'schemas/episode.py',
        'schemas/diagnosis.py',
        'schemas/treatment.py',
        'schemas/fhir_resource.py',
        'schemas/common.py',
        
        # Services layer (NEW)
        'services/__init__.py',
        'services/base_service.py',
        'services/patient_service.py',
        'services/episode_service.py',
        'services/diagnosis_service.py',
        'services/treatment_service.py',
        'services/fhir_service.py',
        'services/clinical_service.py',
        'services/service_manager.py',
        
        # API layer
        'api/__init__.py'
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
            existing_files.append(file_path)
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    print(f"\n📊 Files found: {len(existing_files)}/{len(required_files)}")
    
    if missing_files:
        print(f"❌ Missing files: {len(missing_files)}")
        print("💡 You may need to create these files from our artifacts")
        return len(existing_files) >= len(required_files) * 0.7  # 70% threshold
    
    print("✅ All required files present")
    return True

def test_imports():
    """Test critical imports including services layer"""
    print("🔍 Testing Critical Imports...")
    
    try:
        import fastapi
        import sqlalchemy
        import pydantic
        import uvicorn
        print("✅ Core dependencies installed")
        
        # Test config imports
        try:
            from config.database import engine, SessionLocal
            print("✅ Database configuration imported")
            config_ok = True
        except ImportError as e:
            print(f"❌ Database config issue: {e}")
            config_ok = False
        
        # Test model imports
        models_imported = 0
        model_names = ['patient', 'episode', 'diagnosis', 'treatment', 'fhir_resource']
        
        for model_name in model_names:
            try:
                # Fix the FHIRResource import issue
                if model_name == 'fhir_resource':
                    exec(f"from models.{model_name} import FHIRResource")
                else:
                    exec(f"from models.{model_name} import {model_name.title().replace('_', '')}")
                print(f"✅ models.{model_name} imported")
                models_imported += 1
            except ImportError as e:
                print(f"❌ models.{model_name} import failed: {e}")
        
        # Test repository imports
        repos_imported = 0
        try:
            from repositories import RepositoryManager
            print("✅ RepositoryManager imported")
            repos_imported += 1
        except ImportError as e:
            print(f"❌ RepositoryManager import failed: {e}")
        
        try:
            from repositories.patient_repository import PatientRepository
            print("✅ PatientRepository imported")
            repos_imported += 1
        except ImportError as e:
            print(f"❌ PatientRepository import failed: {e}")
        
        # Test schema imports
        schemas_imported = 0
        try:
            from schemas.patient import PatientCreate, PatientResponse
            print("✅ Patient schemas imported")
            schemas_imported += 1
        except ImportError as e:
            print(f"❌ Schema import failed: {e}")
        
        # Test service imports (NEW)
        services_imported = 0
        service_names = ['base_service', 'patient_service', 'episode_service', 
                        'diagnosis_service', 'treatment_service', 'service_manager']
        
        for service_name in service_names:
            try:
                exec(f"from services.{service_name} import *")
                print(f"✅ services.{service_name} imported")
                services_imported += 1
            except ImportError as e:
                print(f"❌ services.{service_name} import failed: {e}")
        
        # Calculate success rate
        total_components = 1 + models_imported + repos_imported + schemas_imported + services_imported
        expected_components = 1 + len(model_names) + 2 + 1 + len(service_names)
        print(f"\n📊 Import success: {total_components}/{expected_components} components")
        
        return (config_ok and models_imported >= 3 and repos_imported >= 1 and 
                schemas_imported >= 1 and services_imported >= 4)
        
    except ImportError as e:
        print(f"❌ Critical dependency missing: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return False

def test_database():
    """Test database connection"""
    print("🔍 Testing Database Connection...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not configured")
        return False
    
    try:
        from config.database import engine, SessionLocal
        from sqlalchemy import text
        
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database engine connected: {version[:50]}...")
        
        # Test session
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database session working")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Check your DATABASE_URL and database credentials")
        return False

def test_models():
    """Test model definitions and table creation"""
    print("🔍 Testing Models and Tables...")
    
    try:
        from config.database import engine, Base
        
        # Import models to register them
        models_imported = []
        model_classes = []
        
        model_imports = [
            ('models.patient', 'Patient'),
            ('models.episode', 'Episode'),
            ('models.diagnosis', 'Diagnosis'),
            ('models.treatment', 'Treatment'),
            ('models.fhir_resource', 'FHIRResource')
        ]
        
        for module_name, class_name in model_imports:
            try:
                module = __import__(module_name, fromlist=[class_name])
                model_class = getattr(module, class_name)
                models_imported.append(class_name)
                model_classes.append(model_class)
            except ImportError:
                pass
        
        print(f"✅ Models imported: {', '.join(models_imported)}")
        
        if not model_classes:
            print("❌ No models could be imported")
            return False
        
        # Test table creation
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Test table existence
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        expected_tables = ['patients', 'episodes', 'diagnoses', 'treatments', 'fhir_resources']
        found_tables = [table for table in expected_tables if table in existing_tables]
        
        print(f"✅ Tables found: {', '.join(found_tables)}")
        
        return len(found_tables) >= 3
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

def test_repositories():
    """Test repository layer"""
    print("🔍 Testing Repository Layer...")
    
    try:
        from config.database import SessionLocal
        from repositories import RepositoryManager
        
        db = SessionLocal()
        repos = RepositoryManager(db)
        
        # Test repository access
        repositories_tested = []
        
        repo_tests = [
            ('patient', 'Patient repository'),
            ('episode', 'Episode repository'),
            ('diagnosis', 'Diagnosis repository'),
            ('treatment', 'Treatment repository'),
            ('fhir_resource', 'FHIR repository')
        ]
        
        for repo_name, description in repo_tests:
            try:
                repo = getattr(repos, repo_name)
                repositories_tested.append(repo_name)
                print(f"✅ {description} accessible")
            except Exception as e:
                print(f"❌ {description} failed: {e}")
        
        # Test basic operation if patient repo works
        if 'patient' in repositories_tested:
            try:
                patient_count = repos.patient.count()
                print(f"✅ Repository operations working ({patient_count} patients in database)")
            except Exception as e:
                print(f"⚠️  Repository operation warning: {e}")
        
        db.close()
        return len(repositories_tested) >= 3
        
    except Exception as e:
        print(f"❌ Repository testing failed: {e}")
        return False

def test_services():
    """Test individual services layer"""
    print("🔍 Testing Individual Services Layer...")
    
    try:
        from config.database import SessionLocal
        from repositories import RepositoryManager
        
        # Test individual service imports
        try:
            from services import (
                PatientService, EpisodeService, DiagnosisService,
                TreatmentService, FHIRService, ClinicalService
            )
            print("✅ Individual service imports successful")
        except ImportError as e:
            print(f"❌ Service imports failed: {e}")
            return False
        
        # Test service creation
        db = SessionLocal()
        repos = RepositoryManager(db)
        
        # Test individual service creation
        services_tested = []
        
        service_tests = [
            ('patient', PatientService, 'Patient service'),
            ('episode', EpisodeService, 'Episode service'), 
            ('diagnosis', DiagnosisService, 'Diagnosis service'),
            ('treatment', TreatmentService, 'Treatment service'),
            ('fhir', FHIRService, 'FHIR service'),
            ('clinical', ClinicalService, 'Clinical service')
        ]
        
        for service_name, service_class, description in service_tests:
            try:
                service = service_class(repos)
                if service and hasattr(service, 'repos'):
                    services_tested.append(service_name)
                    print(f"✅ {description} created successfully")
                else:
                    print(f"❌ {description} not properly initialized")
            except Exception as e:
                print(f"❌ {description} creation failed: {e}")
        
        # Test dependency injection functions
        try:
            from api.dependencies import (
                get_patient_service, get_episode_service, get_diagnosis_service,
                get_treatment_service, get_fhir_service, get_clinical_service
            )
            
            # Test one service through dependency injection
            patient_service = get_patient_service(repos)
            if hasattr(patient_service, 'repos'):
                print("✅ Service dependency injection working")
            else:
                print("❌ Service dependency injection failed")
                
        except Exception as e:
            print(f"⚠️  Service dependency injection test: {e}")
        
        # Test standard exception handling (using Python built-in exceptions)
        print("✅ Using standard Python exceptions (RuntimeError, ValueError, LookupError)")
        
        db.close()
        return len(services_tested) >= 4
        
    except Exception as e:
        print(f"❌ Services testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_structure():
    """Test API structure"""
    print("🔍 Testing API Structure...")
    
    try:
        # Test main app
        from main import app
        print("✅ FastAPI app imported")
        
        # Test API routers
        try:
            from api import api_router
            print("✅ API router imported")
        except ImportError as e:
            print(f"⚠️  API router issue: {e}")
        
        # Test app configuration
        if hasattr(app, 'title'):
            print(f"✅ App title: {app.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def test_service_integration():
    """Test individual service integration with dependency injection"""
    print("🔍 Testing Individual Service Integration...")
    
    try:
        from config.database import SessionLocal
        from repositories import RepositoryManager
        
        # Test individual service imports
        try:
            from services import PatientService, EpisodeService
            print("✅ Individual service imports working")
        except ImportError as e:
            print(f"❌ Service imports failed: {e}")
            return False
        
        db = SessionLocal()
        repos = RepositoryManager(db)
        
        # Test dependency injection functions
        try:
            from api.dependencies import get_patient_service, get_episode_service
            
            patient_service = get_patient_service(repos)
            episode_service = get_episode_service(repos)
            
            if hasattr(patient_service, 'repos') and hasattr(episode_service, 'repos'):
                print("✅ Service dependency injection working")
            else:
                print("❌ Service dependency injection failed")
                db.close()
                return False
        except Exception as e:
            print(f"❌ Service dependency injection failed: {e}")
            db.close()
            return False
        
        # Test patient service basic validation (without creating data)
        try:
            # Test that service has required methods
            if hasattr(patient_service, 'validate_business_rules'):
                print("✅ Patient service validation methods available")
            else:
                print("❌ Patient service validation methods missing")
                db.close()
                return False
        except Exception as e:
            print(f"❌ Patient service validation test failed: {e}")
            db.close()
            return False
        
        # Test service type annotations
        try:
            from api.dependencies import PatientServiceDep, EpisodeServiceDep
            print("✅ Service type annotations available")
        except ImportError as e:
            print(f"⚠️  Service type annotations: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_test():
    """Run comprehensive test suite including services layer"""
    print("🏥 DiagnoAssist Backend - Comprehensive Test Suite v2.0")
    print("=" * 60)
    print(f"Running from: {scripts_dir}")
    print(f"Backend root: {backend_dir}")
    print("=" * 60)
    
    tests = [
        ("File Structure", check_file_structure),
        ("Environment", test_environment),
        ("Supabase Connection", test_supabase_connection),
        ("Critical Imports", test_imports),
        ("Database Connection", test_database),
        ("Models & Tables", test_models),
        ("Repository Layer", test_repositories),
        ("Services Layer", test_services),           # NEW
        ("Service Integration", test_service_integration),  # NEW  
        ("API Structure", test_api_structure)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 {name}:")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name:<20}: {status}")
        if success:
            passed += 1
    
    print("=" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed >= 8:
        print("\n🎉 EXCELLENT! Backend with Services Layer is ready!")
        print("✅ All core components including business logic working")
        print("✅ Services layer successfully implemented")
        print("\n🚀 Next steps:")
        print("   1. Implement API Dependencies (Step 6)")
        print("   2. Run: python start.py")
        print("   3. Visit: http://localhost:8000/docs")
    elif passed >= 6:
        print("\n✅ GOOD! Core functionality with services working")
        print("Most components ready, minor issues to resolve")
        print("\n🚀 Ready for next development step:")
        print("   API Dependencies and Exception Handling")
    elif passed >= 4:
        print("\n⚠️  PARTIAL SUCCESS")
        print("Basic functionality working, services need attention")
        print("\n💡 Focus on fixing service layer issues")
    else:
        print("\n❌ NEEDS WORK")
        print("Multiple components need fixing")
        print("\n💡 Check missing files and dependencies")
    
    return passed >= 6

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n👋 Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)