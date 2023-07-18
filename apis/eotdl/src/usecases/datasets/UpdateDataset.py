from pydantic import BaseModel
from typing import List
from typing import Union
from datetime import datetime

from ...models import Dataset, Usage, User, Limits
from ...errors import (
    DatasetDoesNotExistError,
    DatasetAlreadyExistsError,
    UserUnauthorizedError,
    InvalidTagError,
)


class UpdateDataset:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str
        dataset_id: str
        name: Union[str, None]
        description: Union[str, None]
        authors: Union[List[str], None]
        source: Union[str, None]
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
        # validate tags
        if inputs.tags:
            tags_data = self.db_repo.retrieve("tags")
            tags = [tag["name"] for tag in tags_data]
            for tag in inputs.tags:
                if tag not in tags:
                    raise InvalidTagError()
        # update dataset
        data.update(
            updatedAt=datetime.now(),
            name=inputs.name if inputs.name is not None else dataset.name,
            description=inputs.description
            if inputs.description is not None
            else dataset.description,
            authors=inputs.authors if inputs.authors is not None else dataset.authors,
            source=inputs.source if inputs.source is not None else dataset.source,
            license=inputs.license if inputs.license is not None else dataset.license,
            tags=inputs.tags if inputs.tags is not None else dataset.tags,
        )
        updated_dataset = Dataset(**data)
        # update dataset in db
        self.db_repo.update("datasets", inputs.dataset_id, updated_dataset.dict())
        return self.Outputs(dataset=updated_dataset)
