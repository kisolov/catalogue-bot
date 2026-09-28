# Архитектура backend

Один деплоймент (монолит), одна БД PostgreSQL, Redis для токенов. Цепочка вызовов:
`endpoint → use case → service → port ← adapter`; сборка — [`di.py`](../../di.py).
Спеки и планы: [`docs/superpowers/`](../superpowers/specs/2026-09-28-backend-polish-design.md).

## Домены

| Домен | Сущности | Порт → адаптер |
|---|---|---|
| [users](../../src/users) | `User` (`telegram_id` уникален, роль `user`/`admin`) | [`UserRepository`](../../src/users/ports.py) → [`PonyUserRepository`](../../src/users/adapters/pony.py) |
| [auth](../../src/auth) | JWT, `initData` | [`TokenRepository`](../../src/auth/ports.py) → [`RedisTokenRepository`](../../src/auth/redis_adapter.py) |
| [products](../../src/products) | `Product` (цена, остаток, `is_active`, категория) | [`ProductRepository`](../../src/products/ports.py) → [`PonyProductRepository`](../../src/products/adapters/pony.py) |
| [categories](../../src/categories) | `Category` (дерево через `parent_id`) | [`CategoryRepository`](../../src/categories/ports.py) → [`PonyCategoryRepository`](../../src/categories/adapters/pony.py) |
| [cart](../../src/cart) | `Cart`, `CartItem` (уникален по user+product) | [`CartRepository`](../../src/cart/ports.py) → [`PonyCartRepository`](../../src/cart/adapters/pony.py) |
| [wishlist](../../src/wishlist) | `Favorite` | [`WishlistRepository`](../../src/wishlist/ports.py) → [`PonyWishlistRepository`](../../src/wishlist/adapters/pony.py) |
| [orders](../../src/orders) | `Order`, `OrderItem` (снимок цены и названия), `OrderStatus` | [`OrderRepository`](../../src/orders/ports.py) → [`PonyOrderRepository`](../../src/orders/adapters/pony.py) |

Вход через Telegram проверяет [`TelegramInitDataService`](../../src/auth/telegram.py)
(домен `auth`, без порта — чистая логика).

## Endpoints

Префикс `/api` (nginx / `root_path`). «Авторизация»: — нет, U — любой вошедший, A — админ.

| Метод | Путь | Авторизация | Что делает |
|---|---|---|---|
| GET | `/health` | — | liveness |
| POST | `/auth/telegram` | — | вход по `initData`, создаёт пользователя при первом входе |
| GET | `/auth/me` | U | текущий пользователь |
| POST | `/auth/logout` | U | отзыв текущего токена |
| POST | `/users/` | A | создать пользователя (в т.ч. с ролью) |
| GET | `/users/{user_id}`, `/users/by_telegram/{telegram_id}` | A | найти пользователя |
| GET | `/products/` (`?category_id=`), `/products/{id}` | — | каталог |
| POST / PATCH / DELETE | `/products/`, `/products/{id}` | A | управление товарами |
| GET | `/categories/`, `/categories/{id}` | — | категории |
| POST / PATCH / DELETE | `/categories/`, `/categories/{id}` | A | управление категориями |
| GET / POST / DELETE | `/cart/products`, `/cart/products/{product_id}` | U | корзина |
| GET / POST / DELETE | `/wishlist/products`, `/wishlist/products/{product_id}` | U | избранное |
| POST | `/orders/` | U | заказ из корзины |
| GET | `/orders/` | U | мои заказы, новые первыми |
| GET | `/orders/{id}` | U | свой заказ; админ — любой; чужой = 404 |
| POST | `/orders/{id}/cancel` | U | отмена своего заказа в статусе `new` |
| PATCH | `/orders/{id}/status` | A | смена статуса по матрице переходов |

Маршруты: [`src/bootstrap/endpoints`](../../src/bootstrap/endpoints). Маппинг доменных
исключений на HTTP — [`server_factory.py`](../../src/bootstrap/server_factory.py).

## Инфраструктура

| Компонент | Роль | Где |
|---|---|---|
| PostgreSQL | данные; схема — [`db.sql`](../../migrations/sql/db.sql), применяется при старте | [`shared/db.py`](../../src/shared/db.py) |
| Redis | хранилище выданных JWT (для отзыва) | [`RedisTokenRepository`](../../src/auth/redis_adapter.py) |
| nginx | вход на `:PORT`, проксирует `/api/` в backend | [`docker/nginx`](../../docker/nginx/default.conf) |

Запуск целиком — [`docker-compose.yaml`](../../docker-compose.yaml).
