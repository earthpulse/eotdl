from pydantic import BaseModel
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits, UploadingFile, File
from ...errors import (
    DatasetDoesNotExistError,
    TierLimitError,
    UploadIdDoesNotExist,
    ChecksumMismatch,
)


class CompleteMultipartUpload:
    def __init__(self, db_repo, os_repo, s3_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.s3_repo = s3_repo

    class Inputs(BaseModel):
        uid: str
        upload_id: str

    class Outputs(BaseModel):
        dataset: Dataset

    async def __call__(self, inputs: Inputs) -> Outputs:
        # check if upload already exists
        data = self.db_repo.find_one(
            "uploading",
            {"uid": inputs.uid, "upload_id": inputs.upload_id},
        )
        if not data:
            raise UploadIdDoesNotExist()
        uploading = UploadingFile(**data)
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", uploading.dataset)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        # check if user owns dataset
        if inputs.uid != dataset.uid:
            raise DatasetDoesNotExistError()
        # check files limit
        if (
            len(dataset.files) + 1 > limits.datasets.files
            and uploading.name not in dataset.files
        ):
            raise TierLimitError(
                "You cannot have more than {} files".format(limits.datasets.files)
            )
        storage = self.os_repo.get_object(dataset.id, uploading.name)
        self.s3_repo.complete_multipart_upload(storage, inputs.upload_id)
        object_info = self.os_repo.object_info(dataset.id, uploading.name)
        # calculate checksum
        checksum = await self.os_repo.calculate_checksum(
            dataset.id, uploading.name
        )  # con md5 fallaba para large files, a ver si con sha1 va mejor
        if checksum != uploading.checksum:
            self.os_repo.delete_file(dataset.id, uploading.name)
            if len(dataset.files) == 0:
                self.db_repo.delete("datasets", dataset.id)
            raise ChecksumMismatch()
        if uploading.name in [f.name for f in dataset.files]:
            dataset.files = [f for f in dataset.files if f.name != uploading.name]
        dataset.files.append(
            File(name=uploading.name, size=object_info.size, checksum=checksum)
        )
        dataset.updatedAt = datetime.now()
        dataset.size = dataset.size + object_info.size
        self.db_repo.update("datasets", dataset.id, dataset.dict())
        # report usage
        usage = Usage.FileIngested(
            uid=inputs.uid,
            payload={
                "dataset": dataset.id,
                "file": uploading.name,
                "size": object_info.size,
            },
        )
        self.db_repo.persist("usage", usage.dict())
        self.db_repo.delete("uploading", uploading.id)
        return self.Outputs(dataset=dataset)
