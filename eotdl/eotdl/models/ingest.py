from pathlib import Path
import yaml

from ..auth import with_auth
from .metadata import Metadata
from ..repos import ModelsAPIRepo
from ..shared import calculate_checksum
from ..files import ingest_files


def ingest_model(path, verbose=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger)


def retrieve_model(metadata, user):
    repo = ModelsAPIRepo()
    data, error = repo.retrieve_model(metadata.name)
    # print(data, error)
    if data and data["uid"] != user["uid"]:
        raise Exception("Model already exists.")
    if error and error == "Model doesn't exist":
        # create dataset
        data, error = repo.create_model(metadata.dict(), user)
        # print(data, error)
        if error:
            raise Exception(error)
        data["id"] = data["model_id"]
    return data["id"]


@with_auth
def ingest_folder(folder, verbose=False, logger=print, user=None):
    repo = ModelsAPIRepo()
    # load metadata
    metadata = yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
    metadata = Metadata(**metadata)
    # retrieve model (create if doesn't exist)
    model_id = retrieve_model(metadata, user)
    # ingest files
    return ingest_files(
        repo, model_id, folder, verbose, logger, user, endpoint="models"
    )
