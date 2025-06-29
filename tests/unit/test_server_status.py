#!/usr/bin/env python3
"""
Test RSMT Server Status
"""
import requests
import json

def test_server():
    print("🧪 Testing RSMT Server...")
    
    try:
        # Test status endpoint
        response = requests.get('http://localhost:8001/api/status', timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"📊 Server: {data.get('server', 'Unknown')}")
            print(f"🤖 Models loaded: {data.get('models_initialized', False)}")
            print(f"🔥 GPU available: {data.get('gpu_available', False)}")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:8001")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 RSMT Server is working properly!")
        print("🌐 Web Interface: http://localhost:8001")
        print("📚 API Documentation: http://localhost:8001/docs")
    else:
        print("\n❌ Server test failed")
