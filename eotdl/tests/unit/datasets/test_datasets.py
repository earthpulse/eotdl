import pytest
from unittest import mock

from eotdl.src.usecases.datasets.RetrieveDatasets import RetrieveDatasets
from eotdl.src.usecases.datasets.RetrieveDataset import RetrieveDataset
from eotdl.src.usecases.datasets.DownloadDataset import DownloadDataset
from eotdl.src.usecases.datasets.IngestDataset import IngestDataset
from eotdl.src.usecases.datasets.IngestLargeDataset import IngestLargeDataset


# def test_retrieve_datasets():
#     repo = mock.Mock()
#     retrieve = RetrieveDatasets(repo)
#     inputs = RetrieveDatasets.Inputs()
#     repo.retrieve_datasets.return_value = [{"name": "test1"}, {"name": "test2"}]
#     outputs = retrieve(inputs)
#     repo.retrieve_datasets.assert_called_once()
#     assert outputs.datasets == ["test1", "test2"]


# def test_retrieve_dataset():
#     repo = mock.Mock()
#     retrieve = RetrieveDataset(repo)
#     inputs = RetrieveDataset.Inputs(name="test")
#     repo.retrieve_dataset.return_value = {"name": "test"}, None
#     outputs = retrieve(inputs)
#     assert outputs.dataset == {"name": "test"}
#     repo.retrieve_dataset.assert_called_once_with("test")


# def test_retrieve_dataset_fails():
#     repo = mock.Mock()
#     retrieve = RetrieveDataset(repo)
#     inputs = RetrieveDataset.Inputs(name="test")
#     repo.retrieve_dataset.return_value = None, "error"
#     with pytest.raises(Exception):
#         retrieve(inputs)
#     repo.retrieve_dataset.assert_called_once_with("test")


# def test_download_dataset():
#     repo = mock.Mock()
#     download = DownloadDataset(repo)
#     inputs = DownloadDataset.Inputs(
#         dataset="test", path="test path", user={"id_token": "test token"}
#     )
#     repo.download_dataset.return_value = "dst path"
#     outputs = download(inputs)
#     assert outputs.dst_path == "dst path"
#     repo.download_dataset.assert_called_once_with("test", "test token", "test path")


# def test_ingest_dataset_fails_if_not_zip():
#     repo = mock.Mock()
#     logger = mock.Mock()
#     ingest = IngestDataset(repo, logger)
#     inputs = IngestDataset.Inputs(
#         name="test",
#         description="test description",
#         path="test path",
#         user={"id_token": "test token"},
#     )
#     with pytest.raises(Exception):
#         ingest(inputs)


# def test_ingest_dataset():
#     repo = mock.Mock()
#     repo.ingest_dataset.return_value = {"name": "test"}, None
#     logger = mock.Mock()
#     ingest = IngestDataset(repo, logger)
#     inputs = IngestDataset.Inputs(
#         name="test",
#         description="test description",
#         path="test_path.zip",
#         user={"id_token": "test token"},
#     )
#     outputs = ingest(inputs)
#     repo.ingest_dataset.assert_called_once_with(
#         "test", "test description", "test_path.zip", "test token"
#     )
#     assert outputs.dataset == {"name": "test"}


# def test_ingest_large_dataset_fails_if_not_zip():
#     repo = mock.Mock()
#     logger = mock.Mock()
#     ingest = IngestLargeDataset(repo, logger)
#     inputs = IngestLargeDataset.Inputs(
#         name="test",
#         description="test description",
#         path="test path",
#         user={"id_token": "test token"},
#     )
#     with pytest.raises(Exception):
#         ingest(inputs)


# def test_ingest_large_dataset():
#     repo = mock.Mock()
#     repo.ingest_large_dataset.return_value = {"name": "test"}, None
#     logger = mock.Mock()
#     ingest = IngestLargeDataset(repo, logger)
#     inputs = IngestLargeDataset.Inputs(
#         name="test",
#         description="test description",
#         path="test_path.zip",
#         user={"id_token": "test token"},
#     )
#     outputs = ingest(inputs)
#     repo.ingest_large_dataset.assert_called_once_with(
#         "test", "test description", "test_path.zip", "test token"
#     )
#     assert outputs.dataset == {"name": "test"}
