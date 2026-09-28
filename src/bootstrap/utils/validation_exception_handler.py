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
        input_type = error.get("input", None)

        if error_type == "missing":
            message = f"Поле '{field_name}' обязательно, но отсутствует в запросе."
        elif error_type == "type_error":
            expected = error.get("expected_type", "неизвестно")
            message = (
                f"Поле '{field_name}' имеет неверный тип. "
                f"Ожидается: {expected}. Получено: {input_type}."
            )
        else:
            message = f"Ошибка в поле '{field_name}': {error_msg}"

        errors.append(
            {
                "field": field_name,
                "path": field_path,
                "type": error_type,
                "message": message,
                "input": str(input_type),
            }
        )

    logger.error(type(exc), exc, exc_info=True)
    response = {
        "detail": {
            "error": "ValidationError",
            "message": "Ошибка валидации входных данных",
            "request": {
                "method": request.method,
                "url": str(request.url),
            },
            "errors": errors,
        }
    }
    return JSONResponse(
        status_code=422,
        content=response,
    )
