from pydantic import BaseModel


class IngestDataset:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        name: str
        description: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # allow only zip files
        if not inputs.path.endswith(".zip"):
            raise Exception("Only zip files are allowed")
        self.logger("Ingesting dataset...")
        data, error = self.repo.ingest_dataset(
            inputs.name, inputs.description, inputs.path, inputs.user["id_token"]
        )
        # response = self.repo.ingest_large_dataset(inputs.name, inputs.description, inputs.path, inputs.user['id_token'])
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(dataset=data)
