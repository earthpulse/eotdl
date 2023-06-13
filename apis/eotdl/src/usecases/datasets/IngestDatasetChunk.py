from pydantic import BaseModel
import typing
from datetime import datetime

from ...models import UploadingDataset
from ...errors import ChunkUploadChecksumMismatch

class IngestDatasetChunk:
    def __init__(self, os_repo, s3_repo, db_repo):
        self.os_repo = os_repo
        self.s3_repo = s3_repo
        self.db_repo = db_repo

    class Inputs(BaseModel):
        chunk: typing.Any
        id: str
        upload_id: str
        part_number: int
        checksum: str

    class Outputs(BaseModel):
        id: str
        upload_id: str

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve("uploading", inputs.upload_id, "upload_id")
        if not data:
            raise Exception("Upload ID does not exist")
        uploading = UploadingDataset(**data)
        storage = self.os_repo.get_object(inputs.id)
        etag = self.s3_repo.store_chunk(
            inputs.chunk, storage, inputs.part_number, inputs.upload_id
        )
        if inputs.checksum != etag.strip('"'):
            raise ChunkUploadChecksumMismatch()
        uploading.parts.append(inputs.part_number)
        uploading.updatedAt = datetime.now()
        self.db_repo.update("uploading", uploading.id, uploading.dict())
        return self.Outputs(id=inputs.id, upload_id=inputs.upload_id)
