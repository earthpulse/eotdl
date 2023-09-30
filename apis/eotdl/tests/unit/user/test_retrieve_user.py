import pytest
from unittest.mock import patch

from ....src.models import User
from ....src.usecases.user import retrieve_user
from ....src.errors import UserDoesNotExistError

@pytest.fixture
def user():
    return User(**{
        'id': '123',
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
    })

@patch('api.src.usecases.user.retrieve_user.UserDBRepo')
def test_retrieve_user_fails_if_user_does_not_exists(mocked_repo, user):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_user_by_uid.return_value = None
    with pytest.raises(UserDoesNotExistError):
        retrieve_user(user.uid)
    mocked_repo_instance.retrieve_user_by_uid.assert_called_once_with(user.uid)

@patch('api.src.usecases.user.retrieve_user.UserDBRepo')
def test_retrieve_user(mocked_repo, user):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_user_by_uid.return_value = user.model_dump()
    result = retrieve_user(user.uid)
    assert result.uid == user.uid
    mocked_repo_instance.retrieve_user_by_uid.assert_called_once_with(user.uid)

