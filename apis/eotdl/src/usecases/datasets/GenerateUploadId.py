from pydantic import BaseModel

from ...models import User, Limits, UploadingFile, Dataset
from ...errors import DatasetDoesNotExistError, TierLimitError
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
        dataset_id: str

    class Outputs(BaseModel):
        upload_id: str
        parts: List[int] = []

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if upload already exists
        data = self.db_repo.find_one(
            "uploading",
            {"uid": inputs.uid, "name": inputs.name, "dataset": inputs.dataset_id},
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
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        if dataset.uid != inputs.uid:
            raise DatasetDoesNotExistError()
        # check if user can ingest file
        if (
            len(dataset.files) + 1 > limits.datasets.files
            and inputs.name not in dataset.files
        ):
            raise TierLimitError(
                "You cannot have more than {} files".format(limits.datasets.files)
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
            dataset=inputs.dataset_id,
            name=inputs.name,
            checksum=inputs.checksum,
        )
        self.db_repo.persist("uploading", uploading.dict(), uploading.id)
        return self.Outputs(upload_id=upload_id)
