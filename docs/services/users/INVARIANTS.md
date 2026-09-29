# users — инварианты

| Правило | Где обеспечено |
|---|---|
| `telegram_id` уникален: проверка перед вставкой + `UNIQUE` в БД; нарушение — 409 | [`PostgresUserRepository.create`](../../../src/users/adapters/postgres.py) |
| `telegram_id` может быть `NULL` (пользователь без Telegram, создан админом) | `Mapped[int | None]` в [`UserRow`](../../../src/shared/orm/models.py) |
| `POST /users/` только у админа: роль `admin` нельзя выдать себе при регистрации | [`endpoints/users.py`](../../../src/bootstrap/endpoints/users.py) |
| Роль читается из БД при каждом запросе; смена роли SQL-командой действует сразу | [`AuthenticateByToken`](../../../src/auth/uc/session.py) |
| Обычные пользователи не могут читать чужие профили (`/users/*` только админу); свой — через `/auth/me` | `get_current_admin` |
| Удаления пользователей нет; `orders.user_id` — nullable (заказ переживёт пользователя, если его удалят SQL-ом) | [`OrderRow.user_id`](../../../src/shared/orm/models.py) |

Тесты: [`test_users.py`](../../../tests/cases/groups/test_users.py).
