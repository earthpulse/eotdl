import pytest
from unittest.mock import patch

from ....src.models import User
from ....src.usecases.user import update_user 
from ....src.errors import UserDoesNotExistError, UserAlreadyExistsError, NameLengthValidationError, NameCharsValidationError

@pytest.fixture
def user():
    return User(**{
        'id': '123',
        'uid': 'test',
        'name': 'test-name',
        'email': 'test email',
        'picture': 'test picture',
    })

@patch('api.src.usecases.user.update_user.UserDBRepo')
@patch('api.src.usecases.user.update_user.retrieve_user', side_effect=UserDoesNotExistError)
def test_update_user_fails_if_user_does_not_exists(mocked_retrieve, mocked_repo, user):
    with pytest.raises(UserDoesNotExistError):
        update_user(user, user.model_dump())
    mocked_retrieve.assert_called_once_with(user.uid)

@patch('api.src.usecases.user.update_user.UserDBRepo')
@patch('api.src.usecases.user.update_user.retrieve_user')
def test_update_user_fails_if_new_name_exists(mocked_retrieve, mocked_repo, user):
    mocked_retrieve.return_value = user
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.find_one_user_by_name.return_value = user
    with pytest.raises(UserAlreadyExistsError):
        update_user(user, user.model_dump())
    mocked_retrieve.assert_called_once_with(user.uid)
    mocked_repo_instance.find_one_user_by_name.assert_called_once_with(user.name)
    mocked_repo_instance.update_user.assert_not_called()

@patch('api.src.usecases.user.update_user.UserDBRepo')
@patch('api.src.usecases.user.update_user.retrieve_user')
def test_update_user_fails_if_invalid_name(mocked_retrieve, mocked_repo, user):
    mocked_retrieve.return_value = user
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.find_one_user_by_name.return_value = None
    with pytest.raises(NameCharsValidationError):
        update_user(user, {'name': '123'})
    with pytest.raises(NameCharsValidationError):
        update_user(user, {'name': 'sab_asd'})
    with pytest.raises(NameCharsValidationError):
        update_user(user, {'name': 'asdf@alsdk'})
    with pytest.raises(NameCharsValidationError):
        update_user(user, {'name': 'asd*15'})
    mocked_repo_instance.update_user.assert_not_called()

@patch('api.src.usecases.user.update_user.UserDBRepo')
@patch('api.src.usecases.user.update_user.retrieve_user')
def test_update_user(mocked_retrieve, mocked_repo, user):
    mocked_retrieve.return_value = user
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.find_one_user_by_name.return_value = None
    result = update_user(user, {'name': 'sdfg'})
    assert result.uid == user.uid
    assert result.name == 'sdfg'
    mocked_retrieve.assert_called_once_with(user.uid)
    mocked_repo_instance.find_one_user_by_name.assert_called_once_with('sdfg')
    mocked_repo_instance.update_user.assert_called_once()
