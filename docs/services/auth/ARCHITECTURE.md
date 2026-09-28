# auth

Вход через Telegram Mini App и JWT-сессии. Пароля и регистрации нет: личность подтверждается
подписью `initData`, выданной Telegram.

## Компоненты

| Компонент | Роль | Файл |
|---|---|---|
| `TelegramInitDataService` | проверка подписи и возраста `initData`; чистая логика, без порта | [`telegram.py`](../../../src/auth/telegram.py) |
| `TokenService` | выпуск, проверка, отзыв JWT | [`services.py`](../../../src/auth/services.py) |
| `TokenRepository` (port) → `RedisTokenRepository` | хранит выданные токены `ключ → user_id` с TTL | [`ports.py`](../../../src/auth/ports.py), [`redis_adapter.py`](../../../src/auth/redis_adapter.py) |
| `LoginWithTelegram`, `Logout` | сценарии входа/выхода | [`uc/telegram.py`](../../../src/auth/uc/telegram.py) |
| `AuthenticateByToken`, `GetMe` | токен → пользователь; профиль | [`uc/session.py`](../../../src/auth/uc/session.py) |
| DTO | `TelegramLoginRequest {init_data}`, `TokenResponse {access_token, token_type, user}` | [`schema.py`](../../../src/auth/schema.py) |

Домен зависит от [users](../users/ARCHITECTURE.md): `UserService` в use case'ах.

## Endpoint'ы

[`endpoints/auth.py`](../../../src/bootstrap/endpoints/auth.py)

| Метод | Путь | Авт. | Use case | Ответ |
|---|---|---|---|---|
| POST | `/auth/telegram` | — | `LoginWithTelegram` | 200 `{access_token, token_type: "bearer", user}`; 401 при неверной/устаревшей подписи |
| GET | `/auth/me` | U | `GetMe` | `User` |
| POST | `/auth/logout` | U | `Logout` | 204; токен отозван |

Авторизация запросов — заголовок `Authorization: Bearer <access_token>`; зависимости описаны в
[bootstrap](../bootstrap/ARCHITECTURE.md#авторизация).

## Токен

| Параметр | Значение |
|---|---|
| Алгоритм / ключ | `JWT_ALGORITHM` (`HS256`) / `JWT_SECRET_KEY` |
| Payload | `sub` = id пользователя, `exp` |
| Срок жизни | `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` (24 ч) |
| Хранилище | Redis, ключ `<REDIS_PREFIX>:<jwt>` → `user_id`, TTL = срок токена |
| Refresh | нет; по истечении — новый вход через Telegram |
