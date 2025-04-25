import copy
from unittest.mock import patch
import mongomock
import pytest
from bson import ObjectId

MODEL = {
    "uid": "123",
    "id": str(ObjectId("680b61b9f4e7d3c2e71ec3a4")),
    "name": "model-name",
    "metadata": {
        "description": "test",
        "authors": ["test"],
        "source": "http://test@m",
        "license": "test",
        "files": "123",
    },
    "versions": [],
    "tags": ["tag1", "tag2"],
    "createdAt": "2023-10-01T00:00:00Z",
    "updatedAt": "2023-10-01T00:00:00Z",
    "likes": 0,
    "downloads": 0,
    "quality": 0,
    "active": True,
    "allowedUsers": [],
}

@pytest.fixture
def mock_mongo_model():
    mock_db = mongomock.MongoClient().db

    mock_db.models.insert_one(MODEL)
    with (
        patch("api.src.repos.mongo.MongoRepo.get_db", return_value=mock_db),
         patch("api.src.repos.mongo.client.get_db", return_value=mock_db),
    ):
        yield mock_db


@pytest.fixture
def model():
    return copy.deepcopy(MODEL)
