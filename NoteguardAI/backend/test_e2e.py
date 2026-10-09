import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_end_to_end():
    random_str = str(uuid.uuid4())[:8]
    # 1. Login or register
    auth_data = {
        "email": f"testuser_{random_str}@example.com",
        "password": "Password123!"
    }
    reg_data = {
        "full_name": "Test User",
        "email": auth_data["email"],
        "password": auth_data["password"]
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    r = requests.post(f"{BASE_URL}/auth/login", json=auth_data)
    
    if "data" not in r.json() or "access_token" not in r.json()["data"]:
        return

    token = r.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload image
    img_path = r"c:\PROJECTS\fakecurrency\dataset\split\val\real_2000\14.jpg"
    with open(img_path, "rb") as f:
        files = {"image_front": ("14.jpg", f, "image/jpeg")}
        r = requests.post(f"{BASE_URL}/verify", headers=headers, files=files)
        print("Verify Status:", r.status_code)
        resp = r.json()
        print(json.dumps(resp, indent=2))
        
if __name__ == "__main__":
    test_end_to_end()
