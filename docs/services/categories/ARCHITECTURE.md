# categories

Дерево категорий (`parent_id`). Чтение публичное, изменение — только админ.

## Сущности

| Сущность | Поля |
|---|---|
| [`Category`](../../../src/categories/models.py) | `id`, `name`, `slug` (уникален), `parent_id?`, `created_at`, `children` |
| `CreateCategoryCmd` | `name`, `slug`, `parent_id?` |
| `UpdateCategoryCmd` | `id` + `name?`, `slug?`, `parent_id?` |

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`CategoryRepository`](../../../src/categories/ports.py) → [`PostgresCategoryRepository`](../../../src/categories/adapters/postgres.py) |
| Service | [`CategoryService`](../../../src/categories/services.py) |
| Use case | [`CreateCategory`, `UpdateCategory`, `GetCategoryById`, `ListCategories`, `DeleteCategory`](../../../src/categories/uc/crud.py) |
| DTO | [`CreateCategoryRequest`, `UpdateCategoryRequest`](../../../src/categories/schema.py) |

## Endpoint'ы

[`endpoints/categories.py`](../../../src/bootstrap/endpoints/categories.py)

| Метод | Путь | Авт. | Use case | Ответ / ошибки |
|---|---|---|---|---|
| GET | `/categories/` | — | `ListCategories` | плоский список категорий по возрастанию `id`; `limit`/`offset` ([пагинация](../shared/ARCHITECTURE.md#пагинация)); у каждой в `children` вложено всё поддерево |
| GET | `/categories/{id}` | — | `GetCategoryById` | `Category`; 404 |
| POST | `/categories/` | A | `CreateCategory` | 201; 404 если родителя нет; 409 при занятом `slug` |
| PATCH | `/categories/{id}` | A | `UpdateCategory` | `Category`; 404 (категория или родитель); 409; 422 если родитель — сама категория или её потомок |
| DELETE | `/categories/{id}` | A | `DeleteCategory` | 204; 404; 409 если есть товары или подкатегории |

Товары категории: `GET /products/?category_id=` ([products](../products/ARCHITECTURE.md)).
