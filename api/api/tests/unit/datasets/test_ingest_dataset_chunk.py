import pytest
from unittest import mock

from ....src.usecases.datasets.IngestDatasetChunk import IngestDatasetChunk
from ....src.errors import UploadIdDoesNotExist, ChunkUploadChecksumMismatch


@pytest.fixture
def upload():
    return {
        "id": "123",
        "uid": "123",
        "name": "test",
        "dataset": "test",
        "upload_id": "456",
        "checksum": "123",
    }


def test_ingest_chunk_should_fail_if_upload_id_does_not_exists():
    os_repo, s3_repo, db_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.retrieve.return_value = None
    ingest = IngestDatasetChunk(os_repo, s3_repo, db_repo)
    inputs = IngestDatasetChunk.Inputs(
        chunk="test chunk", uid="123", upload_id="456", part_number=1, checksum="123"
    )
    with pytest.raises(UploadIdDoesNotExist):
        ingest(inputs)
    db_repo.retrieve.assert_called_once_with("uploading", "456", "upload_id")
    os_repo.get_object.assert_not_called()


def test_ingest_chunk_should_fail_if_upload_checksum_does_not_match(upload):
    os_repo, s3_repo, db_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.retrieve.return_value = upload
    os_repo.get_object.return_value = "storage"
    s3_repo.store_chunk.return_value = "invalid checksum"
    ingest = IngestDatasetChunk(os_repo, s3_repo, db_repo)
    inputs = IngestDatasetChunk.Inputs(
        chunk="test chunk", uid="123", upload_id="456", part_number=1, checksum="123"
    )
    with pytest.raises(ChunkUploadChecksumMismatch):
        ingest(inputs)
    os_repo.get_object.assert_called_once_with(upload["id"], upload["name"])
    s3_repo.store_chunk.assert_called_once_with("test chunk", "storage", 1, "456")
    db_repo.update.assert_not_called()


def test_ingest_chunk(upload):
    os_repo, s3_repo, db_repo = mock.Mock(), mock.Mock(), mock.Mock()
    db_repo.retrieve.return_value = upload
    os_repo.get_object.return_value = "storage"
    s3_repo.store_chunk.return_value = "123"
    ingest = IngestDatasetChunk(os_repo, s3_repo, db_repo)
    inputs = IngestDatasetChunk.Inputs(
        chunk="test chunk", uid="123", upload_id="456", part_number=1, checksum="123"
    )
    outputs = ingest(inputs)
    assert outputs.message == "Chunk uploaded"
    os_repo.get_object.assert_called_once_with(upload["id"], upload["name"])
    s3_repo.store_chunk.assert_called_once_with("test chunk", "storage", 1, "456")
    db_repo.update.assert_called_once()
