import requests
import json

def test_api():
    url = "http://localhost:8000/api/v1/verify"
    img_path = r"c:\PROJECTS\fakecurrency\dataset\split\val\real_2000\14.jpg"
    with open(img_path, "rb") as f:
        files = {"image_front": ("14.jpg", f, "image/jpeg")}
        response = requests.post(url, files=files)
        print(response.status_code)
        
        # Save to file to avoid console print errors
        with open("response.json", "w", encoding="utf-8") as out:
            json.dump(response.json(), out, indent=2)
        print("Response saved to response.json")

if __name__ == "__main__":
    test_api()
