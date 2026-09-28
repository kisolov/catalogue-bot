from typing import Optional, Callable, Awaitable
from fastapi import Request, Response
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware
import logging


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        logger: Optional[logging.Logger] = None,
        log_request: bool = True,
        log_response: bool = True,
        max_body_length: int = 1024,
    ) -> None:
        super().__init__(app)
        self.logger = logger or logging.getLogger("uvicorn.access")
        self.log_request = log_request
        self.log_response = log_response
        self.max_body_length = max_body_length

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if self.log_request:
            await self._log_request(request)

        response = await self._intercept_response(call_next, request)

        if self.log_response:
            await self._log_response(response)

        return response

    async def _intercept_response(
        self, call_next: Callable[[Request], Awaitable[Response]], request: Request
    ) -> Response:
        response = await call_next(request)

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        from fastapi.responses import Response as FastAPIResponse

        intercepted_response = FastAPIResponse(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        setattr(intercepted_response, "_body", response_body)

        return intercepted_response

    async def _log_request(self, request: Request) -> None:
        body = await self._get_body(request)
        self.logger.info(
            f"Request: method={request.method} path={request.url.path} "
            f"headers={dict(request.headers)} body={body}"
        )

    async def _log_response(self, response: Response) -> None:
        body = getattr(response, "_body", b"")
        if len(body) > self.max_body_length:
            body_str = f"<body_too_large {len(body)} bytes>"
        else:
            body_str = body.decode(errors="replace")

        self.logger.info(
            f"Response: status_code={response.status_code} "
            f"headers={dict(response.headers)} body={body_str}"
        )

    async def _get_body(self, request: Request) -> str:
        body_bytes = await request.body()
        if len(body_bytes) > self.max_body_length:
            return f"<body_too_large {len(body_bytes)} bytes>"
        return body_bytes.decode(errors="replace")
