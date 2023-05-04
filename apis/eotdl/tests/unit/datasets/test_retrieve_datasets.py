import pytest 
from unittest import mock
from datetime import datetime

from ....src.usecases.datasets.RetrieveDatasets import RetrieveDatasets

@pytest.fixture
def datasets():
    return [
        {'uid': '123', 'id': '123', 'name': 'test1', 'description': 'test 1'},
        {'uid': '123', 'id': '123', 'name': 'test2', 'description': 'test 2'},
        {'uid': '123', 'id': '123', 'name': 'test3', 'description': 'test 3'}
    ]

def test_retrieve_all_datasets(datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets
    retrieve = RetrieveDatasets(db_repo)
    inputs = RetrieveDatasets.Inputs()
    outputs = retrieve(inputs)
    assert len(outputs.datasets) == 3
    
def test_retrieve_datasets_with_limits(datasets):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = datasets[:1]
    retrieve = RetrieveDatasets(db_repo)
    inputs = RetrieveDatasets.Inputs(limit=1)
    outputs = retrieve(inputs)
    assert len(outputs.datasets) == 1