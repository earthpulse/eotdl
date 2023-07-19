from pydantic import BaseModel
import os
from pathlib import Path
import yaml
from ...models import Metadata


class IngestFolder:
    def __init__(self, repo, ingest_file, allowed_extensions, logger):
        self.repo = repo
        self.ingest_file = ingest_file
        self.allowed_extensions = allowed_extensions
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        folder: Path
        user: dict
        force: bool = False
        delete: bool = False

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        # validate folder
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
        if "metadata.yml" not in [item.name for item in filtered_items]:
            raise Exception("metadata.yml not found in directory")
        # load metadata
        metadata = yaml.safe_load(
            open(inputs.folder.joinpath("metadata.yml"), "r").read()
        )
        metadata = Metadata(**metadata)
        # remove metadata.yml from files
        filtered_items = [
            item for item in filtered_items if item.name != "metadata.yml"
        ]
        # create dataset
        data, error = self.repo.create_dataset(metadata.dict(), inputs.user["id_token"])
        # dataset may already exists, but if user is owner continue ingesting files
        current_files = []
        if error:
            data, error2 = self.repo.retrieve_dataset(metadata.name)
            if error2:
                raise Exception(error)
            if data["uid"] != inputs.user["sub"]:
                raise Exception("Dataset already exists.")
            data["dataset_id"] = data["id"]
            current_files = [item["name"] for item in data["files"]]
            if len(current_files) > 0 and not inputs.force:
                self.logger(
                    "The following files already exist and will not be uploaded (use --f to force re-upload):"
                )
                for item in current_files:
                    self.logger(f"{item}")
            hanged_files = [
                file
                for file in current_files
                if file not in [item.name for item in filtered_items]
            ]
            if len(hanged_files) > 0:
                self.logger(
                    "The following files are no longer in your dataset (use --d to delete):"
                )
                for item in hanged_files:
                    self.logger(f"{item}")
                    if inputs.delete:
                        self.logger(f"Deleting file {item}...")
                        _, error = self.repo.delete_file(
                            data["dataset_id"], item, inputs.user["id_token"]
                        )
                        if error:
                            self.logger(error)
                        else:
                            self.logger("Done")
            if not inputs.force:
                filtered_items = [
                    item for item in filtered_items if item.name not in current_files
                ]
        dataset_id = data["dataset_id"]
        # upload files
        if len(filtered_items) == 0:
            raise Exception("No files to upload")
        self.logger("The following files will be uploaded:")
        for item in filtered_items:
            self.logger(f"{item.name}")
        for item in filtered_items:
            data = self.ingest_file(item, dataset_id, logger=self.logger)
        return self.Outputs(dataset=data)
