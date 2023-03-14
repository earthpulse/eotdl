from pydantic import BaseModel

class RetrieveDataset():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        name: str

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        response = self.repo.retrieve_dataset(inputs.name)
        data = response.json()
        if response.status_code == 200:
            return self.Outputs(dataset=data)
        raise Exception(data['detail'])
        