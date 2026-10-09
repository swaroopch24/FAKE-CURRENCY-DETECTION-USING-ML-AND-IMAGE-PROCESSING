import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General Configs
    ENV: str = Field(default="development")
    PROJECT_NAME: str = Field(default="NoteGuard AI")
    API_V1_STR: str = Field(default="/api/v1")
    AI_PROVIDER: str = Field(default="mock")
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000", "http://localhost:3001"])

    # Security & Abuse Protection
    MAX_CONCURRENT_INFERENCES: int = Field(default=8)
    VERIFY_RATE_LIMIT: int = Field(default=60)
    VERIFY_RATE_WINDOW_SECONDS: int = Field(default=60)
    AUTH_RATE_LIMIT: int = Field(default=30)
    AUTH_RATE_WINDOW_SECONDS: int = Field(default=300)
    # PostgreSQL Database Configs
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/noteguard"
    )

    # Redis Cache & Queue Configs
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0"
    )

    # S3 Compatible Object Storage Configs
    S3_ENDPOINT_URL: str = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = Field(default="minioadmin")
    S3_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET_NAME: str = Field(default="noteguard")
    S3_REGION: str = Field(default="us-east-1")

    # Security & JWT Tokens
    JWT_SECRET_KEY: str = Field(
        default="8c253a6ff232411abd8812c8b87ab74164b3ef8b939fbfbf"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # AI Verification Threshold Parameters
    VERIFICATION_THRESHOLD_WATERMARK: float = Field(default=0.80)
    VERIFICATION_THRESHOLD_THREAD: float = Field(default=0.80)
    VERIFICATION_THRESHOLD_ASHOKA: float = Field(default=0.80)
    VERIFICATION_THRESHOLD_MICROTEXT: float = Field(default=0.80)

    # AI Model Registries
    MODEL_REGISTRY_DIR: str = Field(
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models"
        )
    )

settings = Settings()
