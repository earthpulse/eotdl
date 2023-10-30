from datetime import datetime

from ...repos import FilesDBRepo, OSRepo, S3Repo, DatasetsDBRepo
from ...models import UploadingFile, File
from .retrieve_dataset import retrieve_owned_dataset
from ...errors import UploadIdDoesNotExist, ChunkUploadChecksumMismatch


def generate_upload_id(user, checksum, filename, dataset_id):
    files_repo, os_repo, s3_repo = FilesDBRepo(), OSRepo(), S3Repo()
    # check if dataset already exists
    dataset = retrieve_owned_dataset(dataset_id, user.uid)
    # check if file exists
    files = files_repo.retrieve_file(dataset.files, filename)
    if files and "files" in files:
        # retrieve most recent version
        file = sorted(files["files"], key=lambda x: x["version"])[-1]
        if file["checksum"] == checksum:  # the file has not been modified
            raise Exception("File already exists")
    # check if upload already exists
    data = files_repo.find_upload(user.uid, filename, dataset_id)
    if data:
        uploading = UploadingFile(**data)
        # abort if trying to resume existing upload with a different file
        if uploading.checksum != checksum:
            files_repo.delete_upload(uploading.id)
        else:  # resume upload
            return uploading.upload_id, uploading.parts
    # TODO: check if user can ingest file
    # create new upload
    id = files_repo.generate_id()
    storage = os_repo.get_object(dataset.id, filename)
    upload_id = s3_repo.multipart_upload_id(
        storage
    )  # does this work if the file already exists ?
    uploading = UploadingFile(
        uid=user.uid,
        id=id,
        upload_id=upload_id,
        dataset=dataset_id,
        filename=filename,
        checksum=checksum,
    )
    files_repo.persist_upload(uploading.id, uploading.model_dump())
    return upload_id, []


def ingest_dataset_chunk(file, part_number, upload_id, checksum, user):
    files_repo, os_repo, s3_repo = FilesDBRepo(), OSRepo(), S3Repo()
    data = files_repo.retrieve_upload(upload_id)
    if not data or data["uid"] != user.uid:
        raise UploadIdDoesNotExist()
    uploading = UploadingFile(**data)
    storage = os_repo.get_object(uploading.dataset, uploading.filename)
    _checksum = s3_repo.store_chunk(file, storage, part_number, upload_id)
    if checksum != _checksum:
        raise ChunkUploadChecksumMismatch()
    uploading.parts.append(part_number)
    uploading.updatedAt = datetime.now()
    files_repo.update("uploading", uploading.id, uploading.model_dump())
    return "Chunk uploaded"


def complete_multipart_upload(user, upload_id):
    datasets_repo = files_repo, os_repo, s3_repo = (
        DatasetsDBRepo(),
        FilesDBRepo(),
        OSRepo(),
        S3Repo(),
    )
    # check if upload already exists
    data = files_repo.find_upload_by_id(user.uid, upload_id)
    if not data:
        raise UploadIdDoesNotExist()
    uploading = UploadingFile(**data)
    # check if dataset exists
    dataset = retrieve_owned_dataset(uploading.dataset, user.uid)
    # TODO: check if user can ingest
    storage = os_repo.get_object(dataset.id, uploading.filename)
    s3_repo.complete_multipart_upload(storage, upload_id)
    object_info = os_repo.object_info(dataset.id, uploading.filename)
    # # calculate checksum (too expensive for big files)
    # checksum = await self.os_repo.calculate_checksum(
    #     dataset.id, uploading.name
    # )
    # if checksum != uploading.checksum:
    #     self.os_repo.delete_file(dataset.id, uploading.name)
    #     if len(dataset.files) == 0:
    #         self.db_repo.delete("datasets", dataset.id)
    #     raise ChecksumMismatch()

    # TODO: versioning
    # if uploading.filename in [f.name for f in dataset.files]:
    #     dataset.files = [f for f in dataset.files if f.name != uploading.name]
    # dataset.files.append(
    #     File(
    #         name=uploading.filename,
    #         size=object_info.size,
    #         checksum=uploading.checksum,
    #         version=1,
    #     )
    # )

    dataset.updatedAt = datetime.now()
    # TODO: update version size
    # dataset.size = dataset.size + object_info.size
    datasets_repo.update_dataset(dataset.id, dataset.model_dump())
    # TODO: report usage
    # usage = Usage.FileIngested(
    #     uid=inputs.uid,
    #     payload={
    #         "dataset": dataset.id,
    #         "file": uploading.name,
    #         "size": object_info.size,
    #     },
    # )
    # self.db_repo.persist("usage", usage.dict())
    files_repo.delete_upload(uploading.id)
    return dataset
