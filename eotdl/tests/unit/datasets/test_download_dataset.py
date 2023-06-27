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


# @patch("eotdl.src.utils.calculate_checksum")  # mock not working :(
# def test_download_one_file(mock_checksum, dataset, user):
#     repo, retrieve_dataset, logger = mock.Mock(), mock.Mock(), mock.Mock()
#     mock_checksum.return_value = "123"
#     download = DownloadDataset(repo, retrieve_dataset, logger)
#     inputs = DownloadDataset.Inputs(
#         dataset=dataset["name"], file="test-file", user=user
#     )
#     retrieve_dataset.return_value = dataset
#     repo.download_file.return_value = "dst_path"
#     outputs = download(inputs)
#     assert outputs.dst_path == "dst_path"
#     repo.download_file.assert_called_once_with(
#         dataset["name"], dataset["id"], "test-file", user["id_token"], None
#     )
