import pytest
from unittest import mock

from ....src.usecases.user.RetrieveUser import RetrieveUser
from ....src.errors import UserDoesNotExistError

@pytest.fixture
def user():
    return {
        '_id': '123',
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
    }

def test_retrieve_user_fails_if_user_does_not_exists(user):
    repo = mock.Mock()
    repo.retrieve.return_value = None
    retrieve_user = RetrieveUser(repo)
    inputs = RetrieveUser.Inputs(uid=user['uid'])
    with pytest.raises(UserDoesNotExistError):
        outputs = retrieve_user(inputs)
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    
def test_retrieve_user(user):
    repo = mock.Mock()
    repo.retrieve.return_value = user
    update_tier = RetrieveUser(repo)
    inputs = RetrieveUser.Inputs(uid=user['uid'])
    outputs = update_tier(inputs)
    assert outputs.user.uid == user['uid']
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')

