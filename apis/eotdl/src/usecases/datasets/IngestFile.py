from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits, File, STACDataset
from ...errors import (
    TierLimitError,
    DatasetDoesNotExistError,
    ChecksumMismatch,
)


class IngestFile:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        dataset_id: str
        file: typing.Any
        uid: str
        checksum: Union[str, None] = None

    class Outputs(BaseModel):
        dataset_id: str
        dataset_name: str
        file_name: str

    def get_file_name(self, file):
        return file.filename

    def persist_file(self, file, dataset_id, filename):
        return self.os_repo.persist_file(file.file, dataset_id, filename)

    async def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset_id)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data) if data["quality"] == 0 else STACDataset(**data)
        # check if user can ingest file
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        # check user owns dataset
        if dataset.uid != inputs.uid:
            raise DatasetDoesNotExistError()
        # check if user can ingest file
        filename = self.get_file_name(inputs.file)
        if dataset.quality == 0:
            if len(dataset.files) + 1 > limits.datasets.files and filename not in [
                file.name for file in dataset.files
            ]:
                raise TierLimitError(
                    "You cannot have more than {} files".format(limits.datasets.files)
                )
        # save file in storage
        self.persist_file(inputs.file, dataset.id, filename)
        # calculate checksum
        checksum = await self.os_repo.calculate_checksum(dataset.id, filename)
        if inputs.checksum and checksum != inputs.checksum:
            self.os_repo.delete_file(dataset.id, inputs.file.name)
            if len(dataset.files) == 0:
                self.db_repo.delete("datasets", dataset.id)
            raise ChecksumMismatch()
        file_size = self.os_repo.object_info(dataset.id, filename).size
        if dataset.quality == 0:
            if filename in [f.name for f in dataset.files]:  # update file
                current_file = [f for f in dataset.files if f.name == filename][0]
                dataset.size -= current_file.size
                dataset.files = [f for f in dataset.files if f.name != filename]
            dataset.files.append(File(name=filename, size=file_size, checksum=checksum))
            dataset.size += file_size
        dataset.updatedAt = datetime.now()
        self.db_repo.update("datasets", dataset.id, dataset.dict())
        # report usage
        usage = Usage.FileIngested(
            uid=inputs.uid,
            payload={
                "dataset": dataset.id,
                "file": filename,
                "size": file_size,
            },
        )
        self.db_repo.persist("usage", usage.dict())
        return self.Outputs(
            dataset_id=dataset.id,
            dataset_name=dataset.name,
            file_name=filename,
        )
