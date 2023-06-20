import pytest
from unittest import mock

from ....src.usecases.auth.Logout import Logout


def test_logout():
    repo = mock.Mock()
    logout_url = "123"
    repo.generate_logout_url.return_value = logout_url
    logout = Logout(repo)
    redirect_uri = "test"
    inputs = Logout.Inputs(redirect_uri=redirect_uri)
    outputs = logout(inputs)
    assert outputs.logout_url == logout_url
    repo.generate_logout_url.assert_called_once_with(redirect_uri)
