# NoteGuard AI - API Contract Design

This document specifies the complete REST API Contract for **NoteGuard AI**. The design serves as the single source of truth for communication between the Next.js frontend and the FastAPI backend.

---

## 1. Global API Standards

### 1.1 Base URL & Versioning
All API endpoints must be prefixed with the API version:
`https://api.noteguard.domain/api/v1`

*   **Versioning Strategy**: URL-based path versioning (`/v1/`). Major breaking changes will increment the version (`/v2/`). Minor non-breaking updates will be handled through backwards-compatible schemas.

### 1.2 Common Request Headers
*   `Authorization`: `Bearer <JWT_ACCESS_TOKEN>` (Required for all endpoints except public/auth routes)
*   `Content-Type`: `application/json` (Unless specified otherwise, e.g., `multipart/form-data` for uploads)
*   `X-Client-Version`: `v1.2.0` (For client telemetry and version mapping)

### 1.3 Standard Envelope Format
All responses must conform to a consistent envelope structure:

#### Success Response Envelope
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2026-08-05T09:15:00Z"
  }
}
```

#### Paginated Response Envelope
```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "limit": 10,
    "total_records": 1250,
    "total_pages": 125,
    "timestamp": "2026-08-05T09:15:00Z"
  }
}
```

#### Error Response Envelope
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable description of what went wrong.",
    "details": [
      {
        "field": "username",
        "issue": "Field must be a valid email address."
      }
    ],
    "timestamp": "2026-08-05T09:15:00Z"
  }
}
```

### 1.4 Common Query Parameters (Pagination, Filtering, Sorting)
-   `page`: `integer` (Default: `1`) - Target page.
-   `limit`: `integer` (Default: `20`, Max: `100`) - Records per page.
-   `sort_by`: `string` - Field name to sort on (e.g. `created_at`).
-   `sort_order`: `string` - Direction (e.g. `asc` or `desc`).
-   `search`: `string` - Global text query (e.g. partial UUID search).

---

## 2. API Endpoint Specification

### 2.1 Authentication Module

#### 1. POST `/auth/login`
Authenticates a user session and issues access tokens.
*   **Authorization**: Public
*   **Rate Limit**: 5 attempts per 1 minute (per IP)
*   **Request Body**:
    ```json
    {
      "username": "teller_01",
      "password": "SecurePassword123"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "access_token": "eyJhbGciOiJIUzI1...",
        "token_type": "Bearer",
        "expires_in": 900,
        "user": {
          "id": "e2c34d3d-c12e-4b67-bd1c-1f6027ab5744",
          "username": "teller_01",
          "email": "teller01@bank.com",
          "role": "ROLE_TELLER"
        }
      },
      "meta": { "timestamp": "2026-08-05T09:15:00Z" }
    }
    ```
*   **Errors**:
    *   `401 Unauthorized`: Code `INVALID_CREDENTIALS`

#### 2. POST `/auth/refresh`
Issues a new access token using a refresh token stored in an HTTP-only secure cookie.
*   **Authorization**: Public (Cookie-validated)
*   **Request Body**: None (Validates cookie `refresh_token` automatically)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "access_token": "eyJhbGciOiJIUzI1...",
        "token_type": "Bearer",
        "expires_in": 900
      },
      "meta": { "timestamp": "2026-08-05T09:15:00Z" }
    }
    ```

---

### 2.2 User Profile Module

#### 1. GET `/users/me`
Retrieves the logged-in user's profile.
*   **Authorization**: Required (`ROLE_USER`, `ROLE_TELLER`, `ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "id": "e2c34d3d-c12e-4b67-bd1c-1f6027ab5744",
        "username": "teller_01",
        "email": "teller01@bank.com",
        "role": "ROLE_TELLER",
        "status": "active",
        "created_at": "2026-08-01T12:00:00Z"
      },
      "meta": { "timestamp": "2026-08-05T09:15:00Z" }
    }
    ```

---

### 2.3 Currency Verification Module

#### 1. POST `/verify`
Uploads currency note images for authentication processing.
*   **Authorization**: Required (`ROLE_TELLER`, `ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Content-Type**: `multipart/form-data`
*   **Rate Limit**: 60 requests per 1 minute (per User ID)
*   **Request Body**:
    *   `image_front`: `file` (Required, JPG/PNG, Max 10MB)
    *   `image_back`: `file` (Optional, JPG/PNG, Max 10MB)
*   **Success Response (201 Created)**:
    ```json
    {
      "success": true,
      "data": {
        "verification_id": "c1f2b6e1-95bc-4882-9f3b-fa1b2e5c8e22",
        "status": "processing",
        "created_at": "2026-08-05T09:15:00Z"
      },
      "meta": { "timestamp": "2026-08-05T09:15:00Z" }
    }
    ```
*   **Errors**:
    *   `400 Bad Request`: Code `IMAGE_QUALITY_CHECK_FAILED` (Blurry image / insufficient resolution)
    *   `422 Unprocessable Entity`: Code `INVALID_FILE_TYPE`

#### 2. GET `/verify/{id}`
Retrieves results for a specific verification scan.
*   **Authorization**: Required (`ROLE_USER`, `ROLE_TELLER`, `ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Path Parameters**: `id` (UUID of the verification scan)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "verification_id": "c1f2b6e1-95bc-4882-9f3b-fa1b2e5c8e22",
        "status": "completed",
        "verdict": {
          "is_authentic": false,
          "overall_confidence": 0.9840,
          "system_verdict": "counterfeit",
          "verdict_reason": "Watermark structure mismatch and missing security thread elements"
        },
        "base_prediction": {
          "denomination": 500,
          "orientation": "front",
          "inference_time_ms": 320
        },
        "feature_details": [
          {
            "feature_name": "watermark",
            "is_authentic": false,
            "confidence": 0.1200,
            "crop_image_url": "https://s3.amazonaws.com/noteguard/crops/c1f2_watermark.jpg",
            "roi_coordinates": { "x": 120, "y": 80, "w": 40, "h": 40 }
          },
          {
            "feature_name": "security_thread",
            "is_authentic": true,
            "confidence": 0.9400,
            "crop_image_url": "https://s3.amazonaws.com/noteguard/crops/c1f2_thread.jpg",
            "roi_coordinates": { "x": 340, "y": 0, "w": 10, "h": 224 }
          }
        ],
        "images": {
          "raw_image_url": "https://s3.amazonaws.com/noteguard/raw/c1f2_front.jpg",
          "grad_cam_url": "https://s3.amazonaws.com/noteguard/explain/c1f2_gradcam.jpg"
        },
        "report_url": "https://s3.amazonaws.com/noteguard/reports/c1f2_report.pdf",
        "created_at": "2026-08-05T09:15:00Z"
      },
      "meta": { "timestamp": "2026-08-05T09:15:05Z" }
    }
    ```

---

### 2.4 Verification History Module

#### 1. GET `/history`
Retrieves a paginated list of previous scans.
*   **Authorization**: Required (`ROLE_USER` logs self, others log broad data)
*   **Query Parameters**: Standard filters (`page`, `limit`, `sort_by`, `sort_order`, `search`)
    *   `denomination`: `integer` (Optional, filter by currency value)
    *   `verdict`: `string` (Optional, `authentic`, `counterfeit`, `suspicious`)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "verification_id": "c1f2b6e1-95bc-4882-9f3b-fa1b2e5c8e22",
          "denomination": 500,
          "system_verdict": "counterfeit",
          "confidence_score": 0.9840,
          "created_at": "2026-08-05T09:15:00Z"
        }
      ],
      "meta": {
        "page": 1,
        "limit": 20,
        "total_records": 4820,
        "total_pages": 241,
        "timestamp": "2026-08-05T09:20:00Z"
      }
    }
    ```

---

### 2.5 Reports Module

#### 1. POST `/reports/{id}/regenerate`
Triggers asynchronous regeneration of a verification PDF report.
*   **Authorization**: Required (`ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Path Parameters**: `id` (UUID of verification scan)
*   **Success Response (202 Accepted)**:
    ```json
    {
      "success": true,
      "data": {
        "report_id": "c1f2b6e1-95bc-4882-9f3b-fa1b2e5c8e22",
        "status": "queued",
        "message": "Asynchronous report generation task queued."
      },
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```

---

### 2.6 Analytics Module

#### 1. GET `/analytics/overview`
Retrieves aggregated metrics for the dashboard.
*   **Authorization**: Required (`ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Query Parameters**:
    *   `start_date`: `string` (Format: `YYYY-MM-DD`, default to 30 days ago)
    *   `end_date`: `string` (Format: `YYYY-MM-DD`, default to today)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "total_processed": 14209,
        "authenticity_rate": 0.9642,
        "flagged_counterfeit": 490,
        "flagged_suspicious": 68,
        "denomination_breakdown": {
          "500": 9820,
          "100": 3402,
          "200": 987
        },
        "daily_trends": [
          {
            "date": "2026-08-04",
            "total_scans": 480,
            "counterfeits": 12
          }
        ]
      },
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```

---

### 2.7 Currency Information Hub Module

#### 1. GET `/currency-info`
Retrieves system reference details for all Indian banknotes.
*   **Authorization**: Required (`ROLE_USER`, `ROLE_TELLER`, `ROLE_MANAGER`, `ROLE_ADMIN`)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "denomination": 500,
          "dimensions": "150mm x 66mm",
          "color": "Stone Grey",
          "security_features": {
            "front": ["Gandhi Portrait Watermark", "Security Thread with Color Shift", "Ashoka Pillar Emblem"],
            "back": ["Swachh Bharat Logo", "Red Fort Motif"]
          }
        }
      ],
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```

---

### 2.8 AI Model Center (Admin Module)

#### 1. GET `/admin/models`
Lists all staged and active neural models in the registry.
*   **Authorization**: Required (`ROLE_ADMIN`)
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": [
        {
          "model_id": "8c253a6f-f232-411a-bd88-12c8b87ab741",
          "model_name": "MobileNetV2-Denom-Classifier",
          "model_version": "v1.4.2",
          "is_active": true,
          "sha256_checksum": "9b12a812...",
          "created_at": "2026-08-01T10:00:00Z"
        }
      ],
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```

#### 2. POST `/admin/models/swap`
Instructs the engine to swap the active classifier model.
*   **Authorization**: Required (`ROLE_ADMIN`)
*   **Request Body**:
    ```json
    {
      "target_model_id": "8c253a6f-f232-411a-bd88-12c8b87ab741"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "status": "swapped",
        "active_model_id": "8c253a6f-f232-411a-bd88-12c8b87ab741",
        "warmed_up": true,
        "health_check": "passed"
      },
      "meta": { "timestamp": "2026-08-05T09:20:05Z" }
    }
    ```

---

### 2.9 System Configurations (Admin Module)

#### 1. PUT `/admin/configs/{key}`
Modifies a system settings parameter (e.g. classification threshold).
*   **Authorization**: Required (`ROLE_ADMIN`)
*   **Path Parameters**: `key` (Key of configuration item)
*   **Request Body**:
    ```json
    {
      "config_value": "0.85"
    }
    ```
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "config_key": "VERIFICATION_THRESHOLD_WATERMARK",
        "old_value": "0.80",
        "new_value": "0.85",
        "updated_at": "2026-08-05T09:20:00Z"
      },
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```

---

### 2.10 System Monitoring Module

#### 1. GET `/monitor/health`
Validates health status of Monolith subsystems.
*   **Authorization**: Public
*   **Success Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "status": "healthy",
        "subsystems": {
          "postgresql": "up",
          "redis": "up",
          "s3_storage": "up",
          "inference_engine": "up"
        },
        "uptime_seconds": 1204850
      },
      "meta": { "timestamp": "2026-08-05T09:20:00Z" }
    }
    ```
*   **Failure Response (503 Service Unavailable)**:
    Returned if a core service is down.
    ```json
    {
      "success": false,
      "error": {
        "code": "DATABASE_CONNECTION_ERROR",
        "message": "PostgreSQL database instance is offline.",
        "timestamp": "2026-08-05T09:20:00Z"
      }
    }
    ```
