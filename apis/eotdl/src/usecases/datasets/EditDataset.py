from pydantic import BaseModel
from typing import List
from datetime import datetime

from ...models import Dataset
from ...errors import DatasetAlreadyExistsError, DatasetDoesNotExistError, UserUnauthorizedError, InvalidTagError

class EditDataset():
    def __init__(self, db_repo, retrieve_tags):
        self.db_repo = db_repo
        self.retrieve_tags = retrieve_tags

    class Inputs(BaseModel):
        id: str
        name: str = None
        description: str = None
        tags: List[str] = None
        uid: str

    class Outputs(BaseModel):
        dataset: Dataset

    def __call__(self, inputs: Inputs) -> Outputs:
        # check if dataset exists 
        data = self.db_repo.retrieve('datasets', inputs.id)
        if data is None:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        # check if user owns dataset
        if dataset.uid != inputs.uid:
            raise UserUnauthorizedError()
        # check if dataset name is already taken
        if inputs.name is not None and dataset.name != inputs.name:
            data = self.db_repo.find_one_by_name('datasets', inputs.name)
            if data is not None:
                raise DatasetAlreadyExistsError()
        # check tags are valid
        if inputs.tags is not None:
            data = self.retrieve_tags()
            for tag in inputs.tags:
                if tag not in data:
                    raise InvalidTagError()
        # update dataset
        updated_data = dataset.dict().copy()
        updated_data.update(
            name=inputs.name if inputs.name is not None else dataset.name,
            description=inputs.description if inputs.description is not None else dataset.description,
            tags=inputs.tags if inputs.tags is not None else dataset.tags,
            updatedAt=datetime.now()
        )
        updated_dataset = Dataset(**updated_data)
        self.db_repo.update('datasets', inputs.id, updated_dataset.dict())
        return self.Outputs(dataset=dataset)
