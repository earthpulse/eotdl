from pydantic import BaseModel
from ....utils import calculate_checksum


class IngestLargeDataset:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        name: str
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        data, error = self.repo.retrieve_dataset(inputs.name)
        if data:
            raise Exception("Dataset already exists")
        # allow only zip files
        if not inputs.path.endswith(".zip"):
            raise Exception("Only zip files are allowed")
        self.logger("Computing checksum...")
        checksum = calculate_checksum(inputs.path)
        self.logger(checksum)
        self.logger("Ingesting dataset...")
        id_token = inputs.user["id_token"]
        dataset_id, upload_id, parts = self.repo.prepare_large_upload(
            inputs.name, id_token, checksum
        )
        self.repo.ingest_large_dataset(
            inputs.path, upload_id, dataset_id, id_token, parts
        )
        self.logger("\nCompleting upload...")
        data, error = self.repo.complete_upload(
            inputs.name, id_token, upload_id, dataset_id, checksum
        )
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(dataset=data)
