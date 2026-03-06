import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request and response details.
    Includes slow request detection.
    """
    SLOW_REQUEST_THRESHOLD = 0.5  # 500ms
    
    async def dispatch(self, request: Request, call_next):
        # Use IDs from state (set by RequestContextMiddleware)
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            start_time = getattr(request.state, "start_time", time.time())
            process_time = time.time() - start_time
            
            # Log response
            log_method = logger.info if process_time < self.SLOW_REQUEST_THRESHOLD else logger.warning
            
            log_method(
                "request_finished",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=int(process_time * 1000),
                slow_request=process_time >= self.SLOW_REQUEST_THRESHOLD
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - getattr(request.state, "start_time", time.time())
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=int(process_time * 1000)
            )
            raise e
