import pytest 
from unittest import mock

from api.src.usecases.datasets.RetrieveDatasetsLeaderboard import RetrieveDatasetsLeaderboard

@pytest.fixture
def users():
    return [
        {'uid': '123', 'email': 'test1', 'name': 'test1', 'picture': 'test1', 'dataset_count': 1},
        {'uid': '456', 'email': 'test2', 'name': 'test2', 'picture': 'test2', 'dataset_count': 2},
        {'uid': '789', 'email': 'test3', 'name': 'test3', 'picture': 'test3', 'dataset_count': 3},
    ]        


def test_retrieve_leaderboard(users):
    db_repo = mock.Mock()
    db_repo.find_top.return_value = sorted(users, key=lambda x: x['dataset_count'], reverse=True)
    leaderboard = RetrieveDatasetsLeaderboard(db_repo)
    inputs = RetrieveDatasetsLeaderboard.Inputs()
    outputs = leaderboard(inputs)
    assert outputs.leaderboard == [
        {'name': 'test3', 'datasets': 3},
        {'name': 'test2', 'datasets': 2},
        {'name': 'test1', 'datasets': 1}
    ]
    db_repo.find_top.assert_called_once_with('users', 'dataset_count', 5)
    
