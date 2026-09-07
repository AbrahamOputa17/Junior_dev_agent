import os
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

API_KEY_ENV_VAR = "JUNIOR_DEV_API_KEY"

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude dashboard, docs, and health checks from auth
        if request.url.path in ["/", "/dashboard", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        expected_api_key = os.getenv(API_KEY_ENV_VAR)
        if expected_api_key:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Missing or invalid Authorization header", "code": "UNAUTHORIZED"}
                )
            token = auth_header.split(" ", 1)[1].strip()
            if token != expected_api_key:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Invalid API key provided", "code": "FORBIDDEN"}
                )

        response = await call_next(request)
        return response
