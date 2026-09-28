import pytest

from tests.fixtures.factories import FactoriesFixtures


class ModelsFixtures(FactoriesFixtures):
    @pytest.fixture
    def sample_user(self, user_factory):
        return user_factory.create()

    @pytest.fixture
    def sample_admin(self, user_factory):
        from src.users.models import UserRole

        return user_factory.create(role=UserRole.ADMIN)

    @pytest.fixture
    def sample_product(self, product_factory):
        return product_factory.create()

    @pytest.fixture
    def sample_category(self, category_factory):
        return category_factory.create()

    @pytest.fixture
    def auth_headers(self, sample_user, container):
        token_service = container.token_service()
        token = token_service.create_token(sample_user.id)
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def admin_auth_headers(self, sample_admin):
        token_service = self.container.token_service()
        token = token_service.create_token(sample_admin.id)
        return {"Authorization": f"Bearer {token}"}
