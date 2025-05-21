import pytest
from unittest.mock import patch


from api.src.usecases.datasets import retrieve_datasets
from api.src.models import Dataset


@patch("api.src.usecases.datasets.retrieve_datasets.DatasetsDBRepo")
def test_retrieve_all_datasets(mocked_repo, datasets):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_datasets.return_value = datasets
    datasets = retrieve_datasets()
    assert len(datasets) == 3
    assert datasets[0].name == "test3"
    assert datasets[1].name == "test4"
    assert datasets[2].name == "test5"
    assert isinstance(datasets[0], Dataset)
    assert isinstance(datasets[1], Dataset)
    mocked_repo_instance.retrieve_datasets.assert_called_once()
