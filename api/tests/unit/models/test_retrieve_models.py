from copy import deepcopy
import pytest
from unittest.mock import patch


from api.src.usecases.models import retrieve_models

@pytest.fixture
def models():
    base = {
        "uid": "123",
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

    return [
        {**deepcopy(base), "id": "123", "name": "test3", "likes": 1, "quality": 0},
        {**deepcopy(base), "id": "456", "name": "test4", "likes": 2, "quality": 0},
        {**deepcopy(base), "id": "789", "name": "test5", "likes": 3, "quality": 1},
    ]

@patch("api.src.usecases.models.retrieve_models.ModelsDBRepo")
def test_retrieve_all_models(mocked_repo, models):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_models.return_value = models
    models = retrieve_models()
    assert len(models) == 3
    assert models[0].name == "test3"
    assert models[1].name == "test4"
    assert models[2].name == "test5"
    mocked_repo_instance.retrieve_models.assert_called_once()
