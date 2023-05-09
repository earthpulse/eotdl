from pydantic import BaseModel
import typing

from ...models import Dataset, Usage, User, Limits
from ...errors import DatasetAlreadyExistsError, TierLimitError
from typing import Optional, Union


class IngestDatasetChunk:
    def __init__(self, db_repo, os_repo, s3_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        uid: str
        name: Union[str, None]
        description: Union[str, None]
        chunk: typing.Any
        is_first: bool = False
        is_last: bool = False
        id: Optional[str] = None
        upload_id: Optional[str] = None
        part_number: Optional[int] = 0
        size: Optional[int] = 0

    class Outputs(BaseModel):
        dataset: Optional[Dataset] = None
        id: Optional[str] = None
        upload_id: Optional[str] = None

    def __call__(self, inputs: Inputs) -> Outputs:
        # TODO: name is checked in the first chunk, but during upload may be taken by another user
        # TODO: possibility to resume upload if it fails
        if inputs.is_first:
            # check if user can ingest dataset
            data = self.db_repo.retrieve("users", inputs.uid, "uid")
            user = User(**data)
            data = self.db_repo.find_one_by_name("tiers", user.tier)
            limits = Limits(**data["limits"])
            usage = self.db_repo.find_in_time_range(
                "usage", inputs.uid, "dataset_ingested", "type"
            )
            if len(usage) + 1 >= limits.datasets.upload:
                raise TierLimitError(
                    "You cannot ingest more than {} datasets per day".format(
                        limits.datasets.upload
                    )
                )
            # check if name already exists
            if self.db_repo.find_one_by_name("datasets", inputs.name):
                raise DatasetAlreadyExistsError()
            # generate new dataset id and validate name, description
            id = self.db_repo.generate_id()
            dataset = Dataset(
                uid=inputs.uid,
                id=id,
                name=inputs.name,
                description=inputs.description,
                size=inputs.size,
            )
            # generate multipart upload id
            storage = self.os_repo.get_object(id)
            upload_id = self.s3_repo.multipart_upload_id(storage)
            self.s3_repo.store_chunk(
                inputs.chunk, storage, inputs.part_number, upload_id
            )
            return self.Outputs(id=id, upload_id=upload_id)
        elif inputs.is_last:
            storage = self.os_repo.get_object(inputs.id)
            self.s3_repo.store_chunk(
                inputs.chunk, storage, inputs.part_number, inputs.upload_id
            )
            self.s3_repo.complete_multipart_upload(storage, inputs.upload_id)
            # save dataset in db
            dataset = Dataset(
                uid=inputs.uid,
                id=inputs.id,
                name=inputs.name,
                description=inputs.description,
                size=inputs.size,
            )
            self.db_repo.persist("datasets", dataset.dict(), inputs.id)
            # update user dataset count
            self.db_repo.increase_counter("users", "uid", inputs.uid, "dataset_count")
            # report usage
            usage = Usage.DatasetIngested(
                uid=inputs.uid, payload={"dataset": inputs.id}
            )
            self.db_repo.persist("usage", usage.dict())
            return self.Outputs(dataset=dataset)
        else:
            storage = self.os_repo.get_object(inputs.id)
            self.s3_repo.store_chunk(
                inputs.chunk, storage, inputs.part_number, inputs.upload_id
            )
            return self.Outputs(id=inputs.id, upload_id=inputs.upload_id)
