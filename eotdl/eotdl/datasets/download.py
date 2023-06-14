from ..src.repos import APIRepo
from ..src.usecases.datasets import DownloadDataset
from .retrieve import retrieve_dataset
from ..auth import with_auth


@with_auth
def download_dataset(name, path=None, logger=None, user=None):
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
