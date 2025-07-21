#!/usr/bin/env python3
"""
Supabase Connection Diagnostic Script
This will help identify exactly what's wrong with your connection
"""

import os
import socket
import psycopg2
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def test_network_connectivity():
    """Test if we can reach the Supabase host"""
    print("🌐 Testing network connectivity...")
    
    host = "db.gygpestixmjkpoqrrtzb.supabase.co"
    port = 5432
    
    try:
        # Test DNS resolution
        print(f"🔍 Resolving DNS for {host}...")
        ip = socket.gethostbyname(host)
        print(f"✅ DNS resolved to: {ip}")
        
        # Test port connectivity
        print(f"🔌 Testing connection to {host}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print("✅ Port 5432 is reachable!")
            return True
        else:
            print("❌ Port 5432 is not reachable")
            print("💡 This could mean:")
            print("   - Database is paused")
            print("   - Firewall blocking connection")
            print("   - Network issue")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Network test failed: {e}")
        return False

def test_database_connection():
    """Test the actual database connection"""
    print("\n🗄️  Testing database connection...")
    
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ DATABASE_URL not found in .env")
        return False
    
    print(f"🔗 Using connection string: {db_url[:50]}...{db_url[-20:]}")
    
    try:
        print("🔌 Attempting PostgreSQL connection...")
        conn = psycopg2.connect(
            db_url,
            connect_timeout=10  # 10 second timeout
        )
        
        print("✅ Connection established!")
        
        # Test a simple query
        print("🧪 Testing simple query...")
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 PostgreSQL version: {version[:50]}...")
        
        # Test if we can create tables (permissions check)
        print("🔧 Testing table creation permissions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connection_test (
                id SERIAL PRIMARY KEY,
                test_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("INSERT INTO connection_test DEFAULT VALUES;")
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM connection_test;")
        count = cursor.fetchone()[0]
        print(f"✅ Table operations work! Test records: {count}")
        
        # Clean up
        cursor.execute("DROP TABLE connection_test;")
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("✅ All database tests passed!")
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).lower()
        print(f"❌ Connection failed: {e}")
        
        if "could not connect to server" in error_msg:
            print("\n💡 Diagnosis: Cannot reach database server")
            print("   Possible causes:")
            print("   1. Database is PAUSED (most likely)")
            print("   2. Wrong host/port")
            print("   3. Network/firewall issue")
            print("\n🔧 Solutions:")
            print("   1. Go to Supabase dashboard and RESUME your database")
            print("   2. Check if you're on a corporate network blocking port 5432")
            
        elif "authentication failed" in error_msg or "password authentication failed" in error_msg:
            print("\n💡 Diagnosis: Authentication problem")
            print("   Possible causes:")
            print("   1. Wrong password")
            print("   2. Wrong username")
            print("   3. Database user doesn't exist")
            print("\n🔧 Solutions:")
            print("   1. Double-check your password in Supabase dashboard")
            print("   2. Regenerate the database password")
            
        elif "database" in error_msg and "does not exist" in error_msg:
            print("\n💡 Diagnosis: Database doesn't exist")
            print("   Solution: Make sure database name is 'postgres'")
            
        else:
            print(f"\n💡 Diagnosis: Other connection error")
            print(f"   Full error: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_supabase_status():
    """Check if we can determine Supabase status"""
    print("\n📊 Checking Supabase project status...")
    print("🌐 Please manually check your Supabase dashboard:")
    print("   1. Go to https://app.supabase.com")
    print("   2. Select your project")
    print("   3. Look for any 'PAUSED' or 'RESUME' indicators")
    print("   4. If paused, click 'RESUME' and wait 2-3 minutes")
    print("   5. Check Settings > Database for correct connection details")

def main():
    """Run all diagnostic tests"""
    print("🏥 DiagnoAssist Supabase Connection Diagnostic")
    print("=" * 60)
    
    # Test 1: Network connectivity
    network_ok = test_network_connectivity()
    
    if not network_ok:
        print("\n❌ Network connectivity failed!")
        print("💡 This is likely why your connection isn't working.")
        check_supabase_status()
        return
    
    # Test 2: Database connection
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n❌ Database connection failed!")
        check_supabase_status()
        return
    
    print("\n🎉 All tests passed!")
    print("✅ Your Supabase connection is working correctly!")
    print("🚀 You can now run: python start.py")

if __name__ == "__main__":
    main()