from pydantic import BaseModel
from typing import List

from ...models import Dataset, User, Limits
from ...errors import (
    DatasetAlreadyExistsError,
    TierLimitError,
)


class CreateDataset:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        name: str
        uid: str
        authors: List[str]
        source: str
        license: str

    class Outputs(BaseModel):
        dataset_id: str

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset already exists
        data = self.db_repo.find_one_by_name("datasets", inputs.name)
        if data:
            raise DatasetAlreadyExistsError()
        # check if user can create dataset
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        user = User(**data)
        data = self.db_repo.find_one_by_name("tiers", user.tier)
        limits = Limits(**data["limits"])
        usage = self.db_repo.find_in_time_range(
            "usage", inputs.uid, "dataset_ingested", "type"
        )
        if len(usage) + 1 >= limits.datasets.upload:
            raise TierLimitError(
                "You cannot create more than {} datasets per day".format(
                    limits.datasets.upload
                )
            )
        if user.dataset_count + 1 > limits.datasets.count:
            raise TierLimitError(
                "You cannot have more than {} datasets".format(limits.datasets.count)
            )
        # generate new id
        id = self.db_repo.generate_id()
        dataset = Dataset(
            uid=inputs.uid,
            id=id,
            name=inputs.name,
            authors=inputs.authors,
            source=inputs.source,
            license=inputs.license,
        )
        self.db_repo.persist("datasets", dataset.dict(), dataset.id)
        self.db_repo.increase_counter("users", "uid", inputs.uid, "dataset_count")
        return self.Outputs(dataset_id=dataset.id)
