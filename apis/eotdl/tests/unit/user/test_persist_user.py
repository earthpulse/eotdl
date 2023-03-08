import pytest
from unittest import mock

from ....src.models import User
from ....src.usecases.user.PersistUser import PersistUser

@pytest.fixture
def user():
    return {
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
    }


def test_create_new_user(user):
    repo = mock.Mock()
    repo.retrieve.return_value = False
    persist_user = PersistUser(repo)
    inputs = PersistUser.Inputs(data=user)
    outputs = persist_user(inputs)
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    repo.persist.assert_called_once_with('users', User(**user).dict())
    repo.update.assert_not_called()
    assert outputs.user.uid == user['uid']
    assert outputs.user.name == user['name']
    assert outputs.user.email == user['email']
    assert outputs.user.picture == user['picture']
    assert outputs.user.dataset_count == 0
    assert outputs.user.model_count == 0
