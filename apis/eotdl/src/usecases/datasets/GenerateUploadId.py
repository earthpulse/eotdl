from pydantic import BaseModel
import typing

from ...models import Dataset, User, Limits, UploadingFile
from ...errors import DatasetAlreadyExistsError, TierLimitError, UserUnauthorizedError
from typing import Optional, List


class GenerateUploadId:
    def __init__(self, db_repo, os_repo, s3_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        uid: str
        checksum: str
        name: str
        dataset: str

    class Outputs(BaseModel):
        upload_id: str
        parts: List[int] = []

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if upload already exists
        data = self.db_repo.find_one(
            "uploading",
            {"uid": inputs.uid, "name": inputs.name, "dataset": inputs.dataset},
        )
        if data:
            uploading = UploadingFile(**data)
            if uploading.checksum != inputs.checksum:
                self.db_repo.delete("uploading", uploading.id)
            else:
                return self.Outputs(
                    upload_id=uploading.upload_id,
                    parts=uploading.parts,
                )
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
        # check if dataset already exists for other user
        data = self.db_repo.find_one_by_name("datasets", inputs.dataset)
        if data and data["uid"] != inputs.uid:
            raise DatasetAlreadyExistsError()
        # create new upload
        id = self.db_repo.generate_id()
        storage = self.os_repo.get_object(id, inputs.name)
        upload_id = self.s3_repo.multipart_upload_id(
            storage
        )  # does this work if the file already exists ?
        uploading = UploadingFile(
            uid=inputs.uid,
            id=id,
            upload_id=upload_id,
            dataset=inputs.dataset,
            name=inputs.name,
            checksum=inputs.checksum,
        )
        self.db_repo.persist("uploading", uploading.dict(), uploading.id)
        return self.Outputs(upload_id=upload_id)
