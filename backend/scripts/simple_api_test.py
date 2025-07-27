"""
Simple API test to check if server is responding
"""

import requests
import json

def test_basic_connectivity():
    """Test basic server connectivity"""
    print("Testing Basic Server Connectivity")
    print("=" * 40)
    
    # Test different endpoints to see what works
    endpoints_to_test = [
        ("Root", "http://localhost:8000/"),
        ("Docs", "http://localhost:8000/api/docs"),
        ("Health", "http://localhost:8000/health"),
        ("API Status", "http://localhost:8000/api/status"),
    ]
    
    for name, url in endpoints_to_test:
        print(f"\n[TEST] {name}: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"[RESULT] Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"[RESULT] Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"[RESULT] Response (text): {response.text[:100]}...")
            else:
                print(f"[RESULT] Error: {response.text[:100]}...")
        except Exception as e:
            print(f"[RESULT] Connection failed: {e}")
    
    print("\n" + "=" * 40)
    print("Basic connectivity test completed")

if __name__ == "__main__":
    test_basic_connectivity()