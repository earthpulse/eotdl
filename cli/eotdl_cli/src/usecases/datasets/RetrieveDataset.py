from pydantic import BaseModel


class RetrieveDataset:
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        data, error = self.repo.retrieve_dataset(inputs.name)
        if error:
            raise Exception(error)
        return self.Outputs(dataset=data)
