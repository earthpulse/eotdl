from pathlib import Path
from glob import glob
import yaml

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo


def ingest_dataset(path, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, logger)


@with_auth
def ingest_folder(folder, logger=print, user=None):
    repo = DatasetsAPIRepo()
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
    # remove metadata.yml from files
    items = [item for item in items if item.name != "metadata.yml"]
    # if zip or tar file, send error
    if any(item.suffix.endswith((".zip", ".tar", ".tar.gz", ".gz")) for item in items):
        raise Exception(
            f"At least one zip, tar or gz file found in {folder}, please unzip and try again"
        )
    # create dataset
    data, error = repo.create_dataset(metadata.dict(), user["id_token"])
    print(data, error)
    # # dataset may already exist, but if user is owner continue ingesting files
    # current_files = []
    # if error:
    #     data, error2 = self.repo.retrieve_dataset(metadata.name)
    #     print(data, error2)
    #     if error2:
    #         raise Exception(error)
    #     if data["uid"] != user["sub"]:
    #         raise Exception("Dataset already exists.")
    #     data["dataset_id"] = data["id"]
    #     # current_files = [item["name"] for item in data["files"]]
    #     # print("current_files", current_files)
    # dataset_id = data["dataset_id"]
    # # create new version
    # data, error = self.repo.create_version(dataset_id, user["id_token"])
    # print(data, error)
    # version = data["version"]
    # # upload files
    # for item in tqdm(items):
    #     data = self.ingest_file(
    #         str(item),
    #         dataset_id,
    #         version,
    #         str(item.relative_to(folder).parent),
    #         logger=logger,
    #         verbose=False,
    #     )
    # return self.Outputs(dataset=data)


# @with_auth
# def ingest_file(
#     file,
#     dataset_id,
#     version,
#     parent,
#     logger=None,
#     verbose=True,
#     root=None,
#     user=None,
# ):
#     api_repo = APIRepo()
#     ingest = IngestFile(api_repo, logger, verbose)
#     inputs = ingest.Inputs(file=file, version=version, parent=parent, dataset_id=dataset_id, user=user, root=root)
#     outputs = ingest(inputs)
#     return outputs.data


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestSTAC(api_repo, ingest_file, logger)
#     inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset
