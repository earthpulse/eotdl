from pydantic import BaseModel
import typing
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits
from ...errors import (
    DatasetDoesNotExistError,
    DatasetAlreadyExistsError,
    UserUnauthorizedError,
)


class UpdateDataset:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
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

    def __call__(self, inputs: Inputs) -> Outputs:
        # retrieve dataset
        data = self.db_repo.retrieve("datasets", inputs.dataset_id, "id")
        if data is None:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        # check if user owns dataset
        if dataset.uid != inputs.uid:
            raise UserUnauthorizedError()
        if inputs.name:
            # check dataset does not exists already
            data2 = self.db_repo.find_one_by_name("datasets", inputs.name)
            if data2:
                raise DatasetAlreadyExistsError()
        # update dataset
        data.update(
            updatedAt=datetime.now(),
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
        # update dataset in db
        self.db_repo.update("datasets", inputs.dataset_id, updated_dataset.dict())
        return self.Outputs(dataset=updated_dataset)
