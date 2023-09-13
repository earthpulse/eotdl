from ..src.repos import APIRepo
from ..src.usecases.datasets import DownloadDataset, DownloadFileURL
from .retrieve import retrieve_dataset
from ..auth import with_auth


@with_auth
def download_dataset(
    dataset, file=None, path=None, logger=None, assets=False, force=False, user=None
):
    api_repo = APIRepo()
    download = DownloadDataset(api_repo, retrieve_dataset, logger)
    inputs = download.Inputs(
        dataset=dataset, file=file, path=path, user=user, assets=assets, force=force
    )
    outputs = download(inputs)
    return outputs.dst_path


@with_auth
def download_file_url(url, path, progress=True, logger=None, user=None):
    api_repo = APIRepo()
    download = DownloadFileURL(api_repo, logger, progress)
    inputs = DownloadFileURL.Inputs(url=url, path=path, user=user)
    outputs = download(inputs)
    return outputs.dst_path
