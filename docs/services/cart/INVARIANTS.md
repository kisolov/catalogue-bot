# cart — инварианты

| Правило | Где обеспечено |
|---|---|
| Одна позиция на пару (пользователь, товар); повторное добавление **увеличивает** `quantity` | [`CartItemRow`](../../../src/shared/orm/models.py) `UNIQUE(user_id, product_id)`, блокировка строки `FOR UPDATE`, [`add_item`](../../../src/cart/adapters/postgres.py) |
| `user_id` берётся из токена, а не из тела запроса: чужую корзину изменить нельзя | [`endpoints/cart.py`](../../../src/bootstrap/endpoints/cart.py) |
| Корзина не проверяет `is_active` и остаток при добавлении — они проверяются в момент заказа | [`create_from_cart`](../../../src/orders/adapters/postgres.py) |
| `quantity` от 1 до 1000 | `CHECK` в [`db.sql`](../../../migrations/sql/db.sql) |
| Оформление заказа очищает корзину в той же транзакции | [orders](../orders/INVARIANTS.md) |
| Удаление позиции: 404, если её нет | [`remove_item`](../../../src/cart/adapters/postgres.py) |

## Количество

| Запрос | Результат |
|---|---|
| `quantity` вне 1..1000 | 422 ([`schema.py`](../../../src/cart/schema.py)) |
| Прибавка к существующей позиции, после которой больше 1000 | 422 ([`add_item`](../../../src/cart/adapters/postgres.py)), позиция не меняется |

Тесты: [`test_cart.py`](../../../tests/cases/groups/test_cart.py).
