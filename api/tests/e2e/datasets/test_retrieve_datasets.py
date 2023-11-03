# all in one file to avoid problems with db

import pytest
import os

from fastapi.testclient import TestClient
from api.main import app

from api.routers.auth import get_current_user, key_auth
from api.src.models import User
from ..setup import users, db, s3, boto3

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


# retrieve datasets


def test_retrieve_all_datasets(url, db):
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert data[0]["name"] == "test1"
    assert data[1]["name"] == "test2"
    assert data[2]["name"] == "test3"


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_retrieve_datasets_with_limits(url, db):
#     response = client.get(f"{url}?limit=2")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["name"] == "test1"
#     assert data[1]["name"] == "test2"


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_retireve_dataset_by_name(url, db):
#     response = client.get(f"{url}?name=test1")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "test1"


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_retrieve_liked_datasets(url, db):
#     url += "/liked"
#     response = client.get(url)
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["name"] == "test4"
#     assert data[1]["name"] == "test5"


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_retrieve_popular_datasets(url, db):
#     url += "/popular"
#     response = client.get(url)
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 6
#     assert data[0]["name"] == "test5"
#     assert data[1]["name"] == "test4"


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_retrieve_popular_datasets_with_limit(url, db):
#     url += "/popular?limit=2"
#     response = client.get(url)
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["name"] == "test5"
#     assert data[1]["name"] == "test4"
