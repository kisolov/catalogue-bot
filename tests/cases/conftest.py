import os
import pytest

from dotenv import load_dotenv

from tests.test_di import TestContainer
from di import container as production_container

load_dotenv(".env")
load_dotenv("tests/.env.test", override=True)


def pytest_collection_modifyitems(config, items):
    has_focused = any(
        "focused" in [m.name for m in item.iter_markers()] for item in items
    )

    if has_focused:
        selected = [
            item
            for item in items
            if any(m.name == "focused" for m in item.iter_markers())
        ]
        deselected = [item for item in items if item not in selected]
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
        print("\n💡 Выполняются тесты с маркером @pytest.mark.focused")


@pytest.fixture(autouse=True)
def validate_environment():
    if os.getenv("ENVIRONMENT") == "production":
        pytest.fail("Tests cannot run in production environment!")


@pytest.fixture(autouse=True, scope="function")
async def container():
    test_container = TestContainer()
    test_container.wire(packages=["tests", "src", "src.auth"])
    database = test_container.database()
    await database.reset()
    production_container.override(test_container)
    yield test_container
    production_container.reset_override()
    await database.dispose()
