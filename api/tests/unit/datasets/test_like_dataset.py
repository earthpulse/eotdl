import pytest
from unittest.mock import patch

from api.src.usecases.datasets import toggle_like_dataset
from api.src.errors import DatasetDoesNotExistError
from api.src.models import User, Dataset, Metadata


@pytest.fixture
def user():
    return User(
        id="123",
        uid="123",
        email="test",
        name="test",
        picture="test",
        tier="free",
        liked_datasets=["456"],
    )


@pytest.fixture
def dataset():
    return Dataset(
        uid="123",
        id="123",
        name="test",
        authors=["test"],
        source="http://test@m.com",
        license="test",
        files="123",
        active=True,
        metadata=Metadata(
                description="test 3",
                authors=["test"],
                source="http://test@m",
                license="test",
                files="123",
            ),
    )


@patch(
    "api.src.usecases.datasets.update_dataset.retrieve_dataset",
    side_effect=DatasetDoesNotExistError,
)
def test_like_dataset_fails_if_dataset_not_found(mocked_retrieve, user):
    with pytest.raises(DatasetDoesNotExistError):
        toggle_like_dataset("123", user)
    mocked_retrieve.assert_called_once_with("123")


@patch("api.src.usecases.datasets.update_dataset.DatasetsDBRepo")
@patch("api.src.usecases.datasets.update_dataset.retrieve_dataset")
@patch("api.src.usecases.datasets.update_dataset.retrieve_user")
def test_like_dataset(
    mockeed_retrieve_user, mocker_retrieve_dataset, mocked_repo, user, dataset
):
    mockeed_retrieve_user.return_value = user
    mocker_retrieve_dataset.return_value = dataset
    mocked_repo_instance = mocked_repo.return_value
    toggle_like_dataset(dataset.id, user)
    mocked_repo_instance.like_dataset.assert_called_once_with(dataset.id, user.uid)
    user.liked_datasets.append(dataset.id)
    toggle_like_dataset(dataset.id, user)
    mocked_repo_instance.unlike_dataset.assert_called_once_with(dataset.id, user.uid)
