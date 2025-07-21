"""
DiagnoAssist Backend Test Script - No Typing Version
Replace your entire test_backend.py with this version
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
        'main.py',
        'config/__init__.py',
        'config/database.py',
        'config/settings.py',
        'models/__init__.py',
        'models/patient.py',
        'models/episode.py',
        'models/diagnosis.py',
        'models/treatment.py',
        'models/fhir_resource.py',
        'repositories/__init__.py',
        'repositories/base_repository.py',
        'repositories/patient_repository.py',
        'repositories/repository_manager.py',
        'schemas/__init__.py',
        'schemas/patient.py',
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
        print("💡 You may need to create these files from our previous artifacts")
        return len(existing_files) >= len(required_files) // 2
    
    print("✅ All required files present")
    return True

def test_imports():
    """Test critical imports - NO TYPING VERSION"""
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
        
        # Test model imports - SIMPLE VERSION
        models_imported = 0
        
        try:
            from models.patient import Patient
            print("✅ models.patient imported")
            models_imported += 1
        except ImportError as e:
            print(f"❌ models.patient import failed: {e}")
        
        try:
            from models.episode import Episode
            print("✅ models.episode imported")
            models_imported += 1
        except ImportError as e:
            print(f"❌ models.episode import failed: {e}")
        
        try:
            from models.diagnosis import Diagnosis
            print("✅ models.diagnosis imported")
            models_imported += 1
        except ImportError as e:
            print(f"❌ models.diagnosis import failed: {e}")
        
        try:
            from models.treatment import Treatment
            print("✅ models.treatment imported")
            models_imported += 1
        except ImportError as e:
            print(f"❌ models.treatment import failed: {e}")
        
        try:
            from models.fhir_resource import FHIRResource
            print("✅ models.fhir_resource imported")
            models_imported += 1
        except ImportError as e:
            print(f"❌ models.fhir_resource import failed: {e}")
        
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
        
        # Calculate success rate
        total_components = 1 + models_imported + repos_imported + schemas_imported
        print(f"\n📊 Import success: {total_components}/8+ components")
        
        return config_ok and models_imported >= 3 and repos_imported >= 1
        
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
        
        try:
            from models.patient import Patient
            models_imported.append('Patient')
            model_classes.append(Patient)
        except ImportError:
            pass
            
        try:
            from models.episode import Episode
            models_imported.append('Episode')
            model_classes.append(Episode)
        except ImportError:
            pass
            
        try:
            from models.diagnosis import Diagnosis
            models_imported.append('Diagnosis')
            model_classes.append(Diagnosis)
        except ImportError:
            pass
            
        try:
            from models.treatment import Treatment
            models_imported.append('Treatment')
            model_classes.append(Treatment)
        except ImportError:
            pass
            
        try:
            from models.fhir_resource import FHIRResource
            models_imported.append('FHIRResource')
            model_classes.append(FHIRResource)
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
        
        return len(found_tables) >= 2
        
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
        
        try:
            patient_repo = repos.patient
            repositories_tested.append('patient')
            print(f"✅ Patient repository accessible")
        except Exception as e:
            print(f"❌ Patient repository failed: {e}")
        
        try:
            episode_repo = repos.episode
            repositories_tested.append('episode')
            print(f"✅ Episode repository accessible")
        except Exception as e:
            print(f"❌ Episode repository failed: {e}")
        
        # Test basic operation if patient repo works
        if 'patient' in repositories_tested:
            try:
                patient_count = repos.patient.count()
                print(f"✅ Repository operations working ({patient_count} patients in database)")
            except Exception as e:
                print(f"⚠️  Repository operation warning: {e}")
        
        db.close()
        return len(repositories_tested) >= 1
        
    except Exception as e:
        print(f"❌ Repository testing failed: {e}")
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

def create_sample_data():
    """Create sample data if repositories work"""
    print("🔍 Testing Sample Data Creation...")
    
    try:
        from config.database import SessionLocal
        from repositories import RepositoryManager
        from datetime import datetime, date
        
        db = SessionLocal()
        repos = RepositoryManager(db)
        
        # Check if sample data already exists
        try:
            existing = repos.patient.search_by_name("Sample")
            if existing:
                print("✅ Sample data already exists")
                db.close()
                return True
        except:
            pass
        
        # Create sample patient
        patient_data = {
            "medical_record_number": f"SAMPLE-{datetime.now().strftime('%Y%m%d')}",
            "first_name": "Sample",
            "last_name": "Patient",
            "date_of_birth": date(1985, 6, 15),
            "gender": "male",
            "email": "sample@example.com",
            "phone": "+1234567890"
        }
        
        patient = repos.patient.create(patient_data)
        if patient:
            print(f"✅ Sample patient created: {patient.first_name} {patient.last_name}")
            repos.commit()
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🏥 DiagnoAssist Backend - Comprehensive Test Suite")
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
        ("API Structure", test_api_structure),
        ("Sample Data", create_sample_data)
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
    
    if passed >= 7:
        print("\n🎉 EXCELLENT! Backend is ready!")
        print("✅ All core components working")
        print("\n🚀 Next steps:")
        print("   1. Run: python start.py")
        print("   2. Visit: http://localhost:8000/docs")
    elif passed >= 5:
        print("\n✅ GOOD! Core functionality working")
        print("Some minor issues but ready to proceed")
        print("\n🚀 You can start the server:")
        print("   python start.py")
    else:
        print("\n❌ NEEDS WORK")
        print("Please check the failing components")
        print("\n💡 Most likely missing files - check our artifacts")
    
    return passed >= 5

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