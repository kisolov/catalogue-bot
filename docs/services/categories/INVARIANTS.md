# categories — инварианты

| Правило | Где обеспечено |
|---|---|
| `slug` уникален (проверка + `UNIQUE`); при PATCH сравнивается с текущим, своё же значение не конфликтует | [`PonyCategoryRepository`](../../../src/categories/adapters/pony.py) |
| Категорию с товарами или подкатегориями нельзя удалить (409) | [`delete`](../../../src/categories/adapters/pony.py) |
| В БД `products.category_id` имеет `ON DELETE CASCADE`, а `categories.parent_id` — `SET NULL`; потерю товаров при удалении категории предотвращает **только** проверка в приложении | [`db.sql`](../../../migrations/sql/db.sql), `delete` |
| PATCH частичный (`exclude_unset`); `parent_id` можно менять | `update` |
| `GET /categories/` возвращает все категории плоским списком (`parent_id` указывает на родителя); фильтра по родителю на уровне API нет | [`ListCategories`](../../../src/categories/uc/crud.py) |

## Дерево

| Правило | Где обеспечено |
|---|---|
| Родитель должен существовать: иначе 404 (POST и PATCH) | [`_get_parent`](../../../src/categories/adapters/pony.py) |
| Родитель не может быть самой категорией или её потомком (обход предков): иначе 422 | [`_check_no_cycle`](../../../src/categories/adapters/pony.py) |
| `parent_id: null` в PATCH снимает родителя | `update` |
| `name`/`slug` — 1..100 символов | [`models.py`](../../../src/categories/models.py) |
| В ответе `parent_id` берётся из связи `parent`, `children` — рекурсивно (у `Category` поле `parent_id`, у сущности Pony `parent`, поэтому маппинг явный) | [`_to_domain`](../../../src/categories/adapters/pony.py) |

Тесты: [`test_categories.py`](../../../tests/cases/groups/test_categories.py).
