import pytest
import os 
from bson import ObjectId

from ...src.repos.mongo.client import get_db
from ...src.repos.minio.client import get_client

datasets = [
    {'uid': '123', '_id': ObjectId(), 'id': '123', 'name': 'test1', 'description': 'test 1'},
    {'uid': '123', '_id': ObjectId(), 'id': '123', 'name': 'test2', 'description': 'test 2'},
    {'uid': '123', '_id': ObjectId(), 'id': '123', 'name': 'test3', 'description': 'test 3', 'likes': 1},
    {'uid': '123', '_id': ObjectId(), 'id': '456', 'name': 'test4', 'description': 'test 4', 'likes': 2},
    {'uid': '123', '_id': ObjectId(), 'id': '789', 'name': 'test5', 'description': 'test 5', 'likes': 3, 'tags': ['tag1', 'tag2']},
    {'uid': '456', '_id': ObjectId(), 'id': '000', 'name': 'test6', 'description': 'test 6'},
]

user = {
    'uid': '123', 
    'name': 'test', 
    'email': 'test', 
    'picture': 'test', 
    'tier': 'dev', 
    'liked_datasets': [str(datasets[3]['_id']), str(datasets[4]['_id'])]
}

tiers = [
    {
        "name": "dev",
        "limits": {
            "datasets": {
                "upload": 1000,
                "download": 1000
            }
        }
    },
    {
        "name": "free",
        "limits": {
            "datasets": {
                "upload": 1,
                "download": 1     
            }
        }
    }
]

tags = [
    {'name': 'tag1'},
    {'name': 'tag2'},
    {'name': 'tag3'},
]

@pytest.fixture
def db():
    db = get_db()
    db['users'].insert_one(user)
    db['tiers'].insert_many(tiers)
    db['datasets'].insert_many(datasets)
    db['tags'].insert_many(tags)
    yield db
    db.drop_collection('users')
    db.drop_collection('tiers')
    db.drop_collection('datasets')
    db.drop_collection('tags')

bucket = os.environ.get('S3_BUCKET')

@pytest.fixture
def s3():
    s3 = get_client()
    if not s3.bucket_exists(bucket):
        s3.make_bucket(bucket)
    test_path = os.path.join(os.path.dirname(__file__), '../test.zip')
    for d in datasets:
        s3.fput_object(bucket, f'{d["id"]}.zip', test_path)
    yield s3
    for obj in s3.list_objects(bucket):
        s3.remove_object(bucket, obj.object_name)
    s3.remove_bucket(bucket)