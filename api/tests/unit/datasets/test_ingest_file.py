 import pytest
from unittest import mock
from unittest.mock import MagicMock, AsyncMock
from fastapi import UploadFile
from io import BytesIO
import asyncio

from ....src.usecases.datasets.ingest_file import IngestFile
from ....src.errors import DatasetDoesNotExistError, TierLimitError


@pytest.fixture
def user():
    return {"uid": "123", "name": "test", "email": "test", "picture": "test"}


@pytest.fixture
def tier():
    return {
        "name": "dev",
        "limits": {
            "datasets": {"upload": 10, "download": 100, "count": 10, "files": 10}
        },
    }


@pytest.mark.asyncio
async def test_ingest_file_to_new_dataset(user, tier):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        None,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    db_repo.find_in_time_range.return_value = []  # usage
    db_repo.generate_id.return_value = "123"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    outputs = await ingest_file(inputs)
    assert outputs.dataset.name == "test-dataset-name"
    db_repo.retrieve.assert_called_once_with("users", "123", "uid")


@pytest.fixture
def dataset():
    return {"uid": "123", "id": "123", "name": "test-dataset-name"}


@pytest.mark.asyncio
async def test_ingest_file_to_existing_dataset(user, tier, dataset):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        dataset,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    outputs = await ingest_file(inputs)
    assert outputs.dataset.name == "test-dataset-name"


@pytest.mark.asyncio
async def test_ingest_file_to_existing_dataset_fails_if_user_is_not_owner(
    user, tier, dataset
):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    dataset["uid"] = "456"
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        dataset,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    with pytest.raises(DatasetDoesNotExistError):
        outputs = await ingest_file(inputs)


@pytest.mark.asyncio
async def test_ingest_file_to_new_dataset_fails_if_limits_exceeded(user, tier, dataset):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    tier["limits"]["datasets"]["upload"] = 0
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        None,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    db_repo.find_in_time_range.return_value = []  # usage
    db_repo.generate_id.return_value = "123"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    with pytest.raises(TierLimitError):
        outputs = await ingest_file(inputs)


@pytest.mark.asyncio
async def test_ingest_file_to_existing_dataset_sucess_if_limits_exceeded(
    user, tier, dataset
):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    tier["limits"]["datasets"]["upload"] = 0
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        dataset,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    db_repo.find_in_time_range.return_value = []  # usage
    db_repo.generate_id.return_value = "123"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    outputs = await ingest_file(inputs)
    assert outputs.dataset.name == "test-dataset-name"


@pytest.mark.asyncio
async def test_ingest_file_to_existing_dataset_fails_if_count_exceeded(
    user, tier, dataset
):
    db_repo, os_repo = mock.Mock(), mock.Mock()
    tier["limits"]["datasets"]["files"] = 0
    db_repo.find_one_by_name.side_effect = [
        tier,  # tier
        dataset,  # dataset,
        None,  # new dataset name
    ]
    db_repo.retrieve.return_value = user
    db_repo.find_in_time_range.return_value = []  # usage
    db_repo.generate_id.return_value = "123"
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "example.txt"
    mock_file.file = BytesIO(b"Mock file content")
    mock_file.size = 100
    os_repo.calculate_checksum = AsyncMock(return_value="123")
    ingest_file = IngestFile(db_repo, os_repo)
    inputs = IngestFile.Inputs(
        dataset="test-dataset-name", file=mock_file, uid="123", checksum="123"
    )
    with pytest.raises(TierLimitError):
        outputs = await ingest_file(inputs)
