from datetime import datetime
from decimal import Decimal
from enum import Enum

from pony.orm import *


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


class OrderStatus(Enum):
    NEW = "new"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


db = Database()


class PonyUser(db.Entity):
    _table_ = "users"

    id = PrimaryKey(int, auto=True)
    telegram_id = Optional(int, unique=True, size=64)
    role = Required(str, default=UserRole.USER.value)
    created_at = Required(datetime, default=datetime.now)
    updated_at = Required(datetime, default=datetime.now)

    cart_items = Set("PonyCartItem")
    orders = Set("PonyOrder")
    favorites = Set("PonyFavorite")

    @property
    def role_enum(self) -> UserRole:
        return UserRole(self.role)

    @role_enum.setter
    def role_enum(self, value: UserRole):
        if not isinstance(value, UserRole):
            raise TypeError("role_enum must be an instance of UserRole")
        self.role = value.value


class PonyCategory(db.Entity):
    _table_ = "categories"

    id = PrimaryKey(int, auto=True)
    name = Required(str, 100)
    slug = Required(str, 100, unique=True)
    created_at = Required(datetime, default=datetime.now)

    # ИСПРАВЛЕНО: Явно указываем имя колонки для внешнего ключа
    parent = Optional("PonyCategory", column="parent_id", reverse="children")
    children = Set("PonyCategory", reverse="parent")
    products = Set("PonyProduct", cascade_delete=False)


class PonyProduct(db.Entity):
    _table_ = "products"

    id = PrimaryKey(int, auto=True)
    name = Required(str, 200)
    slug = Required(str, 200, unique=True)
    description = Optional(str, lazy=True, nullable=True)
    sku = Optional(str, 50, unique=True, nullable=True)
    price = Required(Decimal, 10, 2)
    compare_at_price = Optional(Decimal, 10, 2)
    stock = Required(int, default=0)
    is_active = Required(bool, default=True)
    created_at = Required(datetime, default=datetime.now)
    updated_at = Required(datetime, default=datetime.now)
    # ИСПРАВЛЕНО: Добавлено отсутствующее поле fts
    fts = Optional(str, lazy=True)

    # ИСПРАВЛЕНО: Явно указываем имя колонки для внешнего ключа
    category = Required(PonyCategory, column="category_id")

    cart_items = Set("PonyCartItem")
    order_items = Set("PonyOrderItem")
    favorites = Set("PonyFavorite")


class PonyCartItem(db.Entity):
    _table_ = "cart_items"

    id = PrimaryKey(int, auto=True)
    quantity = Required(int, default=1)
    added_at = Required(datetime, default=datetime.now)
    updated_at = Required(datetime, default=datetime.now)

    # ИСПРАВЛЕНО: Явно указываем имена колонок для внешних ключей
    user = Required(PonyUser, column="user_id")
    product = Required(PonyProduct, column="product_id")

    # composite_key теперь будет использовать правильные атрибуты
    composite_key(user, product)


class PonyOrder(db.Entity):
    _table_ = "orders"

    id = PrimaryKey(int, auto=True)
    status = Required(str, default=OrderStatus.NEW.value)
    total_price = Required(Decimal, 12, 2)
    created_at = Required(datetime, default=datetime.now)
    updated_at = Required(datetime, default=datetime.now)

    # ИСПРАВЛЕНО: Явно указываем имя колонки для внешнего ключа
    user = Optional(PonyUser, column="user_id")
    items = Set("PonyOrderItem")

    @property
    def status_enum(self) -> OrderStatus:
        return OrderStatus(self.status)

    @status_enum.setter
    def status_enum(self, value: OrderStatus):
        if not isinstance(value, OrderStatus):
            raise TypeError("status_enum must be an instance of OrderStatus")
        self.status = value.value


class PonyOrderItem(db.Entity):
    _table_ = "order_items"

    id = PrimaryKey(int, auto=True)
    product_name = Required(str, 200)
    price = Required(Decimal, 10, 2)
    quantity = Required(int)

    # ИСПРАВЛЕНО: Явно указываем имена колонок для внешних ключей
    order = Required(PonyOrder, column="order_id")
    product = Required(PonyProduct, column="product_id")


class PonyFavorite(db.Entity):
    _table_ = "favorites"

    id = PrimaryKey(int, auto=True)
    added_at = Required(datetime, default=datetime.now)

    # ИСПРАВЛЕНО: Явно указываем имена колонок для внешних ключей
    user = Required(PonyUser, column="user_id")
    product = Required(PonyProduct, column="product_id")

    composite_key(user, product)
