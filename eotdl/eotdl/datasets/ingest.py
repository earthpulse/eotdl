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


def retrieve_files(folder):
    # get all files in directory recursively
    items = [Path(item) for item in glob(str(folder) + "/**/*", recursive=True)]
    if not any(item.name == "metadata.yml" for item in items):
        raise Exception("metadata.yml not found in directory")
    # remove directories
    items = [item for item in items if not item.is_dir()]
    if len(items) == 0:
        raise Exception("No files found in directory")
    return items


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


def prepare_item(item, folder):
    return {
        "filename": item.name,
        "path": str(item.relative_to(folder)),
        "absolute_path": item.absolute(),
        "size": os.path.getsize(item.absolute()),
        "checksum": calculate_checksum(item.absolute()),
    }


def generate_files_lists(items, folder, dataset_id, logger, max_size=1024 * 1024 * 16):
    files_repo = FilesAPIRepo()
    current_files, error = files_repo.retrieve_dataset_files(dataset_id)
    # print(len(current_files), len(items) - len(current_files))
    # print(current_files, error)
    if error:
        current_files = []
    # generate list of files to upload
    logger("generating list of files to upload...")
    upload_files, existing_files, large_files = [], [], []
    current_names = [f["filename"] for f in current_files]
    current_checksums = [f["checksum"] for f in current_files]
    for item in tqdm(items):
        data = prepare_item(item, folder)
        if data["path"] in current_names and data["checksum"] in current_checksums:
            existing_files.append(data)
        else:
            if data["size"] > max_size:
                large_files.append(data)
            else:
                upload_files.append(data)
    if len(upload_files) == 0:
        raise Exception("No files to upload")
    return upload_files, existing_files, large_files


def create_new_version(dataset_id, user):
    repo = DatasetsAPIRepo()
    data, error = repo.create_version(dataset_id, user["id_token"])
    if error:
        raise Exception(error)
    return data["version"]


def generate_batches(files, max_batch_size=1024 * 1024 * 10, max_batch_files=10):
    batches = []
    for item in tqdm(files):
        if not batches:
            batches.append([item])
            continue
        if max_batch_size:
            size_check = sum([i["size"] for i in batches[-1]]) < max_batch_size
        else:
            size_check = True
        if size_check and len(batches[-1]) < max_batch_files:
            batches[-1].append(item)
        else:
            batches.append([item])
    return batches


def generate_batches2(files, max_batch_files=10):
    batches = []
    for item in tqdm(files):
        if len(batches) == 0:
            batches.append([item])
        else:
            if len(batches[-1]) < max_batch_files:
                batches[-1].append(item)
            else:
                batches.append([item])
    return batches


def compress_batch(batch):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        for f in batch:
            zf.write(f["absolute_path"], arcname=f["path"])
    memory_file.seek(0)
    return memory_file


@with_auth
def ingest_folder(folder, verbose=False, logger=print, user=None):
    repo, files_repo = DatasetsAPIRepo(), FilesAPIRepo()
    logger(f"Uploading directory {folder}...")
    items = retrieve_files(folder)
    # load metadata
    metadata = yaml.safe_load(open(folder.joinpath("metadata.yml"), "r").read()) or {}
    metadata = Metadata(**metadata)
    # retrieve dataset
    dataset_id = retrieve_dataset(metadata, user)
    # retrieve files
    upload_files, existing_files, large_files = generate_files_lists(
        items, folder, dataset_id, logger
    )
    print(len(upload_files) + len(large_files), "new files will be ingested")
    print(len(existing_files), "files already exist in dataset")
    print(len(large_files), "large files will be ingested separately")
    # create new version
    version = create_new_version(dataset_id, user)
    logger("New version created, version: " + str(version))
    if len(large_files) > 0:
        logger("ingesting large files...")
        for file in large_files:
            logger("ingesting file: " + file["path"])
            upload_id, parts = files_repo.prepare_large_upload(
                file["path"], dataset_id, file["checksum"], user["id_token"]
            )
            # print(upload_id, parts)
            files_repo.ingest_large_file(
                file["absolute_path"], file["size"], upload_id, user["id_token"], parts
            )
            files_repo.complete_upload(user["id_token"], upload_id)
    # ingest files in batches
    if len(upload_files) > 0:
        logger("generating batches...")
        batches = generate_batches(upload_files)
        logger(
            f"Uploading {len(upload_files)} small files in {len(batches)} batches..."
        )
        repo = FilesAPIRepo()
        for batch in tqdm(
            batches, desc="Uploading batches", unit="batches", disable=verbose
        ):
            # compress batch
            memory_file = compress_batch(batch)
            # ingest batch
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
        batches = generate_batches(existing_files, max_batch_size=None)
        for batch in tqdm(
            batches,
            desc="Ingesting existing files",
            unit="batches",
            disable=verbose,
        ):
            data, error = files_repo.add_files_batch_to_version(
                batch,
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
