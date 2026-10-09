import os
import sys
import time
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

test_dir = r"d:\PROJECTS\notegurd\NoteguardAI\dataset\split\test"
classes_to_test = [
    "real_10", "real_20", "real_100", "real_200", "real_500", "real_2000",
    "fake_10", "fake_50", "fake_100", "fake_500", "fake_2000"
]

print("=== TESTING REAL & COUNTERFEIT NOTES WITH RATE-LIMIT DELAYS ===\n")

for c in classes_to_test:
    cdir = os.path.join(test_dir, c)
    if not os.path.exists(cdir):
        continue
    
    # Pick a file >= 10KB
    valid_files = [
        f for f in os.listdir(cdir) 
        if f.lower().endswith(('.jpg', '.png', '.jpeg')) 
        and os.path.getsize(os.path.join(cdir, f)) >= 10240
    ]
    if not valid_files:
        print(f"Skipping {c}: No image >= 10KB found.")
        continue
    
    test_file = os.path.join(cdir, valid_files[0])
    with open(test_file, 'rb') as f:
        # Retry loop for rate limit (HTTP 429)
        for attempt in range(5):
            r = requests.post('http://localhost:8000/api/v1/verify', files={'image_front': ('note.jpg', f, 'image/jpeg')})
            if r.status_code == 429:
                time.sleep(2)
                f.seek(0)
                continue
            break

        if r.status_code == 200:
            data = r.json()
            res = data.get('result')
            if res:
                auth = res['authenticity']
                conf = res['authenticity_confidence']
                denom = res['denomination_label']
                status = data['status']
                print(f"True: {c:12s} -> Predicted: {auth:12s} {denom:6s} (Confidence: {conf:.1%}) [Status: {status}]")
            else:
                reason = data.get('action', {}).get('decision_reason', '')
                status = data.get('status')
                print(f"True: {c:12s} -> Status: {status:20s} | Reason: {reason}")
        else:
            print(f"True: {c:12s} -> HTTP {r.status_code}: {r.text}")
    
    time.sleep(1.5)
