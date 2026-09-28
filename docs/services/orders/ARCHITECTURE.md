# orders

Заказы из корзины с контролем остатков. Оплаты нет: заказ создаётся в статусе `new`.

## Сущности

| Сущность | Поля |
|---|---|
| [`Order`](../../../src/orders/models.py) | `id`, `user_id`, `status`, `total_price`, `items[]`, `created_at`, `updated_at` |
| `OrderItem` | `id`, `order_id`, `product_id`, `product_name`, `price`, `quantity` — **снимок** названия и цены на момент заказа |
| `OrderStatus` | `new`, `processing`, `shipped`, `delivered`, `cancelled` |
| `ALLOWED_TRANSITIONS` | матрица переходов, см. [INVARIANTS](INVARIANTS.md) |

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`OrderRepository`](../../../src/orders/ports.py) → [`PonyOrderRepository`](../../../src/orders/adapters/pony.py) |
| Service | [`OrderService`](../../../src/orders/services.py): видимость заказа, матрица статусов, отмена владельцем |
| Use case | [`CreateOrderFromCart`, `GetOrderById`, `ListOrdersByUser`, `UpdateOrderStatus`, `CancelOrder`](../../../src/orders/uc/crud.py) |
| DTO | [`UpdateOrderStatusRequest {status}`](../../../src/orders/schema.py) |

Порт держит два атомарных метода — `create_from_cart` и `set_status` — потому что заказ пишет
в таблицы корзины и товаров (обоснование — [DESIGN](DESIGN.md)). Методы `create`, `update`,
`OrderService.create/update` и use case `CreateOrder` остались от исходного кода и через API не
вызываются.

## Endpoint'ы

[`endpoints/orders.py`](../../../src/bootstrap/endpoints/orders.py)

| Метод | Путь | Авт. | Use case | Ответ / ошибки |
|---|---|---|---|---|
| POST | `/orders/` | U | `CreateOrderFromCart` | 201, `Order`; 409 пустая корзина / товар недоступен / не хватает остатка |
| GET | `/orders/` | U | `ListOrdersByUser` | свои заказы, новые первыми, без пагинации |
| GET | `/orders/{id}` | U | `GetOrderById` | свой заказ; админ — любой; чужой — 404 |
| POST | `/orders/{id}/cancel` | U | `CancelOrder` | `Order`; 404 (в т.ч. чужой); 409 если статус не `new` |
| PATCH | `/orders/{id}/status` | A | `UpdateOrderStatus` | `Order`; 404; 409 если переход недопустим; 422 при неизвестном статусе |

Пример:

```bash
curl -X POST $API/orders/ -H "Authorization: Bearer $TOKEN"
# 201 {"id": 12, "status": "new", "total_price": "25.00",
#      "items": [{"product_id": 3, "product_name": "…", "price": "12.50", "quantity": 2}], …}
```

Смежные домены: [cart](../cart/ARCHITECTURE.md), [products](../products/ARCHITECTURE.md).
