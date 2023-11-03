import pytest
from fastapi.testclient import TestClient
from api.main import app

from api.src.repos.mongo.client import get_db

client = TestClient(app)

@pytest.fixture
def db():
    db = get_db()
    db['tags'].insert_many([{'name': 'tag1'}, {'name': 'tag2'}])
    yield db
    db.drop_collection('tags')
    
@pytest.fixture
def url():
    yield '/tags'

def test_retrieve_tags(url, db):
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data == ['tag1', 'tag2']

def test_retrieve_empty_tags(url):
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    assert data == []