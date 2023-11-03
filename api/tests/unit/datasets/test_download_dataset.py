import pytest 
from unittest import mock

<<<<<<< HEAD:apis/eotdl/tests/unit/datasets/test_download_dataset.py
from ....src.usecases.datasets.DownloadDataset import DownloadDataset
from ....src.errors import TierLimitError, DatasetDoesNotExistError
from ....src.models import Usage
=======
from api.src.usecases.datasets.download_dataset import DownloadDataset
from api.src.errors import (
    TierLimitError,
    DatasetDoesNotExistError,
    FileDoesNotExistError,
)

>>>>>>> develop:api/tests/unit/datasets/test_download_dataset.py

@pytest.fixture
def tier():
    return {
        "name": "free",
        "limits": {
            "datasets": {
                "upload": 10,
                "download": 10
            }
        }
    }

@pytest.fixture
def user():
	return {'uid': '123', 'email': 'test', 'name': 'test', 'picture': 'test', 'tier': 'free'}

@pytest.fixture
def dataset():
	return {'uid': '123', 'id': '123', 'name': 'test', 'description': 'test'}

def test_download_dataset_fails_if_tier_limits_surpassed(tier, user):
	db_repo = mock.Mock()
	db_repo.retrieve.return_value = user
	db_repo.find_one_by_name.return_value = tier
	db_repo.find_in_time_range.return_value = [1]*100
	os_repo = mock.Mock()
	download = DownloadDataset(db_repo, os_repo)
	inputs = DownloadDataset.Inputs(id="123", uid="123")
	with pytest.raises(TierLimitError):
		download(inputs)
	db_repo.retrieve.assert_called_once_with('users', user['uid'], 'uid')
	db_repo.find_one_by_name.assert_called_once_with('tiers', user['tier'])
	db_repo.find_in_time_range.assert_called_once_with('usage', user['uid'], 'dataset_download', 'type')
	
def test_download_dataset_fails_if_dataset_not_found(tier, user, dataset):
	db_repo = mock.Mock()
	db_repo.retrieve.side_effect = [user, None]
	db_repo.find_one_by_name.return_value = tier
	db_repo.find_in_time_range.return_value = []
	os_repo = mock.Mock()
	download = DownloadDataset(db_repo, os_repo)
	inputs = DownloadDataset.Inputs(id="123", uid="123")
	with pytest.raises(DatasetDoesNotExistError):
		download(inputs)
	
def test_download_dataset(tier, user, dataset):
	db_repo = mock.Mock()
	db_repo.retrieve.side_effect = [user, dataset]
	db_repo.find_one_by_name.return_value = tier
	db_repo.find_in_time_range.return_value = []
	os_repo = mock.Mock()
	os_repo.data_stream = 'test'
	os_repo.object_info.return_value = 'test'
	download = DownloadDataset(db_repo, os_repo)
	inputs = DownloadDataset.Inputs(id="123", uid="123")
	outputs = download(inputs)
	assert outputs.data_stream == 'test'
	assert outputs.object_info == 'test'
	assert outputs.name == 'test'
	usage = Usage.DatasetDownload(uid=user['uid'], payload={'dataset': dataset['id']})
	db_repo.persist.assert_called_once_with('usage', usage.dict())
	db_repo.increase_counter.assert_called_once_with('datasets', 'id', dataset['id'], 'downloads')