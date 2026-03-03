import requests

BASE_URL = "http://127.0.0.1:8000"

# Login
r = requests.post(f"{BASE_URL}/api/v1/auth/login", data={"username": "newuser123", "password": "123456"})
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get Trending
r = requests.get(f"{BASE_URL}/api/v1/trending", headers=headers)
print(f"Trending Status: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"Platforms count: {len(data)}")
    for p in data[:3]:
        print(f"  - {p.get('platform')}: {len(p.get('data', []))} items")
