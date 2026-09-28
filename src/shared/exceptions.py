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
