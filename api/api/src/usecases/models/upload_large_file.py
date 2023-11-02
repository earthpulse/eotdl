from datetime import datetime

from ...repos import FilesDBRepo, OSRepo, S3Repo, ModelsDBRepo
from ...models import UploadingFile, File
from .retrieve_model import retrieve_owned_model
from ...errors import UploadIdDoesNotExist, ChunkUploadChecksumMismatch


def generate_upload_id(user, checksum, filename, model_id):
    files_repo, os_repo, s3_repo = FilesDBRepo(), OSRepo(), S3Repo()
    # check if model already exists
    model = retrieve_owned_model(model_id, user.uid)
    # check if file exists
    files = files_repo.retrieve_file(model.files, filename)
    if files and "files" in files:
        # retrieve most recent version
        file = sorted(files["files"], key=lambda x: x["version"])[-1]
        if file["checksum"] == checksum:  # the file has not been modified
            raise Exception("File already exists")
        file_version = file["version"] + 1
    else:
        file_version = 1
    # check if upload already exists
    data = files_repo.find_upload(user.uid, filename, file_version, model_id)
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
    storage = os_repo.get_object(model.id, f"{filename}_{file_version}")
    upload_id = s3_repo.multipart_upload_id(
        storage
    )  # does this work if the file already exists ?
    uploading = UploadingFile(
        uid=user.uid,
        id=id,
        upload_id=upload_id,
        model=model_id,
        version=file_version,
        filename=filename,
        checksum=checksum,
    )
    files_repo.persist_upload(uploading.id, uploading.model_dump())
    return upload_id, []


def ingest_model_chunk(file, part_number, upload_id, checksum, user):
    files_repo, os_repo, s3_repo = FilesDBRepo(), OSRepo(), S3Repo()
    data = files_repo.retrieve_upload(upload_id)
    if not data or data["uid"] != user.uid:
        raise UploadIdDoesNotExist()
    uploading = UploadingFile(**data)
    storage = os_repo.get_object(
        uploading.model, f"{uploading.filename}_{uploading.version}"
    )
    _checksum = s3_repo.store_chunk(file, storage, part_number, upload_id)
    if checksum != _checksum:
        raise ChunkUploadChecksumMismatch()
    uploading.parts.append(part_number)
    uploading.updatedAt = datetime.now()
    files_repo.update("uploading", uploading.id, uploading.model_dump())
    return "Chunk uploaded"


def complete_multipart_upload(user, upload_id, version):
    models_repo, files_repo, os_repo, s3_repo = (
        ModelsDBRepo(),
        FilesDBRepo(),
        OSRepo(),
        S3Repo(),
    )
    # check if upload already exists
    data = files_repo.find_upload_by_id(user.uid, upload_id)
    if not data:
        raise UploadIdDoesNotExist()
    uploading = UploadingFile(**data)
    # check if model exists
    model = retrieve_owned_model(uploading.model, user.uid)
    # complete upload
    storage = os_repo.get_object(model.id, f"{uploading.filename}_{uploading.version}")
    s3_repo.complete_multipart_upload(storage, upload_id)
    object_info = os_repo.object_info(
        model.id, f"{uploading.filename}_{uploading.version}"
    )
    # we don't compute checksum since for very large files will take a long time...
    # We are not checking if the fil already exists here...
    new_file = File(
        name=uploading.filename,
        size=object_info.size,
        checksum=uploading.checksum,  # should compute again, but can be expensive...
        version=uploading.version,
        versions=[version],
    )
    files_repo.add_file(model.files, new_file.model_dump())
    # TODO: check if user can ingest
    version = [v for v in model.versions if v.version_id == version][0]
    version.size += object_info.size
    model.updatedAt = datetime.now()
    models_repo.update_model(model.id, model.model_dump())
    # TODO: report usage
    files_repo.delete_upload(uploading.id)
    return model
