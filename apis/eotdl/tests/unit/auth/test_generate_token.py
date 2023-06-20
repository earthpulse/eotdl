import pytest
from unittest import mock

from ....src.usecases.auth.GenerateToken import GenerateToken


def test_generate_token():
    repo = mock.Mock()
    id_token = {"id_token": "123"}
    repo.generate_id_token.return_value = id_token
    token = GenerateToken(repo)
    code = "test"
    inputs = GenerateToken.Inputs(code=code)
    outputs = token(inputs)
    assert outputs.token == id_token
    repo.generate_id_token.assert_called_once_with(code)
