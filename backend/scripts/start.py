"""
Enhanced DiagnoAssist Startup Script
Comprehensive testing of Steps 1-4: Models, Database, Schemas, Repositories
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, date
from uuid import uuid4
import json

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiagnoAssistTester:
    """Comprehensive testing of DiagnoAssist backend components"""
    
    def __init__(self):
        self.test_results = {
            'environment': False,
            'imports': False,
            'database_connection': False,
            'models': False,
            'repositories': False,
            'crud_operations': False,
            'server_ready': False
        }
        self.db = None
        self.repos = None
    
    def print_header(self, title: str):
        """Print formatted header"""
        logger.info("=" * 60)
        logger.info(f"🧪 {title}")
        logger.info("=" * 60)
    
    def print_success(self, message: str):
        """Print success message"""
        logger.info(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        logger.error(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        logger.warning(f"⚠️  {message}")
    
    def test_environment(self) -> bool:
        """Test environment configuration"""
        self.print_header("Testing Environment Configuration")
        
        required_vars = {
            'DATABASE_URL': 'PostgreSQL database URL',
            'SECRET_KEY': 'Secret key for security'
        }
        
        optional_vars = {
            'SUPABASE_URL': 'Supabase project URL',
            'SUPABASE_ANON_KEY': 'Supabase anonymous key',
            'FHIR_BASE_URL': 'FHIR base URL'
        }
        
        missing_required = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_required.append(f"  - {var}: {description}")
            else:
                self.print_success(f"{var} is configured")
        
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if value:
                self.print_success(f"{var} is configured")
            else:
                self.print_warning(f"{var} not configured (optional)")
        
        if missing_required:
            self.print_error("Missing required environment variables:")
            for var in missing_required:
                logger.error(var)
            return False
        
        self.test_results['environment'] = True
        self.print_success("Environment configuration validated")
        return True
    
    def test_imports(self) -> bool:
        """Test all critical imports"""
        self.print_header("Testing Critical Imports")
        
        imports_to_test = [
            ('fastapi', 'FastAPI framework'),
            ('sqlalchemy', 'Database ORM'),
            ('pydantic', 'Data validation'),
            ('uvicorn', 'ASGI server'),
            ('config.database', 'Database configuration'),
            ('config.settings', 'Application settings'),
            ('models', 'Database models'),
            ('repositories', 'Data access layer'),
            ('schemas', 'API schemas')
        ]
        
        failed_imports = []
        
        for module, description in imports_to_test:
            try:
                __import__(module)
                self.print_success(f"{module} - {description}")
            except ImportError as e:
                self.print_error(f"{module} - {description}: {str(e)}")
                failed_imports.append(module)
        
        if failed_imports:
            self.print_error(f"Failed imports: {', '.join(failed_imports)}")
            return False
        
        self.test_results['imports'] = True
        self.print_success("All critical imports successful")
        return True
    
    def test_database_connection(self) -> bool:
        """Test database connection"""
        self.print_header("Testing Database Connection")
        
        try:
            from config.database import engine, SessionLocal, get_db
            from sqlalchemy import text
            
            # Test engine connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                self.print_success("Database engine connection successful")
            
            # Test session creation
            db = SessionLocal()
            self.db = db
            result = db.execute(text("SELECT version()"))
            db_version = result.scalar()
            self.print_success(f"Database session created: {db_version}")
            
            # Test dependency function
            db_gen = get_db()
            db_from_dep = next(db_gen)
            self.print_success("Database dependency function working")
            db_from_dep.close()
            
            self.test_results['database_connection'] = True
            return True
            
        except Exception as e:
            self.print_error(f"Database connection failed: {str(e)}")
            return False
    
    def test_models(self) -> bool:
        """Test database models"""
        self.print_header("Testing Database Models")
        
        try:
            from models.patient import Patient
            from models.episode import Episode
            from models.diagnosis import Diagnosis
            from models.treatment import Treatment
            from models.fhir_resource import FHIRResource
            from config.database import Base, engine
            from sqlalchemy import inspect
            
            # Test model imports
            models = [Patient, Episode, Diagnosis, Treatment, FHIRResource]
            for model in models:
                self.print_success(f"{model.__name__} model imported")
            
            # Test table creation
            Base.metadata.create_all(bind=engine)
            self.print_success("Database tables created/verified")
            
            # Check if tables exist
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            expected_tables = ['patients', 'episodes', 'diagnoses', 'treatments', 'fhir_resources']
            for table in expected_tables:
                if table in existing_tables:
                    self.print_success(f"Table '{table}' exists")
                else:
                    self.print_warning(f"Table '{table}' not found")
            
            self.test_results['models'] = True
            return True
            
        except Exception as e:
            self.print_error(f"Model testing failed: {str(e)}")
            return False
    
    def test_repositories(self) -> bool:
        """Test repository layer"""
        self.print_header("Testing Repository Layer")
        
        try:
            from repositories import (
                RepositoryManager, 
                PatientRepository,
                EpisodeRepository,
                DiagnosisRepository,
                TreatmentRepository,
                FHIRResourceRepository
            )
            
            # Test repository imports
            repos = [
                PatientRepository, EpisodeRepository, DiagnosisRepository,
                TreatmentRepository, FHIRResourceRepository
            ]
            for repo in repos:
                self.print_success(f"{repo.__name__} imported")
            
            # Test repository manager
            repo_manager = RepositoryManager(self.db)
            self.repos = repo_manager
            self.print_success("RepositoryManager created")
            
            # Test repository access
            patient_repo = repo_manager.patient
            episode_repo = repo_manager.episode
            diagnosis_repo = repo_manager.diagnosis
            treatment_repo = repo_manager.treatment
            fhir_repo = repo_manager.fhir_resource
            
            self.print_success("All repositories accessible through manager")
            
            self.test_results['repositories'] = True
            return True
            
        except Exception as e:
            self.print_error(f"Repository testing failed: {str(e)}")
            return False
    
    def test_crud_operations(self) -> bool:
        """Test CRUD operations with sample data"""
        self.print_header("Testing CRUD Operations")
        
        try:
            # Test patient creation
            patient_data = {
                "medical_record_number": f"MRN-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "first_name": "Test",
                "last_name": "Patient",
                "date_of_birth": date(1990, 1, 15),
                "gender": "female",
                "email": "test.patient@example.com",
                "phone": "+1234567890"
            }
            
            patient = self.repos.patient.create(patient_data)
            if patient:
                self.print_success(f"Patient created: {patient.first_name} {patient.last_name}")
                
                # Test patient retrieval
                retrieved_patient = self.repos.patient.get_by_id(patient.id)
                if retrieved_patient:
                    self.print_success(f"Patient retrieved: ID {retrieved_patient.id}")
                
                # Test patient search
                search_results = self.repos.patient.search_by_name("Test")
                if search_results:
                    self.print_success(f"Patient search found {len(search_results)} results")
                
                # Test episode creation
                episode_data = {
                    "patient_id": patient.id,
                    "episode_type": "consultation",
                    "chief_complaint": "Test chest pain for verification",
                    "status": "active",
                    "priority": "normal",
                    "start_time": datetime.utcnow()
                }
                
                episode = self.repos.episode.create(episode_data)
                if episode:
                    self.print_success(f"Episode created: {episode.chief_complaint}")
                    
                    # Test diagnosis creation
                    diagnosis_data = {
                        "episode_id": episode.id,
                        "condition_name": "Test Condition",
                        "icd10_code": "Z00.00",
                        "ai_probability": 0.85,
                        "confidence_level": "high",
                        "ai_reasoning": "Test reasoning for verification"
                    }
                    
                    diagnosis = self.repos.diagnosis.create(diagnosis_data)
                    if diagnosis:
                        self.print_success(f"Diagnosis created: {diagnosis.condition_name}")
                        
                        # Test treatment creation
                        treatment_data = {
                            "episode_id": episode.id,
                            "diagnosis_id": diagnosis.id,
                            "treatment_type": "medication",
                            "treatment_name": "Test Treatment",
                            "medication_name": "Test Medicine",
                            "dosage": "10mg",
                            "frequency": "Once daily",
                            "status": "planned"
                        }
                        
                        treatment = self.repos.treatment.create(treatment_data)
                        if treatment:
                            self.print_success(f"Treatment created: {treatment.treatment_name}")
                
                # Test FHIR resource creation
                fhir_data = {
                    "fhir_id": str(uuid4()),
                    "resource_type": "Patient",
                    "version": 1,
                    "content": {
                        "resourceType": "Patient",
                        "id": str(patient.id),
                        "name": [{
                            "given": [patient.first_name],
                            "family": patient.last_name
                        }],
                        "gender": patient.gender,
                        "birthDate": patient.date_of_birth.isoformat()
                    },
                    "status": "active"
                }
                
                fhir_resource = self.repos.fhir_resource.create(fhir_data)
                if fhir_resource:
                    self.print_success(f"FHIR resource created: {fhir_resource.resource_type}")
                
                # Test repository statistics
                patient_stats = self.repos.patient.get_patient_statistics()
                if patient_stats:
                    self.print_success(f"Patient statistics: {patient_stats['total_patients']} total patients")
                
                episode_stats = self.repos.episode.get_episode_statistics()
                if episode_stats:
                    self.print_success(f"Episode statistics: {episode_stats['total_episodes']} total episodes")
                
                self.test_results['crud_operations'] = True
                return True
            else:
                self.print_error("Failed to create test patient")
                return False
                
        except Exception as e:
            self.print_error(f"CRUD operations testing failed: {str(e)}")
            return False
    
    def test_schemas(self) -> bool:
        """Test Pydantic schemas"""
        self.print_header("Testing API Schemas")
        
        try:
            from schemas.patient import PatientCreate, PatientResponse
            from schemas.episode import EpisodeCreate, EpisodeResponse
            from schemas.diagnosis import DiagnosisCreate, DiagnosisResponse
            from schemas.treatment import TreatmentCreate, TreatmentResponse
            
            # Test schema imports
            schemas = [
                ('PatientCreate', PatientCreate),
                ('PatientResponse', PatientResponse),
                ('EpisodeCreate', EpisodeCreate),
                ('EpisodeResponse', EpisodeResponse),
                ('DiagnosisCreate', DiagnosisCreate),
                ('DiagnosisResponse', DiagnosisResponse),
                ('TreatmentCreate', TreatmentCreate),
                ('TreatmentResponse', TreatmentResponse)
            ]
            
            for schema_name, schema_class in schemas:
                self.print_success(f"{schema_name} schema imported")
            
            # Test schema validation
            patient_data = {
                "medical_record_number": "TEST-123",
                "first_name": "Test",
                "last_name": "Patient",
                "date_of_birth": "1990-01-15",
                "gender": "female",
                "email": "test@example.com"
            }
            
            patient_schema = PatientCreate(**patient_data)
            self.print_success("Patient schema validation successful")
            
            return True
            
        except Exception as e:
            self.print_error(f"Schema testing failed: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            if self.repos and self.db:
                # Delete test data (in reverse order due to foreign keys)
                test_patients = self.repos.patient.search_by_name("Test")
                for patient in test_patients:
                    # Delete related episodes, diagnoses, treatments
                    episodes = self.repos.episode.get_by_patient_id(patient.id)
                    for episode in episodes:
                        # Delete treatments first
                        treatments = self.repos.treatment.get_by_episode_id(episode.id)
                        for treatment in treatments:
                            self.repos.treatment.delete(treatment.id)
                        
                        # Delete diagnoses
                        diagnoses = self.repos.diagnosis.get_by_episode_id(episode.id)
                        for diagnosis in diagnoses:
                            self.repos.diagnosis.delete(diagnosis.id)
                        
                        # Delete episode
                        self.repos.episode.delete(episode.id)
                    
                    # Delete patient
                    self.repos.patient.delete(patient.id)
                
                self.repos.commit()
                self.print_success("Test data cleaned up")
                
        except Exception as e:
            self.print_warning(f"Cleanup warning: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = sum(self.test_results.values())
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
        
        logger.info("=" * 60)
        logger.info(f"Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.print_success("🎉 ALL TESTS PASSED! Ready for Step 5: Services")
            self.test_results['server_ready'] = True
        else:
            self.print_error("Some tests failed. Please fix issues before proceeding.")
        
        return passed_tests == total_tests
    
    def start_server(self):
        """Start the FastAPI server if tests pass"""
        if not self.test_results['server_ready']:
            self.print_error("Cannot start server - tests failed")
            return False
        
        self.print_header("Starting FastAPI Server")
        
        # Server configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = os.getenv('PORT', '8000')
        environment = os.getenv('ENVIRONMENT', 'development')
        
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info(f"📋 API Documentation: http://localhost:{port}/docs")
        logger.info(f"🔍 FHIR Base: {os.getenv('FHIR_BASE_URL', 'http://localhost:8000/fhir')}")
        logger.info(f"📊 Health Check: http://localhost:{port}/health")
        logger.info(f"🏃 Environment: {environment}")
        
        # Server command
        cmd = [
            "uvicorn", "main:app",
            "--host", host,
            "--port", port,
            "--log-level", "info"
        ]
        
        if environment == 'development':
            cmd.append("--reload")
            logger.info("🔄 Auto-reload enabled")
        
        logger.info("🚀 Starting server...\n")
        
        try:
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            logger.info("\n👋 Server stopped by user")
        except Exception as e:
            self.print_error(f"Server startup failed: {str(e)}")
            return False
    
    def run_complete_test(self):
        """Run complete test suite"""
        self.print_header("DiagnoAssist Backend - Complete Test Suite")
        logger.info("Testing Steps 1-4: Models, Database, Schemas, Repositories")
        logger.info("=" * 60)
        
        try:
            # Run all tests
            tests = [
                ('Environment', self.test_environment),
                ('Imports', self.test_imports),
                ('Database Connection', self.test_database_connection),
                ('Models', self.test_models),
                ('Repositories', self.test_repositories),
                ('Schemas', self.test_schemas),
                ('CRUD Operations', self.test_crud_operations)
            ]
            
            for test_name, test_func in tests:
                logger.info(f"\n🧪 Running {test_name} test...")
                success = test_func()
                if not success:
                    logger.error(f"❌ {test_name} test failed!")
                    break
            
            # Print summary
            self.print_summary()
            
            # Cleanup test data
            self.cleanup_test_data()
            
            # Start server if all tests pass
            if self.test_results['server_ready']:
                input("\n🎯 Press Enter to start the server...")
                self.start_server()
            
        except KeyboardInterrupt:
            logger.info("\n👋 Testing interrupted by user")
        except Exception as e:
            self.print_error(f"Testing failed: {str(e)}")
        finally:
            if self.db:
                self.db.close()


def main():
    """Main entry point"""
    try:
        tester = DiagnoAssistTester()
        tester.run_complete_test()
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()