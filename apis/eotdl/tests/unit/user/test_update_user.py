import pytest
from unittest import mock
from ....src.models import User
from ....src.usecases.user.UpdateUser import UpdateUser
from ....src.errors import UserDoesNotExistError, UserAlreadyExistsError, NameLengthValidationError, NameCharsValidationError

@pytest.fixture
def user():
    return {
        '_id': '123',
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
    }

def test_update_user_fails_if_user_does_not_exists(user):
    repo = mock.Mock()
    repo.retrieve.return_value = None
    update_user = UpdateUser(repo)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': 'test name 2'})
    with pytest.raises(UserDoesNotExistError):
        outputs = update_user(inputs)
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    
def test_update_user_fails_if_new_name_exists(user):
    repo = mock.Mock()
    repo.retrieve.return_value = user
    repo.find_one_by_name.return_value = user
    update_user = UpdateUser(repo)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': user['name']})
    with pytest.raises(UserAlreadyExistsError):
        outputs = update_user(inputs)
    repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
    repo.find_one_by_name.assert_called_once_with('users', user['name'])

def test_update_user_fails_if_invalid_name(user):
    repo = mock.Mock()
    repo.retrieve.return_value = user
    repo.find_one_by_name.return_value = None
    update_user = UpdateUser(repo)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': '123'})
    with pytest.raises(NameCharsValidationError):
        outputs = update_user(inputs)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': 'sab_asd'})
    with pytest.raises(NameCharsValidationError):
        outputs = update_user(inputs)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': 'asdf@alsdk'})
    with pytest.raises(NameCharsValidationError):
        outputs = update_user(inputs)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': 'asd'*15})
    with pytest.raises(NameLengthValidationError):
        outputs = update_user(inputs)

def test_update_user(user):
    repo = mock.Mock()
    repo.retrieve.return_value = user
    repo.find_one_by_name.return_value = None 
    repo.update.return_value = user.copy().update(name='test name 2')
    update_user = UpdateUser(repo)
    inputs = UpdateUser.Inputs(uid=user['uid'], data={'name': 'test-name-2'})
    outputs = update_user(inputs)
    updated_user = outputs.user 
    assert updated_user.name == 'test-name-2'
    repo.update.assert_called_once_with('users', user['_id'], updated_user.dict())

