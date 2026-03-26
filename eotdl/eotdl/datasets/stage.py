import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
import geopandas as gpd

from ..auth import with_auth
from .retrieve import retrieve_dataset
from ..repos import FilesAPIRepo
from ..files.metadata import Metadata

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
    dataset = retrieve_dataset(dataset_name, user)
    if version is None:
        version = sorted([v['version_id'] for v in dataset["versions"]])[-1]
    else:
        assert version in [
            v["version_id"] for v in dataset["versions"]
        ], f"Version {version} not found"
    download_base_path = os.getenv(
        "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/datasets"
    )
    if path is None:
        download_path = download_base_path + "/" + dataset_name 
    else:
        download_path = path + "/" + dataset_name 
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
    catalog_path = repo.stage_file(dataset["id"], f"catalog.v{version}.parquet", user, download_path)
    # stage README.md
    metadata = Metadata(**dataset['metadata'], name=dataset['name'])
    metadata.save_metadata(download_path)
    # stage assets
    if assets:
        gdf = gpd.read_parquet(catalog_path)
        asset_urls = []
        for _, row in gdf.iterrows():
            for _, v in row["assets"].items():
                asset_urls.append(v["href"])

        workers = max(1, int(os.getenv("EOTDL_STAGE_WORKERS", "8")))
        workers = min(workers, len(asset_urls) or 1)

        if workers == 1:
            for href in tqdm(asset_urls, total=len(asset_urls), desc="Staging assets"):
                repo.stage_file_url(href, download_path, user)
        else:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [
                    executor.submit(repo.stage_file_url, href, download_path, user)
                    for href in asset_urls
                ]
                for future in tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc=f"Staging assets ({workers} workers)",
                ):
                    future.result()
    return download_path


@with_auth
def stage_dataset_file(file_url, path, user):
    repo = FilesAPIRepo()
    return repo.stage_file_url(file_url, path, user)
