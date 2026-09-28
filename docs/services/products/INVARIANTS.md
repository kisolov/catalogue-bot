# products — инварианты

| Правило | Где обеспечено |
|---|---|
| `slug` и `sku` уникальны; проверка перед вставкой/обновлением (без учёта самого товара) + `UNIQUE` в БД → 409 | [`_check_uniqueness`, `_check_update_uniqueness`](../../../src/products/adapters/pony.py) |
| `sku` и `description` могут быть `NULL`; `sku` уникален, поэтому пустая строка недопустима | `nullable=True` в [`models.py`](../../../src/shared/orm/models.py) |
| `price >= 0`, `stock >= 0`, `compare_at_price >= price` | 422 на входе; `CHECK` в [`db.sql`](../../../migrations/sql/db.sql) остаётся последней линией |
| PATCH частичный: обновляются только переданные поля (`exclude_unset`); пустое тело не меняет ничего | [`PonyProductRepository.update`](../../../src/products/adapters/pony.py) |
| Список показывает только активные товары; `GET /products/{id}` отдаёт и неактивный | `ListProducts` не передаёт `is_active`, по умолчанию `True` |
| Неактивный товар нельзя заказать (`ProductUnavailable`), даже если лежит в корзине | [`create_from_cart`](../../../src/orders/adapters/pony.py) |
| Товар, попавший в заказ, нельзя удалить (409), иначе пропали бы позиции заказов | [`PonyProductRepository.delete`](../../../src/products/adapters/pony.py) |
| Pony каскадно удаляет зависимое **в обход** `ON DELETE RESTRICT`, поэтому проверка заказов явная | там же |
| Удаление товара удаляет его из корзин и избранного каскадом (`ON DELETE CASCADE` в БД и Pony) | [`db.sql`](../../../migrations/sql/db.sql) |
| Изменение товара не меняет уже созданные заказы (в них снимок цены и названия) | [orders](../orders/INVARIANTS.md) |

## Проверки ввода

| Запрос | Результат |
|---|---|
| `price`/`compare_at_price` < 0, больше `99999999.99` или больше двух знаков после запятой; `stock` < 0 или больше 2³¹−1; пустые `name`/`slug`/`sku`; `name`/`slug` > 200, `sku` > 50 символов | 422, границы в [`models.py`](../../../src/products/models.py) |
| `compare_at_price` < `price`; при PATCH сравнивается с сохранённым значением второго поля | 422, [`ProductService._check_prices`](../../../src/products/services.py) |
| Несуществующая `category_id` при POST и PATCH | 404 «Category[id=…] не существует», [`_get_category`](../../../src/products/adapters/pony.py) |

Тесты: [`test_products.py`](../../../tests/cases/groups/test_products.py).
