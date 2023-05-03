import pytest

from ...src.repos.auth import Auth0Repo

def test_generate_login_url():
    repo = Auth0Repo()
    login_url = repo.generate_login_url()
    assert 'login_url' in login_url
    assert 'code' in login_url
    assert 'message' in login_url

def test_generate_login_url_fails_bad_domain():
    repo = Auth0Repo()
    repo.domain = 'bad_domain'
    with pytest.raises(Exception) as e:
        repo.generate_login_url()
        assert str(e) == 'Error generating the device code'

def test_generate_login_url_fails_bad_client():
    repo = Auth0Repo()
    repo.client_id = 'bad_client'
    with pytest.raises(Exception) as e:
        repo.generate_login_url()
        assert str(e) == 'Error generating the device code'