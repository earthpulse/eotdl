# all in one file to avoid problems with db

import pytest
import os

from fastapi.testclient import TestClient
from api.main import app

from api.routers.auth import get_current_user, admin_key_auth
from api.src.models import User
from ..setup import users, db, s3, boto3

client = TestClient(app)


# override token auth


def get_current_user_mock():
    return User(**users[0])


def admin_key_auth_mock():
    return True


app.dependency_overrides[get_current_user] = get_current_user_mock
app.dependency_overrides[admin_key_auth] = admin_key_auth_mock


@pytest.fixture
def url():
    yield "/datasets"


def test_ingest_dataset(url, db):
    response = client.post(
        url,
        data={"dataset": "test"},
        files={
            "file": open(
                os.path.join(os.path.dirname(__file__), "../../test.zip"), "rb"
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test"
    assert data["tags"] == []
    assert data["uid"] == "123"
