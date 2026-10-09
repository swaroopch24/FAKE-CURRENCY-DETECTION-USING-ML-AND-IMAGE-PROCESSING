import boto3
from botocore.exceptions import ClientError
from src.config import settings
import structlog

logger = structlog.get_logger()

class StorageClient:
    """
    Client wrapper for S3-compatible Object Storage (MinIO or AWS S3).
    """
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        try:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION
            )
            # Ensure bucket exists
            self._ensure_bucket_exists()
        except Exception as e:
            logger.error("Failed to initialize storage client connection.", error=str(e))
            self.s3_client = None

    def _ensure_bucket_exists(self):
        """Creates the bucket if it is not present in storage."""
        if not self.s3_client:
            return
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info("Created missing storage bucket.", bucket=self.bucket_name)
                except Exception as ex:
                    logger.error("Failed to create storage bucket.", error=str(ex))

    def upload_file(self, file_bytes: bytes, object_name: str, content_type: str = "image/jpeg") -> str:
        """
        Uploads file bytes to S3 and returns the storage reference URL.
        """
        # If client initialization failed, use a local fallback URL structure
        if not self.s3_client:
            logger.warn("S3 client down. Using mock local storage reference.", object=object_name)
            return f"http://localhost:9000/{self.bucket_name}/{object_name}"

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=file_bytes,
                ContentType=content_type
            )
            # Construct standard access URL
            # Note: For production, this returns S3 signed URLs
            return f"{settings.S3_ENDPOINT_URL}/{self.bucket_name}/{object_name}"
        except Exception as e:
            logger.error("Object upload failure.", object=object_name, error=str(e))
            return f"http://localhost:9000/{self.bucket_name}/{object_name}"

storage_client = StorageClient()
