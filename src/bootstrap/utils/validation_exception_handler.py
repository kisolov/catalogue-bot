from typing import Dict, List
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.shared.logger import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: List[Dict[str, str]] = []

    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"])
        field_name = error["loc"][-1]
        error_type = error["type"]
        error_msg = error["msg"]

        if error_type == "missing":
            message = f"Поле '{field_name}' обязательно, но отсутствует в запросе."
        elif error_type == "type_error":
            expected = error.get("expected_type", "неизвестно")
            message = (
                f"Поле '{field_name}' имеет неверный тип. " f"Ожидается: {expected}."
            )
        else:
            message = f"Ошибка в поле '{field_name}': {error_msg}"

        errors.append(
            {
                "field": field_name,
                "path": field_path,
                "type": error_type,
                "message": message,
            }
        )

    logger.warning(
        "Validation rejection", extra={"path": request.url.path, "errors": len(errors)}
    )
    response = {
        "detail": {
            "error": "ValidationError",
            "message": "Ошибка валидации входных данных",
            "request": {
                "method": request.method,
                "url": request.url.path,
            },
            "errors": errors,
        }
    }
    return JSONResponse(
        status_code=422,
        content=response,
    )
