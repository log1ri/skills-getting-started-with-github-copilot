from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as activities_module


@pytest.fixture
def client():
    """Provide a TestClient and restore the in-memory activities after each test."""
    orig = deepcopy(activities_module)
    with TestClient(app) as c:
        yield c
    # restore original activities to avoid cross-test contamination
    activities_module.clear()
    activities_module.update(deepcopy(orig))
