import pytest
from unittest.mock import patch

from api.src.usecases.auth import generate_logout_url

@patch('api.src.usecases.auth.logout.AuthRepo')
def test_logout(mocked_repo):
    mock_return_value = "http://mockedlogout.url"
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.generate_logout_url.return_value = mock_return_value
    result = generate_logout_url("test")
    assert result == mock_return_value
    mocked_repo_instance.generate_logout_url.assert_called_once()
