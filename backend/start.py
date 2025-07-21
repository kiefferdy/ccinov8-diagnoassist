#!/usr/bin/env python3
"""
DiagnoAssist Startup Script with Direct Supabase API
Uses HTTP requests instead of Supabase client library
Database setup assumed to be already completed
"""

import os
import subprocess
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DiagnoAssistSupabaseStarter:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.secret_key = os.getenv("SECRET_KEY")
        self.fhir_base_url = os.getenv("FHIR_BASE_URL")
        
        if not all([self.supabase_url, self.supabase_key, self.secret_key, self.fhir_base_url]):
            print("❌ Missing required environment variables!")
            print("Required: SUPABASE_URL, SUPABASE_ANON_KEY, SECRET_KEY, FHIR_BASE_URL")
            print("\nYour .env should look like:")
            print("SUPABASE_URL=https://your-project.supabase.co")
            print("SUPABASE_ANON_KEY=your-anon-key")
            print("SECRET_KEY=your-secret-key")
            print("FHIR_BASE_URL=http://localhost:8000/fhir")
            exit(1)
        
        # Setup headers for Supabase REST API
        self.headers = {
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        self.rest_url = f"{self.supabase_url}/rest/v1"
    
    def test_supabase_connection(self):
        """Test connection to Supabase using REST API"""
        print("🔍 Testing Supabase connection...")
        
        try:
            # Test with a simple request to the REST API
            response = requests.get(
                f"{self.rest_url}/",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Supabase connection successful!")
                return True
            else:
                print(f"❌ Supabase connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Supabase connection failed: {e}")
            print("\n💡 Possible solutions:")
            print("1. Check your SUPABASE_URL and SUPABASE_ANON_KEY")
            print("2. Ensure your Supabase project is not paused")
            print("3. Check your internet connection")
            return False
    
    def verify_setup(self):
        """Verify the database setup is working"""
        print("🔍 Verifying database setup...")
        
        tables_to_check = ['patients', 'episodes', 'fhir_resources', 'observations']
        
        for table in tables_to_check:
            try:
                response = requests.get(
                    f"{self.rest_url}/{table}?select=id&limit=1",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✅ {table.title()} table: accessible")
                else:
                    print(f"   ⚠️  {table.title()} table: {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  {table.title()} table: {str(e)[:50]}...")
        
        print("✅ Database verification complete!")
        return True
    
    def start_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting DiagnoAssist FHIR Server...")
        
        port = os.getenv("PORT", "8000")
        host = os.getenv("HOST", "0.0.0.0")
        
        print(f"\n🌐 Server will be available at:")
        print(f"   📋 API Documentation: http://localhost:{port}/docs")
        print(f"   🔍 FHIR Metadata: {self.fhir_base_url}/R4/metadata")
        print(f"   👥 FHIR Patients: {self.fhir_base_url}/R4/Patient")
        print(f"   📊 Health Check: http://localhost:{port}/health")
        print(f"\n🔄 Starting server...\n")
        
        try:
            subprocess.run([
                "uvicorn", "main:app",
                "--reload",
                "--host", host,
                "--port", port,
                "--log-level", "info"
            ])
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except FileNotFoundError:
            print("❌ Could not find main:app")
            print("💡 Make sure you have a main.py file with FastAPI app")
            print("💡 Or try: uvicorn your_main_file:app --reload")
        except Exception as e:
            print(f"❌ Server failed to start: {e}")
            return False
    
    def run(self):
        """Main startup sequence"""
        print("🏥 DiagnoAssist FHIR Server Startup (Direct Supabase API)")
        print("=" * 65)
        
        # Test Supabase connection
        if not self.test_supabase_connection():
            print("\n💡 Troubleshooting:")
            print("1. Check your Supabase project is not paused")
            print("2. Verify SUPABASE_URL and SUPABASE_ANON_KEY in .env")
            print("3. Try accessing your Supabase dashboard")
            exit(1)
        
        # Verify existing setup
        self.verify_setup()
        
        # Start the server
        self.start_server()

def main():
    """Entry point"""
    starter = DiagnoAssistSupabaseStarter()
    starter.run()

if __name__ == "__main__":
    main()