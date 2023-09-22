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
        catalog = self.geodb_repo.insert(inputs.dataset, inputs.stac)
        # the catalog should contain all the info we want to show in the UI
        dataset.catalog = catalog
        keys = list(catalog.keys())
        if "ml-dataset:name" in keys:
            dataset.quality = 2
            # TODO: compute and report automatic qa metrics
        # TODO: validate Q2 dataset, not only check name
        # TODO: validate Q1 dataset with required fields/extensions (author, license)
        self.db_repo.update("datasets", inputs.dataset, dataset.model_dump())
        return self.Outputs(dataset=dataset)
