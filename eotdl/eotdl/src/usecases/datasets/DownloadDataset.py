from pydantic import BaseModel
from pathlib import Path
import os
from typing import Union
from tqdm import tqdm

from ....curation.stac import STACDataFrame
from ....src.utils import calculate_checksum


class DownloadDataset:
    def __init__(self, repo, retrieve_dataset, logger):
        self.repo = repo
        self.retrieve_dataset = retrieve_dataset
        self.logger = logger if logger else print

    class Inputs(BaseModel):
        dataset: str
        file: Union[str, None] = None
        path: Union[str, None] = None
        user: dict
        assets: bool = False
        force: bool = False

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
        download_base_path = os.getenv(
            "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/datasets"
        )
        if inputs.path is None:
            download_path = download_base_path + "/" + inputs.dataset
        else:
            download_path = inputs.path + "/" + inputs.dataset
        os.makedirs(download_path, exist_ok=True)
        # check if dataset already exists
        if os.path.exists(download_path) and not inputs.force:
            raise Exception(
                f"Dataset {inputs.dataset} already exists at {download_path}. To force download, use force=True or -f in the CLI."
            )

        if dataset["quality"] == 0:
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
                    download_path,
                    inputs.user,
                )
                return self.Outputs(dst_path=dst_path)
            for file in dataset["files"]:
                dst_path = self.download(
                    inputs.dataset,
                    dataset["id"],
                    file["name"],
                    file["checksum"],
                    download_path,
                    inputs.user,
                )
            return self.Outputs(dst_path="/".join(dst_path.split("/")[:-1]))
        else:
            self.logger("Downloading STAC metadata...")
            gdf, error = self.repo.download_stac(
                dataset["id"],
                inputs.user["id_token"],
            )
            if error:
                raise Exception(error)
            df = STACDataFrame(gdf)
            # df.geometry = df.geometry.apply(lambda x: Polygon() if x is None else x)
            path = inputs.path
            if path is None:
                path = download_base_path + "/" + dataset["name"]
            df.to_stac(path)
            # download assets
            if inputs.assets:
                self.logger("Downloading assets...")
                df = df.dropna(subset=["assets"])
                for row in tqdm(df.iterrows(), total=len(df)):
                    id = row[1]["stac_id"]
                    # print(row[1]["links"])
                    for k, v in row[1]["assets"].items():
                        href = v["href"]
                        self.repo.download_file_url(
                            href, f"{path}/assets/{id}", inputs.user["id_token"]
                        )
            else:
                self.logger("To download assets, set assets=True or -a in the CLI.")
            return self.Outputs(dst_path=path)
