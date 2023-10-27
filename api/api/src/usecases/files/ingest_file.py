from ...errors import ChecksumMismatch
from ...repos import OSRepo, FilesDBRepo
from ...models import File, Folder

# TODO: al ingestar file, comprobar que es la última versión y que el file no está ya en esa versión


async def save_file(path, dataset_or_model_id, filename, file_version, checksum):
    os_repo = OSRepo()
    filename += "_" + str(file_version)
    os_repo.persist_file(path, dataset_or_model_id, filename)
    _checksum = await os_repo.calculate_checksum(dataset_or_model_id, filename)
    if checksum and checksum != _checksum:
        os_repo.delete(dataset_or_model_id, filename)
        raise ChecksumMismatch()
    file_size = os_repo.object_info(dataset_or_model_id, filename).size
    return file_size


async def ingest_file(
    filename, path, version, dataset_or_model_id, checksum, quality, files_id
):
    db_repo = FilesDBRepo()
    # retrieve all files with same name
    files = db_repo.retrieve_file(files_id, filename)
    if files and "files" in files:
        # retrieve most recent file
        file = sorted(files["files"], key=lambda x: x["version"])[-1]
        # print(filename, "already exists")
        if file["checksum"] != checksum:  # the file has been modified
            # print("new version of", filename)
            file_size = await save_file(
                path, dataset_or_model_id, filename, file["version"] + 1, checksum
            )
            new_file = File(
                name=filename,
                size=file_size,
                checksum=checksum,
                version=file["version"] + 1,
                versions=[version],
            )
            db_repo.add_file(files_id, new_file.model_dump())
        else:  # the file is the same
            # print("same version of", filename)
            new_file = File(
                name=filename,
                size=file["size"],
                checksum=checksum,
                version=file["version"],
                versions=file["versions"] + [version],
            )
            db_repo.update_file(
                files_id, filename, file["version"], new_file.model_dump()
            )
    else:
        # print("new file", filename)
        file_size = await save_file(path, dataset_or_model_id, filename, 1, checksum)
        new_file = File(
            name=filename,
            size=file_size,
            checksum=checksum,
            version=1,
            versions=[version],
        )
        db_repo.add_file(files_id, new_file.model_dump())
    # folders = filename.split("/")
    # TODO: esto no está bien
    # if len(folders) > 1:
    #     folder_name = "/".join(folders[:-1])
    #     result = db_repo.add_folder_version(files_id, folder_name, version)
    #     if result.matched_count == 0:
    #         new_folder = Folder(name=folder_name, versions=[version])
    #         db_repo.add_folder(files_id, new_folder.dict())
    return new_file.size


def ingest_existing_file(
    filename, checksum, version, files_id, dataset_or_model_id, quality
):
    db_repo = FilesDBRepo()
    # retrieve latest version file
    # Problem: existing file could not be the latest version...
    files = db_repo.retrieve_file(files_id, filename)
    if not files or "files" not in files:
        raise Exception("File does not exist")
    file = sorted(files["files"], key=lambda x: x["version"])[-1]
    if file["checksum"] != checksum:
        raise ChecksumMismatch()
    file_version = file["version"]
    new_file = File(
        name=filename,
        size=file["size"],
        checksum=file["checksum"],
        version=file_version,
        versions=file["versions"] + [version],
    )
    db_repo.update_file(files_id, filename, file_version, new_file.model_dump())
    return file["size"]


def ingest_file_url():
    # TODO
    return
    # def get_file_name(self, file):
    #     return file.split("/")[-1]

    # def persist_file(self, file, model_id, filename):
    #     return os_repo.persist_file_url(file, model_id, filename)


def ingest_stac():
    # TODO
    return
    # # check if dataset exists
    # data = db_repo.retrieve("datasets", dataset)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = STACDataset(**data)
    # # check user owns dataset
    # if dataset.uid != user.uid:
    #     raise DatasetDoesNotExistError()
    # # TODO: check all assets exist in os
    # # ingest to geodb
    # credentials = retrieve_user_credentials(user)
    # geodb_repo = geodb_repo(credentials)
    # catalog = geodb_repo.insert(dataset, stac)
    # # the catalog should contain all the info we want to show in the UI
    # dataset.catalog = catalog
    # keys = list(catalog.keys())
    # if "ml-dataset:name" in keys:
    #     dataset.quality = 2
    #     # TODO: compute and report automatic qa metrics
    # # TODO: validate Q2 dataset, not only check name
    # # TODO: validate Q1 dataset with required fields/extensions (author, license)
    # db_repo.update("datasets", dataset, dataset.model_dump())
    # return Outputs(dataset=dataset)
