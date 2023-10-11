from pathlib import Path
from glob import glob
import yaml
from tqdm import tqdm
import os

from ..auth import with_auth
from .metadata import Metadata
from ..repos import DatasetsAPIRepo, FilesAPIRepo
from .utils import calculate_checksum


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
    # remove metadata.yml from files
    items = [item for item in items if item.name != "metadata.yml"]
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
        )
    return data


def ingest_file(
    file,
    dataset_id,
    version,
    parent,
    logger=None,
    verbose=True,
    root=None,
    user=None,
    current_files=[],
):
    id_token = user["id_token"]
    if verbose:
        logger(f"Uploading file {file}...")
    repo = FilesAPIRepo()
    if file.startswith("http://") or file.startswith("https://"):
        raise NotImplementedError("URL ingestion not implemented yet")
        # data, error = repo.ingest_file_url(file, dataset_id, id_token)
    else:
        file_path = Path(file)
        if not file_path.is_absolute():
            # file_path = glob(
            #     str(root) + "/**/" + os.path.basename(file_path),
            #     recursive=True,
            # )
            # if len(file_path) == 0:
            #     raise Exception(f"File {file} not found")
            # elif len(file_path) > 1:
            #     raise Exception(f"Multiple files found for {file}")
            # file_path = file_path[0]
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
                    print(f"File {file_path} already exists in dataset, skipping...")
                data, error = repo.ingest_existing_file(
                    filename,
                    dataset_id,
                    version,
                    matches[0]["version"],
                    id_token,
                    checksum,
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
        if filesize < 1024 * 1024 * 16:  # 16 MB
            data, error = repo.ingest_file(
                file_path,
                dataset_id,
                version,
                parent,
                id_token,
                checksum,
            )
            if error:
                raise Exception(error)
            if verbose:
                logger("Done")
            return data
        raise NotImplementedError("Large file ingestion not implemented yet")
        # # ingest large file
        # upload_id, parts = repo.prepare_large_upload(
        #     file_path, dataset_id, checksum, id_token
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


# @with_auth
# def ingest_stac(stac_catalog, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestSTAC(api_repo, ingest_file, logger)
#     inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset
