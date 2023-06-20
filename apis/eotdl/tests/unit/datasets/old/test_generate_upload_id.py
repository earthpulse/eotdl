import pytest
from unittest import mock

from ....src.usecases.datasets.GenerateUploadId import GenerateUploadId
from ....src.errors import DatasetAlreadyExistsError, TierLimitError


@pytest.fixture
def user():
    return {
        "uid": "123",
        "email": "test",
        "name": "test",
        "picture": "test",
        "tier": "free",
    }


@pytest.fixture
def tier():
    return {"name": "dev", "limits": {"datasets": {"upload": 10, "download": 100}}}


@pytest.fixture
def dataset():
    return {"name": "test", "description": "test", "uid": "123"}


def test_generate_upload_id_fails_if_tier_limits_surpassed(user, tier):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = [1] * 100
    os_repo = mock.Mock()
    s3_repo = mock.Mock()
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(name="test", description="test", uid="123")
    with pytest.raises(TierLimitError):
        retrieve(inputs)
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")
    db_repo.find_one_by_name.assert_called_once_with("tiers", "free")
    db_repo.find_in_time_range.assert_called_once_with(
        "usage", "123", "dataset_ingested", "type"
    )


def test_generate_upload_id_fails_if_dataset_exists(user, tier, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    os_repo = mock.Mock()
    s3_repo = mock.Mock()
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(name="test", description="test", uid="123")
    with pytest.raises(DatasetAlreadyExistsError):
        retrieve(inputs)


def test_generate_upload_id(user, tier, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]
    db_repo.find_in_time_range.return_value = []
    db_repo.generate_id.return_value = "123"
    os_repo = mock.Mock()
    os_repo.get_object.return_value = "test"
    s3_repo = mock.Mock()
    s3_repo.multipart_upload_id.return_value = "456"
    retrieve = GenerateUploadId(db_repo, os_repo, s3_repo)
    inputs = GenerateUploadId.Inputs(name="test", description="test", uid="123")
    outputs = retrieve(inputs)
    assert outputs.dataset_id == "123"
    assert outputs.upload_id == "456"
    db_repo.generate_id.assert_called_once()
    os_repo.get_object.assert_called_once_with("123")
    s3_repo.multipart_upload_id.assert_called_once_with("test")
