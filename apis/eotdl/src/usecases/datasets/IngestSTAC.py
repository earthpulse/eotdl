from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits, File
from ...errors import (
    DatasetAlreadyExistsError,
    TierLimitError,
    DatasetDoesNotExistError,
    ChecksumMismatch,
)


class IngestSTAC:
    def __init__(self, db_repo, os_repo, geodb_repo):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.geodb_repo = geodb_repo

    class Inputs(BaseModel):
        dataset: str
        stac: dict
        uid: str

    class Outputs(BaseModel):
        dataset: Dataset

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.find_one_by_name("datasets", inputs.dataset)
        if not data:
            raise DatasetAlreadyExistsError()
        dataset = Dataset(**data)
        # check user owns dataset
        if dataset.uid != inputs.uid:
            raise DatasetDoesNotExistError()
        # TODO: check all assets exist in os
        # ingest to geodb
        self.geodb_repo.insert(dataset.name, inputs.stac)
        return self.Outputs(dataset=dataset)
