import pytest
from unittest.mock import patch

from ....src.usecases.auth import generate_id_token

@patch('api.src.usecases.auth.generate_token.AuthRepo')
def test_generate_token(mocked_repo):
    mock_return_value = "test_token"
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.generate_id_token.return_value = mock_return_value
    result = generate_id_token('test_code')
    assert result == mock_return_value
    mocked_repo_instance.generate_id_token.assert_called_once()
