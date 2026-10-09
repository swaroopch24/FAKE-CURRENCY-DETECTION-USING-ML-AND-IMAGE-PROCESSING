from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.modules.ai_engine.router import router as ai_router
from src.modules.auth.router import router as auth_router
from src.modules.verification.router import router as verification_router
from src.modules.ai_engine.loaders import ModelLoader
import time

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Configurable from environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import Request
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uuid

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
        msg = err.get("msg", "Invalid parameter")
        errors.append(f"{loc}: {msg}" if loc else msg)
    error_msg = "; ".join(errors) if errors else "Invalid request payload."
    return JSONResponse(
        status_code=400,
        content={
            "request_id": str(uuid.uuid4()),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "INVALID_IMAGE",
            "result": None,
            "action": {
                "requires_retake": True,
                "requires_manual_review": False,
                "decision_reason": f"Request validation error: {error_msg}"
            },
            "meta": {
                "processing_time_ms": 0,
                "model_version": "1.0-stage2",
                "policy_threshold": 0.8
            }
        }
    )

# Register functional modules
app.include_router(ai_router, prefix=settings.API_V1_STR, tags=["AI Engine"])
app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(verification_router, prefix=settings.API_V1_STR, tags=["Verification"])

@app.on_event("startup")
def startup_event():
    from src.core.database.connection import SessionLocal, engine, Base
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from src.modules.auth.models import Role
        roles_data = [
            {"name": "Administrator", "key": "ROLE_ADMIN", "description": "System administrator with full access"},
            {"name": "Bank Teller", "key": "ROLE_TELLER", "description": "Teller officer processing scan audits"}
        ]
        for r in roles_data:
            existing = db.query(Role).filter(Role.key == r["key"]).first()
            if not existing:
                db_role = Role(
                    name=r["name"],
                    key=r["key"],
                    description=r["description"]
                )
                db.add(db_role)
        db.commit()
    finally:
        db.close()

model_loader = ModelLoader()

@app.get(f"{settings.API_V1_STR}/health", status_code=status.HTTP_200_OK)
@app.get(f"{settings.API_V1_STR}/monitor/health", status_code=status.HTTP_200_OK)
def get_health():
    """
    Service monitoring endpoint mapping the API health checks.
    """
    return {
      "success": True,
      "data": {
        "status": "healthy",
        "subsystems": {
          "postgresql": "up",  # Concrete checks will bind here
          "redis": "up",
          "s3_storage": "up",
          "inference_engine": "loaded" if model_loader.is_loaded() else "lazy_on_demand"
        },
        "uptime_seconds": 0  # In production, compute elapsed uptime
      },
      "meta": {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
      }
    }

@app.get("/")
def read_root():
    return {
        "name": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": f"{settings.API_V1_STR}/docs"
    }
