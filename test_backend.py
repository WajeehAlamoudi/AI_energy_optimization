#!/usr/bin/env python3
"""
Backend Verification Test Script
This script tests all major backend endpoints to ensure the system is working correctly.
"""

import subprocess
import time
import requests
import sys
import json


def start_server():
    """Start the FastAPI server in a subprocess."""
    print("🚀 Starting backend server...")
    server = subprocess.Popen(
        ["python3", "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)  # Wait for server to start
    return server


def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint."""
    base_url = "http://127.0.0.1:8000"
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
        else:
            response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
        
        return response.status_code == 200, response.status_code, response.text
    except Exception as e:
        return False, 0, str(e)


def main():
    """Main test routine."""
    server = None
    try:
        server = start_server()
        
        print("\n" + "="*60)
        print("BACKEND VERIFICATION TEST")
        print("="*60 + "\n")
        
        tests = [
            ("GET", "/api/init", None, "System initialization"),
            ("GET", "/api/homes", None, "List homes"),
            ("GET", "/api/devices", None, "List devices"),
            ("GET", "/api/weather", None, "Get weather data"),
            ("GET", "/api/kpis", None, "Get KPIs (may not have data)"),
        ]
        
        passed = 0
        failed = 0
        
        for method, endpoint, data, description in tests:
            success, status, response_text = test_endpoint(method, endpoint, data)
            
            if success:
                print(f"✅ PASS - {description}")
                print(f"   {method} {endpoint} → Status: {status}")
                if status == 200:
                    try:
                        response_json = json.loads(response_text)
                        # Show a preview of the response
                        response_preview = str(response_json)[:100]
                        if len(str(response_json)) > 100:
                            response_preview += "..."
                        print(f"   Response: {response_preview}")
                    except:
                        pass
                passed += 1
            else:
                print(f"❌ FAIL - {description}")
                print(f"   {method} {endpoint} → Status: {status}")
                print(f"   Error: {response_text[:100]}")
                failed += 1
            print()
        
        print("="*60)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("="*60)
        
        if failed == 0:
            print("\n🎉 All tests passed! Backend is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        return 1
    finally:
        if server:
            print("\n🛑 Stopping server...")
            server.terminate()
            server.wait()
            print("Server stopped.\n")


if __name__ == "__main__":
    sys.exit(main())
