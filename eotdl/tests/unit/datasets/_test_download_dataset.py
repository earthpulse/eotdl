import pytest
from unittest import mock
from unittest.mock import patch

from eotdl.src.usecases.datasets.DownloadDataset import DownloadDataset


@pytest.fixture
def dataset():
    return {
        "name": "test",
        "id": "test-id",
        "files": [{"name": "test-file", "size": 123, "checksum": "123"}],
    }


@pytest.fixture
def user():
    return {"id_token": "test token"}
