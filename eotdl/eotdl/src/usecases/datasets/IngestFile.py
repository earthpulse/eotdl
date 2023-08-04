from pydantic import BaseModel
import os
import typing

from ....src.utils import calculate_checksum


class IngestFile:
    def __init__(self, repo, allowed_extensions, logger):
        self.repo = repo
        self.allowed_extensions = allowed_extensions
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        file: typing.Any
        dataset_id: str
        user: dict

    class Outputs(BaseModel):
        data: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # validate file extension
        extension = os.path.splitext(inputs.file)[1]
        if extension not in self.allowed_extensions:
            raise Exception(
                f"Only {', '.join(self.allowed_extensions)} files are allowed"
            )
        id_token = inputs.user["id_token"]
        self.logger(f"Uploading file {inputs.file}...")
        # if inputs.file.startswith("http://") or inputs.file.startswith("https://"):
        #     data, error = self.repo.ingest_file_url(
        #         inputs.file, inputs.metadata.name, id_token
        #     )
        # else:
        self.logger("Computing checksum...")
        checksum = calculate_checksum(inputs.file)
        self.logger(checksum)
        self.logger("Ingesting file...")
        filesize = os.path.getsize(inputs.file)
        # ingest small file
        if filesize < 1024 * 1024 * 16:  # 16 MB
            data, error = self.repo.ingest_file(
                inputs.file, inputs.dataset_id, id_token, checksum
            )
            if error:
                raise Exception(error)
            self.logger("Done")
            return self.Outputs(data=data)
        # ingest large file
        upload_id, parts = self.repo.prepare_large_upload(
            inputs.file, inputs.dataset_id, checksum, id_token
        )
        self.repo.ingest_large_dataset(inputs.file, upload_id, id_token, parts)
        self.logger("\nCompleting upload...")
        data, error = self.repo.complete_upload(id_token, upload_id)
        if error:
            raise Exception(error)
        self.logger("Done")
        return self.Outputs(data=data)
