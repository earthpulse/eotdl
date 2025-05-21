import pytest
from unittest.mock import patch

from api.src.usecases.datasets import retrieve_popular_datasets
from api.src.models import Dataset


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
    mocked_repo_instance.retrieve_popular_datasets.assert_called_once()
