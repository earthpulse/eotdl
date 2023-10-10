import pytest
from unittest import mock

from ....src.usecases.datasets.like_dataset import LikeDataset
from ....src.errors import DatasetDoesNotExistError


@pytest.fixture
def user():
    return {
        "uid": "123",
        "email": "test",
        "name": "test",
        "picture": "test",
        "tier": "free",
    }


def test_like_dataset_fails_if_dataset_not_found():
    db_repo = mock.Mock()
    db_repo.exists.return_value = False
    like = LikeDataset(db_repo)
    inputs = LikeDataset.Inputs(id="123", uid="123")
    with pytest.raises(DatasetDoesNotExistError):
        like(inputs)
    db_repo.exists.assert_called_once_with("datasets", "123")


def test_like_dataset(user):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    like = LikeDataset(db_repo)
    inputs = LikeDataset.Inputs(id="123", uid="123")
    like(inputs)
    db_repo.exists.assert_called_once_with("datasets", "123")
    db_repo.increase_counter.assert_called_once_with(
        "datasets", "_id", "123", "likes", 1
    )
    db_repo.append_to_list.assert_called_once_with(
        "users", "uid", "123", "liked_datasets", "123"
    )
    user["liked_datasets"] = ["123"]
    like(inputs)
    db_repo.increase_counter.assert_called_with("datasets", "_id", "123", "likes", -1)
    db_repo.remove_from_list.assert_called_once_with(
        "users", "uid", "123", "liked_datasets", "123"
    )
