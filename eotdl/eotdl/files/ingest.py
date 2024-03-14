from pathlib import Path
import os
from tqdm import tqdm
import zipfile
import io
from glob import glob
import os

from ..repos import FilesAPIRepo
from ..shared import calculate_checksum


def retrieve_files(folder):
    # get all files in directory recursively
    items = [Path(item) for item in glob(str(folder) + "/**/*", recursive=True)]
    if not any(item.name == "metadata.yml" for item in items) and not any(
        item.name == "README.md" for item in items
    ):
        raise Exception("README.md not found in directory")
    # remove metadata files
    items = [item for item in items if item.name != "metadata.yml"]
    items = [item for item in items if item.name != "README.md"]
    # remove directories
    items = [item for item in items if not item.is_dir()]
    if len(items) == 0:
        raise Exception("No files found in directory")
    return items


def prepare_item(item, folder):
    return {
        "filename": item.name,
        "path": str(item.relative_to(folder)),
        "absolute_path": item.absolute(),
        "size": os.path.getsize(item.absolute()),
        "checksum": calculate_checksum(item.absolute()),
    }


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


def compress_batch(batch):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
        for f in batch:
            zf.write(f["absolute_path"], arcname=f["path"])
    memory_file.seek(0)
    return memory_file


def generate_files_lists(
    items, folder, dataset_or_model_id, endpoint, logger, max_size=1024 * 1024 * 16
):
    files_repo = FilesAPIRepo()
    current_files, error = files_repo.retrieve_files(dataset_or_model_id, endpoint)
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
    # TODO: should ingest new version if files removed
    if len(upload_files) == 0 and len(large_files) == 0:
        raise Exception("No new files to upload")
    return upload_files, existing_files, large_files


def create_new_version(repo, dataset_or_model_id, user):
    data, error = repo.create_version(dataset_or_model_id, user)
    if error:
        raise Exception(error)
    return data["version"]


def ingest_files(repo, dataset_or_model_id, folder, verbose, logger, user, endpoint):
    files_repo = FilesAPIRepo()
    logger(f"Uploading directory {folder}...")
    items = retrieve_files(folder)
    # retrieve files
    upload_files, existing_files, large_files = generate_files_lists(
        items, folder, dataset_or_model_id, endpoint, logger
    )
    logger(f"{len(upload_files) + len(large_files)} new files will be ingested")
    logger(f"{len(existing_files)} files already exist in dataset")
    logger(f"{len(large_files)} large files will be ingested separately")
    # create new version
    version = create_new_version(repo, dataset_or_model_id, user)
    logger("New version created, version: " + str(version))
    # ingest new large files
    if len(large_files) > 0:
        logger("ingesting large files...")
        for file in large_files:
            logger("ingesting file: " + file["path"])
            upload_id, parts = files_repo.prepare_large_upload(
                file["path"],
                dataset_or_model_id,
                file["checksum"],
                user,
                endpoint,
            )
            # print(upload_id, parts)
            files_repo.ingest_large_file(
                file["absolute_path"],
                file["size"],
                upload_id,
                user,
                parts,
                endpoint,
            )
            data, error = files_repo.complete_upload(user, upload_id, version, endpoint)
    # ingest new small files in batches
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
                dataset_or_model_id,
                user,
                endpoint,
                version,
            )
    # ingest existing files
    if len(existing_files) > 0:
        batches = generate_batches(existing_files, max_batch_size=None)
        for batch in tqdm(
            batches,
            desc="Ingesting existing files",
            unit="batches",
            disable=verbose,
        ):
            data, error = files_repo.add_files_batch_to_version(
                batch,
                dataset_or_model_id,
                version,
                user,
                endpoint,
            )
            if error:
                raise Exception(error)
    return data
