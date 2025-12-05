import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None):
    """Тестирует один эндпоинт"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        print(f"{method} {path} -> Status: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text[:100]}")
        else:
            print(f"  Success: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"{method} {path} -> ERROR: {e}")
        return False

print("=" * 50)
print("Testing all endpoints...")
print("=" * 50)

# 1. Тестируем базовые эндпоинты
print("\n1. Basic endpoints:")
test_endpoint("GET", "/")
test_endpoint("GET", "/health")
test_endpoint("GET", "/docs")

# 2. Тестируем Auth
print("\n2. Auth endpoints:")
test_endpoint("POST", "/auth/register", {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})

# 3. Тестируем Trips
print("\n3. Trip endpoints:")
test_endpoint("GET", "/trips/")
test_endpoint("POST", "/trips/", {
    "name": "Test Trip",
    "city_id": 1,
    "description": "A test trip"
})

# 4. Тестируем Participants
print("\n4. Participant endpoints:")
# Сначала нужно создать поездку чтобы получить join_code
test_endpoint("POST", "/trips/join", {
    "join_code": "ABC123XYZ"
})

# 5. Тестируем Places
print("\n5. Place endpoints:")
test_endpoint("GET", "/trips/1/places/")
test_endpoint("POST", "/trips/1/places/", {
    "name": "Test Place",
    "city_id": 1,
    "latitude": 55.7558,
    "longitude": 37.6176
})
test_endpoint("GET", "/trips/1/places/route")

print("\n" + "=" * 50)
print("Testing complete!")
print("=" * 50)