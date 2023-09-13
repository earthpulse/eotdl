from pydantic import BaseModel
from typing import List, Union

from ...models import Dataset, User, STACDataset
from ...errors import UserDoesNotExistError


class RetrieveLikedDatasets:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        uid: str

    class Outputs(BaseModel):
        datasets: Union[List[Dataset], List[STACDataset]]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve("users", inputs.uid, "uid")
        if data is None:
            raise UserDoesNotExistError()
        user = User(**data)
        data = self.db_repo.retrieve_many("datasets", user.liked_datasets)
        datasets = []
        for d in data:
            if d["quality"] == 0:
                datasets.append(Dataset(**d))
            else:
                datasets.append(STACDataset(**d))
        return self.Outputs(datasets=datasets)
