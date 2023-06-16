from pydantic import BaseModel
import os
from pathlib import Path


class IngestFolder:
    def __init__(self, repo, ingest_file, allowed_extensions, logger):
        self.repo = repo
        self.ingest_file = ingest_file
        self.allowed_extensions = allowed_extensions
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        folder: Path
        dataset: str = None
        user: dict

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        self.logger("Uploading directory (only files, not recursive)")
        items = list(inputs.folder.glob("*"))
        filtered_items = [item for item in items if item.is_file()]
        filtered_items = [
            item for item in filtered_items if item.suffix in self.allowed_extensions
        ]
        if len(filtered_items) == 0:
            raise Exception("No files found in directory")
        if len(filtered_items) > 10:
            raise Exception("Too many files in directory, limited to 10")
        self.logger("The following files will be uploaded:")
        for item in filtered_items:
            self.logger(f"{item.name}")
        for item in filtered_items:
            data = self.ingest_file(item, inputs.dataset, logger=self.logger)
        return self.Outputs(dataset=data)
