import copy
from unittest.mock import patch
from bson import ObjectId
import mongomock
import pytest



DATASET = {
    "uid": "123",
    "id": str(ObjectId()),
    "name": "test3",
    "metadata": {
        "description": "test",
        "authors": ["test"],
        "source": "http://test@m",
        "license": "test",
        "files": "123",
    },
    "versions": [],
    "tags": [],
    "createdAt": "2023-10-01T00:00:00Z",
    "updatedAt": "2023-10-01T00:00:00Z",
    "likes": 1,
    "downloads": 0,
    "quality": 0,
    "active": True,
    "allowedUsers": []
}


@pytest.fixture
def mock_mongo_dataset():
    mock_db = mongomock.MongoClient().db

    mock_db.datasets.insert_one(DATASET)
    with (
        patch("api.src.repos.mongo.client.get_db", return_value=mock_db),
        patch("api.src.repos.mongo.MongoRepo.get_db", return_value=mock_db),
    ):
        yield mock_db


@pytest.fixture
def dataset():
    return copy.deepcopy(DATASET)


@pytest.fixture
def datasets():
    return [
        {
            "uid": "123",
            "id": "123",
            "name": "test3",
            "description": "test 3",
            "likes": 1,
            "quality": 0,
            "authors": ["test"],
            "source": "http://test@m",
            "license": "test",
            "files": "123",
            "metadata": {
                "description": "test 3",
                "authors": ["test"],
                "source": "http://test@m",
                "license": "test",
                "files": "123",
            },
        },
        {
            "uid": "123",
            "id": "456",
            "name": "test4",
            "description": "test 4",
            "likes": 2,
            "quality": 0,
            "authors": ["test"],
            "source": "http://test@m",
            "license": "test",
            "files": "123",
            "metadata": {
                "description": "test 4",
                "authors": ["test"],
                "source": "http://test@m",
                "license": "test",
                "files": "123",
            },
        },
        {
            "uid": "123",
            "id": "789",
            "name": "test5",
            "description": "test 5",
            "likes": 3,
            "quality": 1,
            "authors": ["test"],
            "source": "http://test@m",
            "license": "test",
            "files": "123",
            "metadata": {
                "description": "test 5",
                "authors": ["test"],
                "source": "http://test@m",
                "license": "test",
                "files": "123",
            },
        },
    ]
