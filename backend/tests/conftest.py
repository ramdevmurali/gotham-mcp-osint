import os

import pytest

def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_INTEGRATION_TESTS") == "1":
        return
    skip_integration = pytest.mark.skip(reason="Set RUN_INTEGRATION_TESTS=1 to run integration tests.")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
