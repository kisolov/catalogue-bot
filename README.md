# Catalogue backend

Backend каталога товаров для Telegram Mini App: вход через Telegram, каталог,
корзина, избранное, заказы с контролем остатков. FastAPI + Pony ORM (PostgreSQL) +
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
cp .env.example .env          # заполните CHANGEME: DB_PASSWORD, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN
make up                       # postgres + redis + backend + nginx
```

API: `http://localhost:8080/api/docs` (порт задаётся `PORT` в `.env`).
Миграции применяются автоматически при старте, повторный запуск безопасен.
pgAdmin: `make pgadmin` (профиль `tools`).

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
       REDIS_HOST=localhost JWT_SECRET_KEY=dev SERVER_ALLOWED_ORIGINS='["*"]' \
       SERVER_PORT=8000 SERVER_HOST=127.0.0.1 ENVIRONMENT=test
make test        # тесты пересоздают схему БД — используйте отдельную базу!
make lint        # flake8 + black --check
```

Тестовая БД обнуляется при каждом тесте: не указывайте рабочую базу.

## Архитектура

`endpoint → use case → service → port ← adapter`, зависимости собираются в
[`di.py`](di.py). Подробности, инварианты и решения — в [`docs/services/`](docs/services/ARCHITECTURE.md).

```
src/
  <domain>/        users, auth, products, categories, cart, wishlist, orders
    models.py      pydantic-модели домена
    ports.py       интерфейсы репозиториев
    services.py    бизнес-логика
    uc/            use case'ы (один сценарий — один класс)
    adapters/      реализации портов (Pony, Redis)
  bootstrap/       FastAPI: endpoints, middleware, обработка ошибок
  shared/          ORM-модели, БД и миграции, исключения, логгер
```

## Переменные окружения

См. [`.env.example`](.env.example). Обязательные: `DB_PASSWORD`, `JWT_SECRET_KEY`,
`TELEGRAM_BOT_TOKEN` — приложение не стартует без них.
