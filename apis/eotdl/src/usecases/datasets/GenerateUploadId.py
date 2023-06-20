from pydantic import BaseModel

from ...models import User, Limits, UploadingFile, Dataset
from ...errors import DatasetAlreadyExistsError, TierLimitError
from typing import List


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
            # abort if trying to resume existing upload with a different file
            if uploading.checksum != inputs.checksum:
                self.db_repo.delete("uploading", uploading.id)
            else:  # resume upload
                return self.Outputs(
                    upload_id=uploading.upload_id,
                    parts=uploading.parts,
                )
        # check if dataset already exists
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        data = self.db_repo.find_one_by_name("datasets", inputs.dataset)
        if data:
            dataset = Dataset(**data)
            # error if dataset already exists for another user
            if dataset.uid != inputs.uid:
                raise DatasetAlreadyExistsError()
            # check if user can ingest file
            if (
                len(dataset.files) + 1 >= limits.datasets.files
                and inputs.name not in dataset.files
            ):
                raise TierLimitError(
                    "You cannot have more than {} files".format(limits.datasets.files)
                )
        else:  # first upload to new dataset
            # check if user can ingest dataset
            usage = self.db_repo.find_in_time_range(
                "usage", inputs.uid, "dataset_ingested", "type"
            )
            if len(usage) + 1 >= limits.datasets.upload:
                raise TierLimitError(
                    "You cannot ingest more than {} datasets per day".format(
                        limits.datasets.upload
                    )
                )
            if user.dataset_count + 1 >= limits.datasets.count:
                raise TierLimitError(
                    "You cannot have more than {} datasets".format(
                        limits.datasets.count
                    )
                )
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
