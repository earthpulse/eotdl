from pydantic import BaseModel
from src.utils import calculate_checksum


class IngestLargeDataset:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger

    class Inputs(BaseModel):
        name: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # allow only zip files
        if not inputs.path.endswith(".zip"):
            raise Exception("Only zip files are allowed")
        self.logger("Computing checksum...")
        checksum = calculate_checksum(inputs.path)
        self.logger(checksum)
        self.logger("Ingesting dataset...")
        data, error = self.repo.ingest_large_dataset(
            inputs.name, inputs.path, inputs.user["id_token"], checksum
        )
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(dataset=data)
        return
