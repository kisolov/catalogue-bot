from fastapi import HTTPException


def http_exception_wrapper(status):
    async def handler(request, exc):
        raise HTTPException(status, detail=str(exc))

    return handler
