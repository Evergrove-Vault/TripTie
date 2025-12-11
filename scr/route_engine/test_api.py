import requests
import json

url = "http://localhost:8001/generate-route"
data = {
    "city": "Нижний Новгород",
    "interests": ["архитектура", "история"],
    "days": 2
}

response = requests.post(url, json=data)
print("Status:", response.status_code)
print("Response:", json.dumps(response.json(), ensure_ascii=False, indent=2))
