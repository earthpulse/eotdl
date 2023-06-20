import pytest
from unittest import mock

from ....src.usecases.datasets.CompleteMultipartUpload import CompleteMultipartUpload
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


def test_complete_upload_fails_if_tier_limits_surpassed(user, tier):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.return_value = tier
    db_repo.find_in_time_range.return_value = [1] * 100
    os_repo = mock.Mock()
    s3_repo = mock.Mock()
    retrieve = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(
        name="test", description="test", uid="123", id="456", upload_id="789"
    )
    with pytest.raises(TierLimitError):
        retrieve(inputs)
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")
    db_repo.find_one_by_name.assert_called_once_with("tiers", "free")
    db_repo.find_in_time_range.assert_called_once_with(
        "usage", "123", "dataset_ingested", "type"
    )


def test_complete_upload_fails_if_dataset_exists(user, tier, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    os_repo = mock.Mock()
    s3_repo = mock.Mock()
    retrieve = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(
        name="test", description="test", uid="123", id="456", upload_id="789"
    )
    with pytest.raises(DatasetAlreadyExistsError):
        retrieve(inputs)


def test_complete_upload(user, tier, dataset):
    db_repo = mock.Mock()
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]
    db_repo.find_in_time_range.return_value = []
    db_repo.persist.return_value = dataset
    os_repo = mock.Mock()
    os_repo.get_object.return_value = "test"
    os_repo.get_size.return_value = 100
    s3_repo = mock.Mock()
    s3_repo.multipart_upload_id.return_value = "456"
    retrieve = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(
        name="test", description="test", uid="123", id="456", upload_id="789"
    )
    outputs = retrieve(inputs)
    assert outputs.dataset.id == "456"
    assert outputs.dataset.name == "test"
    assert outputs.dataset.description == "test"
    # db_repo.persist.assert_called_once_with("datasets", outputs.dataset.dict(), "456")
    db_repo.increase_counter.assert_called_once_with(
        "users", "uid", "123", "dataset_count"
    )
    s3_repo.complete_multipart_upload.assert_called_once_with("test", "789")
    os_repo.get_object.assert_called_once_with("456")
    os_repo.get_size.assert_called_once_with("456")
