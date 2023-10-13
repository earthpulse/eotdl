from pydantic import BaseModel
from ....utils import calculate_checksum


class DownloadFile:
    def __init__(self, repo, retrieve_dataset, logger):
        self.repo = repo
        self.retrieve_dataset = retrieve_dataset
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        dataset: str
        file: str
        path: str = None
        user: dict
        checksum: str

    class Outputs(BaseModel):
        dst_path: str

    def __call__(self, inputs: Inputs) -> Outputs:
        dataset = self.retrieve_dataset(inputs.dataset)
        dst_path = self.repo.download_file(
            inputs.dataset, inputs.file, inputs.user["id_token"], inputs.path
        )
        checksum = calculate_checksum(dst_path)
        self.logger(f"Checksum: {checksum}")
        if dataset["checksum"] != checksum:
            self.logger("Checksums do not match")
        return self.Outputs(dst_path=dst_path)
