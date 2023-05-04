from pydantic import BaseModel
from typing import Union

from ...models import Dataset
from ...errors import DatasetDoesNotExistError

class RetrieveOneDatasetByName():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        dataset: Dataset

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.find_one_by_name('datasets', inputs.name)
        if not data:
            raise DatasetDoesNotExistError()
        dataset = Dataset(**data)
        return self.Outputs(dataset=dataset)