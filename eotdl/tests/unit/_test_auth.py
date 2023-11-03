import pytest
from unittest import mock

from eotdl.eotdl.auth.auth import Auth
from eotdl.src.errors.auth import LoginError, AuthTimeOut
from eotdl.eotdl.auth.is_logged import IsLogged
from eotdl.eotdl.auth.logout import Logout


def test_auth():
    repo = mock.Mock()
    api_repo = mock.Mock()
    auth = Auth(repo, api_repo)
    inputs = Auth.Inputs()
    api_repo.login.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value={"code": 123, "login_url": "123123"}),
    )
    token_data = {"id_token": "lkajshdflkjahsldkfjhalskjdfhlkasjdhf"}
    api_repo.token.return_value = mock.Mock(
        status_code=200, json=mock.Mock(return_value=token_data)
    )
    repo.save_creds.return_value = "creds_path"
    repo.decode_token.return_value = {
        "uid": "test",
        "name": "test name",
        "email": "test email",
        "picture": "test picture",
    }
    outputs = auth(inputs)
    api_repo.login.assert_called_once()
    api_repo.token.assert_called_once_with(123)
    repo.save_creds.assert_called_once_with(token_data)
    repo.decode_token.assert_called_once_with(token_data)
    assert outputs.user["uid"] == "test"
    assert outputs.user["name"] == "test name"
    assert outputs.user["email"] == "test email"
    assert outputs.user["picture"] == "test picture"


def test_auth_fails_if_not_logged_in():
    repo = mock.Mock()
    api_repo = mock.Mock()
    auth = Auth(repo, api_repo)
    inputs = Auth.Inputs()
    api_repo.login.return_value = mock.Mock(status_code=400)
    with pytest.raises(LoginError):
        auth(inputs)
    api_repo.login.assert_called_once()


def test_auth_fails_if_auth_timeout():
    repo = mock.Mock()
    api_repo = mock.Mock()
    auth = Auth(
        repo, api_repo, max_t=0.1, interval=0.01
    )  # will try to login 10 times, then timeout
    inputs = Auth.Inputs()
    api_repo.login.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value={"code": 123, "login_url": "123123"}),
    )
    api_repo.token.return_value = mock.Mock(status_code=400)
    with pytest.raises(AuthTimeOut):
        auth(inputs)


def test_is_logged_in():
    repo = mock.Mock()
    repo.load_creds.return_value = {"uid": 123}
    is_logged = IsLogged(repo)
    inputs = IsLogged.Inputs()
    outputs = is_logged(inputs)
    repo.load_creds.assert_called_once()
    assert outputs.user == {"uid": 123}


def test_is_not_logged_in():
    repo = mock.Mock()
    repo.load_creds.return_value = None
    is_logged = IsLogged(repo)
    inputs = IsLogged.Inputs()
    outputs = is_logged(inputs)
    repo.load_creds.assert_called_once()
    assert outputs.user is None


def test_logout():
    repo = mock.Mock()
    api_repo = mock.Mock()
    logout = Logout(repo, api_repo)
    inputs = Logout.Inputs()
    api_repo.logout_url.return_value = "ñklasjdf"
    outputs = logout(inputs)
    api_repo.logout_url.assert_called_once()
    repo.logout.assert_called_once()
    assert outputs.logout_url == "ñklasjdf"
