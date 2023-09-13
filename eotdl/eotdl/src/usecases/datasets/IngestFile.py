from pydantic import BaseModel
import os
import typing
from pathlib import Path
from glob import glob

from ....src.utils import calculate_checksum


class IngestFile:
    def __init__(self, repo, allowed_extensions, logger, verbose=True):
        self.repo = repo
        self.allowed_extensions = allowed_extensions
        self.logger = logger if logger else print
        self.verbose = verbose

    class Inputs(BaseModel):
        file: typing.Any
        dataset_id: str
        user: dict
        root: typing.Optional[Path] = None

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
        if self.verbose:
            self.logger(f"Uploading file {inputs.file}...")
        if inputs.file.startswith("http://") or inputs.file.startswith("https://"):
            data, error = self.repo.ingest_file_url(
                inputs.file, inputs.dataset_id, id_token
            )
        else:
            file_path = Path(inputs.file)
            if not file_path.is_absolute():
                file_path = glob(
                    str(inputs.root) + "/**/" + os.path.basename(file_path),
                    recursive=True,
                )
                if len(file_path) == 0:
                    raise Exception(f"File {inputs.file} not found")
                elif len(file_path) > 1:
                    raise Exception(f"Multiple files found for {inputs.file}")
                file_path = file_path[0]
            if self.verbose:
                self.logger("Computing checksum...")
            checksum = calculate_checksum(file_path)
            if self.verbose:
                self.logger("Ingesting file...")
            filesize = os.path.getsize(file_path)
            # ingest small file
            if filesize < 1024 * 1024 * 16:  # 16 MB
                data, error = self.repo.ingest_file(
                    file_path, inputs.dataset_id, id_token, checksum
                )
                if error:
                    raise Exception(error)
                if self.verbose:
                    self.logger("Done")
                return self.Outputs(data=data)
            # ingest large file
            upload_id, parts = self.repo.prepare_large_upload(
                file_path, inputs.dataset_id, checksum, id_token
            )
            self.repo.ingest_large_dataset(file_path, upload_id, id_token, parts)
            if self.verbose:
                self.logger("\nCompleting upload...")
            data, error = self.repo.complete_upload(id_token, upload_id)
        if error:
            raise Exception(error)
        if self.verbose:
            self.logger("Done")
        return self.Outputs(data=data)
