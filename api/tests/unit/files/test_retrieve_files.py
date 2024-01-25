import pytest
from unittest.mock import patch


from api.src.usecases.files import retrieve_files
from api.src.models import Version


@pytest.fixture
def files():
    return {
        "id": "123",
        "dataset": "123",
        "files": [
            {"name": "test3", "version": "1", "checksum": "123", "size": 123},
            {"name": "test4", "version": "1", "checksum": "123", "size": 123},
        ],
    }


@pytest.fixture
def versions():
    return [Version(version_id="1"), Version(version_id="2"), Version(version_id="3")]


@patch("api.src.usecases.files.retrieve_files.FilesDBRepo")
def test_retrieve_all_files(mocked_repo, files, versions):
    mocked_repo_instance = mocked_repo.return_value
    mocked_repo_instance.retrieve_files.return_value = [files]
    files = retrieve_files(versions, files["id"])
    assert len(files) == 2
    assert files[0]["filename"] == "test3"
    assert files[1]["filename"] == "test4"
    mocked_repo_instance.retrieve_files.assert_called_once()
