# wishlist — инварианты

| Правило | Где обеспечено |
|---|---|
| Товар в избранном пользователя один раз; повторное добавление — 409 (проверка + `UNIQUE(user_id, product_id)`) | [`PostgresWishlistRepository.add`](../../../src/wishlist/adapters/postgres.py) |
| `user_id` берётся из токена | [`endpoints/wishlist.py`](../../../src/bootstrap/endpoints/wishlist.py) |
| Удаление отсутствующего — 404 | `remove` |
| Избранное отдаёт только id товаров; данные товара клиент запрашивает через [products](../products/ARCHITECTURE.md) | [`Wishlist`](../../../src/wishlist/models.py) |
| Удаление товара удаляет его из избранного | `ON DELETE CASCADE` в [`db.sql`](../../../migrations/sql/db.sql) |
| Добавление несуществующего товара — 404 (явная проверка до вставки) | `add` |

Тесты: [`test_wishlist.py`](../../../tests/cases/groups/test_wishlist.py).
