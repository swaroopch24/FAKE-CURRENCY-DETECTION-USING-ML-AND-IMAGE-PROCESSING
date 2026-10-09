import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from fastapi.testclient import TestClient
from backend.src.main import app
import json

client = TestClient(app)

image_path = r"C:\PROJECTS\fakecurrency\dataset\split\val\real_500\10.jpg"
with open(image_path, "rb") as f:
    image_bytes = f.read()

response = client.post("/api/v1/verify", files={"image_front": ("10.jpg", image_bytes, "image/jpeg")})

print("Status Code:", response.status_code)
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
