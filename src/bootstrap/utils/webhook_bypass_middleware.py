from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class WebhookBypassMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/webhook":
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = "*"
            return response
        return await call_next(request)
