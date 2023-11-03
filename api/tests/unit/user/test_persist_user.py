import pytest
from unittest.mock import patch

from api.src.models import User
from api.src.usecases.user import persist_user
from api.src.errors import UserDoesNotExistError

@pytest.fixture
def user():
    return User(**{
        'uid': 'test',
        'name': 'test name',
        'email': 'test email',
        'picture': 'test picture',
        'id': '123'
    })

@patch('api.src.usecases.user.persist_user.UserDBRepo')
@patch('api.src.usecases.user.persist_user.retrieve_user')
def test_update_user(mocked_retrieve, mocked_repo, user):
    mocked_retrieve.return_value = user
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.update_user.return_value = user
    result = persist_user(user.model_dump())
    # repo.persist.assert_called_once_with('users', User(**user).dict())
    # repo.update.assert_not_called()
    assert result.uid == user.uid
    assert result.name == user.name
    assert result.email == user.email
    assert result.picture == user.picture
    assert result.dataset_count == 0
    assert result.models_count == 0
    mocked_retrieve.assert_called_once_with(user.uid)
    mocked_repo_instance.update_user.assert_called_once()
    mocked_repo_instance.persist_user.assert_not_called()

@patch('api.src.usecases.user.persist_user.UserDBRepo')
@patch('api.src.usecases.user.persist_user.retrieve_user', side_effect=UserDoesNotExistError)
def test_create_new_user(mocked_retrieve, mocked_repo, user):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.generate_id.return_value = '456'
    # with pytest.raises(UserDoesNotExistError):
    result = persist_user(user.model_dump())
    assert result.id == '456'
    assert result.uid == user.uid
    assert result.name == user.name
    assert result.email == user.email
    assert result.picture == user.picture
    mocked_retrieve.assert_called_once_with(user.uid)
    mocked_repo_instance.update_user.assert_not_called()
    mocked_repo_instance.persist_user.assert_called_once()    
    mocked_repo_instance.persist_user.generate_id()