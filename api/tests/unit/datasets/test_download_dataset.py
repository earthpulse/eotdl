import pytest
from unittest import mock
from pydantic import BaseModel

from api.src.usecases.datasets.download_dataset import DownloadDataset
from api.src.errors import (
    TierLimitError,
    DatasetDoesNotExistError,
    FileDoesNotExistError,
)


@pytest.fixture
def tier():
    return {
        "name": "free",
        "limits": {
            "datasets": {"upload": 10, "download": 10, "count": 10, "files": 10}
        },
    }


@pytest.fixture
def user():
    return {
        "uid": "123",
        "email": "test",
        "name": "test",
        "picture": "test",
        "tier": "free",
    }


@pytest.fixture
def dataset():
    return {
        "uid": "123",
        "id": "123",
        "name": "test",
        "description": "test",
        "files": [{"name": "test-file", "size": 1, "checksum": "123"}],
    }


def test_download_dataset_fails_if_tier_limits_surpassed(tier, user):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = [1] * 100
    download = DownloadDataset(db_repo, os_repo)
    inputs = DownloadDataset.Inputs(id="123", uid="123", file="test")
    with pytest.raises(TierLimitError):
        download(inputs)
    db_repo.retrieve.assert_called_once_with("users", user["uid"], "uid")
    db_repo.find_one_by_name.assert_called_once_with("tiers", user["tier"])
    db_repo.find_in_time_range.assert_called_once_with(
        "usage", user["uid"], "dataset_download", "type"
    )


def test_download_dataset_fails_if_dataset_not_found(tier, user):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.retrieve.side_effect = [user, None]
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = []
    download = DownloadDataset(db_repo, os_repo)
    inputs = DownloadDataset.Inputs(id="123", uid="123", file="test")
    with pytest.raises(DatasetDoesNotExistError):
        download(inputs)
    assert db_repo.retrieve.call_count == 2
    os_repo.object_info.assert_not_called()


def test_download_dataset_fails_if_file_not_found(tier, user, dataset):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    dataset["files"] = []
    db_repo.retrieve.side_effect = [user, dataset]
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = []
    download = DownloadDataset(db_repo, os_repo)
    inputs = DownloadDataset.Inputs(id="123", uid="123", file="test")
    with pytest.raises(FileDoesNotExistError):
        download(inputs)
    assert db_repo.retrieve.call_count == 2
    os_repo.object_info.assert_not_called()


class ObjectInfo(BaseModel):
    size: int = 100


def test_download(tier, user, dataset):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.retrieve.side_effect = [user, dataset]
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = []
    os_repo.object_info.return_value = ObjectInfo()
    download = DownloadDataset(db_repo, os_repo)
    inputs = DownloadDataset.Inputs(id="123", uid="123", file="test-file")
    outputs = download(inputs)
    assert outputs.object_info == ObjectInfo()
    assert outputs.name == "test-file"
    assert db_repo.retrieve.call_count == 2
    db_repo.persist.assert_called_once()
    db_repo.increase_counter.assert_called_once_with(
        "datasets", "id", "123", "downloads"
    )
