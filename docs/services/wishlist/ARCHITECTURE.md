# wishlist

Избранные товары пользователя.

## Сущности

| Сущность | Поля |
|---|---|
| [`Favorite`](../../../src/wishlist/models.py) | `id`, `user_id`, `product_id`, `added_at` |
| `Wishlist` | `user_id`, `products[]` — список `Favorite` (id товаров, не сами товары) |
| `AddInWishlistCmd` / `RemoveFromWishlistCmd` | `user_id`, `product_id` |

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`WishlistRepository`](../../../src/wishlist/ports.py) → [`PonyWishlistRepository`](../../../src/wishlist/adapters/pony.py) |
| Service | [`WishlistService`](../../../src/wishlist/services.py) |
| Use case | [`AddInWishlist`, `RemoveFromWishlist`, `GetWishlist`](../../../src/wishlist/uc/crud.py) |
| DTO | [`AddInWishlistRequest {product_id}`](../../../src/wishlist/schema.py) |

## Endpoint'ы

[`endpoints/wishlist.py`](../../../src/bootstrap/endpoints/wishlist.py), все **U**, только своё избранное.

| Метод | Путь | Use case | Ответ / ошибки |
|---|---|---|---|
| GET | `/wishlist/products` | `GetWishlist` | `Wishlist` |
| POST | `/wishlist/products` | `AddInWishlist` | 201, `Favorite`; 404 если товара нет; 409 если уже в избранном |
| DELETE | `/wishlist/products/{product_id}` | `RemoveFromWishlist` | 204; 404 если не было |
