#!/usr/bin/env python3
"""
Quick Database Connection Fix for DiagnoAssist
Resolves the "Database not available" warning
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent if 'scripts' in str(Path(__file__).parent) else Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

import logging
import requests
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, DateTime
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionFixer:
    """Fix database connection issues"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        
        # Colors for output
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m', 
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'reset': '\033[0m'
        }
    
    def print_header(self, message: str):
        """Print section header"""
        print(f"\n{self.colors['blue']}{'='*60}{self.colors['reset']}")
        print(f"{self.colors['blue']}🔧 {message}{self.colors['reset']}")
        print(f"{self.colors['blue']}{'='*60}{self.colors['reset']}")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"{self.colors['green']}✅ {message}{self.colors['reset']}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"{self.colors['red']}❌ {message}{self.colors['reset']}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{self.colors['yellow']}⚠️ {message}{self.colors['reset']}")
    
    def check_environment_variables(self) -> bool:
        """Check that all required environment variables are set"""
        self.print_header("Step 1: Environment Variables Check")
        
        required_vars = {
            'SUPABASE_URL': self.supabase_url,
            'SUPABASE_ANON_KEY': self.supabase_key,
            'DATABASE_URL': self.database_url,
            'SECRET_KEY': os.getenv('SECRET_KEY')
        }
        
        all_set = True
        for var_name, var_value in required_vars.items():
            if var_value:
                # Mask sensitive values
                display_value = var_value
                if 'KEY' in var_name or 'SECRET' in var_name:
                    display_value = var_value[:8] + '...' + var_value[-4:] if len(var_value) > 12 else '***'
                elif 'URL' in var_name:
                    display_value = var_value.split('@')[0] + '@***' if '@' in var_value else var_value
                
                self.print_success(f"{var_name}: {display_value}")
            else:
                self.print_error(f"{var_name}: Not set")
                all_set = False
        
        return all_set
    
    def test_supabase_rest_api(self) -> bool:
        """Test Supabase REST API connection"""
        self.print_header("Step 2: Supabase REST API Test")
        
        if not self.supabase_url or not self.supabase_key:
            self.print_error("Supabase credentials missing")
            return False
        
        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Test basic connection
            response = requests.get(
                f"{self.supabase_url}/rest/v1/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.print_success("Supabase REST API connection: OK")
                return True
            else:
                self.print_error(f"Supabase REST API failed: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            self.print_error("Supabase connection timeout (check internet connection)")
            return False
        except requests.exceptions.ConnectionError:
            self.print_error("Supabase connection error (check URL)")
            return False
        except Exception as e:
            self.print_error(f"Supabase test error: {e}")
            return False
    
    def test_postgresql_connection(self) -> bool:
        """Test direct PostgreSQL connection"""
        self.print_header("Step 3: PostgreSQL Connection Test")
        
        if not self.database_url:
            self.print_error("DATABASE_URL not set")
            return False
        
        try:
            # Create engine with connection pooling
            engine = create_engine(
                self.database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,  # Validate connections
                echo=False
            )
            
            # Test connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test")).scalar()
                if result == 1:
                    self.print_success("PostgreSQL connection: OK")
                    
                    # Test database info
                    db_info = connection.execute(text("SELECT version()")).scalar()
                    self.print_success(f"Database: {db_info.split(',')[0]}")
                    
                    return True
                else:
                    self.print_error("PostgreSQL basic query failed")
                    return False
                    
        except SQLAlchemyError as e:
            self.print_error(f"SQLAlchemy error: {str(e)}")
            return False
        except Exception as e:
            self.print_error(f"PostgreSQL connection error: {str(e)}")
            return False
    
    def verify_database_tables(self) -> bool:
        """Verify that required tables exist"""
        self.print_header("Step 4: Database Tables Verification")
        
        if not self.database_url:
            self.print_error("DATABASE_URL not set")
            return False
        
        try:
            engine = create_engine(self.database_url, echo=False)
            
            with engine.connect() as connection:
                # Check for existing tables
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                
                existing_tables = [row[0] for row in connection.execute(tables_query)]
                
                if existing_tables:
                    self.print_success(f"Existing tables: {', '.join(existing_tables)}")
                else:
                    self.print_warning("No tables found in database")
                
                # Check for our required tables
                required_tables = ['patients', 'episodes', 'fhir_resources']
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if not missing_tables:
                    self.print_success("All required tables exist")
                    return True
                else:
                    self.print_warning(f"Missing tables: {', '.join(missing_tables)}")
                    
                    # Offer to create missing tables
                    create = input(f"\n{self.colors['yellow']}Would you like to create missing tables? (y/N): {self.colors['reset']}")
                    if create.lower() == 'y':
                        return self.create_missing_tables(connection, missing_tables)
                    else:
                        return False
                        
        except Exception as e:
            self.print_error(f"Table verification error: {e}")
            return False
    
    def create_missing_tables(self, connection, missing_tables: list) -> bool:
        """Create missing database tables"""
        self.print_header("Step 5: Creating Missing Tables")
        
        try:
            metadata = MetaData()
            
            # Define table schemas
            if 'patients' in missing_tables:
                patients_table = Table(
                    'patients', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('first_name', String(100)),
                    Column('last_name', String(100)), 
                    Column('email', String(255)),
                    Column('phone', String(50)),
                    Column('date_of_birth', String(10)),
                    Column('gender', String(10)),
                    Column('address', Text),
                    Column('created_at', DateTime),
                    Column('updated_at', DateTime)
                )
                
                patients_table.create(connection.engine)
                self.print_success("Created 'patients' table")
            
            if 'episodes' in missing_tables:
                episodes_table = Table(
                    'episodes', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('patient_id', Integer),
                    Column('status', String(50)),
                    Column('chief_complaint', Text),
                    Column('created_at', DateTime),
                    Column('updated_at', DateTime)
                )
                
                episodes_table.create(connection.engine)
                self.print_success("Created 'episodes' table")
            
            if 'fhir_resources' in missing_tables:
                fhir_table = Table(
                    'fhir_resources', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('resource_type', String(50)),
                    Column('resource_id', String(100)),
                    Column('fhir_data', Text),  # JSON data
                    Column('patient_id', Integer),
                    Column('episode_id', Integer),
                    Column('created_at', DateTime),
                    Column('updated_at', DateTime)
                )
                
                fhir_table.create(connection.engine)
                self.print_success("Created 'fhir_resources' table")
            
            self.print_success("All missing tables created successfully!")
            return True
            
        except Exception as e:
            self.print_error(f"Table creation error: {e}")
            return False
    
    def update_application_config(self) -> bool:
        """Update application configuration files if needed"""
        self.print_header("Step 6: Application Configuration Update")
        
        try:
            # Check if database config needs updating
            config_file = backend_dir / 'config' / 'database.py'
            
            if config_file.exists():
                self.print_success("Database configuration file exists")
                
                # You could add specific config updates here if needed
                # For now, just verify it can be imported
                sys.path.insert(0, str(backend_dir))
                from config.database import test_database_connection
                
                if test_database_connection():
                    self.print_success("Database configuration is working")
                    return True
                else:
                    self.print_warning("Database configuration test failed")
                    return False
            else:
                self.print_error("Database configuration file not found")
                return False
                
        except Exception as e:
            self.print_error(f"Configuration update error: {e}")
            return False
    
    def run_complete_fix(self) -> bool:
        """Run complete database connection fix"""
        print(f"{self.colors['blue']}{'='*80}{self.colors['reset']}")
        print(f"{self.colors['blue']}🔧 DiagnoAssist Database Connection Fix{self.colors['reset']}")
        print(f"{self.colors['blue']}{'='*80}{self.colors['reset']}")
        
        steps = [
            self.check_environment_variables,
            self.test_supabase_rest_api,
            self.test_postgresql_connection,
            self.verify_database_tables,
            self.update_application_config
        ]
        
        all_passed = True
        
        for step in steps:
            try:
                result = step()
                if not result:
                    all_passed = False
                    break  # Stop on first failure
            except Exception as e:
                self.print_error(f"Step failed with exception: {e}")
                all_passed = False
                break
        
        # Final result
        print(f"\n{self.colors['blue']}{'='*60}{self.colors['reset']}")
        if all_passed:
            self.print_success("✅ Database connection fix completed successfully!")
            self.print_success("You can now restart your server and the database warning should be gone.")
            print(f"\n{self.colors['blue']}Next step:{self.colors['reset']}")
            print("1. Stop your current server (Ctrl+C)")
            print("2. Restart: python main.py")
            print("3. Run Step 10 tests: python step_10_testing.py")
        else:
            self.print_error("❌ Database connection fix failed!")
            self.print_error("Please check the errors above and try again.")
        
        return all_passed


def main():
    """Main execution"""
    fixer = DatabaseConnectionFixer()
    success = fixer.run_complete_fix()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())