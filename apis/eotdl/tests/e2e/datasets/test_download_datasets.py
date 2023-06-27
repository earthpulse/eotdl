# all in one file to avoid problems with db

import pytest
import os

from fastapi.testclient import TestClient
from api.main import app

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


# download


# def test_download_dataset(url, db, s3):
#     url += "/123/download"
#     response = client.get(url)
#     assert response.status_code == 200
#     assert response.headers["Content-Disposition"] == 'attachment; filename="test1.zip"'
#     assert response.headers["Content-Type"] == "application/zip"
#     original = os.path.join(os.path.dirname(__file__), "../test.zip")
#     assert response.headers["Content-Length"] == str(os.path.getsize(original))
#     # save file to disk
#     dst = os.path.join(os.path.dirname(__file__), "test_download.zip")
#     with open(dst, "wb") as f:
#         f.write(response.content)
#     # check file size
#     assert os.path.getsize(dst) == os.path.getsize(original)
#     # remove file
#     os.remove(dst)
