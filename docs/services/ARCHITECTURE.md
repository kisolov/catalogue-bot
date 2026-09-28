# Архитектура backend

Один деплоймент (монолит), одна БД PostgreSQL, Redis для токенов. Backend каталога товаров
для Telegram Mini App: вход через Telegram, каталог, корзина, избранное, заказы.

Цепочка вызовов, всегда в одну сторону:

```
endpoint → use case → service → port ← adapter
```

| Слой | Знает о | Не знает о |
|---|---|---|
| endpoint (`bootstrap/endpoints`) | use case, `schema`, модели домена | service, port, adapter |
| use case (`<домен>/uc`) | сервисы (свои и чужих доменов) | ports, adapters |
| service (`<домен>/services.py`) | свой port | adapters, FastAPI, ORM |
| adapter (`<домен>/adapters`) | свой port, ORM/Redis | вышележащие слои |

Сборка — [`di.py`](../../di.py): порты объявлены как `AbstractSingleton`, к адаптерам привязаны
через `override` в одном месте.

## Карта документации

| Что | Где |
|---|---|
| Домены (у каждого `ARCHITECTURE.md` и `INVARIANTS.md`) | [users](users/ARCHITECTURE.md) · [auth](auth/ARCHITECTURE.md) · [products](products/ARCHITECTURE.md) · [categories](categories/ARCHITECTURE.md) · [cart](cart/ARCHITECTURE.md) · [wishlist](wishlist/ARCHITECTURE.md) · [orders](orders/ARCHITECTURE.md) |
| HTTP-слой: endpoint'ы, авторизация, ошибки, middleware | [bootstrap](bootstrap/ARCHITECTURE.md) |
| БД, ORM, миграции, исключения, настройки, логи | [shared](shared/ARCHITECTURE.md) |
| Сквозные сценарии | [DATA_FLOWS.md](DATA_FLOWS.md) |
| Отказы Postgres/Redis | [FAILURE_MODES.md](FAILURE_MODES.md) |
| Почему так, а не иначе | [DESIGN.md](DESIGN.md) |

## Домены

| Домен | Сущности | Порт → адаптер |
|---|---|---|
| [users](../../src/users) | `User` (`telegram_id` уникален, роль `user`/`admin`) | [`UserRepository`](../../src/users/ports.py) → [`PonyUserRepository`](../../src/users/adapters/pony.py) |
| [auth](../../src/auth) | JWT, `initData` Telegram | [`TokenRepository`](../../src/auth/ports.py) → [`RedisTokenRepository`](../../src/auth/redis_adapter.py) |
| [products](../../src/products) | `Product` (цена, остаток, `is_active`, категория) | [`ProductRepository`](../../src/products/ports.py) → [`PonyProductRepository`](../../src/products/adapters/pony.py) |
| [categories](../../src/categories) | `Category` (дерево через `parent_id`) | [`CategoryRepository`](../../src/categories/ports.py) → [`PonyCategoryRepository`](../../src/categories/adapters/pony.py) |
| [cart](../../src/cart) | `Cart`, `CartItem` (уникален по user+product) | [`CartRepository`](../../src/cart/ports.py) → [`PonyCartRepository`](../../src/cart/adapters/pony.py) |
| [wishlist](../../src/wishlist) | `Favorite` | [`WishlistRepository`](../../src/wishlist/ports.py) → [`PonyWishlistRepository`](../../src/wishlist/adapters/pony.py) |
| [orders](../../src/orders) | `Order`, `OrderItem` (снимок цены и названия), `OrderStatus` | [`OrderRepository`](../../src/orders/ports.py) → [`PonyOrderRepository`](../../src/orders/adapters/pony.py) |

Зависимости между доменами: `auth` → `users` (use case входа и проверки токена используют
`UserService`); `orders` читает таблицы корзины и товаров прямо в адаптере
(одна транзакция, см. [DESIGN.md](DESIGN.md)). Остальные домены независимы.

## Все endpoint'ы

Префикс `/api` (nginx и `root_path`). Авторизация: — нет, **U** любой вошедший, **A** админ.

| Метод | Путь | Авт. | Домен |
|---|---|---|---|
| GET | `/health` | — | [bootstrap](bootstrap/ARCHITECTURE.md) |
| POST | `/auth/telegram` | — | [auth](auth/ARCHITECTURE.md) |
| GET | `/auth/me` | U | auth |
| POST | `/auth/logout` | U | auth |
| POST | `/users/` | A | [users](users/ARCHITECTURE.md) |
| GET | `/users/{user_id}`, `/users/by_telegram/{telegram_id}` | A | users |
| GET | `/products/`, `/products/{id}` | — | [products](products/ARCHITECTURE.md) |
| POST / PATCH / DELETE | `/products/`, `/products/{id}` | A | products |
| GET | `/categories/`, `/categories/{id}` | — | [categories](categories/ARCHITECTURE.md) |
| POST / PATCH / DELETE | `/categories/`, `/categories/{id}` | A | categories |
| GET / POST / DELETE | `/cart/products`, `/cart/products/{product_id}` | U | [cart](cart/ARCHITECTURE.md) |
| GET / POST / DELETE | `/wishlist/products`, `/wishlist/products/{product_id}` | U | [wishlist](wishlist/ARCHITECTURE.md) |
| POST / GET | `/orders/` | U | [orders](orders/ARCHITECTURE.md) |
| GET | `/orders/{id}` | U | orders |
| POST | `/orders/{id}/cancel` | U | orders |
| PATCH | `/orders/{id}/status` | A | orders |

Полный контракт с типами полей — Swagger `/api/docs`.

## Инфраструктура

| Компонент | Роль | Где |
|---|---|---|
| PostgreSQL 16 | данные; схема — [`db.sql`](../../migrations/sql/db.sql), применяется при старте | [`shared/db.py`](../../src/shared/db.py) |
| Redis 7 | хранилище выданных JWT (для отзыва) | [`RedisTokenRepository`](../../src/auth/redis_adapter.py) |
| nginx | вход на `:PORT`, проксирует `/api/` в backend | [`docker/nginx`](../../docker/nginx/default.conf) |
| backend | FastAPI + uvicorn, образ non-root, healthcheck `/health` | [`Dockerfile`](../../docker/python/Dockerfile) |

Запуск целиком — [`docker-compose.yaml`](../../docker-compose.yaml).

## Известные ограничения (как есть)

| Ограничение | Домен |
|---|---|
| У списков нет фильтров и сортировки, кроме `category_id` у товаров; общее число записей не возвращается | products, categories, orders |
| `GET /categories/` вкладывает в `children` всё поддерево каждой категории, поэтому страница из N категорий может весить больше N записей | [categories](categories/INVARIANTS.md) |
| Токен живёт до истечения срока или выхода, refresh-токенов нет; TLS терминируется выше nginx | [auth](auth/DESIGN.md) |
