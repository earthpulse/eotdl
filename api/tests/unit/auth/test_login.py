import pytest 
from unittest.mock import patch

from ....src.usecases.auth import generate_login_url 

@patch('api.src.usecases.auth.login.AuthRepo')
def test_generate_login_url(mocked_repo):
    mock_return_value = "http://mockedlogin.url"
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.generate_login_url.return_value = mock_return_value
    result = generate_login_url()
    assert result == mock_return_value
    mocked_repo_instance.generate_login_url.assert_called_once()