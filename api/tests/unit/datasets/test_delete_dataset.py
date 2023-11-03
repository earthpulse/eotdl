import pytest
from unittest import mock

from api.src.usecases.datasets.delete_dataset import DeleteDataset
from api.src.errors import DatasetDoesNotExistError


@pytest.fixture
def user():
    return {
        "uid": "123",
        "email": "test1",
        "name": "test1",
        "picture": "test1",
        "dataset_count": 1,
    }


@pytest.fixture
def dataset():
    return {
        "id": "123",
        "name": "test",
        "uid": "123",
        "files": [{"name": "test-file", "size": 1, "checksum": "123"}],
    }


def test_delete_dataset_fails_if_dataset_not_found(user):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.find_one_by_name.return_value = None
    delete = DeleteDataset(db_repo, os_repo)
    inputs = DeleteDataset.Inputs(name="test")
    with pytest.raises(DatasetDoesNotExistError):
        delete(inputs)
    db_repo.find_one_by_name.assert_called_once_with("datasets", "test")


def test_delete_dataset(user, dataset):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.find_one_by_name.return_value = dataset
    delete = DeleteDataset(db_repo, os_repo)
    inputs = DeleteDataset.Inputs(name="test")
    outputs = delete(inputs)
    assert outputs.message == "Dataset deleted successfully"
    assert os_repo.delete.call_count == len(dataset["files"])
    db_repo.delete.assert_called_once_with("datasets", "123")
    db_repo.increase_counter.assert_called_once_with(
        "users", "uid", "123", "dataset_count", -1
    )
