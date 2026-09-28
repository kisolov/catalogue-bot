# wishlist — инварианты

| Правило | Где обеспечено |
|---|---|
| Товар в избранном пользователя один раз; повторное добавление — 409 (проверка + `UNIQUE(user_id, product_id)`) | [`PonyWishlistRepository.add`](../../../src/wishlist/adapters/pony.py) |
| `user_id` берётся из токена | [`endpoints/wishlist.py`](../../../src/bootstrap/endpoints/wishlist.py) |
| Удаление отсутствующего — 404 | `remove` |
| Избранное отдаёт только id товаров; данные товара клиент запрашивает через [products](../products/ARCHITECTURE.md) | [`Wishlist`](../../../src/wishlist/models.py) |
| Удаление товара удаляет его из избранного | `ON DELETE CASCADE` в [`db.sql`](../../../migrations/sql/db.sql) |

## Как есть (известные ограничения)

| Запрос | Результат | Замечание |
|---|---|---|
| POST с несуществующим `product_id` | 409 «Нарушение уникальности Favorite[…]» | отказ верный (FK), сообщение вводит в заблуждение; явной проверки существования товара нет |

Тесты: [`test_wishlist.py`](../../../tests/cases/groups/test_wishlist.py).
