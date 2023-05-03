import pytest
import os 
from unittest.mock import patch

from fastapi.testclient import TestClient
from api.main import app

from ....routers.auth import get_current_user
from ....src.repos.mongo.client import get_db
from ....src.models import User
from ...utils import tiers

client = TestClient(app)

user = {'uid': '123', 'name': 'test', 'email': 'test', 'picture': 'test', 'tier': 'dev'}

@pytest.fixture
def db():
    db = get_db()
    db['users'].insert_one(user)
    db['tiers'].insert_many(tiers)
    yield db
    db.drop_collection('users')
    db.drop_collection('tiers')
    db.drop_collection('datasets')
    
    
@pytest.fixture
def url():
    yield '/datasets'

def get_current_user_mock():
	return User(**user)

app.dependency_overrides[get_current_user] = get_current_user_mock

def test_ingest_dataset(url, db):
    response = client.post(
        url, 
        data={'name': 'test', 'description': 'test'},
        files={'file': open(os.path.join(os.path.dirname(__file__), '../../test.zip'), 'rb')}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test'
    assert data['description'] == 'test'
    assert data['tags'] == []
    assert data['uid'] == '123'
