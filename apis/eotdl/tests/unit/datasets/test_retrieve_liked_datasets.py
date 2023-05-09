import pytest 
from unittest import mock

from ....src.usecases.datasets.RetrieveLikedDatasets import RetrieveLikedDatasets
from ....src.errors import UserDoesNotExistError

@pytest.fixture
def datasets():
    return [
        {'uid': '123', 'id': '456', 'name': 'test2', 'description': 'test 2'},
        {'uid': '123', 'id': '789', 'name': 'test3', 'description': 'test 3'}
    ]

@pytest.fixture
def user():
    return {'uid': '123', 'name': 'test', 'email': 'test', 'picture': 'test', 'liked_datasets': ['456', '789']}

def test_retrieve_liked_datasets(datasets, user):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.retrieve_many.return_value = datasets
    retrieve = RetrieveLikedDatasets(db_repo)
    inputs = RetrieveLikedDatasets.Inputs(uid=user['uid'])
    outputs = retrieve(inputs)
    assert len(outputs.datasets) == 2
    db_repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    db_repo.retrieve_many.assert_called_once_with('datasets', user['liked_datasets'])
    
def test_retrieve_liked_datasets_fail_if_user_not_found(datasets, user):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = None
    retrieve = RetrieveLikedDatasets(db_repo)
    inputs = RetrieveLikedDatasets.Inputs(uid=user['uid'])
    with pytest.raises(UserDoesNotExistError):
        retrieve(inputs)