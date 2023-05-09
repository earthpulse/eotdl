import pytest 
from unittest import mock

from ....src.usecases.datasets.RetrievePopularDatasets import RetrievePopularDatasets

@pytest.fixture
def datasets():
    return [
        {'uid': '123', 'id': '123', 'name': 'test3', 'description': 'test 3', 'likes': 1},
        {'uid': '123', 'id': '456', 'name': 'test4', 'description': 'test 4', 'likes': 2},
        {'uid': '123', 'id': '789', 'name': 'test5', 'description': 'test 5', 'likes': 3},
    ]

def test_retrieve_popular_datasets(datasets):
    db_repo = mock.Mock()
    db_repo.find_top.return_value = sorted(datasets, key=lambda x: x['likes'], reverse=True)
    retrieve = RetrievePopularDatasets(db_repo)
    inputs = RetrievePopularDatasets.Inputs()
    outputs = retrieve(inputs)
    assert len(outputs.datasets) == 3
    assert outputs.datasets[0].name == 'test5'
    assert outputs.datasets[1].name == 'test4'
    db_repo.find_top.assert_called_once_with('datasets', 'likes', None)
    
def test_retrieve_popular_datasets_with_limit(datasets):
    db_repo = mock.Mock()
    db_repo.find_top.return_value = sorted(datasets, key=lambda x: x['likes'], reverse=True)[:2]
    retrieve = RetrievePopularDatasets(db_repo)
    inputs = RetrievePopularDatasets.Inputs(limit=2)
    outputs = retrieve(inputs)
    assert len(outputs.datasets) == 2
    assert outputs.datasets[0].name == 'test5'
    assert outputs.datasets[1].name == 'test4'
    db_repo.find_top.assert_called_once_with('datasets', 'likes', 2)