import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from backend.app.utils.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Path: {request.url.path} | Method: {request.method} | "
            f"Status: {response.status_code} | Duration: {process_time:.2f}ms"
        )
        response.headers["X-Process-Time-Ms"] = str(process_time)
        return response
