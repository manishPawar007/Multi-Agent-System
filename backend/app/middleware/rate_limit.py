import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if client_ip in self.client_requests:
            count, start_time = self.client_requests[client_ip]
            if now - start_time < 60:
                if count >= self.requests_per_minute:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Try again in a minute."
                    )
                self.client_requests[client_ip] = (count + 1, start_time)
            else:
                self.client_requests[client_ip] = (1, now)
        else:
            self.client_requests[client_ip] = (1, now)

        return await call_next(request)
