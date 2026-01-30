"""Test login manager endpoint after fix"""
import sys
import os
import time
import requests
from multiprocessing import Process

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def start_server():
    """Start Flask server in background"""
    from app import app
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

def test_endpoint():
    """Test the login manager endpoint"""
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test the endpoint
        response = requests.get('http://127.0.0.1:5001/api/login-manager/current-user')
        
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("=" * 60)
        
        if response.status_code == 200:
            print("✅ SUCCESS: Endpoint is working!")
            return True
        else:
            print("❌ FAILED: Got non-200 status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    # Start server in background
    server_process = Process(target=start_server)
    server_process.start()
    
    try:
        # Test the endpoint
        success = test_endpoint()
        sys.exit(0 if success else 1)
    finally:
        # Stop server
        server_process.terminate()
        server_process.join()