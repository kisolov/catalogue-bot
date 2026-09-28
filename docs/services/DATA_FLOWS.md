# Сценарии

## Вход через Telegram

```
Mini App → POST /auth/telegram {init_data}
  → LoginWithTelegram
      → TelegramInitDataService.validate   (подпись, возраст auth_date)
      → UserService.get_by_telegram_id     (нет → create role=user; гонка → повторный get)
      → TokenService.create_token          (JWT + запись в Redis с TTL)
  ← {access_token, user}
```

## Оформление заказа

```
POST /orders/ → CreateOrderFromCart(user_id) → OrderService → PonyOrderRepository.create_from_cart
  один db_session (одна транзакция):
    корзина пуста                       → EmptyCart          (409)
    для каждой позиции: SELECT ... FOR UPDATE по товару
      товар неактивен                   → ProductUnavailable (409)
      остаток < количества              → InsufficientStock  (409)
    создать Order(new) + OrderItem со снимком цены/названия
    списать остаток, удалить позицию корзины
  любое исключение → откат, корзина и остатки не тронуты
```

## Отмена и смена статуса

```
POST /orders/{id}/cancel (владелец) → OrderService.cancel_by_owner → только из new
PATCH /orders/{id}/status (админ)   → OrderService.change_status  → матрица переходов
  → repo.set_status(restore_stock = новый статус == cancelled)  # статус и возврат остатков атомарно
```
