from pydantic import BaseModel
import os

from ....src.utils import calculate_checksum


class IngestFile:
    def __init__(self, repo, allowed_extensions, logger):
        self.repo = repo
        self.allowed_extensions = allowed_extensions
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        file: str
        dataset: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        data, error = self.repo.retrieve_dataset(inputs.dataset)
        if data:
            raise Exception("Dataset already exists")
        if not inputs.suffix in self.allowed_extensions:
            raise Exception(
                "Only zip, tar, tar.gz, csv, txt, json, pdf, md files are allowed"
            )
        self.logger(f"Uploading file {inputs.file}...")
        self.logger("Computing checksum...", end=" ")
        checksum = calculate_checksum(inputs.file)
        self.logger(checksum)
        self.logger("Ingesting dataset...", end=" ")
        id_token = inputs.user["id_token"]
        filesize = os.path.getsize(inputs.file)
        # samll file
        if filesize < 1024 * 1024 * 16:  # 16 MB
            data, error = self.repo.ingest_file(
                inputs.file, inputs.dataset, id_token, checksum
            )
            self.logger("Done")
            if error:
                raise Exception(error)
            return self.Outputs(dataset=data)
        # large file
        dataset_id, upload_id, parts = self.repo.prepare_large_upload(
            inputs.file, id_token, checksum
        )
        self.repo.ingest_large_dataset(
            inputs.file, upload_id, dataset_id, id_token, parts
        )
        self.logger("\nCompleting upload...")
        data, error = self.repo.complete_upload(
            inputs.name, id_token, upload_id, dataset_id, checksum
        )
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(dataset=data)
