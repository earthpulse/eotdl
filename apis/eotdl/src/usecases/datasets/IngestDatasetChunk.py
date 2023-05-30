from pydantic import BaseModel
import typing


class IngestDatasetChunk:
    def __init__(self, os_repo, s3_repo):
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        chunk: typing.Any
        id: str
        upload_id: str
        part_number: int

    class Outputs(BaseModel):
        id: str
        upload_id: str

    def __call__(self, inputs: Inputs) -> Outputs:
        storage = self.os_repo.get_object(inputs.id)
        self.s3_repo.store_chunk(
            inputs.chunk, storage, inputs.part_number, inputs.upload_id
        )
        return self.Outputs(id=inputs.id, upload_id=inputs.upload_id)
