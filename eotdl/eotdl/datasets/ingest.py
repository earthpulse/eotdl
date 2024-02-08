from pathlib import Path
import yaml
from tqdm import tqdm
import json

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..files import ingest_files, create_new_version
from ..curation.stac import STACDataFrame
from ..shared import calculate_checksum


def ingest_dataset(path, verbose=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    if "catalog.json" in [f.name for f in path.iterdir()]:
        return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger)


def retrieve_dataset(metadata, user):
    repo = DatasetsAPIRepo()
    data, error = repo.retrieve_dataset(metadata.name)
    # print(data, error)
    if data and data["uid"] != user["uid"]:
        raise Exception("Dataset already exists.")
    if error and error == "Dataset doesn't exist":
        # create dataset
        data, error = repo.create_dataset(metadata.dict(), user)
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


def retrieve_stac_dataset(dataset_name, user):
    repo = DatasetsAPIRepo()
    data, error = repo.retrieve_dataset(dataset_name)
    # print(data, error)
    if data and data["uid"] != user["uid"]:
        raise Exception("Dataset already exists.")
    if error and error == "Dataset doesn't exist":
        # create dataset
        data, error = repo.create_stac_dataset(dataset_name, user)
        # print(data, error)
        if error:
            raise Exception(error)
        data["id"] = data["dataset_id"]
    return data["id"]


@with_auth
def ingest_stac(stac_catalog, logger=None, user=None):
    repo, files_repo = DatasetsAPIRepo(), FilesAPIRepo()
    # load catalog
    logger("Loading STAC catalog...")
    df = STACDataFrame.from_stac_file(stac_catalog)
    catalog = df[df["type"] == "Catalog"]
    assert len(catalog) == 1, "STAC catalog must have exactly one root catalog"
    dataset_name = catalog.id.iloc[0]
    # retrieve dataset (create if doesn't exist)
    dataset_id = retrieve_stac_dataset(dataset_name, user)
    # create new version
    version = create_new_version(repo, dataset_id, user)
    logger("New version created, version: " + str(version))
    df2 = df.dropna(subset=["assets"])
    for row in tqdm(df2.iterrows(), total=len(df2)):
        try:
            for k, v in row[1]["assets"].items():
                data, error = files_repo.ingest_file(
                    v["href"],
                    dataset_id,
                    user,
                    calculate_checksum(v["href"]),  # is always absolute?
                    "datasets",
                    version,
                )
                if error:
                    raise Exception(error)
                file_url = f"{repo.url}datasets/{data['dataset_id']}/download/{data['filename']}"
                df.loc[row[0], "assets"][k]["href"] = file_url
        except Exception as e:
            logger(f"Error uploading asset {row[0]}: {e}")
            break
    # ingest the STAC catalog into geodb
    logger("Ingesting STAC catalog...")
    data, error = repo.ingest_stac(json.loads(df.to_json()), dataset_id, user)
    if error:
        # TODO: delete all assets that were uploaded
        raise Exception(error)
    logger("Done")
    return
