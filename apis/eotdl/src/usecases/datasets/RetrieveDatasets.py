from pydantic import BaseModel
import typing
from typing import List

from ...models import Dataset

class RetrieveDatasets():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        datasets: List[Dataset]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve('datasets')
        datasets = [Dataset(**d) for d in data]
        return self.Outputs(datasets=datasets)