from pydantic import BaseModel
import typing

from ...models import Dataset, User, Limits
from ...errors import DatasetAlreadyExistsError, TierLimitError, UserUnauthorizedError
from typing import Optional


class GenerateUploadId:
    def __init__(self, db_repo, os_repo, s3_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        uid: str
        name: str = None
        id: str = None

    class Outputs(BaseModel):
        dataset_id: Optional[str] = None
        upload_id: Optional[str] = None

    def __call__(self, inputs: Inputs) -> Outputs:
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
        # create new dataset
        if inputs.id is None:
            # generate new dataset id and validate name, description
            id = self.db_repo.generate_id()
            Dataset(
                uid=inputs.uid,
                id=id,
                name=inputs.name,
                checksum="",  # mandatory but not used
            )
            # generate multipart upload id
            storage = self.os_repo.get_object(id)
            upload_id = self.s3_repo.multipart_upload_id(storage)
            return self.Outputs(dataset_id=id, upload_id=upload_id)
        # update existing dataset
        # check if user is owner
        data = self.db_repo.retrieve("datasets", inputs.id, "id")
        dataset = Dataset(**data)
        if dataset.uid != inputs.uid:
            raise UserUnauthorizedError()
        # generate multipart upload id
        storage = self.os_repo.get_object(inputs.id)
        upload_id = self.s3_repo.multipart_upload_id(
            storage
        )  # does this work if the file already exists ?
        return self.Outputs(upload_id=upload_id)
