# orders — инварианты

| Правило | Где обеспечено |
|---|---|
| Переходы: `new→processing\|cancelled`, `processing→shipped\|cancelled`, `shipped→delivered`; `delivered` и `cancelled` конечные. Иначе 409 | [`ALLOWED_TRANSITIONS`](../../../src/orders/models.py), [`OrderService.change_status`](../../../src/orders/services.py) |
| Владелец может отменить только заказ в `new`; остальное — через админа | [`OrderService.cancel_by_owner`](../../../src/orders/services.py) |
| Чужой заказ неотличим от несуществующего (404, не 403) — не раскрываем существование | [`OrderService.get_visible`](../../../src/orders/services.py) |
| Админ видит любой заказ | `is_admin` в `GetOrderById` |
| `OrderItem` хранит цену и название на момент заказа; правки товара заказ не меняют | [`create_from_cart`](../../../src/orders/adapters/postgres.py) |
| `total_price` = сумма `price × quantity` по позициям, считается на сервере по текущим ценам | там же |
| Остаток не уходит в минус при параллельных заказах: строки товаров блокируются `SELECT … FOR UPDATE` | `_lock_products` в [`create_from_cart`](../../../src/orders/adapters/postgres.py) |
| Товары блокируются всегда по возрастанию `id`: встречные корзины `[A, B]` и `[B, A]` не дают deadlock | `_lock_products` (`ORDER BY id`) |
| Переход статуса проверяется под блокировкой строки заказа: параллельные отмены не вернут остаток дважды | `allowed_from` в [`set_status`](../../../src/orders/adapters/postgres.py) |
| Заказ, списание остатков и очистка корзины — одна транзакция; при сбое ничего не меняется | одна `Database.transaction()` |
| Отмена (владельцем или админом) возвращает остатки по всем позициям; статус и остатки меняются атомарно | [`set_status`](../../../src/orders/adapters/postgres.py) |
| Возврат остатков только при переходе в `cancelled`; других списаний/возвратов нет | `restore_stock` в `change_status` |
| Заказ нельзя создать из пустой корзины и из неактивных товаров | `EmptyCart`, `ProductUnavailable` |
| Товар из заказа нельзя удалить (`ON DELETE RESTRICT` + явная проверка) | [products](../products/INVARIANTS.md) |
| Все суммы — `Decimal`, без float | [`models.py`](../../../src/orders/models.py) |

Границы: доставка, оплата, редактирование заказа после создания, частичная отмена — вне объёма.
Список заказов постраничный: `limit`/`offset`, новые первыми.

Тесты: [`test_orders.py`](../../../tests/cases/groups/test_orders.py) (19 сценариев: успех, снимок
цены, пустая корзина, недоступный товар, нехватка остатка без побочных изменений, матрица статусов,
возврат остатков при отмене владельцем и админом, чужой заказ, права, запрет удаления товара из заказа).
