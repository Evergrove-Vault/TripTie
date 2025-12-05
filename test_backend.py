import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_backend():
    """Ждет пока бекенд станет доступен"""
    max_retries = 30
    retry_interval = 2
    
    print("⏳ Waiting for backend to start...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        if i < max_retries - 1:
            print(f"  Attempt {i+1}/{max_retries}...")
            time.sleep(retry_interval)
    
    print("❌ Backend failed to start")
    return False

def test_endpoints():
    """Тестирует все эндпоинты"""
    endpoints = [
        ("GET", "/", None, "Home page"),
        ("GET", "/health", None, "Health check"),
        ("GET", "/docs", None, "Swagger docs"),
        ("POST", "/auth/register", {
            "username": "docker_test",
            "email": "docker@test.com",
            "password": "test123"
        }, "User registration"),
        ("GET", "/trips/", None, "Get trips"),
        ("POST", "/trips/", {
            "name": "Docker Test Trip",
            "city_id": 1,
            "description": "Test from Docker"
        }, "Create trip"),
    ]
    
    print("\n" + "="*60)
    print("Testing all endpoints:")
    print("="*60)
    
    for method, path, data, description in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            print(f"\n🔍 {description}:")
            print(f"   {method} {path}")
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code >= 400:
                print(f"   Error: {response.text[:200]}")
            else:
                print(f"   Success!")
                if response.text:
                    print(f"   Response: {response.json()}")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    if wait_for_backend():
        test_endpoints()
    else:
        sys.exit(1)