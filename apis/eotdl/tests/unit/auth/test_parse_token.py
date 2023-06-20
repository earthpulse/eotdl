import pytest
from unittest import mock

from ....src.usecases.auth.ParseToken import ParseToken


def test_parse_token():
    repo = mock.Mock()
    data = {"username": "123"}
    repo.parse_token.return_value = data
    parse = ParseToken(repo)
    token = "test"
    inputs = ParseToken.Inputs(token=token)
    outputs = parse(inputs)
    assert outputs.payload == data
    repo.parse_token.assert_called_once_with(token)
