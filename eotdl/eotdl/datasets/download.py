from ..src.repos import APIRepo
from ..src.usecases.datasets import DownloadDataset, DownloadFile
from .retrieve import retrieve_dataset
from ..auth import with_auth


@with_auth
def download_dataset(dataset, file, path=None, logger=None, user=None):
    api_repo = APIRepo()
    download = DownloadDataset(api_repo, retrieve_dataset, logger)
    inputs = download.Inputs(dataset=dataset, file=file, path=path, user=user)
    outputs = download(inputs)
    return outputs.dst_path
