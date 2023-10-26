from ...errors import ChecksumMismatch
from ...repos import OSRepo, FilesDBRepo
from ...models import File, Folder

# TODO: al ingestar file, comprobar que es la última versión y que el file no está ya en esa versión


async def ingest_file(
    file, version, parent, dataset_or_model_id, checksum, quality, files_id
):
    db_repo, os_repo = FilesDBRepo(), OSRepo()
    # save file in storage
    filename = file.filename
    if parent != ".":
        filename = parent + "/" + filename
    file_version = os_repo.persist_file(file.file, dataset_or_model_id, filename)
    filename0 = filename
    filename += "_" + str(file_version)
    # delete if checksums don't match
    _checksum = await os_repo.calculate_checksum(dataset_or_model_id, filename)
    if checksum and checksum != _checksum:
        os_repo.delete(dataset_or_model_id, file.name)
        raise ChecksumMismatch()
    file_size = os_repo.object_info(dataset_or_model_id, filename).size
    if quality == 0:
        files = db_repo.retrieve_file(files_id, filename0, file_version - 1)
        if files and "files" in files and len(files["files"]) == 1:
            # update file
            # print(filename0, "already exists")
            file = files["files"][0]
            if file["checksum"] != checksum:  # the file has been modified
                # print("new version of", filename0, filename)
                new_file = File(
                    name=filename0,
                    size=file_size,
                    checksum=checksum,
                    version=file_version,
                    versions=[version],
                )
                db_repo.add_file(files_id, new_file.model_dump())
            else:
                # print("same version of", filename0, filename)
                os_repo.delete(dataset_or_model_id, filename)
                new_file = File(
                    name=filename0,
                    size=file_size,
                    checksum=checksum,
                    version=file["version"],
                    versions=file["versions"] + [version],
                )
                db_repo.update_file(
                    files_id, filename0, file_version - 1, new_file.model_dump()
                )
                # for f in files_id:
                #     print(f.name, f.version, f.name != filename0 or f.version != file.version)
                # files = [f for f in files if (f['name'] != filename0 or f['version'] != file.version)] + [file.dict()]
                # print([(f.name, f.version) for f in files_id])
        else:
            # print("new file", filename)
            new_file = File(
                name=filename0,
                size=file_size,
                checksum=checksum,
                version=file_version,
                versions=[version],
            )
            db_repo.add_file(files_id, new_file.model_dump())
        folders = filename0.split("/")
        # TODO: esto no está bien
        if len(folders) > 1:
            folder_name = "/".join(folders[:-1])
            result = db_repo.add_folder_version(files_id, folder_name, version)
            if result.matched_count == 0:
                new_folder = Folder(name=folder_name, versions=[version])
                db_repo.add_folder(files_id, new_folder.dict())
    return filename, file_size


async def ingest_existing_file(
    filename, version, files_id, file_version, dataset_or_model_id, checksum, quality
):
    db_repo, os_repo = FilesDBRepo(), OSRepo()
    # retrieve file
    current_file = db_repo.retrieve_file(files_id, filename, file_version)["files"][0]
    # check file is in storage
    filename0 = f"{filename}_{file_version}"
    if not os_repo.exists(dataset_or_model_id, filename0):
        raise Exception("File does not exist")
    # check checksums match
    _checksum = await os_repo.calculate_checksum(dataset_or_model_id, filename0)
    if _checksum != checksum:
        raise ChecksumMismatch()
    file_size = os_repo.object_info(dataset_or_model_id, filename0).size
    if quality == 0:
        new_file = File(
            name=filename,
            size=file_size,
            checksum=checksum,
            version=current_file["version"],
            versions=current_file["versions"] + [version],
        )
        db_repo.update_file(files_id, filename, file_version, new_file.model_dump())
    # TODO: report usage
    # usage = Usage.FileIngested(
    #     uid=uid,
    #     payload={
    #         "dataset": dataset_or_model_id,
    #         "file": filename,
    #         "size": file_size,
    #     },
    # )
    # db_repo.persist("usage", usage.dict())
    return filename, file_size


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
