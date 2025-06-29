#!/usr/bin/env python3
"""
Test BVH file access on RSMT server
"""
import requests
import time

def test_bvh_access():
    print("🧪 Testing BVH file access...")
    
    # Wait for server to be ready
    time.sleep(3)
    
    bvh_files = [
        'neutral_reference.bvh',
        'angry_reference.bvh', 
        'elated_reference.bvh'
    ]
    
    for bvh_file in bvh_files:
        try:
            url = f'http://localhost:8001/{bvh_file}'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {bvh_file}: {len(response.text)} bytes")
            else:
                print(f"❌ {bvh_file}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {bvh_file}: Error - {e}")
    
    # Test API status
    try:
        response = requests.get('http://localhost:8001/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ API is working")
        else:
            print(f"❌ API error: {response.status_code}")
    except Exception as e:
        print(f"❌ API error: {e}")

if __name__ == "__main__":
    test_bvh_access()
