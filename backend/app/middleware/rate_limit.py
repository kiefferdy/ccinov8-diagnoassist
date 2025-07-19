"""
Rate limiting middleware for DiagnoAssist Backend
"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict, deque


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store requests as (timestamp, count) per IP
        self.requests: Dict[str, deque] = defaultdict(deque)
        
        # Rate limit configurations
        self.limits = {
            "default": (100, 60),  # 100 requests per minute
            "auth": (10, 60),      # 10 auth requests per minute
            "login": (5, 300),     # 5 login attempts per 5 minutes
        }
    
    def is_allowed(self, client_ip: str, endpoint_type: str = "default") -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        max_requests, window_seconds = self.limits.get(endpoint_type, self.limits["default"])
        current_time = time.time()
        
        # Clean old requests outside the window
        requests_queue = self.requests[client_ip]
        while requests_queue and requests_queue[0] <= current_time - window_seconds:
            requests_queue.popleft()
        
        # Check if under limit
        current_count = len(requests_queue)
        
        if current_count >= max_requests:
            # Rate limit exceeded
            oldest_request = requests_queue[0] if requests_queue else current_time
            retry_after = int(oldest_request + window_seconds - current_time)
            
            return False, {
                "error": "Rate limit exceeded",
                "retry_after": max(retry_after, 1),
                "limit": max_requests,
                "window": window_seconds,
                "current": current_count
            }
        
        # Add current request
        requests_queue.append(current_time)
        
        return True, {
            "limit": max_requests,
            "window": window_seconds,
            "current": current_count + 1,
            "remaining": max_requests - current_count - 1
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware interface"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract client IP
        client_ip = self._get_client_ip(scope)
        
        # Determine endpoint type for rate limiting
        path = scope.get("path", "")
        endpoint_type = self._get_endpoint_type(path)
        
        # Check rate limit
        allowed, rate_info = rate_limiter.is_allowed(client_ip, endpoint_type)
        
        if not allowed:
            # Rate limit exceeded
            response = {
                "status_code": 429,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"retry-after", str(rate_info["retry_after"]).encode()),
                    (b"x-ratelimit-limit", str(rate_info["limit"]).encode()),
                    (b"x-ratelimit-window", str(rate_info["window"]).encode()),
                    (b"x-ratelimit-current", str(rate_info["current"]).encode()),
                ],
                "body": {
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": rate_info["error"],
                        "details": {
                            "retry_after": rate_info["retry_after"],
                            "limit": rate_info["limit"],
                            "window_seconds": rate_info["window"]
                        }
                    }
                }
            }
            
            await send({
                "type": "http.response.start",
                "status": response["status_code"],
                "headers": response["headers"]
            })
            
            import json
            await send({
                "type": "http.response.body",
                "body": json.dumps(response["body"]).encode()
            })
            return
        
        # Add rate limit headers to response
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.extend([
                    (b"x-ratelimit-limit", str(rate_info["limit"]).encode()),
                    (b"x-ratelimit-remaining", str(rate_info["remaining"]).encode()),
                    (b"x-ratelimit-window", str(rate_info["window"]).encode()),
                ])
                message["headers"] = headers
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _get_client_ip(self, scope) -> str:
        """Extract client IP from scope"""
        # Check for forwarded headers first
        headers = dict(scope.get("headers", []))
        
        # X-Forwarded-For header
        x_forwarded_for = headers.get(b"x-forwarded-for")
        if x_forwarded_for:
            return x_forwarded_for.decode().split(",")[0].strip()
        
        # X-Real-IP header
        x_real_ip = headers.get(b"x-real-ip")
        if x_real_ip:
            return x_real_ip.decode().strip()
        
        # Fallback to client IP from scope
        client = scope.get("client")
        if client:
            return client[0]
        
        return "unknown"
    
    def _get_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting"""
        if "/auth/login" in path:
            return "login"
        elif "/auth/" in path:
            return "auth"
        else:
            return "default"


def create_rate_limit_dependency(endpoint_type: str = "default"):
    """Create a dependency for rate limiting specific endpoints"""
    
    async def rate_limit_check(request: Request):
        """Check rate limit for specific endpoint"""
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded headers
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(",")[0].strip()
        elif request.headers.get("x-real-ip"):
            client_ip = request.headers.get("x-real-ip")
        
        allowed, rate_info = rate_limiter.is_allowed(client_ip, endpoint_type)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=rate_info["error"],
                headers={
                    "Retry-After": str(rate_info["retry_after"]),
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Window": str(rate_info["window"]),
                }
            )
        
        return True
    
    return rate_limit_check


# Common rate limit dependencies
auth_rate_limit = create_rate_limit_dependency("auth")
login_rate_limit = create_rate_limit_dependency("login")