import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Register (new user)
print("=== 1. Register (new user) ===")
r = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
    "username": "newuser123",
    "password": "123456"
})
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

# 2. Login
print("\n=== 2. Login ===")
r = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
    "username": "newuser123",
    "password": "123456"
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Token: {token[:50]}...")
    
    # 3. Get VIP Status
    print("\n=== 3. VIP Status ===")
    r = requests.get(f"{BASE_URL}/api/v1/vip/status", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    # 4. Get VIP Products
    print("\n=== 4. VIP Products ===")
    r = requests.get(f"{BASE_URL}/api/v1/vip/products")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    
    # 5. Create VIP Order
    print("\n=== 5. Create VIP Order ===")
    r = requests.post(f"{BASE_URL}/api/v1/vip/pay", headers=headers, json={
        "duration_days": 30
    })
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    # 6. Get Trending
    print("\n=== 6. Get Trending ===")
    r = requests.get(f"{BASE_URL}/api/v1/trending", headers=headers)
    print(f"Status: {r.status_code}")
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        print(f"Platforms: {[p.get('platform') for p in data[:3]]}")
