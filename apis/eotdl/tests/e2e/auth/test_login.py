
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture
def url():
    yield '/auth'

def test_login(url):
    login_url = url + '/login'
    response = client.get(login_url)
    assert response.status_code == 200
    data = response.json()
    assert 'login_url' in data
    assert 'code' in data
    assert 'message' in data


