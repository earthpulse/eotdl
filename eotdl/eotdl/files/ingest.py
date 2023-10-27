from pathlib import Path
import os

from ..repos import FilesAPIRepo
from ..shared import calculate_checksum


def ingest_files_batch(
    batch,
    dataset_or_model_id,
    version,
    logger=None,
    verbose=True,
    user=None,
    endpoint="datasets",
):
    id_token = user["id_token"]
    if verbose:
        logger(f"Uploading files {batch}...")
    repo = FilesAPIRepo()
    print(batch)
    # if file.startswith("http://") or file.startswith("https://"):
    #     raise NotImplementedError("URL ingestion not implemented yet")
    #     # data, error = repo.ingest_file_url(file, dataset_or_model_id, id_token)
    # ingest small file
    data, error = repo.ingest_files_batch(
        batch,
        dataset_or_model_id,
        version,
        parent,
        id_token,
        checksum,
        endpoint,
    )
    if error:
        raise Exception(error)
    return data


def ingest_existing_file(
    file,
    dataset_or_model_id,
    version,
    user,
    endpoint="datasets",
    logger=None,
    verbose=True,
):
    repo = FilesAPIRepo()
    id_token = user["id_token"]
    data, error = repo.ingest_existing_file(
        file["filename"],
        dataset_or_model_id,
        version,
        file["version"],
        id_token,
        file["checksum"],
        endpoint,
    )


def ingest_file(
    file,
    dataset_or_model_id,
    version,
    parent,
    logger=None,
    verbose=True,
    user=None,
    current_files=[],
    endpoint="datasets",
):
    id_token = user["id_token"]
    if verbose:
        logger(f"Uploading file {file}...")
    repo = FilesAPIRepo()
    if file.startswith("http://") or file.startswith("https://"):
        raise NotImplementedError("URL ingestion not implemented yet")
        # data, error = repo.ingest_file_url(file, dataset_or_model_id, id_token)
    else:
        file_path = Path(file)
        if not file_path.is_absolute():
            file_path = str(file_path.absolute())
        if verbose:
            logger("Computing checksum...")
        checksum = calculate_checksum(file_path)
        # check if file already exists in dataset
        filename = os.path.basename(file_path)
        if parent != ".":
            filename = parent + "/" + filename
        if len(current_files) > 0:
            matches = [
                f
                for f in current_files
                if f["filename"] == filename and f["checksum"] == checksum
            ]  # this could slow down ingestion in large datasets... should think of faster search algos, puede que sea mejor hacer el re-upload simplemente...
            if len(matches) == 1:
                if verbose:
                    print(f"File {file_path} already exists, skipping...")
                data, error = repo.ingest_existing_file(
                    filename,
                    dataset_or_model_id,
                    version,
                    matches[0]["version"],
                    id_token,
                    checksum,
                    endpoint,
                )
                if error:
                    raise Exception(error)
                if verbose:
                    logger("Done")
                return data
        if verbose:
            logger("Ingesting file...")
        filesize = os.path.getsize(file_path)
        # ingest small file
        if filesize < 1024 * 1024 * 160:  # 160 MB
            data, error = repo.ingest_file(
                file_path,
                dataset_or_model_id,
                version,
                parent,
                id_token,
                checksum,
                endpoint,
            )
            if error:
                raise Exception(error)
            if verbose:
                logger("Done")
            return data
        raise NotImplementedError("Large file ingestion not implemented yet")
        # # ingest large file
        # upload_id, parts = repo.prepare_large_upload(
        #     file_path, dataset_or_model_id, checksum, id_token
        # )
        # repo.ingest_large_dataset(file_path, upload_id, id_token, parts)
        # if verbose:
        #     logger("\nCompleting upload...")
        # data, error = repo.complete_upload(id_token, upload_id)
    if error:
        raise Exception(error)
    if verbose:
        logger("Done")
    return data
