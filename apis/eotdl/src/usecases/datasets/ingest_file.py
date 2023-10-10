# al ingestar file, comprobar que es la última versión y que el file no está ya en esa versión
from .retrieve_dataset import retrieve_owned_dataset
from ...errors import DatasetVersionDoesNotExistError


def ingest_file(file, dataset_id, version, parent, checksum, user):
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    versions = [v.version_id for v in dataset.versions]
    if not version in versions:
        raise DatasetVersionDoesNotExistError()
    # save file in storage
    filename = file.filename
    print(parent, filename)
    if parent != ".":
        filename = parent + "/" + filename
    # file_version = self.persist_file(inputs.file, dataset.id, filename)
    # filename0 = filename
    # filename += "_" + str(file_version)
    # # calculate checksum
    # checksum = await self.os_repo.calculate_checksum(dataset.id, filename)
    # if inputs.checksum and checksum != inputs.checksum:
    #     self.os_repo.delete_file(dataset.id, inputs.file.name)
    #     if len(dataset.files) == 0:
    #         self.db_repo.delete("datasets", dataset.id)
    #     raise ChecksumMismatch()
    # file_size = self.os_repo.object_info(dataset.id, filename).size
    # if dataset.quality == 0:
    #     # TODO: handle existing files
    #     print(filename0, file_version)
    #     # print([(f.name, f.version) for f in dataset.files])
    #     # files = self.db_repo.retrieve("files", dataset.files)['files']
    #     # print(files)
    #     # file = [f for f in files if f['name'] == filename0 and f['version'] == file_version - 1]
    #     files = self.db_repo.retrieve2(
    #         "files",
    #         {
    #             "id": dataset.files,
    #             "files": {
    #                 "$elemMatch": {"name": filename0, "version": file_version - 1}
    #             },
    #         },
    #         {"files.$": 1},
    #     )
    #     # print('files', files)
    #     if files and "files" in files and len(files["files"]) == 1:
    #         # update file
    #         # print(filename0, "already exists")
    #         file = files["files"][0]
    #         if file["checksum"] != checksum:  # the file has been modified
    #             print("new version of", filename0, filename)
    #             new_file = File(
    #                 name=filename0,
    #                 size=file_size,
    #                 checksum=checksum,
    #                 version=file_version,
    #                 versions=[inputs.version],
    #             )
    #             self.db_repo.push("files", dataset.files, {"files": new_file.dict()})
    #         else:
    #             # print("same version of", filename0, filename)
    #             self.os_repo.delete(dataset.id, filename)
    #             new_file = File(
    #                 name=filename0,
    #                 size=file_size,
    #                 checksum=checksum,
    #                 version=file["version"],
    #                 versions=file["versions"] + [inputs.version],
    #             )
    #             self.db_repo.update2(
    #                 "files",
    #                 {
    #                     "id": dataset.files,
    #                     "files": {
    #                         "$elemMatch": {
    #                             "name": filename0,
    #                             "version": file_version - 1,
    #                         }
    #                     },
    #                 },
    #                 {"$set": {"files.$": new_file.dict()}},
    #             )
    #             # for f in dataset.files:
    #             #     print(f.name, f.version, f.name != filename0 or f.version != file.version)
    #             # files = [f for f in files if (f['name'] != filename0 or f['version'] != file.version)] + [file.dict()]
    #             # print([(f.name, f.version) for f in dataset.files])
    #     else:
    #         # print("new file", filename)
    #         new_file = File(
    #             name=filename0,
    #             size=file_size,
    #             checksum=checksum,
    #             version=file_version,
    #             versions=[inputs.version],
    #         )
    #         self.db_repo.push("files", dataset.files, {"files": new_file.dict()})
    #     folders = filename0.split("/")
    #     print("folders", folders)
    #     if len(folders) > 1:
    #         folder_name = "/".join(folders[:-1])
    #         print("folder_name", folder_name)
    #         result = self.db_repo.update2(
    #             "files",
    #             {"id": dataset.files, "folders.name": folder_name},
    #             {"$addToSet": {"folders.$.versions": inputs.version}},
    #         )
    #         if result.matched_count == 0:
    #             new_folder = Folder(name=folder_name, versions=[inputs.version])
    #             self.db_repo.push(
    #                 "files", dataset.files, {"folders": new_folder.dict()}
    #             )
    # version = [v for v in dataset.versions if v.version_id == inputs.version][0]
    # version.size += file_size  # for Q0+ will add, so put to 0 before if necessary
    # dataset.updatedAt = datetime.now()
    # self.db_repo.update("datasets", dataset.id, dataset.dict())
    # # report usage
    # usage = Usage.FileIngested(
    #     uid=inputs.uid,
    #     payload={
    #         "dataset": dataset.id,
    #         "file": filename,
    #         "size": file_size,
    #     },
    # )
    # self.db_repo.persist("usage", usage.dict())
    # return self.Outputs(
    #     dataset_id=dataset.id,
    #     dataset_name=dataset.name,
    #     file_name=filename,
    # )
    return 1, 2, 3


def ingest_file_url():
    # TODO
    return
    # def get_file_name(self, file):
    #     return file.split("/")[-1]

    # def persist_file(self, file, dataset_id, filename):
    #     return self.os_repo.persist_file_url(file, dataset_id, filename)


def ingest_stac():
    # TODO
    return
    # # check if dataset exists
    # data = self.db_repo.retrieve("datasets", inputs.dataset)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = STACDataset(**data)
    # # check user owns dataset
    # if dataset.uid != inputs.user.uid:
    #     raise DatasetDoesNotExistError()
    # # TODO: check all assets exist in os
    # # ingest to geodb
    # credentials = self.retrieve_user_credentials(inputs.user)
    # self.geodb_repo = self.geodb_repo(credentials)
    # catalog = self.geodb_repo.insert(inputs.dataset, inputs.stac)
    # # the catalog should contain all the info we want to show in the UI
    # dataset.catalog = catalog
    # keys = list(catalog.keys())
    # if "ml-dataset:name" in keys:
    #     dataset.quality = 2
    #     # TODO: compute and report automatic qa metrics
    # # TODO: validate Q2 dataset, not only check name
    # # TODO: validate Q1 dataset with required fields/extensions (author, license)
    # self.db_repo.update("datasets", inputs.dataset, dataset.model_dump())
    # return self.Outputs(dataset=dataset)
