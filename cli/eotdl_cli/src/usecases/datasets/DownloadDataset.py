from pydantic import BaseModel
from src.utils import calculate_checksum


class DownloadDataset:
    def __init__(self, repo, logger):
        self.repo = repo
        self.logger = logger

    class Inputs(BaseModel):
        dataset: str
        path: str = None
        user: dict
        checksum: str

    class Outputs(BaseModel):
        dst_path: str

    def __call__(self, inputs: Inputs) -> Outputs:
        dst_path = self.repo.download_dataset(
            inputs.dataset, inputs.user["id_token"], inputs.path
        )
        checksum = calculate_checksum(dst_path)
        self.logger(f"Checksum: {checksum}")
        if inputs.checksum != checksum:
            self.logger("Checksums do not match")
        return self.Outputs(dst_path=dst_path)
