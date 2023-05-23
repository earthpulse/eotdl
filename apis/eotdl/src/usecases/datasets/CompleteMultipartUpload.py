from pydantic import BaseModel
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits
from ...errors import DatasetAlreadyExistsError, TierLimitError, UserUnauthorizedError
from ...utils import calculate_checksum


class CompleteMultipartUpload:
    def __init__(self, db_repo, os_repo, s3_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        uid: str
        name: Union[str, None]
        id: str
        upload_id: str
        checksum: str

    class Outputs(BaseModel):
        dataset: Dataset

    async def __call__(self, inputs: Inputs) -> Outputs:
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
        # create new dataset
        if inputs.name is not None:
            # check if name already exists
            if self.db_repo.find_one_by_name("datasets", inputs.name):
                raise DatasetAlreadyExistsError()
            storage = self.os_repo.get_object(inputs.id)
            self.s3_repo.complete_multipart_upload(storage, inputs.upload_id)
            data_stream = self.os_repo.data_stream(inputs.id)
            checksum = await calculate_checksum(data_stream)
            print("checksum", checksum)
            if checksum != inputs.checksum:
                self.os_repo.delete(inputs.id)
                raise Exception("Checksum mismatch. Dataset deleted.")
            size = self.os_repo.get_size(inputs.id)
            dataset = Dataset(
                uid=inputs.uid,
                id=inputs.id,
                name=inputs.name,
                size=size,
                checksum=checksum,
            )
            # save dataset in db
            self.db_repo.persist("datasets", dataset.dict(), inputs.id)
            # update user dataset count
            self.db_repo.increase_counter("users", "uid", inputs.uid, "dataset_count")
            # report usage
            usage = Usage.DatasetIngested(
                uid=inputs.uid, payload={"dataset": inputs.id}
            )
            self.db_repo.persist("usage", usage.dict())
            return self.Outputs(dataset=dataset)
        # update existing dataset
        # check if user is owner
        data = self.db_repo.retrieve("datasets", inputs.id, "id")
        dataset = Dataset(**data)
        if dataset.uid != inputs.uid:
            raise UserUnauthorizedError()
        # update dataset
        storage = self.os_repo.get_object(inputs.id)
        self.s3_repo.complete_multipart_upload(
            storage, inputs.upload_id
        )  # will work if dataset exists?
        data_stream = self.os_repo.data_stream(inputs.id)
        checksum = await calculate_checksum(data_stream)
        print("checksum", checksum)
        if checksum != inputs.checksum:
            self.os_repo.delete(inputs.id)
            raise Exception("Checksum mismatch. Dataset deleted.")
        size = self.os_repo.get_size(inputs.id)
        data.update(size=size, checksum=checksum, updatedAt=datetime.now())
        updated_dataset = Dataset(**data)
        # save dataset in db
        self.db_repo.update("datasets", inputs.id, updated_dataset.dict())
        # report usage
        usage = Usage.DatasetIngested(uid=inputs.uid, payload={"dataset": inputs.id})
        self.db_repo.persist("usage", usage.dict())
        return self.Outputs(dataset=dataset)
