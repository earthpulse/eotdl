import json
import prometheus_client

from ...repos import OSRepo, GeoDBRepo, FilesDBRepo, MongoDBRepo
from .retrieve_dataset import retrieve_dataset
from ..user import retrieve_user_credentials


eotdl_api_downloaded_bytes = prometheus_client.Counter(
    "eotdl_api_downloaded_bytes",
    documentation="Bytes downloaded from this api",
    labelnames=["user_email"],
)


def download_dataset_file(dataset_id, filename, user, version=None):
    os_repo = OSRepo()
    # check_user_can_download_dataset(user)
    if version is None:  # retrieve latest version
       version = retrieve_latest_file_version(dataset_id, filename)
       
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
    # credentials = retrieve_user_credentials(user)
    # geodb_repo = GeoDBRepo(credentials)
    geodb_repo = MongoDBRepo()
    gdf = geodb_repo.retrieve(dataset_id)
    # TODO: report usage
    data = json.loads(gdf.to_json())
    return data

def generate_presigned_url(dataset_id, filename, version=None):
    repo = OSRepo()
    if version is None:  # retrieve latest version
       version = retrieve_latest_file_version(dataset_id, filename)
    filename = f"{filename}_{version}"
    return repo.get_file_url(dataset_id, filename)

def retrieve_latest_file_version(dataset_id, filename):
    files_repo = FilesDBRepo()
    dataset = retrieve_dataset(dataset_id)
    files = files_repo.retrieve_file(dataset.files, filename)
    if not files or "files" not in files:
        raise Exception("File does not exist")
    file = sorted(files["files"], key=lambda x: x["version"])[-1]
    version = file["version"]
    return version