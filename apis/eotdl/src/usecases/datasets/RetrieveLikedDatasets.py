from pydantic import BaseModel
from typing import List

from ...models import Dataset, User

class RetrieveLikedDatasets():
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str

    class Outputs(BaseModel):
        datasets: List[Dataset]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve('users', inputs.uid, 'uid')
        user = User(**data)
        data = self.db_repo.retrieve_many('datasets', user.liked_datasets)
        datasets = [Dataset(**d) for d in data]
        return self.Outputs(datasets=datasets)