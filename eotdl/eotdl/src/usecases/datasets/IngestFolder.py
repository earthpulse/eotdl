from pydantic import BaseModel
from pathlib import Path
import yaml
from ...models import Metadata
from glob import glob
from tqdm import tqdm

class IngestFolder:
    def __init__(self, repo, ingest_file, logger):
        self.repo = repo
        self.ingest_file = ingest_file
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        folder: Path
        user: dict
        force: bool = False
        delete: bool = False

    class Outputs(BaseModel):
        dataset: dict

    def __call__(self, inputs: Inputs) -> Outputs:
        self.logger(f"Uploading directory {inputs.folder}...")
        # get all files in directory recursively
        items = [Path(item) for item in glob(str(inputs.folder) + "/**/*", recursive=True)]
        # remove directories
        items = [item for item in items if not item.is_dir()]
        if len(items) == 0:
            raise Exception("No files found in directory")
        if not any(item.name == "metadata.yml" for item in items):
            raise Exception("metadata.yml not found in directory")
        # load metadata
        metadata = yaml.safe_load(
            open(inputs.folder.joinpath("metadata.yml"), "r").read()
        ) or {}
        metadata = Metadata(**metadata)
        # remove metadata.yml from files
        items = [item for item in items if item.name != "metadata.yml"]
        # if zip or tar file, send error
        if any(item.suffix.endswith((".zip", ".tar", ".tar.gz", ".gz")) for item in items):
            raise Exception(f"At least one zip, tar or gz file found in {inputs.folder}, please unzip and try again")
        # create dataset
        data, error = self.repo.create_dataset(metadata.dict(), inputs.user["id_token"])
        print(data, error)
        # dataset may already exist, but if user is owner continue ingesting files 
        current_files = []
        if error:
            data, error2 = self.repo.retrieve_dataset(metadata.name)
            print(data, error2)
            if error2:
                raise Exception(error)
            if data["uid"] != inputs.user["sub"]:
                raise Exception("Dataset already exists.")
            data["dataset_id"] = data["id"]
            # current_files = [item["name"] for item in data["files"]]
            # print("current_files", current_files)
        dataset_id = data["dataset_id"]
        # create new version
        data, error = self.repo.create_version(dataset_id, inputs.user["id_token"])
        print(data, error)
        version = data["version"]
        # upload files
        for item in tqdm(items):
            data = self.ingest_file(str(item), dataset_id, version, str(item.relative_to(inputs.folder).parent), logger=self.logger, verbose=False)
        return self.Outputs(dataset=data)
