# all in one file to avoid problems with db

import pytest
import os 

from fastapi.testclient import TestClient
from api.main import app

from ...routers.auth import get_current_user, key_auth
from ...src.models import User
from .setup import user, db, s3

client = TestClient(app)

SKIP = False

# override token auth 

def get_current_user_mock():
	return User(**user)

def key_auth_mock():
	return True

app.dependency_overrides[get_current_user] = get_current_user_mock
app.dependency_overrides[key_auth] = key_auth_mock

@pytest.fixture
def url():
    yield '/datasets'

# ingest dataset

@pytest.mark.skipif(SKIP, reason='skip')
def test_ingest_dataset(url, db):
    response = client.post(
        url, 
        data={'name': 'test', 'description': 'test'},
        files={'file': open(os.path.join(os.path.dirname(__file__), '../test.zip'), 'rb')}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test'
    assert data['description'] == 'test'
    assert data['tags'] == []
    assert data['uid'] == '123'

# retrieve datasets

@pytest.mark.skipif(SKIP, reason='skip')
def test_retrieve_all_datasets(url, db):
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert data[0]['name'] == 'test1' 
    assert data[1]['name'] == 'test2'
    assert data[2]['name'] == 'test3'

@pytest.mark.skipif(SKIP, reason='skip')
def test_retrieve_datasets_with_limits(url, db):
    response = client.get(f"{url}?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['name'] == 'test1'
    assert data[1]['name'] == 'test2'

@pytest.mark.skipif(SKIP, reason='skip')
def test_retireve_dataset_by_name(url, db):
    response = client.get(f"{url}?name=test1")
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'test1'

@pytest.mark.skipif(SKIP, reason='skip')
def test_retrieve_liked_datasets(url, db):
    url += '/liked'
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['name'] == 'test4'
    assert data[1]['name'] == 'test5'

@pytest.mark.skipif(SKIP, reason='skip')
def test_retrieve_popular_datasets(url, db):
    url += '/popular'
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6
    assert data[0]['name'] == 'test5' 
    assert data[1]['name'] == 'test4'

@pytest.mark.skipif(SKIP, reason='skip')
def test_retrieve_popular_datasets_with_limit(url, db):
    url += '/popular?limit=2'
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]['name'] == 'test5' 
    assert data[1]['name'] == 'test4'

# download

@pytest.mark.skipif(SKIP, reason='skip')
def test_download_dataset(url, db, s3):
    url += '/123/download'
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers['Content-Disposition'] == 'attachment; filename="test1.zip"'
    assert response.headers['Content-Type'] == 'application/zip'
    original = os.path.join(os.path.dirname(__file__), '../test.zip')
    assert response.headers['Content-Length'] == str(os.path.getsize(original))
    # save file to disk
    dst = os.path.join(os.path.dirname(__file__), 'test_download.zip')
    with open(dst, 'wb') as f: f.write(response.content)
    # check file size
    assert os.path.getsize(dst) == os.path.getsize(original)
    # remove file
    os.remove(dst)

# edit 

@pytest.mark.skipif(SKIP, reason='skip')
def test_edit_dataset(url, db):
    dataset = db['datasets'].find_one({'id': '456'})
    _url = url + f"/{str(dataset['_id'])}"
    response = client.put(_url, json={'name': 'new-name', 'description': 'new description', 'tags': ['tag1', 'tag2']})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'new-name'
    assert data['description'] == 'new description'
    assert data['tags'] == ['tag1', 'tag2']
    # # invalid dataset
    # _url = url + f"/invalid"
    # response = client.put(_url, json={'name': 'new-name', 'description': 'new description', 'tags': ['tag1', 'tag2']})
    # assert response.status_code != 200
    # # invalid user
    # dataset = db['datasets'].find_one({'id': '000'})
    # _url = url + f"/{str(dataset['_id'])}"
    # response = client.put(_url, json={'name': 'new-name', 'description': 'new description', 'tags': ['tag1', 'tag2']})
    # assert response.status_code != 200
    # # invalid new name
    # dataset = db['datasets'].find_one({'id': '456'})
    # _url = url + f"/{str(dataset['_id'])}"
    # response = client.put(_url, json={'name': '123'})
    # assert response.status_code != 200
    # # existing new name
    # response = client.put(_url, json={'name': dataset['name']})
    # assert response.status_code != 200
    # # invalid tags
    # response = client.put(_url, json={'tags': ['tag4']})
    # assert response.status_code != 200
    # update only name
    response = client.put(_url, json={'name': 'new-name2'})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'new-name2'
    assert data['description'] == 'new description'
    assert data['tags'] == ['tag1', 'tag2']
    # update only description
    response = client.put(_url, json={'description': 'new description 2'})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'new-name2'
    assert data['description'] == 'new description 2'
    assert data['tags'] == ['tag1', 'tag2']
    # update only tags
    response = client.put(_url, json={'tags': ['tag3']})
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == 'new-name2'
    assert data['description'] == 'new description 2'
    assert data['tags'] == ['tag3']

@pytest.mark.skipif(SKIP, reason='skip')
def test_like_dataset(url, db):
    dataset = db['datasets'].find_one({'id': '456'})
    assert dataset['likes'] == 2
    assert str(dataset['_id']) in db['users'].find_one({'uid': '123'})['liked_datasets']
    url += f"/{str(dataset['_id'])}/like"
    response = client.put(url)
    assert response.status_code == 200
    assert db['datasets'].find_one({'id': '456'})['likes'] == 1
    assert str(dataset['_id']) not in db['users'].find_one({'uid': '123'})['liked_datasets']
    response = client.put(url)
    assert response.status_code == 200
    assert db['datasets'].find_one({'id': '456'})['likes'] == 2
    assert str(dataset['_id']) in db['users'].find_one({'uid': '123'})['liked_datasets']
