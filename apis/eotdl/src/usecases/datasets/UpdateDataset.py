from pydantic import BaseModel
import typing
from datetime import datetime

from ...models import Dataset, Usage, User, Limits
from ...errors import DatasetDoesNotExistError, TierLimitError, UserUnauthorizedError


class UpdateDataset:
    def __init__(self, db_repo, os_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo

    class Inputs(BaseModel):
        file: typing.Any
        size: int
        uid: str
        dataset_id: str

    class Outputs(BaseModel):
        dataset: Dataset

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
            size=inputs.size,
        )
        updated_dataset = Dataset(**data)
        # save file in storage
        self.os_repo.persist_file(inputs.file, inputs.dataset_id)  # no need to delete !
        # update dataset in db
        self.db_repo.update("datasets", inputs.dataset_id, updated_dataset.dict())
        # report usage
        usage = Usage.DatasetIngested(
            uid=inputs.uid, payload={"dataset": inputs.dataset_id}
        )
        self.db_repo.persist("usage", usage.dict())
        return self.Outputs(dataset=dataset)
