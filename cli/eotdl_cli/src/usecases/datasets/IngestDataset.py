from pydantic import BaseModel

class IngestDataset():
    def __init__(self, repo):
        self.repo = repo

    class Inputs(BaseModel):
        name: str
        description: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        response = self.repo.ingest_dataset(inputs.name, inputs.description, inputs.path, inputs.user['id_token'])
        # response = self.repo.ingest_large_dataset(inputs.name, inputs.description, inputs.path, inputs.user['id_token'])
        data = response.json()
        if response.status_code == 200:
            return self.Outputs(dataset=data)
        raise Exception(data['detail'])