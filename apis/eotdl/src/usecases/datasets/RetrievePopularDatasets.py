from pydantic import BaseModel
from typing import List, Union

from ...models import Dataset, STACDataset


class RetrievePopularDatasets:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        limit: Union[int, None] = None

    class Outputs(BaseModel):
        datasets: Union[List[Dataset], List[STACDataset]]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.find_top("datasets", "likes", inputs.limit)
        datasets = []
        for d in data:
            if d["quality"] == 0:
                datasets.append(Dataset(**d))
            else:
                datasets.append(STACDataset(**d))
        return self.Outputs(datasets=datasets)
