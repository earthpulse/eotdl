from pydantic import BaseModel
from typing import List


class RetrieveDatasets:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        pass

    class Outputs(BaseModel):
        datasets: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        data = self.repo.retrieve_datasets()
        datasets = {d["name"]: [f["name"] for f in d["files"]] for d in data}
        return self.Outputs(datasets=datasets)
