from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import STACDataset, User, User
from ...errors import DatasetDoesNotExistError


class IngestSTAC:
    def __init__(self, db_repo, os_repo, geodb_repo, retrieve_user_credentials):
        self.db_repo = db_repo
        self.os_repo = os_repo
        self.geodb_repo = geodb_repo
        self.retrieve_user_credentials = retrieve_user_credentials

    class Inputs(BaseModel):
        dataset: str
        stac: dict
        user: User

    class Outputs(BaseModel):
        dataset: STACDataset

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists
        data = self.db_repo.retrieve("datasets", inputs.dataset)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = STACDataset(**data)
        # check user owns dataset
        if dataset.uid != inputs.user.uid:
            raise DatasetDoesNotExistError()
        # TODO: check all assets exist in os
        # ingest to geodb
        credentials = self.retrieve_user_credentials(inputs.user)
        self.geodb_repo = self.geodb_repo(credentials)
        self.geodb_repo.insert(inputs.dataset, inputs.stac)
        return self.Outputs(dataset=dataset)
