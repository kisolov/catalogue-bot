# users

Пользователи Mini App. Создаются автоматически при первом входе ([auth](../auth/DATA_FLOWS.md)),
вручную — только админом. Обновления и удаления пользователей нет; роль `admin` выдаётся SQL-командой
(см. [README](../../../README.md)).

## Сущности

| Сущность | Поля |
|---|---|
| [`User`](../../../src/users/models.py) | `id`, `telegram_id` (nullable, уникален), `role` (`user`/`admin`, по умолчанию `user`), `created_at`, `updated_at` |
| `CreateUserCmd` | `telegram_id?`, `role` (по умолчанию `user`) |

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`UserRepository`](../../../src/users/ports.py) → [`PostgresUserRepository`](../../../src/users/adapters/postgres.py) (`get_by_id`, `get_by_telegram_id`, `create`) |
| Service | [`UserService`](../../../src/users/services.py) — тонкая обёртка над портом |
| Use case | [`CreateUser`, `GetUserById`, `GetUserByTelegramId`](../../../src/users/uc/crud.py) |
| DTO | [`CreateUserRequest`](../../../src/users/schema.py) |

## Endpoint'ы

[`endpoints/users.py`](../../../src/bootstrap/endpoints/users.py), все только для админа (**A**).

| Метод | Путь | Use case | Ответ |
|---|---|---|---|
| POST | `/users/` | `CreateUser` | 201, `User`; 409 если `telegram_id` занят |
| GET | `/users/{user_id}` | `GetUserById` | `User`; 404 |
| GET | `/users/by_telegram/{telegram_id}` | `GetUserByTelegramId` | `User`; 404 |

Другие домены используют `UserService` напрямую из своих use case'ов: [auth](../auth/ARCHITECTURE.md).
