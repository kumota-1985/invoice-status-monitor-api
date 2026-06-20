import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture(scope="module")
def client():
    """
    TestClient fixture that triggers the lifespan events on startup/shutdown,
    ensuring that the shared HTTPX client is initialized correctly.
    """
    with TestClient(app) as c:
        yield c
