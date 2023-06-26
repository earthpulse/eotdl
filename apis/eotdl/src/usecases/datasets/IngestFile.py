from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits, File
from ...errors import (
    DatasetAlreadyExistsError,
    TierLimitError,
    DatasetDoesNotExistError,
)


class IngestFile:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        dataset: str
        file: typing.Any
        uid: str
        checksum: Union[str, None]

    class Outputs(BaseModel):
        dataset: Dataset

    async def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        data = self.db_repo.find_one_by_name("datasets", inputs.dataset)
        new_dataset = False
        if not data:
            new_dataset = True
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
            # check if name already exists
            if self.db_repo.find_one_by_name("datasets", inputs.dataset):
                raise DatasetAlreadyExistsError()
            # generate new id
            id = self.db_repo.generate_id()
            # save dataset in db
            data = dict(
                uid=inputs.uid,
                id=id,
                name=inputs.dataset,
            )
        dataset = Dataset(**data)
        # check user owns dataset
        if dataset.uid != inputs.uid:
            raise DatasetDoesNotExistError()
        # check if user can ingest file
        if (
            len(dataset.files) + 1 >= limits.datasets.files
            and inputs.file.filename not in dataset.files
        ):
            raise TierLimitError(
                "You cannot have more than {} files".format(limits.datasets.files)
            )
        # save file in storage
        self.os_repo.persist_file(inputs.file.file, dataset.id, inputs.file.filename)
        # calculate checksum
        checksum = await self.os_repo.calculate_checksum(
            dataset.id, inputs.file.filename
        )
        if inputs.checksum and checksum != inputs.checksum:
            self.os_repo.delete_file(dataset.id, inputs.file.name)
            if len(dataset.files) == 0:
                self.db_repo.delete("datasets", dataset.id)
            raise Exception("Checksum does not match")
        if inputs.file.filename in [f.name for f in dataset.files]:  # update file
            current_file = [f for f in dataset.files if f.name == inputs.file.filename][
                0
            ]
            dataset.size -= current_file.size
            dataset.files = [f for f in dataset.files if f.name != inputs.file.filename]
        dataset.files.append(
            File(name=inputs.file.filename, size=inputs.file.size, checksum=checksum)
        )
        dataset.size += inputs.file.size
        if new_dataset:
            self.db_repo.persist("datasets", dataset.dict(), dataset.id)
            self.db_repo.increase_counter("users", "uid", inputs.uid, "dataset_count")
        else:
            dataset.updatedAt = datetime.now()
            self.db_repo.update("datasets", dataset.id, dataset.dict())
        # report usage
        usage = Usage.FileIngested(
            uid=inputs.uid,
            payload={
                "dataset": dataset.id,
                "file": inputs.file.filename,
                "size": inputs.file.size,
            },
        )
        self.db_repo.persist("usage", usage.dict())
        return self.Outputs(dataset=dataset)
