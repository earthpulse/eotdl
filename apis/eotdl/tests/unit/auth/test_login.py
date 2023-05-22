import pytest 
from unittest import mock

from ....src.usecases.auth.Login import Login

def test_login():
    repo = mock.Mock()
    login_url = {'login_url': '123'}
    repo.generate_login_url.return_value = login_url
    login = Login(repo)
    inputs = Login.Inputs()
    outputs = login(inputs)
    assert outputs.login_url == login_url