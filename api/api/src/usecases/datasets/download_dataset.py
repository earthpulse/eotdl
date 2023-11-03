import json

from ...repos import OSRepo, GeoDBRepo, FilesDBRepo
from .retrieve_dataset import retrieve_dataset, retrieve_owned_dataset
from ..user import retrieve_user_credentials


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
    data_stream = os_repo.data_stream
    filename = f"{filename}_{version}"
    object_info = os_repo.object_info(dataset_id, filename)
    return data_stream, object_info, filename


def download_stac_catalog(dataset_id, user):
    # check if dataset exists and user is owner
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    # retrieve from geodb
    credentials = retrieve_user_credentials(user)
    geodb_repo = GeoDBRepo(credentials)
    gdf = geodb_repo.retrieve(dataset_id)
    # TODO: report usage
    return json.loads(gdf.to_json())
