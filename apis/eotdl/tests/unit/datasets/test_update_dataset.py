import pytest
from unittest import mock

from ....src.usecases.datasets.UpdateDataset import UpdateDataset
from ....src.errors import (
    InvalidTagError,
    DatasetDoesNotExistError,
    UserUnauthorizedError,
    DatasetAlreadyExistsError,
)


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
    return {"uid": "123", "id": "123", "name": "test"}


def test_update_dataset_fails_if_dataset_not_found(user, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = None
    update = UpdateDataset(db_repo)
    inputs = UpdateDataset.Inputs(dataset_id=dataset["id"], uid=user["uid"])
    with pytest.raises(DatasetDoesNotExistError):
        update(inputs)
    db_repo.retrieve.assert_called_once_with("datasets", "123", "id")
    db_repo.update.assert_not_called()


def test_update_dataset_fails_if_user_does_not_own_dataset(user, dataset):
    db_repo = mock.Mock()
    dataset["uid"] = "456"
    db_repo.retrieve.return_value = dataset
    update = UpdateDataset(db_repo)
    inputs = UpdateDataset.Inputs(dataset_id=dataset["id"], uid=user["uid"])
    with pytest.raises(UserUnauthorizedError):
        update(inputs)
    db_repo.retrieve.assert_called_once_with("datasets", "123", "id")
    db_repo.update.assert_not_called()


def test_update_dataset_fails_if_new_name_aready_exists(user, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = dataset
    db_repo.find_one_by_name.return_value = dataset
    update = UpdateDataset(db_repo)
    inputs = UpdateDataset.Inputs(
        dataset_id=dataset["id"], uid=user["uid"], name="test"
    )
    with pytest.raises(DatasetAlreadyExistsError):
        update(inputs)
    db_repo.retrieve.assert_called_once_with("datasets", "123", "id")
    db_repo.find_one_by_name.assert_called_once_with("datasets", "test")


def test_update_dataset(user, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.side_effect = [dataset, ["test-tag"]]
    db_repo.find_one_by_name.return_value = None
    update = UpdateDataset(db_repo)
    inputs = UpdateDataset.Inputs(
        dataset_id=dataset["id"], uid=user["uid"], name="new-name"
    )
    outputs = update(inputs)
    assert outputs.dataset.name == "new-name"
    assert outputs.dataset.description == ""
    assert outputs.dataset.author == ""
    assert outputs.dataset.license == ""
    assert outputs.dataset.tags == []
    assert outputs.dataset.link == ""
    db_repo.retrieve.assert_called_once_with("datasets", "123", "id")
    db_repo.update.assert_called_once_with(
        "datasets", dataset["id"], outputs.dataset.dict()
    )
    db_repo.retrieve.side_effect = [dataset, ["test-tag"]]
    inputs = UpdateDataset.Inputs(
        dataset_id=dataset["id"],
        uid=user["uid"],
        name="new-name",
        description="test-description",
    )
    outputs = update(inputs)
    assert outputs.dataset.name == "new-name"
    assert outputs.dataset.description == "test-description"
    assert outputs.dataset.author == ""
    assert outputs.dataset.license == ""
    assert outputs.dataset.tags == []
    assert outputs.dataset.link == ""
    db_repo.retrieve.side_effect = [dataset, [{"name": "test-tag"}]]
    inputs = UpdateDataset.Inputs(
        dataset_id=dataset["id"],
        uid=user["uid"],
        name="new-name",
        description="test-description",
        author="test-author",
        license="test-license",
        tags=["test-tag"],
        link="test-link",
    )
    outputs = update(inputs)
    assert outputs.dataset.name == "new-name"
    assert outputs.dataset.description == "test-description"
    assert outputs.dataset.author == "test-author"
    assert outputs.dataset.license == "test-license"
    assert outputs.dataset.tags == ["test-tag"]
    assert outputs.dataset.link == "test-link"
