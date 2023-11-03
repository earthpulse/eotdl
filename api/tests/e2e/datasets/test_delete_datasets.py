# all in one file to avoid problems with db

import pytest
import os

from fastapi.testclient import TestClient
from api.main import app

from api.routers.auth import get_current_user, key_auth
from api.src.models import User
from tests.e2e.setup import users, db, s3, boto3, bucket

client = TestClient(app)

# override token auth


def get_current_user_mock():
    return User(**users[0])


def key_auth_mock():
    return True


app.dependency_overrides[get_current_user] = get_current_user_mock
app.dependency_overrides[key_auth] = key_auth_mock


@pytest.fixture
def url():
    yield "/datasets"


def test_delete_dataset(url, db, s3, bucket):
    url += "/test1"
    data = db["datasets"].find_one({"name": "test1"})
    assert data is not None
    assert s3.stat_object(bucket, f'{str(data["id"])}/test.zip') is not None
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json()["message"] == "Dataset deleted successfully"
    data = db["datasets"].find_one({"name": "test1"})
    with pytest.raises(Exception):
        s3.stat_object(bucket, f'{str(data["id"])}/test.zip')
