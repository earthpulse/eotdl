import pytest
import os

from ...src.repos.minio.client import get_client
from ...src.repos.minio import MinioRepo

bucket = os.environ.get('S3_BUCKET')

@pytest.fixture
def s3():
	s3 = get_client()
	test_path = os.path.join(os.path.dirname(__file__), '../test.zip')
	s3.fput_object(bucket, 'test.zip', test_path)
	yield s3
	for obj in s3.list_objects(bucket):
		s3.remove_object(bucket, obj.object_name)
	

def test_get_object():
	repo = MinioRepo()
	assert repo.get_object('test') == 'test.zip'

def test_persist_file(s3):
	repo = MinioRepo()
	test_path = os.path.join(os.path.dirname(__file__), '../test.zip')
	file = open(test_path, 'rb')
	repo.persist_file(file, 'test')
	assert s3.stat_object(bucket, 'test.zip').size == os.path.getsize(test_path)

def test_delete(s3):
	repo = MinioRepo()
	repo.delete('test')
	assert list(s3.list_objects(bucket)) == []