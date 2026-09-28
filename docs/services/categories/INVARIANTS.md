# categories — инварианты

| Правило | Где обеспечено |
|---|---|
| `slug` уникален (проверка + `UNIQUE`); при PATCH сравнивается с текущим, своё же значение не конфликтует | [`PonyCategoryRepository`](../../../src/categories/adapters/pony.py) |
| Категорию с товарами или подкатегориями нельзя удалить (409) | [`delete`](../../../src/categories/adapters/pony.py) |
| В БД `products.category_id` имеет `ON DELETE CASCADE`, а `categories.parent_id` — `SET NULL`; потерю товаров при удалении категории предотвращает **только** проверка в приложении | [`db.sql`](../../../migrations/sql/db.sql), `delete` |
| PATCH частичный (`exclude_unset`); `parent_id` можно менять | `update` |
| `GET /categories/` возвращает все категории плоским списком (`parent_id` указывает на родителя); фильтра по родителю на уровне API нет | [`ListCategories`](../../../src/categories/uc/crud.py) |

## Как есть (известные ограничения)

Проверено запуском, код не менялся.

| Запрос | Результат | Замечание |
|---|---|---|
| POST с несуществующим `parent_id` | 409 «Нарушение уникальности Category[slug=…]» | отказ верный (FK), сообщение вводит в заблуждение |
| PATCH: категория сама себе родитель | необработанный `ValidationError` (рекурсия модели) → 500 | циклы в дереве не предотвращаются |
| Списки без пагинации | — | возвращаются все категории |

Тесты: [`test_categories.py`](../../../tests/cases/groups/test_categories.py).
