from pydantic import BaseModel
from ....src.utils import calculate_checksum


class DownloadDataset:
    def __init__(self, repo, retrieve_dataset, logger):
        self.repo = repo
        self.retrieve_dataset = retrieve_dataset
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        dataset: str
        file: str = None
        path: str = None
        user: dict

    class Outputs(BaseModel):
        dst_path: str

    def download(self, dataset, dataset_id, file, checksum, path, user):
        self.logger(f"Downloading {file}")
        dst_path = self.repo.download_file(
            dataset, dataset_id, file, user["id_token"], path
        )
        if calculate_checksum(dst_path) != checksum:
            self.logger(f"Checksum for {file} does not match")
        self.logger(f"Done")
        return dst_path

    def __call__(self, inputs: Inputs) -> Outputs:
        dataset = self.retrieve_dataset(inputs.dataset)
        if inputs.file:
            files = [f for f in dataset["files"] if f["name"] == inputs.file]
            if not files:
                raise Exception(f"File {inputs.file} not found")
            if len(files) > 1:
                raise Exception(f"Multiple files with name {inputs.file} found")
            dst_path = self.download(
                inputs.dataset,
                dataset["id"],
                inputs.file,
                files[0]["checksum"],
                inputs.path,
                inputs.user,
            )
            return self.Outputs(dst_path=dst_path)
        for file in dataset["files"]:
            dst_path = self.download(
                inputs.dataset,
                dataset["id"],
                file["name"],
                file["checksum"],
                inputs.path,
                inputs.user,
            )
        return self.Outputs(dst_path="/".join(dst_path.split("/")[:-1]))
