import pytest
from unittest.mock import patch

from api.src.usecases.datasets import retrieve_popular_datasets
from api.src.models import Dataset, STACDataset


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
        },
    ]


@patch("api.src.usecases.datasets.retrieve_datasets.DatasetsDBRepo")
def test_retrieve_popular_datasets(mocked_repo, datasets):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_popular_datasets.return_value = datasets
    outputs = retrieve_popular_datasets(3)
    assert len(outputs) == 3
    assert outputs[0].name == "test3"
    assert outputs[1].name == "test4"
    assert outputs[2].name == "test5"
    assert isinstance(outputs[0], Dataset)
    assert isinstance(outputs[1], Dataset)
    assert isinstance(outputs[2], STACDataset)
    mocked_repo_instance.retrieve_popular_datasets.assert_called_once()
