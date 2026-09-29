import pytest

from tests.fixtures.factories import FactoriesFixtures


class ModelsFixtures(FactoriesFixtures):
    @pytest.fixture
    async def sample_user(self, user_factory):
        return await user_factory.create()

    @pytest.fixture
    async def sample_admin(self, user_factory):
        from src.users.models import UserRole

        return await user_factory.create(role=UserRole.ADMIN)

    @pytest.fixture
    async def sample_product(self, product_factory):
        return await product_factory.create()

    @pytest.fixture
    async def sample_category(self, category_factory):
        return await category_factory.create()

    @pytest.fixture
    async def auth_headers(self, sample_user, container):
        token_service = container.token_service()
        token = await token_service.create_token(sample_user.id)
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    async def admin_auth_headers(self, sample_admin):
        token_service = self.container.token_service()
        token = await token_service.create_token(sample_admin.id)
        return {"Authorization": f"Bearer {token}"}
