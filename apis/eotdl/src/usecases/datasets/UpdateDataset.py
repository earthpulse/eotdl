from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits
from ...errors import DatasetDoesNotExistError, TierLimitError, UserUnauthorizedError
from ...utils import calculate_checksum


class UpdateDataset:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        file: Union[typing.Any, None]
        size: Union[int, None]
        uid: str
        dataset_id: str
        name: Union[str, None]
        description: Union[str, None]
        author: Union[str, None]
        link: Union[str, None]
        license: Union[str, None]
        tags: Union[list, None]

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
        # retrieve dataset
        data = self.db_repo.retrieve("datasets", inputs.dataset_id, "id")
        if data is None:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        # check if user owns dataset
        if dataset.uid != inputs.uid:
            raise UserUnauthorizedError()
        # update dataset
        data.update(
            updatedAt=datetime.now(),
            size=inputs.size if inputs.size is not None else dataset.size,
            name=inputs.name if inputs.name is not None else dataset.name,
            description=inputs.description
            if inputs.description is not None
            else dataset.description,
            author=inputs.author if inputs.author is not None else dataset.author,
            link=inputs.link if inputs.link is not None else dataset.link,
            license=inputs.license if inputs.license is not None else dataset.license,
            tags=inputs.tags if inputs.tags is not None else dataset.tags,
        )
        updated_dataset = Dataset(**data)
        # save file in storage
        if inputs.file is not None:
            self.os_repo.persist_file(
                inputs.file, inputs.dataset_id
            )  # no need to delete !
            data_stream = self.os_repo.data_stream(inputs.dataset_id)
            checksum = await calculate_checksum(data_stream)
            updated_dataset.checksum = checksum
            # report usage
            usage = Usage.DatasetIngested(
                uid=inputs.uid, payload={"dataset": inputs.dataset_id}
            )
            self.db_repo.persist("usage", usage.dict())
        # update dataset in db
        self.db_repo.update("datasets", inputs.dataset_id, updated_dataset.dict())
        return self.Outputs(dataset=updated_dataset)
