import json
import prometheus_client

from ...repos import OSRepo, GeoDBRepo, FilesDBRepo
from .retrieve_model import retrieve_model
from ..user import retrieve_user_credentials
from ..datasets.stage_dataset import eotdl_api_downloaded_bytes


def download_model_file(model_id, filename, user, version=None):
    os_repo = OSRepo()
    if version is None:  # retrieve latest version
        version = retrieve_latest_file_version(model_id, filename)

    async def track_download_volume(*args, **kwargs):
        async for data in os_repo.data_stream(*args, **kwargs):
            eotdl_api_downloaded_bytes.labels(user.email).inc(len(data))
            yield data

    filename = f"{filename}_{version}"
    object_info = os_repo.object_info(model_id, filename)
    return track_download_volume, object_info, filename


def download_stac_catalog(model_id, user):
    # check if dataset exists
    dataset = retrieve_model(model_id)
    # retrieve from geodb
    credentials = retrieve_user_credentials(user)
    geodb_repo = GeoDBRepo(credentials)
    gdf = geodb_repo.retrieve(model_id)
    # TODO: report usage
    return json.loads(gdf.to_json())


def retrieve_latest_file_version(model_id, filename):
    files_repo = FilesDBRepo()
    model = retrieve_model(model_id)
    files = files_repo.retrieve_file(model.files, filename)
    if not files or "files" not in files:
        raise Exception("File does not exist")
    file = sorted(files["files"], key=lambda x: x["version"])[-1]
    version = file["version"]
    return version
