import pytest
from unittest.mock import patch

from api.src.usecases.datasets import retrieve_datasets_leaderboard


@pytest.fixture
def users():
    return [
        {
            "name": "test3",
            "dataset_count": 1,
        },
        {
            "name": "test2",
            "dataset_count": 2,
        },
        {
            "name": "test1",
            "dataset_count": 3,
        },
    ]


@patch("api.src.usecases.datasets.retrieve_datasets.DatasetsDBRepo")
def test_retrieve_leaderboard(mocked_repo, users):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_datasets_leaderboard.return_value = users
    leaderboard = retrieve_datasets_leaderboard()
    assert leaderboard == [
        {"name": "test3", "datasets": 1},
        {"name": "test2", "datasets": 2},
        {"name": "test1", "datasets": 3},
    ]
    mocked_repo_instance.retrieve_datasets_leaderboard.assert_called_once()
