import pytest
from unittest.mock import patch

from api.src.usecases.auth import parse_token

@patch('api.src.usecases.auth.parse_token.AuthRepo')
def test_parse_token(mocked_repo):
    mock_return_value = "parsed_token"
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.parse_token.return_value = mock_return_value
    result = parse_token('token')
    assert result == mock_return_value
    mocked_repo_instance.parse_token.assert_called_once()
