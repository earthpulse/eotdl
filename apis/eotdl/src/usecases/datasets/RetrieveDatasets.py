from pydantic import BaseModel
from typing import List, Union

from ...models import Dataset, STACDataset


class RetrieveDatasets:
    def __init__(self, db_repo):
        self.db_repo = db_repo

    class Inputs(BaseModel):
        limit: Union[int, None] = None

    class Outputs(BaseModel):
        datasets: List[Union[Dataset, STACDataset]]

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.db_repo.retrieve(
            "datasets", limit=inputs.limit, sort="createdAt", order=-1
        )
        datasets = []
        for d in data:
            if d["quality"] == 0:
                datasets.append(Dataset(**d))
            else:
                datasets.append(STACDataset(**d))
        return self.Outputs(datasets=datasets)
