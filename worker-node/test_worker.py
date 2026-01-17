#!/usr/bin/env python3
"""
Test script for NADG Worker Node
Tests all endpoints to verify worker functionality
"""

import requests
import json
import sys

def test_worker(worker_url="http://localhost:7860"):
    """Test all worker endpoints"""
    
    print(f"🧪 Testing NADG Worker at {worker_url}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1️⃣  Testing root endpoint (GET /)...")
    try:
        response = requests.get(f"{worker_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2️⃣  Testing health endpoint (GET /health)...")
    try:
        response = requests.get(f"{worker_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Status endpoint
    print("\n3️⃣  Testing status endpoint (GET /status)...")
    try:
        response = requests.get(f"{worker_url}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Status endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Execute task
    print("\n4️⃣  Testing task execution (POST /execute)...")
    try:
        task_data = {
            "task": "Test task from NADG",
            "task_id": 1,
            "timeout": 10
        }
        response = requests.post(
            f"{worker_url}/execute",
            json=task_data,
            timeout=15
        )
        if response.status_code == 200:
            print("✅ Task execution successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Execute Python task
    print("\n5️⃣  Testing Python execution (POST /execute-python)...")
    try:
        python_task = {
            "task": "print('Hello from NADG worker!')",
            "task_id": 2,
            "timeout": 10
        }
        response = requests.post(
            f"{worker_url}/execute-python",
            json=python_task,
            timeout=15
        )
        if response.status_code == 200:
            print("✅ Python execution successful")
            result = response.json()
            print(f"   Status: {result['status']}")
            print(f"   Output: {result['output']}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    return True


if __name__ == "__main__":
    worker_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7860"
    test_worker(worker_url)
