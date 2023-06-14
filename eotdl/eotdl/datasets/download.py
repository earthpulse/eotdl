from ..src.repos import APIRepo
from ..src.usecases.datasets.DownloadDataset import DownloadDataset
from .retrieve import retrieve_dataset


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
