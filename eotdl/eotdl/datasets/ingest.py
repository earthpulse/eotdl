from pathlib import Path
import yaml

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo
from ..files import ingest_files


def ingest_dataset(path, verbose=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger)


def retrieve_dataset(metadata, user):
    repo = DatasetsAPIRepo()
    data, error = repo.retrieve_dataset(metadata.name)
    # print(data, error)
    if data and data["uid"] != user["sub"]:
        raise Exception("Dataset already exists.")
    if error and error == "Dataset doesn't exist":
        # create dataset
        data, error = repo.create_dataset(metadata.dict(), user["id_token"])
        # print(data, error)
        if error:
            raise Exception(error)
        data["id"] = data["dataset_id"]
    return data["id"]


@with_auth
def ingest_folder(folder, verbose=False, logger=print, user=None):
    repo = DatasetsAPIRepo()
    # load metadata
    metadata = yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
    metadata = Metadata(**metadata)
    # retrieve dataset (create if doesn't exist)
    dataset_id = retrieve_dataset(metadata, user)
    # ingest files
    return ingest_files(
        repo, dataset_id, folder, verbose, logger, user, endpoint="datasets"
    )


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestSTAC(api_repo, ingest_file, logger)
#     inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset
