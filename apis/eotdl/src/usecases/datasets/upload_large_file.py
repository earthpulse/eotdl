def generate_upload_id():
    # TODO
    return
    # # check if upload already exists
    # data = self.db_repo.find_one(
    #     "uploading",
    #     {"uid": inputs.uid, "name": inputs.name, "dataset": inputs.dataset_id},
    # )
    # if data:
    #     uploading = UploadingFile(**data)
    #     # abort if trying to resume existing upload with a different file
    #     if uploading.checksum != inputs.checksum:
    #         self.db_repo.delete("uploading", uploading.id)
    #     else:  # resume upload
    #         return self.Outputs(
    #             upload_id=uploading.upload_id,
    #             parts=uploading.parts,
    #         )
    # # check if dataset already exists
    # data = self.db_repo.retrieve("datasets", inputs.dataset_id)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = Dataset(**data)
    # data = self.db_repo.retrieve("users", inputs.uid, "uid")
    # user = User(**data)
    # data = self.db_repo.find_one_by_name("tiers", user.tier)
    # limits = Limits(**data["limits"])
    # if dataset.uid != inputs.uid:
    #     raise DatasetDoesNotExistError()
    # # check if user can ingest file
    # if (
    #     len(dataset.files) + 1 > limits.datasets.files
    #     and inputs.name not in dataset.files
    # ):
    #     raise TierLimitError(
    #         "You cannot have more than {} files".format(limits.datasets.files)
    #     )
    # # create new upload
    # id = self.db_repo.generate_id()
    # storage = self.os_repo.get_object(dataset.id, inputs.name)
    # upload_id = self.s3_repo.multipart_upload_id(
    #     storage
    # )  # does this work if the file already exists ?
    # uploading = UploadingFile(
    #     uid=inputs.uid,
    #     id=id,
    #     upload_id=upload_id,
    #     dataset=inputs.dataset_id,
    #     name=inputs.name,
    #     checksum=inputs.checksum,
    # )
    # self.db_repo.persist("uploading", uploading.dict(), uploading.id)
    # return self.Outputs(upload_id=upload_id)


def ingest_dataset_chunk():
    # TODO
    return
    # data = self.db_repo.retrieve("uploading", inputs.upload_id, "upload_id")
    # if not data or data["uid"] != inputs.uid:
    #     raise UploadIdDoesNotExist()
    # uploading = UploadingFile(**data)
    # storage = self.os_repo.get_object(uploading.dataset, uploading.name)
    # checksum = self.s3_repo.store_chunk(
    #     inputs.chunk, storage, inputs.part_number, inputs.upload_id
    # )
    # if inputs.checksum != checksum:
    #     raise ChunkUploadChecksumMismatch()
    # uploading.parts.append(inputs.part_number)
    # uploading.updatedAt = datetime.now()
    # self.db_repo.update("uploading", uploading.id, uploading.dict())
    # return self.Outputs(message="Chunk uploaded")


def complete_multipart_upload():
    # todo
    return
    # check if upload already exists
    # data = self.db_repo.find_one(
    #     "uploading",
    #     {"uid": inputs.uid, "upload_id": inputs.upload_id},
    # )
    # if not data:
    #     raise UploadIdDoesNotExist()
    # uploading = UploadingFile(**data)
    # # check if dataset exists
    # data = self.db_repo.retrieve("datasets", uploading.dataset)
    # if not data:
    #     raise DatasetDoesNotExistError()
    # dataset = Dataset(**data)
    # data = self.db_repo.retrieve("users", inputs.uid, "uid")
    # user = User(**data)
    # data = self.db_repo.find_one_by_name("tiers", user.tier)
    # limits = Limits(**data["limits"])
    # # check if user owns dataset
    # if inputs.uid != dataset.uid:
    #     raise DatasetDoesNotExistError()
    # # check files limit
    # if (
    #     len(dataset.files) + 1 > limits.datasets.files
    #     and uploading.name not in dataset.files
    # ):
    #     raise TierLimitError(
    #         "You cannot have more than {} files".format(limits.datasets.files)
    #     )
    # storage = self.os_repo.get_object(dataset.id, uploading.name)
    # self.s3_repo.complete_multipart_upload(storage, inputs.upload_id)
    # object_info = self.os_repo.object_info(dataset.id, uploading.name)
    # # # calculate checksum (too expensive for big files)
    # # checksum = await self.os_repo.calculate_checksum(
    # #     dataset.id, uploading.name
    # # )
    # # if checksum != uploading.checksum:
    # #     self.os_repo.delete_file(dataset.id, uploading.name)
    # #     if len(dataset.files) == 0:
    # #         self.db_repo.delete("datasets", dataset.id)
    # #     raise ChecksumMismatch()
    # if uploading.name in [f.name for f in dataset.files]:
    #     dataset.files = [f for f in dataset.files if f.name != uploading.name]
    # dataset.files.append(
    #     File(
    #         name=uploading.name, size=object_info.size, checksum=uploading.checksum
    #     )
    # )
    # dataset.updatedAt = datetime.now()
    # dataset.size = dataset.size + object_info.size
    # self.db_repo.update("datasets", dataset.id, dataset.dict())
    # # report usage
    # usage = Usage.FileIngested(
    #     uid=inputs.uid,
    #     payload={
    #         "dataset": dataset.id,
    #         "file": uploading.name,
    #         "size": object_info.size,
    #     },
    # )
    # self.db_repo.persist("usage", usage.dict())
    # self.db_repo.delete("uploading", uploading.id)
    # return self.Outputs(dataset=dataset)
