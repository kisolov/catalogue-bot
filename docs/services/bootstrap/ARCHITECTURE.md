# bootstrap — HTTP-слой

Входные адаптеры: [`src/bootstrap`](../../../src/bootstrap). Здесь FastAPI-приложение,
маршруты, зависимости авторизации, middleware и превращение исключений в HTTP-ответы.
Бизнес-логики нет: endpoint вызывает только use case.

## Сборка приложения

[`ServerFactory`](../../../src/bootstrap/server_factory.py) создаёт FastAPI (`root_path=/api`),
подключает роутеры, CORS, [`LoggingMiddleware`](../../../src/bootstrap/utils/logging_middleware.py)
(логирует запрос и ответ, тело до 4096 байт; `Authorization`, `Cookie` и поля `token`/`init_data`/`hash`/`password` маскируются `***`, не-JSON тело не пишется) и uvicorn (`proxy_headers=True`,
`forwarded_allow_ips` из настроек). Точка входа — [`main.py`](../../../main.py): читает настройки
(нет обязательных — падение при старте), поднимает ресурсы контейнера, запускает сервер и
в `finally` освобождает ресурсы.

## Авторизация

Зависимости [`bootstrap/dependencies/auth.py`](../../../src/bootstrap/dependencies/auth.py):

| Зависимость | Что делает | Отказ |
|---|---|---|
| `get_bearer_token` | достаёт токен из `Authorization: Bearer <jwt>` | нет заголовка / не `Bearer` → 401 |
| `get_current_user` | токен → пользователь через use case [`AuthenticateByToken`](../../../src/auth/uc/session.py) | просрочен/отозван/неизвестен → 401 |
| `get_current_admin` | `get_current_user` + роль `admin` | не админ → 403 |

Исключения доменные; статусы 401/403 назначает `server_factory`.

## Endpoint'ы

Таблицы по доменам — в их `ARCHITECTURE.md`. Общее:

| Правило | Как |
|---|---|
| Endpoint принимает и отдаёт pydantic-модели, не ORM | `schema.py` домена |
| Роль читается из БД при каждом запросе | `AuthenticateByToken` → `UserService.get_by_id` |
| Чтение каталога публичное, изменение — `A` | `Depends(get_current_admin)` |
| `/health` без авторизации, без БД и Redis | `{"status": "ok"}`, используется healthcheck'ом Docker |

## Обработка ошибок

Таблица «исключение → HTTP» — в [shared](../shared/ARCHITECTURE.md#исключения).
[`http_exception_wrapper`](../../../src/bootstrap/utils/http_exception_wrapper.py) для каждого
отказа пишет `WARNING` (`Business rejection`, класс исключения, статус, путь) и возвращает
`{"detail": "<сообщение>"}`.

Ошибки валидации запроса (`RequestValidationError`) → 422, тело:

```json
{"detail": {"error": "ValidationError", "message": "Ошибка валидации входных данных",
            "request": {"method": "...", "url": "..."},
            "errors": [{"field": "...", "path": "body.field", "type": "missing", "message": "..."}]}}
```

Значения, присланные клиентом, в ответ не возвращаются, `url` — только путь. Отказ пишется
одной строкой `WARNING` («Validation rejection», путь и число ошибок).

## Middleware

| Middleware | Роль |
|---|---|
| CORS | `allow_origins` из `SERVER_ALLOWED_ORIGINS` (`*` запрещён валидатором настроек), credentials выключены (токен в `Authorization`, cookie нет), методы GET/POST/PUT/PATCH/DELETE, заголовки `Authorization` и `Content-Type` |
| [`LoggingMiddleware`](../../../src/bootstrap/utils/logging_middleware.py) | лог запросов/ответов |
| [`WebhookBypassMiddleware`](../../../src/bootstrap/utils/webhook_bypass_middleware.py) | для пути `/webhook` добавляет `Access-Control-Allow-Origin: *`; маршрута `/webhook` в проекте нет, остался от исходного кода |
