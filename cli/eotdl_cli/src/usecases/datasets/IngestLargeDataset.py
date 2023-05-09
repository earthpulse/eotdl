from pydantic import BaseModel

class IngestLargeDataset():
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger

    class Inputs(BaseModel):
        name: str
        description: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # allow only zip files
        if not inputs.path.endswith('.zip'):
            raise Exception('Only zip files are allowed')
        self.logger("Ingesting dataset...")
        response = self.repo.ingest_large_dataset(inputs.name, inputs.description, inputs.path, inputs.user['id_token'])
        data = response.json()
        if response.status_code == 200:
            self.logger("Done")
            return self.Outputs(dataset=data)
        raise Exception(data['detail'])