import json
import functools

import prometheus_client

from ...repos import OSRepo, GeoDBRepo, FilesDBRepo
from .retrieve_dataset import retrieve_dataset, retrieve_owned_dataset
from ..user import retrieve_user_credentials


eotdl_api_downloaded_bytes = prometheus_client.Counter(
    "eotdl_api_downloaded_bytes",
    documentation="Bytes downloaded from this api",
    labelnames=["user_email"],
)


def download_dataset_file(dataset_id, filename, user, version=None):
    os_repo = OSRepo()
    dataset = retrieve_dataset(dataset_id)
    # check_user_can_download_dataset(user)
    if version is None:  # retrieve latest version
        files_repo = FilesDBRepo()
        files = files_repo.retrieve_file(dataset.files, filename)
        if not files or "files" not in files:
            raise Exception("File does not exist")
        file = sorted(files["files"], key=lambda x: x["version"])[-1]
        version = file["version"]

    async def track_download_volume(*args, **kwargs):
        async for data in os_repo.data_stream(*args, **kwargs):
            eotdl_api_downloaded_bytes.labels(user.email).inc(len(data))
            yield data

    filename = f"{filename}_{version}"
    object_info = os_repo.object_info(dataset_id, filename)
    return track_download_volume, object_info, filename


def download_stac_catalog(dataset_id, user):
    # check if dataset exists 
    dataset = retrieve_dataset(dataset_id)
    # retrieve from geodb
    credentials = retrieve_user_credentials(user)
    geodb_repo = GeoDBRepo(credentials)
    gdf = geodb_repo.retrieve(dataset_id)
    # TODO: report usage
    return json.loads(gdf.to_json())
