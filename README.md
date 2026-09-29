# Catalogue backend

Backend каталога товаров для Telegram Mini App: вход через Telegram, каталог,
корзина, избранное, заказы с контролем остатков. FastAPI + SQLAlchemy 2.0 async (asyncpg, PostgreSQL) +
Redis, слоистая архитектура на `dependency-injector`.

## Возможности

- **Вход через Telegram Mini App** — проверка подписи `initData` (HMAC-SHA256), JWT с
  хранением в Redis (токен можно отозвать), роли `user` / `admin`.
- **Каталог** — товары и категории; чтение публичное, изменение только админом.
- **Корзина и избранное** для авторизованного пользователя.
- **Заказы** — оформление из корзины одной транзакцией: цены и названия фиксируются
  снимком, остатки списываются с блокировкой строк (нет перепродажи), отмена возвращает
  остатки, статусы меняются по матрице переходов.
- Единая обработка бизнес-ошибок (401 / 403 / 404 / 409), структурные JSON-логи.

## Быстрый старт (Docker)

```bash
cp .env.example .env          # заполните DB_PASSWORD, REDIS_PASSWORD, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN, SERVER_ALLOWED_ORIGINS
make up                       # postgres + redis + backend + nginx
```

API: `http://localhost:8080/api/` (порт задаётся `PORT` в `.env`). Swagger `/api/docs` по умолчанию выключен: включите `DOCS_ENABLED=true` в `.env`.
Миграции применяются автоматически при старте, повторный запуск безопасен.
pgAdmin: задайте `PGADMIN_PASSWORD` и выполните `make pgadmin` (профиль `tools`, порт только на 127.0.0.1).

Первого админа создайте вручную после первого входа через Telegram:

```bash
docker compose exec postgres psql -U catalogue -d catalogue \
  -c "UPDATE users SET role='admin' WHERE telegram_id = <ваш telegram id>"
```

## Разработка

Нужны Python 3.12, [uv](https://docs.astral.sh/uv/), PostgreSQL и Redis (для тестов).

```bash
make install
export DB_PROVIDER=postgres DB_HOST=localhost DB_PORT=5432 DB_USER=test \
       DB_PASSWORD=test DB_NAME=catalogue_test DB_SCHEMA=public \
       REDIS_HOST=localhost JWT_SECRET_KEY=dev SERVER_ALLOWED_ORIGINS='["http://localhost"]' \
       SERVER_PORT=8000 SERVER_HOST=127.0.0.1 ENVIRONMENT=test
make test        # тесты пересоздают схему БД — используйте отдельную базу!
make lint        # flake8 + black --check
```

Тестовая БД обнуляется при каждом тесте: не указывайте рабочую базу.

## Как пользоваться API

Все пути идут с префиксом `/api`. Полный контракт — Swagger: `/api/docs`.

| Роль | Что может |
|---|---|
| без входа | смотреть товары и категории, `POST /auth/telegram`, `/health` |
| `user` | корзина, избранное, свои заказы (создать, посмотреть, отменить в `new`), `/auth/me`, выход |
| `admin` | всё выше + управление товарами, категориями, пользователями, смена статусов заказов, любой заказ |

```bash
API=http://localhost:8080/api

# 1. Вход: init_data — строка window.Telegram.WebApp.initData из Mini App
TOKEN=$(curl -s -X POST $API/auth/telegram -H 'Content-Type: application/json' \
  -d '{"init_data": "<initData>"}' | jq -r .access_token)
AUTH="Authorization: Bearer $TOKEN"

# 2. Каталог (публично)
curl -s $API/categories/
curl -s "$API/products/?category_id=1"
curl -s "$API/products/?limit=20&offset=40"   # постранично: limit 1..100 (50 по умолчанию), offset >= 0

# 3. Корзина и заказ
curl -s -X POST $API/cart/products -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"product_id": 3, "quantity": 2}'
curl -s -X POST $API/orders/ -H "$AUTH"          # 201, заказ в статусе new, остаток списан
curl -s -X POST $API/orders/12/cancel -H "$AUTH" # пока статус new; остаток вернётся

# 4. Админ: создать товар, продвинуть заказ
curl -s -X POST $API/products/ -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"Кружка","slug":"mug","price":"12.50","stock":10,"is_active":true,"category_id":1}'
curl -s -X PATCH $API/orders/12/status -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"status":"processing"}'
```

Ошибки приходят как `{"detail": "..."}`: 401 нет/просрочен токен, 403 не админ, 404 не найдено
(и чужой заказ), 409 нарушено бизнес-правило (пустая корзина, нет остатка, недопустимый статус,
дубликат), 422 неверный запрос.

## Архитектура

`endpoint → use case → service → port ← adapter`, зависимости собираются в
[`di.py`](di.py). Документация по каждому домену (архитектура, сценарии, инварианты, отказы, решения) — в
[`docs/services/`](docs/services/ARCHITECTURE.md): начните с карты документации в этом файле.

```
src/
  <domain>/        users, auth, products, categories, cart, wishlist, orders
    models.py      pydantic-модели домена
    ports.py       интерфейсы репозиториев
    services.py    бизнес-логика
    uc/            use case'ы (один сценарий — один класс)
    adapters/      реализации портов (PostgreSQL через SQLAlchemy, Redis)
  bootstrap/       FastAPI: endpoints, middleware, обработка ошибок
  shared/          ORM-модели, БД и миграции, исключения, логгер
```

## Переменные окружения

См. [`.env.example`](.env.example). Обязательные: `DB_PASSWORD`, `JWT_SECRET_KEY`,
`TELEGRAM_BOT_TOKEN` — приложение не стартует без них.
