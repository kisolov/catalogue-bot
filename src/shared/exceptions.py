class DomainException(Exception): ...


class NotFoundException(DomainException):
    def __init__(self, desired_object):
        super().__init__(f"{desired_object} не существует")


class MappingException(DomainException):
    def __init__(self, message: str):
        super().__init__(f"Ошибка маппинга: {message}")


class UniqueViolationException(DomainException):
    def __init__(self, unique_key: str):
        super().__init__(f"Нарушение уникальности {unique_key}")


class TokenException(DomainException):
    pass


class TokenExpiredException(TokenException):
    def __init__(self):
        super().__init__("Token expired")


class InvalidTokenException(TokenException):
    def __init__(self):
        super().__init__("Invalid token")


class ProductInUseException(DomainException):
    def __init__(self, product_id: int):
        super().__init__(f"Товар {product_id} используется в заказах")


class CategoryNotEmptyException(DomainException):
    def __init__(self, category_id: int):
        super().__init__(f"Категория {category_id} содержит товары или подкатегории")


class InvalidCategoryParentException(DomainException):
    def __init__(self, category_id: int, parent_id: int):
        super().__init__(
            f"Категория {parent_id} не может быть родителем категории {category_id}"
        )


class InvalidProductPriceException(DomainException):
    def __init__(self):
        super().__init__("Цена до скидки не может быть меньше цены")


class InvalidCartQuantityException(DomainException):
    def __init__(self, product_id: int, limit: int):
        super().__init__(f"Количество товара {product_id} в корзине больше {limit}")


class EmptyCartException(DomainException):
    def __init__(self):
        super().__init__("Корзина пуста")


class InsufficientStockException(DomainException):
    def __init__(self, product_id: int):
        super().__init__(f"Недостаточно товара {product_id} на складе")


class ProductUnavailableException(DomainException):
    def __init__(self, product_id: int):
        super().__init__(f"Товар {product_id} недоступен для заказа")


class InvalidOrderTransitionException(DomainException):
    def __init__(self, current: str, new: str):
        super().__init__(f"Нельзя перевести заказ из {current} в {new}")


class InvalidInitDataException(DomainException):
    def __init__(self, reason: str = "подпись не совпадает"):
        super().__init__(f"Некорректные данные Telegram: {reason}")


class InitDataExpiredException(DomainException):
    def __init__(self):
        super().__init__("Данные Telegram устарели")


class NotAuthenticatedException(DomainException):
    def __init__(self, reason: str = "Not authenticated"):
        super().__init__(reason)


class PermissionDeniedException(DomainException):
    def __init__(self):
        super().__init__("Insufficient permissions. Admin access required.")
