import pytest
from unittest import mock
from unittest.mock import AsyncMock
from pydantic import BaseModel

from api.src.usecases.datasets.CompleteMultipartUpload import CompleteMultipartUpload
from api.src.errors import (
    DatasetAlreadyExistsError,
    TierLimitError,
    UploadIdDoesNotExist,
    ChecksumMismatch,
)


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
    return {
        "name": "dev",
        "limits": {
            "datasets": {"upload": 10, "download": 100, "count": 10, "files": 10}
        },
    }


@pytest.fixture
def dataset():
    return {
        "name": "test-dataset-name",
        "description": "test",
        "uid": "123",
        "id": "123",
    }


@pytest.fixture
def upload():
    return {
        "id": "123",
        "uid": "123",
        "name": "test-file-name",
        "dataset": "test-dataset-name",
        "upload_id": "456",
        "checksum": "123",
    }


@pytest.mark.asyncio
async def test_complete_upload_fails_if_upload_not_found():
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = None
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id="789")
    with pytest.raises(UploadIdDoesNotExist):
        await complete(inputs)
    db_repo.find_one.assert_called_once_with(
        "uploading", {"uid": "123", "upload_id": "789"}
    )
    db_repo.db_repo.find_one_by_name.assert_not_called()


@pytest.mark.asyncio
async def test_complete_upload_fails_if_tier_limits_surpassed(upload, user, tier):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]
    db_repo.find_in_time_range.return_value = [1] * 100
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id="789")
    with pytest.raises(TierLimitError):
        await complete(inputs)
    assert db_repo.find_one_by_name.call_count == 2
    os_repo.get_object.assert_not_called()


@pytest.mark.asyncio
async def test_complete_upload_fails_if_dataset_exists(user, tier, dataset, upload):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    dataset["uid"] = "other uid"
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id="789")
    with pytest.raises(DatasetAlreadyExistsError):
        await complete(inputs)
    os_repo.get_object.assert_not_called()


@pytest.mark.asyncio
async def test_complete_upload_fails_if_file_limit_exceeded(
    user, tier, dataset, upload
):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    tier["limits"]["datasets"]["files"] = 0
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(
        name="test", description="test", uid="123", id="456", upload_id="789"
    )
    with pytest.raises(TierLimitError):
        await complete(inputs)
    os_repo.get_object.assert_not_called()


@pytest.mark.asyncio
async def test_complete_upload_fails_if_checksum_mismatch(user, tier, dataset, upload):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    os_repo.get_object.return_value = "storage"
    os_repo.calculate_checksum = AsyncMock(return_value="invalid checksum")
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id=upload["id"])
    with pytest.raises(ChecksumMismatch):
        await complete(inputs)
    os_repo.get_object.assert_called_once_with(dataset["id"], upload["name"])
    s3_repo.complete_multipart_upload.assert_called_once_with("storage", upload["id"])
    os_repo.object_info.assert_called_once_with(dataset["id"], upload["name"])
    os_repo.delete_file.assert_called_once_with(dataset["id"], upload["name"])
    db_repo.delete.assert_called_once_with("datasets", dataset["id"])
    db_repo.presist.assert_not_called()


class ObjectInfo(BaseModel):
    size: int = 100


@pytest.mark.asyncio
async def test_complete_upload_new_dataset(user, tier, dataset, upload):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, None]
    db_repo.find_in_time_range.return_value = []
    os_repo.get_object.return_value = "storage"
    os_repo.object_info.return_value = ObjectInfo()
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id=upload["id"])
    outputs = await complete(inputs)
    assert outputs.dataset.id == upload["id"]
    assert outputs.dataset.name == upload["dataset"]
    assert db_repo.persist.call_count == 2
    # assert db_repo.persist.call_args_list[0] == (
    #     "datasets",
    #     outputs.dataset.dict(),
    #     upload["id"],
    # )
    db_repo.increase_counter.assert_called_once_with(
        "users", "uid", user["uid"], "dataset_count"
    )
    db_repo.delete.assert_called_once_with("uploading", upload["id"])
    db_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_complete_upload_existing_dataset(user, tier, dataset, upload):
    db_repo, s3_repo, os_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.find_one.return_value = upload
    db_repo.retrieve.return_value = user
    db_repo.find_one_by_name.side_effect = [tier, dataset]
    db_repo.find_in_time_range.return_value = []
    os_repo.get_object.return_value = "storage"
    os_repo.object_info.return_value = ObjectInfo()
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    complete = CompleteMultipartUpload(db_repo, os_repo, s3_repo)
    inputs = CompleteMultipartUpload.Inputs(uid="123", upload_id=upload["id"])
    outputs = await complete(inputs)
    assert outputs.dataset.id == upload["id"]
    assert outputs.dataset.name == upload["dataset"]
    db_repo.persist.assert_called_once()
    db_repo.increase_counter.assert_not_called()
    db_repo.delete.assert_called_once_with("uploading", upload["id"])
    db_repo.update.assert_called_once_with(
        "datasets", upload["id"], outputs.dataset.dict()
    )
