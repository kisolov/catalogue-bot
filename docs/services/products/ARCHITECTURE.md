# products

Каталог товаров. Чтение публичное, изменение — только админ.

## Сущности

| Сущность | Поля |
|---|---|
| [`Product`](../../../src/products/models.py) | `id`, `name`, `slug` (уникален), `description?`, `sku?` (уникален), `price`, `compare_at_price?`, `stock`, `is_active`, `category_id`, `created_at`, `updated_at` |
| `CreateProductCmd` | все поля `Product`, кроме `id` и дат |
| `UpdateProductCmd` | `id` + любые поля для частичного обновления |

Цена — `Decimal` (2 знака). `compare_at_price` — «старая цена» для зачёркнутого отображения.

## Слои

| Слой | Файл |
|---|---|
| Port → adapter | [`ProductRepository`](../../../src/products/ports.py) → [`PostgresProductRepository`](../../../src/products/adapters/postgres.py) |
| Service | [`ProductService`](../../../src/products/services.py) |
| Use case | [`CreateProduct`, `UpdateProduct`, `GetProductById`, `ListProducts`, `DeleteProduct`](../../../src/products/uc/crud.py) |
| DTO | [`CreateProductRequest`, `UpdateProductRequest`](../../../src/products/schema.py) |

## Endpoint'ы

[`endpoints/products.py`](../../../src/bootstrap/endpoints/products.py)

| Метод | Путь | Авт. | Use case | Ответ / ошибки |
|---|---|---|---|---|
| GET | `/products/?category_id=&limit=&offset=` | — | `ListProducts` | список **активных** товаров по возрастанию `id`, фильтр по категории необязателен; `limit`/`offset` ([пагинация](../shared/ARCHITECTURE.md#пагинация)) |
| GET | `/products/{id}` | — | `GetProductById` | `Product` (в том числе неактивный); 404 |
| POST | `/products/` | A | `CreateProduct` | 201; 404 если категории нет; 409 при занятых `slug`/`sku`; 422 при неверных значениях |
| PATCH | `/products/{id}` | A | `UpdateProduct` | обновлённый `Product`; 404 (товар или категория); 409; 422 |
| DELETE | `/products/{id}` | A | `DeleteProduct` | 204; 404; 409 если товар есть в заказах |

Связи: товар принадлежит категории ([categories](../categories/ARCHITECTURE.md)); его остаток
списывает [orders](../orders/DATA_FLOWS.md); его добавляют в [cart](../cart/ARCHITECTURE.md) и
[wishlist](../wishlist/ARCHITECTURE.md).
