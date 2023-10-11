from datetime import datetime

from .retrieve_dataset import retrieve_owned_dataset
from ...errors import DatasetVersionDoesNotExistError, ChecksumMismatch
from ...repos import OSRepo, FilesDBRepo, DatasetsDBRepo
from ...models import File, Folder

# TODO: al ingestar file, comprobar que es la última versión y que el file no está ya en esa versión


async def ingest_file(file, dataset_id, version, parent, checksum, user):
    db_repo, os_repo = FilesDBRepo(), OSRepo()
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    # save file in storage
    filename = file.filename
    if parent != ".":
        filename = parent + "/" + filename
    file_version = os_repo.persist_file(file.file, dataset_id, filename)
    filename0 = filename
    filename += "_" + str(file_version)
    # delete if checksums don't match
    _checksum = await os_repo.calculate_checksum(dataset.id, filename)
    if checksum and checksum != _checksum:
        os_repo.delete_file(dataset.id, file.name)
        raise ChecksumMismatch()
    file_size = os_repo.object_info(dataset.id, filename).size
    if dataset.quality == 0:
        # TODO: handle existing files
        # print([(f.name, f.version) for f in dataset.files])
        # files = db_repo.retrieve("files", dataset.files)['files']
        # print(files)
        # file = [f for f in files if f['name'] == filename0 and f['version'] == file_version - 1]
        files = db_repo.retrieve_file(dataset.files, filename0, file_version - 1)
        if files and "files" in files and len(files["files"]) == 1:
            # update file
            # print(filename0, "already exists")
            file = files["files"][0]
            if file["checksum"] != checksum:  # the file has been modified
                print("new version of", filename0, filename)
                new_file = File(
                    name=filename0,
                    size=file_size,
                    checksum=checksum,
                    version=file_version,
                    versions=[version],
                )
                db_repo.add_file(dataset.files, new_file.model_dump())
            else:
                # print("same version of", filename0, filename)
                os_repo.delete(dataset.id, filename)
                new_file = File(
                    name=filename0,
                    size=file_size,
                    checksum=checksum,
                    version=file["version"],
                    versions=file["versions"] + [version],
                )
                db_repo.update_file(
                    dataset.files, filename0, file_version - 1, new_file.model_dump()
                )
                # for f in dataset.files:
                #     print(f.name, f.version, f.name != filename0 or f.version != file.version)
                # files = [f for f in files if (f['name'] != filename0 or f['version'] != file.version)] + [file.dict()]
                # print([(f.name, f.version) for f in dataset.files])
        else:
            # print("new file", filename)
            new_file = File(
                name=filename0,
                size=file_size,
                checksum=checksum,
                version=file_version,
                versions=[version],
            )
            db_repo.add_file(dataset.files, new_file.model_dump())
        folders = filename0.split("/")
        # TODO: esto no está bien
        if len(folders) > 1:
            folder_name = "/".join(folders[:-1])
            result = db_repo.add_folder_version(dataset.files, folder_name, version)
            if result.matched_count == 0:
                new_folder = Folder(name=folder_name, versions=[version])
                db_repo.add_folder(dataset.files, new_folder.dict())
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    # TODO: report usage
    # usage = Usage.FileIngested(
    #     uid=uid,
    #     payload={
    #         "dataset": dataset.id,
    #         "file": filename,
    #         "size": file_size,
    #     },
    # )
    # db_repo.persist("usage", usage.dict())
    return dataset.id, dataset.name, filename


async def ingest_existing_file(
    filename, dataset_id, file_version, version, checksum, user
):
    db_repo, os_repo = FilesDBRepo(), OSRepo()
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    # retrieve file
    current_file = db_repo.retrieve_file(dataset.files, filename, file_version)[
        "files"
    ][0]
    # check file is in storage
    filename0 = f"{filename}_{file_version}"
    if not os_repo.exists(dataset.id, filename0):
        raise Exception("File does not exist")
    # check checksums match
    _checksum = await os_repo.calculate_checksum(dataset.id, filename0)
    if _checksum != checksum:
        raise ChecksumMismatch()
    file_size = os_repo.object_info(dataset.id, filename0).size
    if dataset.quality == 0:
        new_file = File(
            name=filename,
            size=file_size,
            checksum=checksum,
            version=current_file["version"],
            versions=current_file["versions"] + [version],
        )
        db_repo.update_file(
            dataset.files, filename, file_version, new_file.model_dump()
        )
    version = [v for v in dataset.versions if v.version_id == version][0]
    version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
    dataset.updatedAt = datetime.now()
    dataset_db_repo = DatasetsDBRepo()
    dataset_db_repo.update_dataset(dataset.id, dataset.dict())
    # TODO: report usage
    # usage = Usage.FileIngested(
    #     uid=uid,
    #     payload={
    #         "dataset": dataset.id,
    #         "file": filename,
    #         "size": file_size,
    #     },
    # )
    # db_repo.persist("usage", usage.dict())
    return dataset.id, dataset.name, filename


def ingest_file_url():
    # TODO
    return
    # def get_file_name(self, file):
    #     return file.split("/")[-1]

    # def persist_file(self, file, dataset_id, filename):
    #     return os_repo.persist_file_url(file, dataset_id, filename)


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
