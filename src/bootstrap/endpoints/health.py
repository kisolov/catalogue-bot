from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", operation_id="health", summary="Проверка живости сервиса")
async def health() -> dict[str, str]:
    return {"status": "ok"}
