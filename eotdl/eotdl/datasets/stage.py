import os
from pathlib import Path
from tqdm import tqdm
import geopandas as gpd

from ..auth import with_auth
from .retrieve import retrieve_dataset, retrieve_dataset_files
from ..repos import FilesAPIRepo, DatasetsAPIRepo
# from .metadata import generate_metadata


@with_auth
def stage_dataset(
    dataset_name,
    version=None,
    path=None,
    logger=print,
    assets=False,
    force=False,
    verbose=False,
    user=None,
    file=None,
):
    dataset = retrieve_dataset(dataset_name)
    if version is None:
        version = sorted(dataset["versions"], key=lambda v: v["version_id"])[-1][
            "version_id"
        ]
    else:
        assert version in [
            v["version_id"] for v in dataset["versions"]
        ], f"Version {version} not found"
    download_base_path = os.getenv(
        "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/datasets"
    )
    if path is None:
        download_path = download_base_path + "/" + dataset_name #+ "/v" + str(version)
    else:
        download_path = path + "/" + dataset_name #∫+ "/v" + str(version)
    # check if dataset already exists
    if os.path.exists(download_path) and not force:
        os.makedirs(download_path, exist_ok=True)
        # raise Exception(
        #     f"Dataset `{dataset['name']} v{str(version)}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
        # )
        raise Exception(
            f"Dataset `{dataset['name']}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
        )

    # stage metadata
    repo = FilesAPIRepo()
    catalog_path = repo.stage_file(dataset["id"], "catalog.parquet", user, download_path)

    if assets:
        gdf = gpd.read_parquet(catalog_path)
        for _, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Staging assets"):
            for asset in row["assets"]:
                stage_dataset_file(asset["href"], download_path)

    return download_path


@with_auth
def stage_dataset_file(file_url, path, user):
    repo = FilesAPIRepo()
    return repo.stage_file_url(file_url, path, user)


# @with_auth
# def download_file_url(url, path, progress=True, logger=print, user=None):
#     repo = FilesAPIRepo()
#     _, filename = url.split("/download/")
#     return repo.download_file_url(url, filename, f"{path}/assets", user, progress)
