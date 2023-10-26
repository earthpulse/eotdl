# all in one file to avoid problems with db

import pytest
import os

from fastapi.testclient import TestClient
from api.api.main import app

from ....routers.auth import get_current_user, key_auth
from ....src.models import User
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


# update


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_edit_dataset(url, db):
#     dataset = db["datasets"].find_one({"id": "456"})
#     _url = url + f"/{str(dataset['_id'])}"
#     response = client.put(
#         _url,
#         json={
#             "name": "new-name",
#             "description": "new description",
#             "tags": ["tag1", "tag2"],
#         },
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "new-name"
#     assert data["description"] == "new description"
#     assert data["tags"] == ["tag1", "tag2"]
#     # update only name
#     response = client.put(_url, json={"name": "new-name2"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "new-name2"
#     assert data["description"] == "new description"
#     assert data["tags"] == ["tag1", "tag2"]
#     # update only description
#     response = client.put(_url, json={"description": "new description 2"})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "new-name2"
#     assert data["description"] == "new description 2"
#     assert data["tags"] == ["tag1", "tag2"]
#     # update only tags
#     response = client.put(_url, json={"tags": ["tag3"]})
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "new-name2"
#     assert data["description"] == "new description 2"
#     assert data["tags"] == ["tag3"]


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_like_dataset(url, db):
#     dataset = db["datasets"].find_one({"id": "456"})
#     assert dataset["likes"] == 2
#     assert str(dataset["_id"]) in db["users"].find_one({"uid": "123"})["liked_datasets"]
#     url += f"/{str(dataset['_id'])}/like"
#     response = client.put(url)
#     assert response.status_code == 200
#     assert db["datasets"].find_one({"id": "456"})["likes"] == 1
#     assert (
#         str(dataset["_id"])
#         not in db["users"].find_one({"uid": "123"})["liked_datasets"]
#     )
#     response = client.put(url)
#     assert response.status_code == 200
#     assert db["datasets"].find_one({"id": "456"})["likes"] == 2
#     assert str(dataset["_id"]) in db["users"].find_one({"uid": "123"})["liked_datasets"]


# @pytest.mark.skipif(SKIP, reason="skip")
# def test_leaderboard(url, db):
#     url += "/leaderboard"
#     response = client.get(url)
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["name"] == "test2"
#     assert data[0]["datasets"] == 10
#     assert data[1]["name"] == "test"
#     assert data[1]["datasets"] == 3
