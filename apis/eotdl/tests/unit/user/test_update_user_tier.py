import pytest
from unittest import mock

from ....src.usecases.user.UpdateUserTier import UpdateUserTier
from ....src.errors import UserDoesNotExistError

@pytest.fixture
def user():
    return {
        '_id': '123',
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
        'tier': 'free'
    }

def test_update_user_tier_fails_if_user_does_not_exists(user):
    repo = mock.Mock()
    repo.retrieve.return_value = None
    update_tier = UpdateUserTier(repo)
    inputs = UpdateUserTier.Inputs(uid=user['uid'], tier='dev')
    with pytest.raises(UserDoesNotExistError):
        outputs = update_tier(inputs)
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    
def test_update_user_fails_if_invalid_tier(user):
    repo = mock.Mock()
    update_tier = UpdateUserTier(repo)
    inputs = UpdateUserTier.Inputs(uid=user['uid'], tier='ivalid')
    with pytest.raises(Exception):
        outputs = update_tier(inputs)

def test_update_user_tier(user):
    repo = mock.Mock()
    repo.retrieve.return_value = user
    update_tier = UpdateUserTier(repo)
    inputs = UpdateUserTier.Inputs(uid=user['uid'], tier='free')
    outputs = update_tier(inputs)
    updated_user = outputs.user 
    assert updated_user.tier == 'free'
    repo.update.assert_called_once_with('users', user['_id'], updated_user.dict())

