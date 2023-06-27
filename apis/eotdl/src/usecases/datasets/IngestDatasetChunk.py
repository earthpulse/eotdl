from pydantic import BaseModel
import typing
from datetime import datetime

from ...models import UploadingFile
from ...errors import ChunkUploadChecksumMismatch, UploadIdDoesNotExist


class IngestDatasetChunk:
    def __init__(self, os_repo, s3_repo, db_repo):
        self.os_repo = os_repo
        self.s3_repo = s3_repo
        self.db_repo = db_repo

    class Inputs(BaseModel):
        chunk: typing.Any
        uid: str
        upload_id: str
        part_number: int
        checksum: str

    class Outputs(BaseModel):
        message: str

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve("uploading", inputs.upload_id, "upload_id")
        if not data or data["uid"] != inputs.uid:
            raise UploadIdDoesNotExist()
        uploading = UploadingFile(**data)
        storage = self.os_repo.get_object(uploading.id, uploading.name)
        checksum = self.s3_repo.store_chunk(
            inputs.chunk, storage, inputs.part_number, inputs.upload_id
        )
        if inputs.checksum != checksum:
            raise ChunkUploadChecksumMismatch()
        uploading.parts.append(inputs.part_number)
        uploading.updatedAt = datetime.now()
        self.db_repo.update("uploading", uploading.id, uploading.dict())
        return self.Outputs(message="Chunk uploaded")
