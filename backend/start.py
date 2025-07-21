#!/usr/bin/env python3
"""
DiagnoAssist Startup Script  
Uses your existing Supabase setup (SUPABASE_URL + SUPABASE_ANON_KEY)
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiagnoAssistStarter:
    """Handles complete DiagnoAssist startup process"""
    
    def __init__(self):
        self.validate_environment()
        self.setup_logging()
    
    def validate_environment(self):
        """Validate required environment variables"""
        logger.info("🔍 Validating environment configuration...")
        
        required_vars = {
            'SUPABASE_URL': 'Your Supabase project URL',
            'SUPABASE_ANON_KEY': 'Your Supabase anonymous key',
            'SECRET_KEY': 'Secret key for JWT tokens'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"  - {var}: {description}")
        
        if missing_vars:
            logger.error("❌ Missing required environment variables!")
            logger.error("Required variables:")
            for var in missing_vars:
                logger.error(var)
            
            logger.info("\n💡 Your .env file should contain:")
            logger.info("SUPABASE_URL=https://your-project.supabase.co")
            logger.info("SUPABASE_ANON_KEY=your-long-jwt-token-here")
            logger.info("SECRET_KEY=\"your-secret-key-here\"")
            logger.info("FHIR_BASE_URL=http://localhost:8000/fhir")
            
            sys.exit(1)
        
        # Validate Supabase URL format
        supabase_url = os.getenv('SUPABASE_URL')
        if not supabase_url.startswith('https://') or 'supabase.co' not in supabase_url:
            logger.error("❌ SUPABASE_URL must be a valid Supabase project URL")
            logger.info("💡 Should look like: https://your-project.supabase.co")
            sys.exit(1)
        
        logger.info("✅ Environment validation passed")
    
    def setup_logging(self):
        """Setup application logging"""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE')
        
        if log_file:
            # Create logs directory
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Setup file logging
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add to root logger
            logging.getLogger().addHandler(file_handler)
            logger.info(f"📝 Logging to file: {log_file}")
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        logger.info("🔍 Testing imports...")
        
        try:
            # Test config imports
            from config.settings import get_settings
            logger.info("✅ Settings import successful")
            
            # Test model imports
            from models.patient import Patient
            from models.episode import Episode
            from models.fhir_resource import FHIRResource
            logger.info("✅ Model imports successful")
            
            return True
            
        except ImportError as e:
            logger.error(f"❌ Import error: {e}")
            logger.info("💡 Make sure you've installed all dependencies: pip install -r requirements.txt")
            return False
    
    def test_supabase_connection(self):
        """Test connection to Supabase"""
        logger.info("🔍 Testing Supabase connection...")
        
        try:
            from config.database import test_supabase_connection
            success = test_supabase_connection()
            
            if success:
                logger.info("✅ Supabase connection successful")
                return True
            else:
                logger.error("❌ Supabase connection failed")
                logger.info("💡 Check your SUPABASE_URL and SUPABASE_ANON_KEY")
                logger.info("💡 Make sure your Supabase project is not paused")
                return False
                
        except Exception as e:
            logger.error(f"❌ Supabase connection test error: {e}")
            return False
    
    def verify_database_tables(self):
        """Verify that Supabase tables exist"""
        logger.info("🔍 Verifying database tables...")
        
        try:
            import requests
            from config.settings import get_settings
            
            settings = get_settings()
            headers = settings.get_supabase_headers()
            
            # Test each table
            tables_to_check = ['patients', 'episodes', 'fhir_resources']
            
            for table in tables_to_check:
                try:
                    response = requests.get(
                        f"{settings.supabase_rest_url}/{table}?select=id&limit=1",
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"   ✅ {table.title()} table: accessible")
                    else:
                        logger.warning(f"   ⚠️  {table.title()} table: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"   ⚠️  {table.title()} table: {str(e)[:50]}...")
            
            logger.info("✅ Database table verification complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database table verification error: {e}")
            return False
    
    def start_server(self):
        """Start the FastAPI server"""
        logger.info("🚀 Starting DiagnoAssist FHIR Server...")
        
        # Server configuration
        host = os.getenv('HOST', '0.0.0.0')
        port = os.getenv('PORT', '8000')
        environment = os.getenv('ENVIRONMENT', 'development')
        
        # Show server info
        logger.info("=" * 60)
        logger.info(f"🌐 Server starting on http://{host}:{port}")
        logger.info(f"📋 API Documentation: http://localhost:{port}/docs")
        logger.info(f"🔍 FHIR Base: {os.getenv('FHIR_BASE_URL', 'http://localhost:8000/fhir')}")
        logger.info(f"📊 Health Check: http://localhost:{port}/health")
        logger.info(f"🏃 Environment: {environment}")
        logger.info("=" * 60)
        
        # Server command
        cmd = [
            "uvicorn", "main:app",
            "--host", host,
            "--port", port,
            "--log-level", "info"
        ]
        
        # Add reload for development
        if environment == 'development':
            cmd.append("--reload")
            logger.info("🔄 Auto-reload enabled for development")
        
        logger.info("🚀 Starting server...\n")
        
        try:
            subprocess.run(cmd, check=True)
            
        except KeyboardInterrupt:
            logger.info("\n👋 Server stopped by user")
            
        except FileNotFoundError:
            logger.error("❌ Could not find main:app")
            logger.info("💡 Make sure you have a main.py file with FastAPI app")
            logger.info("💡 Alternative: uvicorn main:app --reload")
            return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Server failed to start: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Unexpected server error: {e}")
            return False
    
    def run(self):
        """Main startup sequence"""
        logger.info("🏥 DiagnoAssist FHIR Server Startup")
        logger.info("=" * 60)
        
        # 1. Test imports
        if not self.test_imports():
            logger.error("❌ Import test failed")
            sys.exit(1)
        
        # 2. Test Supabase connection
        if not self.test_supabase_connection():
            logger.error("❌ Supabase connection failed")
            logger.info("💡 The server will still start, but database operations may fail")
        
        # 3. Verify database tables
        if not self.verify_database_tables():
            logger.warning("⚠️  Database table verification had issues")
            logger.info("💡 The server will still start, but some endpoints may not work")
        
        logger.info("✅ Pre-flight checks completed!")
        logger.info("")
        
        # 4. Start server
        self.start_server()


def main():
    """Entry point"""
    try:
        starter = DiagnoAssistStarter()
        starter.run()
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()