import time
import threading
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from collections import defaultdict
from src.config import settings
import structlog

logger = structlog.get_logger()

class RateLimiter:
    """
    Lightweight, in-memory sliding window rate limiter.
    Thread-safe and natively integrated for local FastAPI deployments.
    """
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.lock = threading.Lock()

    def _get_client_id(self, request: Request) -> str:
        """
        Sensible client identification for local environments.
        DO NOT trust X-Forwarded-For locally without trusted proxy config.
        """
        # For local use, client.host is safe.
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def __call__(self, request: Request):
        client_id = self._get_client_id(request)
        current_time = time.time()

        with self.lock:
            # Clean up old timestamps (sliding window)
            active_requests = [
                ts for ts in self.requests[client_id] 
                if current_time - ts <= self.window_seconds
            ]
            
            if len(active_requests) >= self.limit:
                # Retain the active window before throwing error
                self.requests[client_id] = active_requests
                
                logger.warning(
                    "Rate limit exceeded.",
                    client_id=client_id,
                    endpoint=request.url.path,
                    limit=self.limit
                )
                
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please wait and try again.",
                    headers={"Retry-After": str(self.window_seconds)}
                )
            
            # Record the new request
            active_requests.append(current_time)
            self.requests[client_id] = active_requests

# Instantiate endpoints' specific limiters
verify_rate_limiter = RateLimiter(
    limit=settings.VERIFY_RATE_LIMIT,
    window_seconds=settings.VERIFY_RATE_WINDOW_SECONDS
)

auth_rate_limiter = RateLimiter(
    limit=settings.AUTH_RATE_LIMIT,
    window_seconds=settings.AUTH_RATE_WINDOW_SECONDS
)
