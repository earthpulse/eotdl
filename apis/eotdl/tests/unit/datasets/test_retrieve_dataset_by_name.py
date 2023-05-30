import pytest 
from unittest import mock

from ....src.usecases.datasets.RetrieveOneDatasetByName import RetrieveOneDatasetByName
from ....src.errors import DatasetDoesNotExistError

@pytest.fixture
def dataset():
    return {'uid': '123', 'id': '123', 'name': 'test1', 'description': 'test 1'}

def test_retrieve_dataset_by_name(dataset):
    db_repo = mock.Mock()
    db_repo.find_one_by_name.return_value = dataset
    retrieve = RetrieveOneDatasetByName(db_repo)
    inputs = RetrieveOneDatasetByName.Inputs(name='test1')
    outputs = retrieve(inputs)
    assert outputs.dataset.name == 'test1'
    db_repo.find_one_by_name.assert_called_once_with('datasets', 'test1')
    
def test_retrieve_dataset_by_name_fail_if_datasets_does_not_exist(dataset):
    db_repo = mock.Mock()
    db_repo.find_one_by_name.return_value = None
    retrieve = RetrieveOneDatasetByName(db_repo)
    inputs = RetrieveOneDatasetByName.Inputs(name='test')
    with pytest.raises(DatasetDoesNotExistError):
        retrieve(inputs)