import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app
from src.modules.ai_engine.training.config import training_config
import cv2
import numpy as np
from PIL import Image
from src.config import settings
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_rate_limiters():
    from src.core.security.rate_limit import verify_rate_limiter, auth_rate_limiter
    verify_rate_limiter.requests.clear()
    auth_rate_limiter.requests.clear()

def create_valid_image(width=600, height=600, format="JPEG"):
    """Helper to create a valid in-memory image > 10KB."""
    # Create random noise instead of solid color to ensure JPEG size > 10KB
    array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(array, 'RGB')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format, quality=100)
    return img_byte_arr.getvalue()

@pytest.fixture
def valid_jpg():
    return create_valid_image(200, 200, "JPEG")

@pytest.fixture
def mock_inference():
    with patch('src.modules.ai_engine.inference.AIInferenceService.execute_prediction') as mock:
        with patch(
            'src.modules.ai_engine.pipeline.text_analyzer.analyze_banknote_text',
            return_value={
                "all_text": "RESERVE BANK OF INDIA 500 RUPEES",
                "detected_denomination": 500,
                "is_fake": False,
                "fake_matched_text": None,
            },
        ):
            yield mock

def test_1_high_confidence_genuine_500(mock_inference, valid_jpg):
    mock_inference.return_value = {
        "class_label": "real_500", "confidence": 0.95, "p_real": 0.96, "p_fake": 0.04, "raw_probabilities": []
    }
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["result"]["denomination"] == 500
    assert isinstance(data["result"]["denomination"], int)
    assert data["result"]["authenticity"] == "AUTHENTIC"
    assert data["result"]["circulation_status"] == "ACTIVE"

def test_2_high_confidence_fake_500(mock_inference, valid_jpg):
    mock_inference.return_value = {
        "class_label": "fake_500", "confidence": 0.91, "p_real": 0.05, "p_fake": 0.95, "raw_probabilities": []
    }
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["result"]["denomination"] == 500
    assert data["result"]["authenticity"] == "COUNTERFEIT"

def test_3_low_confidence_prediction(mock_inference, valid_jpg):
    mock_inference.return_value = {
        "class_label": "fake_100", "confidence": 0.79, "p_real": 0.21, "p_fake": 0.79, "raw_probabilities": []
    }
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNABLE_TO_DETERMINE"
    assert data["result"] is None
    assert data["action"]["requires_manual_review"] is True

def test_4_2000_detected(mock_inference, valid_jpg):
    mock_inference.return_value = {
        "class_label": "real_2000", "confidence": 0.99, "p_real": 0.99, "p_fake": 0.01, "raw_probabilities": []
    }
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ACCEPTED"
    assert data["result"]["denomination"] == 2000
    assert data["result"]["circulation_status"] == "WITHDRAWN_FROM_CIRCULATION"

def test_5_invalid_image():
    # Corrupted / not an image
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", b"0" * 15000, "image/jpeg")})
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_IMAGE"

def test_6_unsupported_image():
    img = create_valid_image(200, 200, "PPM")
    response = client.post("/api/v1/verify", files={"image_front": ("test.ppm", img, "image/x-portable-pixmap")})
    assert response.status_code == 415
    assert response.json()["status"] == "UNSUPPORTED_IMAGE"

def test_7_processing_failure(mock_inference, valid_jpg):
    mock_inference.side_effect = Exception("TensorFlow exploded")
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 500
    assert response.json()["status"] == "PROCESSING_ERROR"

def test_file_too_large():
    # Construct a byte string larger than the validator's 20MB limit.
    large_bytes = b"0" * (20 * 1024 * 1024 + 10)
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", large_bytes, "image/jpeg")})
    assert response.status_code == 413
    assert response.json()["status"] == "INVALID_IMAGE"

def test_file_too_small():
    # Construct a byte string < 10KB
    small_bytes = b"0" * 5000
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", small_bytes, "image/jpeg")})
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_IMAGE"

def test_dimensions_too_small():
    img = create_valid_image(16, 16, "JPEG")
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", img, "image/jpeg")})
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_IMAGE"

def test_missing_upload():
    response = client.post("/api/v1/verify")
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_IMAGE"

def test_8_history_unauthenticated_returns_401():
    response = client.get("/api/v1/history")
    assert response.status_code == 401

def test_9_auth_registration_and_login():
    # Register
    reg_res = client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "test@noteguard.ai",
        "password": "Password123!"
    })
    assert reg_res.status_code == 201 or reg_res.status_code == 400 # 400 if already exists

    # Login
    log_res = client.post("/api/v1/auth/login", json={
        "email": "test@noteguard.ai",
        "password": "Password123!"
    })
    assert log_res.status_code == 200
    token = log_res.json()["data"]["access_token"]
    return token

import uuid

def test_10_authenticated_verification_and_history(mock_inference, valid_jpg):
    unique_email = f"test_{uuid.uuid4().hex[:6]}@noteguard.ai"
    client.post("/api/v1/auth/register", json={
        "full_name": "Test User 2",
        "email": unique_email,
        "password": "Password123!"
    })
    
    log_res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    token = log_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_inference.return_value = {
        "class_label": "real_500", "confidence": 0.95, "p_real": 0.96, "p_fake": 0.04, "raw_probabilities": []
    }
    
    # Verify with auth
    res1 = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")}, headers=headers)
    assert res1.status_code == 200
    
    # Query history
    res2 = client.get("/api/v1/history", headers=headers)
    assert res2.status_code == 200
    data = res2.json()
    assert len(data["data"]) == 1

def test_11_security_headers():
    res = client.get("/api/v1/monitor/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert client.get("/api/v1/health").status_code == 200

@patch("src.modules.ai_engine.inference.AIInferenceService.execute_prediction")
def test_12_verify_rate_limit(mock_inference):
    mock_inference.return_value = {
        "class_label": "real_500", "confidence": 0.95, "p_real": 0.96, "p_fake": 0.04, "raw_probabilities": []
    }
    valid_jpg = create_valid_image(224, 224, "JPEG")
    
    from src.core.security.rate_limit import verify_rate_limiter
    from src.config import settings
    # Clear limiter state
    verify_rate_limiter.requests.clear()
    
    with patch(
        "src.modules.ai_engine.pipeline.text_analyzer.analyze_banknote_text",
        return_value={"all_text": "RESERVE BANK OF INDIA 500 RUPEES", "detected_denomination": 500},
    ):
        # Hit limit
        for _ in range(settings.VERIFY_RATE_LIMIT):
            res = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
            assert res.status_code == 200

        # The next one should fail with 429
        res_limit = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
        assert res_limit.status_code == 429
        assert res_limit.json()["detail"] == "Too many requests. Please wait and try again."

def test_13_auth_rate_limit():
    from src.core.security.rate_limit import auth_rate_limiter
    from src.config import settings
    auth_rate_limiter.requests.clear()
    
    for _ in range(settings.AUTH_RATE_LIMIT):
        res = client.post("/api/v1/auth/login", json={"email": "fake@test.com", "password": "wrong"})
        assert res.status_code in [400, 401, 404, 403, 422]
        
    res_limit = client.post("/api/v1/auth/login", json={"email": "fake@test.com", "password": "wrong"})
    assert res_limit.status_code == 429

def test_14_denomination_uncertainty_aggregate_authenticity(mock_inference, valid_jpg):
    # Denomination is uncertain (highest class is 0.40) but authenticity is confident (0.40 + 0.30 + 0.20 = 0.90)
    mock_inference.return_value = {
        "class_label": "real_500", "confidence": 0.40, "p_real": 0.90, "p_fake": 0.10, "raw_probabilities": []
    }
    response = client.post("/api/v1/verify", files={"image_front": ("test.jpg", valid_jpg, "image/jpeg")})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UNABLE_TO_DETERMINE"
    assert data["result"] is None
    assert "Denomination confidence" in data["action"]["decision_reason"]

def test_15_children_bank_marker_returns_rule_warning_without_cnn(mock_inference, valid_jpg):
    with patch(
        "src.modules.ai_engine.pipeline.text_analyzer.analyze_banknote_text",
        return_value={"all_text": "CHILDREN'S BANK OF INDIA", "detected_denomination": None},
    ):
        response = client.post("/api/v1/verify", files={"image_front": ("note.jpg", valid_jpg, "image/jpeg")})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COUNTERFEIT_WARNING"
    assert data["result"]["authenticity"] == "COUNTERFEIT"
    assert data["result"]["detection_method"] == "OCR_SAFETY_RULE"
    assert data["action"]["requires_manual_review"] is True
    assert "CNN inference was not run" in data["action"]["decision_reason"]
    mock_inference.assert_not_called()

@pytest.mark.parametrize(
    "foreign_text",
    [
        "FEDERAL RESERVE UNITED STATES OF AMERICA DOLLAR",
        "EUROPEAN CENTRAL BANK EURO",
        "BANK OF ENGLAND POUNDS",
    ],
)
def test_foreign_currency_is_rejected_before_cnn(mock_inference, valid_jpg, foreign_text):
    with patch(
        "src.modules.ai_engine.pipeline.text_analyzer.analyze_banknote_text",
        return_value={"all_text": foreign_text},
    ):
        response = client.post("/api/v1/verify", files={"image_front": ("note.jpg", valid_jpg, "image/jpeg")})

    assert response.status_code == 200
    assert response.json()["status"] == "UNSUPPORTED_CURRENCY"
    assert "Please upload an Indian banknote" in response.json()["action"]["decision_reason"]
    mock_inference.assert_not_called()

def test_ambiguous_text_reaches_cnn_and_uses_confidence_policy(mock_inference, valid_jpg):
    mock_inference.return_value = {
        "class_label": "real_500",
        "confidence": 0.42,
        "p_real": 0.95,
        "p_fake": 0.05,
        "raw_probabilities": [],
    }
    with patch(
        "src.modules.ai_engine.pipeline.text_analyzer.analyze_banknote_text",
        return_value={"all_text": "A blurry image with no readable text"},
    ):
        response = client.post("/api/v1/verify", files={"image_front": ("note.jpg", valid_jpg, "image/jpeg")})

    assert response.status_code == 200
    assert response.json()["status"] == "UNABLE_TO_DETERMINE"
    mock_inference.assert_called_once()
