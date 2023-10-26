from pathlib import Path
from glob import glob
import yaml
from tqdm import tqdm
import os

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..files import ingest_file


def ingest_dataset(path, verbose=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger)


@with_auth
def ingest_folder(folder, verbose=False, logger=print, user=None):
    repo, files_repo = DatasetsAPIRepo(), FilesAPIRepo()
    logger(f"Uploading directory {folder}...")
    # get all files in directory recursively
    items = [Path(item) for item in glob(str(folder) + "/**/*", recursive=True)]
    # remove directories
    items = [item for item in items if not item.is_dir()]
    if len(items) == 0:
        raise Exception("No files found in directory")
    if not any(item.name == "metadata.yml" for item in items):
        raise Exception("metadata.yml not found in directory")
    # load metadata
    metadata = yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
    metadata = Metadata(**metadata)
    # if zip or tar file, send error
    if any(item.suffix.endswith((".zip", ".tar", ".tar.gz", ".gz")) for item in items):
        raise Exception(
            f"At least one zip, tar or gz file found in {folder}, please unzip and try again"
        )
    # create dataset
    data, error = repo.create_dataset(metadata.dict(), user["id_token"])
    # dataset may already exist, and will return an error, but if user is owner continue ingesting files
    current_files = []
    if error:
        data, error2 = repo.retrieve_dataset(metadata.name)
        if error2:
            raise Exception(error)
        if data["uid"] != user["sub"]:
            raise Exception("Dataset already exists.")
        data["dataset_id"] = data["id"]
    dataset_id = data["dataset_id"]
    # create new version
    data, error = repo.create_version(dataset_id, user["id_token"])
    if error:
        raise Exception(error)
    version = data["version"]
    # upload files
    current_files = []
    if version > 1:
        current_files, error = files_repo.retrieve_dataset_files(
            dataset_id, version - 1
        )
        if error:
            # print("retreive dataset files error: ", error)
            current_files = []
    for item in tqdm(items, desc="Uploading files", unit="files", disable=verbose):
        data = ingest_file(
            str(item),
            dataset_id,
            version,
            str(item.relative_to(folder).parent),
            logger=logger,
            verbose=verbose,
            user=user,
            current_files=current_files,
            endpoint="datasets",
        )
    return data


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestSTAC(api_repo, ingest_file, logger)
#     inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset
