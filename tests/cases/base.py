import pytest

from tests.fixtures.factories import FactoriesFixtures
from tests.fixtures.fastapi import FastAPIFixtures


class BaseTestGroup(FactoriesFixtures, FastAPIFixtures):
    @pytest.fixture(autouse=True, scope="function")
    def setup(self, container):
        self.container = container
