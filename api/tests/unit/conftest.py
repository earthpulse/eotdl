from fastapi.testclient import TestClient
import pytest
from api.main import app
from api.routers.auth.main import get_current_user
from api.src.models.user import User


def mock_get_current_user():
    return User(
        uid="123",
        id="67c85ae605f169ca06f6353f",
        name="william",
        email="willams@example.com",
        picture="https://example.com/avatar.jpg",
    )


@pytest.fixture(autouse=True)
def client():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    client = TestClient(app)
    yield client
