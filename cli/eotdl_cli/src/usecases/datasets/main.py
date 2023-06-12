from ...repos import APIRepo
from .RetrieveDatasets import RetrieveDatasets
from .RetrieveDataset import RetrieveDataset
from .DownloadDataset import DownloadDataset
from .IngestDataset import IngestDataset
from .IngestLargeDataset import IngestLargeDataset
from .IngestLargeDatasetParallel import IngestLargeDatasetParallel
from .UpdateDataset import UpdateDataset


def retrieve_datasets():
    api_repo = APIRepo()
    retrieve = RetrieveDatasets(api_repo)
    inputs = retrieve.Inputs()
    outputs = retrieve(inputs)
    return outputs.datasets


def retrieve_dataset(name):
    api_repo = APIRepo()
    retrieve = RetrieveDataset(api_repo)
    inputs = retrieve.Inputs(name=name)
    outputs = retrieve(inputs)
    return outputs.dataset


def download_dataset(name, path, user, logger):
    dataset = retrieve_dataset(name)
    dataset_id = dataset["id"]
    checksum = dataset["checksum"]
    api_repo = APIRepo()
    download = DownloadDataset(api_repo, logger)
    inputs = download.Inputs(
        dataset=dataset_id, checksum=checksum, path=path, user=user
    )
    outputs = download(inputs)
    return outputs.dst_path


def ingest_dataset(name, description, path, user, logger):
    api_repo = APIRepo()
    ingest = IngestDataset(
        api_repo,
    )
    inputs = ingest.Inputs(name=name, description=description, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


def ingest_large_dataset(name, path, user, logger):
    api_repo = APIRepo()
    ingest = IngestLargeDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


def ingest_large_dataset_parallel(name, path, user, p, logger):
    api_repo = APIRepo()
    ingest = IngestLargeDatasetParallel(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user, threads=p)
    outputs = ingest(inputs)
    return outputs.dataset


def update_dataset(name, path, user, logger):
    api_repo = APIRepo()
    ingest = UpdateDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
