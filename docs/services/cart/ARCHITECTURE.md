# cart

Корзина авторизованного пользователя. Хранится в БД (не в сессии), живёт до оформления заказа
или ручной очистки.

## Сущности

| Сущность | Поля |
|---|---|
| [`CartItem`](../../../src/cart/models.py) | `id`, `user_id`, `product_id`, `quantity`, `added_at` |
| `Cart` | `user_id`, `items[]` (корзины как отдельной записи нет — это позиции пользователя) |
| `AddCartItemCmd` | `user_id`, `product_id`, `quantity` (`user_id` берётся из токена, не из тела) |
| `RemoveCartItemCmd` | `user_id`, `product_id` |

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`CartRepository`](../../../src/cart/ports.py) → [`PostgresCartRepository`](../../../src/cart/adapters/postgres.py) |
| Service | [`CartService`](../../../src/cart/services.py) |
| Use case | [`GetCart`, `AddToCart`, `RemoveFromCart`, `ClearCart`](../../../src/cart/uc/crud.py) |
| DTO | [`AddInCartRequest {product_id, quantity}`](../../../src/cart/schema.py) |

## Endpoint'ы

[`endpoints/cart.py`](../../../src/bootstrap/endpoints/cart.py), все для вошедшего пользователя (**U**), работают только со своей корзиной.

| Метод | Путь | Use case | Ответ / ошибки |
|---|---|---|---|
| GET | `/cart/products` | `GetCart` | `Cart` |
| POST | `/cart/products` | `AddToCart` | 201, `CartItem`; 404 если товара нет; 422 если `quantity` вне 1..1000 или сумма в позиции больше 1000 |
| DELETE | `/cart/products/{product_id}` | `RemoveFromCart` | 204; 404 если позиции нет |
| DELETE | `/cart/products` | `ClearCart` | 204 |

Из корзины создаётся заказ: [orders](../orders/DATA_FLOWS.md).
