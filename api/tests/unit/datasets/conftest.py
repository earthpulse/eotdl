from unittest.mock import patch
from bson import ObjectId
import mongomock
import pytest


DATASET = {
    "id": str(ObjectId()),
    "uid": "123",
    "name": "test3",
    "description": "test 3",
    "likes": 1,
    "quality": 0,
    "authors": ["test"],
    "source": "http://test@m",
    "license": "test",
    "files": "123",
    "active": True,
    "metadata": {
        "description": "test",
        "authors": ["test"],
        "source": "http://test@m",
        "license": "test",
        "files": "123",
    },
}


@pytest.fixture
def mock_mongo_datasets():
    mock_db = mongomock.MongoClient().db

    mock_db.datasets.insert_one(DATASET)
    with (
        patch("api.src.repos.mongo.client.get_db", return_value=mock_db),
        patch("api.src.repos.mongo.MongoRepo.get_db", return_value=mock_db),
    ):
        yield mock_db


@pytest.fixture
def model():
    return DATASET


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
