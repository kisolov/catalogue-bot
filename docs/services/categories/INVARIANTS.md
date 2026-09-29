# categories — инварианты

| Правило | Где обеспечено |
|---|---|
| `slug` уникален (проверка + `UNIQUE`); при PATCH сравнивается с текущим, своё же значение не конфликтует | [`PostgresCategoryRepository`](../../../src/categories/adapters/postgres.py) |
| Категорию с товарами или подкатегориями нельзя удалить (409) | [`delete`](../../../src/categories/adapters/postgres.py) |
| В БД `products.category_id` — `ON DELETE RESTRICT`, а `categories.parent_id` — `SET NULL`; ORM не каскадирует (связей `relationship` нет). Проверка в `delete` даёт 409, БД остаётся последней линией защиты | [`db_002…`](../../../migrations/sql/db_002_products_category_restrict.sql), [`models.py`](../../../src/shared/orm/models.py), `delete` |
| PATCH частичный (`exclude_unset`); `parent_id` можно менять | `update` |
| `GET /categories/` возвращает все категории плоским списком (`parent_id` указывает на родителя); фильтра по родителю на уровне API нет | [`ListCategories`](../../../src/categories/uc/crud.py) |

## Дерево

| Правило | Где обеспечено |
|---|---|
| Родитель должен существовать: иначе 404 (POST и PATCH) | [`_get_parent`](../../../src/categories/adapters/postgres.py) |
| Родитель не может быть самой категорией или её потомком (обход предков): иначе 422 | [`_check_no_cycle`](../../../src/categories/adapters/postgres.py) |
| `parent_id: null` в PATCH снимает родителя | `update` |
| `name`/`slug` — 1..100 символов | [`models.py`](../../../src/categories/models.py) |
| В ответе `children` — всё поддерево; потомков адаптер читает уровень за уровнем (`_with_subtree`), так как ленивой подгрузки в async нет | [`_to_domain`](../../../src/categories/adapters/postgres.py) |

Тесты: [`test_categories.py`](../../../tests/cases/groups/test_categories.py).
