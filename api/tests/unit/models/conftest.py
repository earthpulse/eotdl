from unittest.mock import patch
from bson import ObjectId
import mongomock
import pytest

MODEL = {
    "id": "model_id",
    "name": "model_name",
    "description": "model_description",
    "tags": ["tag1", "tag2"],
    "authors": ["author1", "author2"],
    "source": "model_source",
    "license": "model_license",
    "thumbnail": "model_thumbnail",
    "active": True,
}

@pytest.fixture
def mock_mongo_model():
    mock_db = mongomock.MongoClient().db

    mock_db.models.insert_one(MODEL)
    with patch("api.src.repos.mongo.MongoRepo.get_db", return_value=mock_db):
        yield mock_db


@pytest.fixture
def model():
    return MODEL