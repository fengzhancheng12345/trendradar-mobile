import requests

BASE_URL = "http://127.0.0.1:8000"

# Login
print("=== Login ===")
r = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
    "username": "newuser123",
    "password": "123456"
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Keys: {data.keys()}")
    token = data.get("access_token")
    print(f"Token: {token}")
    print(f"Full Response: {data}")
    
    # Try with explicit header
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n=== Headers ===")
    print(headers)
    
    # Get VIP Status with explicit headers
    print("\n=== VIP Status ===")
    r2 = requests.get(f"{BASE_URL}/api/v1/vip/status", headers=headers)
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text}")
