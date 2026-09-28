from fastapi.responses import JSONResponse

from src.shared.logger import logger


def http_exception_wrapper(status):
    async def handler(request, exc):
        logger.warning(
            "Business rejection",
            extra={
                "exception": exc.__class__.__name__,
                "status": status,
                "path": request.url.path,
            },
        )
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    return handler
