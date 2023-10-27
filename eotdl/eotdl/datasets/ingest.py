from pathlib import Path
from glob import glob
import yaml
from tqdm import tqdm
import os
import zipfile
import io

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..files import ingest_files_batch
from ..shared import calculate_checksum


def ingest_dataset(path, verbose=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    # if "catalog.json" in [f.name for f in path.iterdir()]:
    #     return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, verbose, logger)


def prepare_item(item, folder):
    return {
        "filename": item.name,
        "path": str(item.relative_to(folder)),
        "absolute_path": item.absolute(),
        "size": os.path.getsize(item.absolute()),
        "checksum": calculate_checksum(item.absolute()),
    }


@with_auth
def ingest_folder(folder, verbose=False, logger=print, user=None):
    repo, files_repo = DatasetsAPIRepo(), FilesAPIRepo()
    logger(f"Uploading directory {folder}...")
    # get all files in directory recursively
    items = [Path(item) for item in glob(str(folder) + "/**/*", recursive=True)]
    if not any(item.name == "metadata.yml" for item in items):
        raise Exception("metadata.yml not found in directory")
    # remove directories
    items = [item for item in items if not item.is_dir()]
    if len(items) == 0:
        raise Exception("No files found in directory")
    # load metadata
    metadata = yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
    metadata = Metadata(**metadata)
    # retrieve dataset
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
    dataset_id = data["id"]
    # retrieve files
    current_files, error = files_repo.retrieve_dataset_files(dataset_id)
    # print(current_files, error)
    if error:
        current_files = []
    # generate list of files to upload
    logger("generating list of files to upload...")
    upload_files, existing_files = [], []
    current_names = [f["filename"] for f in current_files]
    current_checksums = [f["checksum"] for f in current_files]
    for item in tqdm(items):
        data = prepare_item(item, folder)
        if data["path"] in current_names and data["checksum"] in current_checksums:
            logger(f"File {data['path']} already exists in dataset")
            existing_files.append(data)
        else:
            logger(f"File {data['path']} will be uploaded")
            upload_files.append(data)
    if len(upload_files) == 0 and len(existing_files) == 0:
        raise Exception("No files to upload")
    # create new version
    data, error = repo.create_version(dataset_id, user["id_token"])
    if error:
        raise Exception(error)
    version = data["version"]
    logger("New version created, version: " + str(version))
    # TODO: separate large files for large file upload (large zips for example)
    # ingest files in batches
    if len(upload_files) > 0:
        logger("generating batches...")
        max_batch_size = 1024 * 1024 * 50  # 50 MB
        batches = []
        for item in tqdm(upload_files):
            if len(batches) == 0:
                batches.append([item])
            else:
                if sum([i["size"] for i in batches[-1]]) < max_batch_size:
                    batches[-1].append(item)
                else:
                    batches.append([item])
        logger(f"Uploading {len(batches)} batches...")
        repo = FilesAPIRepo()
        for batch in tqdm(
            batches, desc="Uploading files", unit="files", disable=verbose
        ):
            # compress batch
            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, "w") as zf:
                for f in batch:
                    zf.write(f["absolute_path"], arcname=f["path"])
            # ingest batch
            memory_file.seek(0)
            data, error = repo.ingest_files_batch(
                memory_file,
                [f["checksum"] for f in batch],
                dataset_id,
                user["id_token"],
                "datasets",
                version,
            )
    if len(existing_files) > 0:
        # ingest existing files
        for file in tqdm(
            existing_files,
            desc="Ingesting existing files",
            unit="files",
            disable=verbose,
        ):
            print(file["path"])
            data, error = files_repo.add_file_to_version(
                file["path"],
                dataset_id,
                version,
                user["id_token"],
                "datasets",
            )
            if error:
                raise Exception(error)
    return data


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestSTAC(api_repo, ingest_file, logger)
#     inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset
