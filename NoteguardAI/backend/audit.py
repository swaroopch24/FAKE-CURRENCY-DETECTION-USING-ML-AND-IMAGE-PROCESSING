import os
import time
import requests
import uuid
import json
from pathlib import Path

# Using FastAPI TestClient to test the complete application natively
from fastapi.testclient import TestClient
import sys
sys.path.append(str(Path(__file__).parent))

from src.main import app

client = TestClient(app)

def run_audit():
    print("=== NOTEGUARD PRODUCT AUDIT ===")
    
    print("\n--- Part 1: Startup ---")
    res = client.get("/api/v1/monitor/health")
    print(f"Health check: {res.status_code}")
    
    print("\n--- Part 2/3: Auth & RBAC ---")
    unique_email = f"audit_{uuid.uuid4().hex[:6]}@noteguard.ai"
    res_reg = client.post("/api/v1/auth/register", json={
        "full_name": "Audit User",
        "email": unique_email,
        "password": "Password123!"
    })
    print(f"Register: {res_reg.status_code}")
    
    res_login = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    print(f"Login: {res_login.status_code}")
    token = res_login.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Part 4-8: Verifications ---")
    val_dir = Path("../dataset/split/val")
    
    # 1. ACCEPTED (real_500/10.jpg or similar, wait I'll use real_500/0.jpg if exists)
    real_img = val_dir / "real_500" / "10.jpg"
    if not real_img.exists():
        # Fallback to any jpg
        real_img = list((val_dir / "real_500").glob("*.jpg"))[0]
        
    print(f"Testing with image: {real_img}")
    with open(real_img, "rb") as f:
        img_bytes = f.read()
        
    ram_during = 0
    # Run 5 requests to simulate stability
    for i in range(5):
        start = time.time()
        res_verify = client.post("/api/v1/verify", files={"image_front": ("test.jpg", img_bytes, "image/jpeg")}, headers=headers)
        if i == 0:
            print(f"Verify 1: {res_verify.status_code} - Status: {res_verify.json().get('status')}")
    
    # Check History
    res_hist = client.get("/api/v1/history", headers=headers)
    print(f"History records count: {len(res_hist.json()['data'])}")
    
    print("\n--- Part 7: Counterfeit ---")
    fake_img = val_dir / "fake_500" / "0.jpg"
    if fake_img.exists():
        res_fake = client.post("/api/v1/verify", files={"image_front": ("fake.jpg", fake_img.read_bytes(), "image/jpeg")}, headers=headers)
        print(f"Fake verify: {res_fake.json().get('status')}")
    
    print("\n--- Part 8: 2000 INR Rule ---")
    img_2000 = val_dir / "real_2000" / "14.jpg"
    if img_2000.exists():
        res_2000 = client.post("/api/v1/verify", files={"image_front": ("2000.jpg", img_2000.read_bytes(), "image/jpeg")}, headers=headers)
        print(f"2000 verify status: {res_2000.json().get('status')}")
        print(f"Circulation status: {res_2000.json().get('data', {}).get('circulation_status')}")

    print("\n--- Part 9: Invalid Files ---")
    res_inv = client.post("/api/v1/verify", files={"image_front": ("test.txt", b"Hello world", "text/plain")})
    print(f"Invalid text file: {res_inv.status_code} (Expected 400 or 415)")
    
if __name__ == "__main__":
    run_audit()
