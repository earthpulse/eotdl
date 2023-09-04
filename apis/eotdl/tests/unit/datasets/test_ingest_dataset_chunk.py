import pytest
from unittest import mock

from ....src.usecases.datasets.IngestDatasetChunk import IngestDatasetChunk


def test_generate_upload_id():
    os_repo = mock.Mock()
    os_repo.get_object.return_value = "test"
    s3_repo = mock.Mock()
    retrieve = IngestDatasetChunk(os_repo, s3_repo)
    inputs = IngestDatasetChunk.Inputs(
        chunk="test chunk", id="123", upload_id="456", part_number=1
    )
    outputs = retrieve(inputs)
    assert outputs.id == "123"
    assert outputs.upload_id == "456"
    os_repo.get_object.assert_called_once_with("123")
    s3_repo.store_chunk.assert_called_once_with("test chunk", "test", 1, "456")
