# shared — БД, ORM, миграции, исключения, настройки, логи

Код общий для всех доменов: [`src/shared`](../../../src/shared), [`settings.py`](../../../settings.py),
[`migrations/`](../../../migrations/sql/db.sql). Бизнес-логики здесь нет.

## Модель данных

```mermaid
erDiagram
    users ||--o{ cart_items : "хранит"
    users ||--o{ orders : "оформляет"
    users ||--o{ favorites : "отмечает"
    categories ||--o{ categories : "родитель"
    categories ||--o{ products : "содержит"
    products ||--o{ cart_items : ""
    products ||--o{ order_items : ""
    products ||--o{ favorites : ""
    orders ||--|{ order_items : "состоит из"
```

| Таблица | Ключевые поля и ограничения БД |
|---|---|
| `users` | `telegram_id BIGINT UNIQUE`, `role` enum `user`/`admin` |
| `categories` | `slug UNIQUE`, `parent_id → categories` |
| `products` | `slug UNIQUE`, `sku UNIQUE` (может быть `NULL`), `price >= 0`, `stock >= 0`, `compare_at_price >= price`, `category_id → categories` (RESTRICT), `fts` (tsvector, триггер) |
| `cart_items` | `UNIQUE(user_id, product_id)`, `quantity BETWEEN 1 AND 1000` |
| `orders` | `status`, `total_price >= 0`, `user_id → users` |
| `order_items` | `price >= 0`, `quantity > 0`, `order_id → orders`, `product_id → products` (RESTRICT) |
| `favorites` | `UNIQUE(user_id, product_id)` |

Схема — [`db.sql`](../../../migrations/sql/db.sql) и [`db_002_products_category_restrict.sql`](../../../migrations/sql/db_002_products_category_restrict.sql). Строки таблиц (`*Row`, SQLAlchemy 2.0) —
[`shared/orm/models.py`](../../../src/shared/orm/models.py); доменные pydantic-модели от них
независимы, адаптеры переводят одно в другое. `relationship` нет намеренно: в async ленивая
подгрузка недоступна, поэтому внешние ключи читаются как обычные колонки, а связанные данные
адаптер запрашивает явно. Типы `user_role_enum` и `order_status_enum` создаёт миграция, ORM только их использует.

## Доступ к БД и асинхронность

[`Database`](../../../src/shared/db.py) — async-движок SQLAlchemy 2.0 поверх `asyncpg`; регистрируется в DI
обычным `Singleton`, конструктор ничего не подключает (соединения открываются лениво).

| Что | Как |
|---|---|
| Транзакция | `async with db.transaction() as session` — одна на операцию адаптера: коммит при выходе, откат при любом исключении, в том числе доменном |
| Пул | `pool_size = DB_POOL_MIN_SIZE`, `max_overflow = MAX − MIN` (`DB_POOL_MAX_SIZE`), `pool_pre_ping`; `search_path` задаётся схемой `DB_SCHEMA` |
| Порты и сервисы | все методы репозиториев и сервисов — `async`, цепочка endpoint → use case → service → port везде с `await`: запрос к БД не блокирует event loop |
| Redis | `redis.asyncio`, порт токенов тоже асинхронный |
| Жизненный цикл | [`main.py`](../../../main.py): `migrate()` на старте, `dispose()` и `close()` Redis при остановке |

Объекты `*Row` живут только внутри транзакции адаптера (`expire_on_commit=False`), наружу уходят
доменные модели. Значения по умолчанию (`created_at`, `role`, …) адаптер задаёт явно, а не читает из БД после вставки.

## Миграции

[`Database.migrate`](../../../src/shared/db.py) на старте применяет каждый `.sql`
из каталога миграций один раз, в алфавитном порядке и в одной транзакции (через сырое
соединение `asyncpg`: тела функций с `;` внутри `$BODY$` не влезают в prepared statement) (поэтому дополнительные файлы называются
`db_00N_…`, а не `00N_…`, иначе они шли бы раньше `db.sql`); имена применённых лежат в
`schema_migrations`. Если этой таблицы нет, но есть `users`, считается применённой только
`db.sql` (совместимость со старыми установками), остальные выполняются. Повторный запуск безопасен.

## Настройки

Один класс на подсистему, читаются только через [`settings.py`](../../../settings.py) и
регистрируются в [`di.py`](../../../di.py). Секреты — `SecretStr`. Обязательные переменные
проверяются при старте.

| Класс | Префикс | Переменные (по умолчанию) |
|---|---|---|
| `ServerSettings` | `SERVER_` | `HOST`, `PORT`, `ALLOWED_ORIGINS` (JSON-список, `*` запрещён), `FORWARDED_ALLOW_IPS` (`127.0.0.1`, `*` запрещён), `DOCS_ENABLED` (`true`; в compose по умолчанию `false`) |
| `DatabaseSettings` | `DB_` | `HOST` (`localhost`), `PORT` (`5432`), `USER`, `PASSWORD`, `NAME`, `SCHEMA`, `POOL_MIN_SIZE` (`5`), `POOL_MAX_SIZE` (`20`), `TIMEOUT` (`30`, подключение), `MIGRATIONS_PATH` |
| `RedisSettings` | `REDIS_` | `HOST`, `PORT` (`6379`), `DB` (`0`), `PASSWORD`, `SSL`, `TIMEOUT`, `PREFIX` (`app:`) |
| `JWTSettings` | `JWT_` | `SECRET_KEY`, `ALGORITHM` (`HS256`), `ACCESS_TOKEN_EXPIRES_MINUTES` (720, допустимо 1…10080) |
| `TelegramSettings` | `TELEGRAM_` | `BOT_TOKEN`, `INIT_DATA_MAX_AGE_SECONDS` (86400) |

Обязательны без значения по умолчанию: `DB_PASSWORD`, `REDIS_PASSWORD` (compose), `JWT_SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, `SERVER_ALLOWED_ORIGINS`
(плюс `DB_USER`, `DB_NAME`, `DB_SCHEMA`, `SERVER_*` в compose задаются сами). Образец — [`.env.example`](../../../.env.example).

## Пагинация

[`Pagination`](../../../src/shared/pagination.py): `limit` 1..100 (по умолчанию 50), `offset` ≥ 0.
Её принимают списки товаров, категорий и заказов (`page` в use case, сервисе, порте и адаптере);
без `page` адаптер вернёт всё. Порядок стабильный: товары и категории по возрастанию `id`,
заказы по убыванию. Ответ остаётся массивом, общее число не возвращается.

## Исключения

[`shared/exceptions.py`](../../../src/shared/exceptions.py): все бизнес-ошибки — `DomainException`.
Домены их бросают, HTTP-статус назначает только [`server_factory`](../../../src/bootstrap/server_factory.py).

| Исключение | HTTP | Когда |
|---|---|---|
| `NotFoundException` | 404 | объект не найден; для чужого заказа тоже |
| `MappingException` | 400 | ошибка преобразования данных |
| `UniqueViolationException` | 409 | нарушена уникальность (slug, sku, telegram_id, позиция корзины/избранного) |
| `ProductInUseException` | 409 | удаление товара, попавшего в заказ |
| `CategoryNotEmptyException` | 409 | удаление категории с товарами/подкатегориями |
| `InvalidCategoryParentException` | 422 | родитель категории — она сама или её потомок |
| `InvalidProductPriceException` | 422 | `compare_at_price` меньше `price` (в том числе после PATCH одного из полей) |
| `InvalidCartQuantityException` | 422 | сумма количества позиции корзины больше 1000 |
| `EmptyCartException` | 409 | заказ при пустой корзине |
| `InsufficientStockException` | 409 | остаток меньше количества в корзине |
| `ProductUnavailableException` | 409 | товар в заказе неактивен |
| `InvalidOrderTransitionException` | 409 | переход статуса вне матрицы |
| `InvalidInitDataException` | 401 | подпись `initData` не сошлась / нет полей |
| `InitDataExpiredException` | 401 | `auth_date` слишком старый или «из будущего» |
| `NotAuthenticatedException` | 401 | нет заголовка `Authorization` или схема не `Bearer` |
| `TokenException` (`TokenExpired…`, `InvalidToken…`) | 401 | токен просрочен, не подписан, отозван; пользователь удалён |
| `PermissionDeniedException` | 403 | не админ на admin-endpoint |

Формат ответа об ошибке: `{"detail": "<сообщение>"}`; ошибки валидации запроса — 422
с подробным телом (см. [bootstrap](../bootstrap/ARCHITECTURE.md)).

## Логи

[`shared/logger.py`](../../../src/shared/logger.py): корневой логгер, вывод в консоль и в
`logs/bot.log` (JSON, ротация 1 МБ × 5). Успех сценария пишет use case (`INFO`, константное
сообщение, в `extra` только id/коды), бизнес-отказ — `WARNING` в одном месте
([`http_exception_wrapper`](../../../src/bootstrap/utils/http_exception_wrapper.py)).
Секреты и данные пользователя в логи не пишутся: `LoggingMiddleware` маскирует токены и `initData` ([`mask_headers`/`mask_body`](../../../src/bootstrap/utils/logging_middleware.py)).
