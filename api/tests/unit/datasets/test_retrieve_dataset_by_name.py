import pytest
from unittest.mock import patch

from api.src.usecases.datasets import retrieve_dataset_by_name
from api.src.errors import DatasetDoesNotExistError


@patch("api.src.usecases.datasets.retrieve_dataset.DatasetsDBRepo")
def test_retrieve_dataset_by_name(mocked_repo, dataset):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.find_one_dataset_by_name.return_value = dataset
    _dataset = retrieve_dataset_by_name(dataset["name"])
    assert _dataset.name == dataset["name"]
    mocked_repo_instance.find_one_dataset_by_name.assert_called_once_with(
        dataset["name"]
    )


@patch("api.src.usecases.datasets.retrieve_dataset.DatasetsDBRepo")
def test_retrieve_dataset_by_name_fail_if_datasets_does_not_exist(mocked_repo):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.find_one_dataset_by_name.return_value = None
    with pytest.raises(DatasetDoesNotExistError):
        retrieve_dataset_by_name("abc")
