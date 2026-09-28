# Инварианты

| Правило | Где обеспечено |
|---|---|
| Переходы заказа: `new→processing\|cancelled`, `processing→shipped\|cancelled`, `shipped→delivered`; `delivered` и `cancelled` конечные. Иначе 409 | [`ALLOWED_TRANSITIONS`](../../src/orders/models.py), [`OrderService.change_status`](../../src/orders/services.py) |
| Владелец может отменить только заказ в `new`; остальное — через админа | [`OrderService.cancel_by_owner`](../../src/orders/services.py) |
| Чужой заказ неотличим от несуществующего (404, не 403) — не раскрываем существование | [`OrderService.get_visible`](../../src/orders/services.py) |
| `OrderItem` хранит цену и название на момент заказа; правки товара заказ не меняют | [`create_from_cart`](../../src/orders/adapters/pony.py) |
| Остаток не уходит в минус при параллельных заказах | `get_for_update` по товару в [`create_from_cart`](../../src/orders/adapters/pony.py) |
| Товар, попавший в заказ, нельзя удалить (409), иначе пропали бы позиции заказов | [`PonyProductRepository.delete`](../../src/products/adapters/pony.py) |
| Категорию с товарами или подкатегориями нельзя удалить (409) | [`PonyCategoryRepository.delete`](../../src/categories/adapters/pony.py) |
| `sku` и `description` товара могут быть `NULL`; `sku` уникален, поэтому пустая строка недопустима | `nullable=True` в [`models.py`](../../src/shared/orm/models.py) |
| `POST /users/` только у админа: роль `admin` нельзя выдать себе при регистрации | [`endpoints/users.py`](../../src/bootstrap/endpoints/users.py) |
| Первый вход создаёт пользователя только с ролью `user`; роль существующего не меняется | [`LoginWithTelegram`](../../src/auth/uc/telegram.py) |
| `initData` принимается, если подпись верна и `auth_date` не старше `TELEGRAM_INIT_DATA_MAX_AGE_SECONDS` (24 ч) и не «из будущего» (>60 с) | [`TelegramInitDataService`](../../src/auth/telegram.py) |
| Токен действителен, только пока он есть в Redis: `logout` отзывает его немедленно | [`TokenService.verify_token`](../../src/auth/services.py) |
| Валидный токен удалённого пользователя — 401 (`InvalidTokenException`), не 404 | [`AuthenticateByToken`](../../src/auth/uc/session.py) |
| Каждый файл миграции применяется один раз (`schema_migrations`); БД без этой таблицы, но с `users`, считается уже мигрированной | [`create_tables_from_migrations`](../../src/shared/db.py) |

## Особенности Pony ORM

- Pony по умолчанию каскадно удаляет зависимые сущности и **обходит** `ON DELETE RESTRICT`
  из БД — поэтому проверки перед `delete()` явные.
- `Optional(str)` не принимает `None`, если не указано `nullable=True`.
