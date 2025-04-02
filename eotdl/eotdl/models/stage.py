import os
from pathlib import Path
from tqdm import tqdm
import geopandas as gpd

from ..auth import with_auth
from .retrieve import retrieve_model
from ..repos import FilesAPIRepo
from ..files.metadata import Metadata

@with_auth
def stage_model(
    model_name,
    version=None,
    path=None,
    logger=print,
    assets=False,
    force=False,
    verbose=False,
    user=None,
    file=None,
):
    model = retrieve_model(model_name)
    if version is None:
        version = sorted([v['version_id'] for v in model["versions"]])[-1]
    else:
        assert version in [
            v["version_id"] for v in model["versions"]
        ], f"Version {version} not found"
    download_base_path = os.getenv(
        "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/models"
    )
    if path is None:
        download_path = download_base_path + "/" + model_name
    else:
        download_path = path + "/" + model_name
    # check if model already exists
    if os.path.exists(download_path) and not force:
        os.makedirs(download_path, exist_ok=True)
        # raise Exception(
        #     f"model `{model['name']} v{str(version)}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
        # )
    
    # stage metadata
    repo = FilesAPIRepo()
    catalog_path = repo.stage_file(model["id"], f"catalog.v{version}.parquet", user, download_path)

    # stage README.md
    metadata = Metadata(**model['metadata'], name=model['name'])
    metadata.save_metadata(download_path)

    if assets:
        gdf = gpd.read_parquet(catalog_path)
        for _, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Staging assets"):
            for k, v in row["assets"].items():
                stage_model_file(v["href"], download_path)

    return download_path

@with_auth
def stage_model_file(file_url, path, user):
    repo = FilesAPIRepo()
    return repo.stage_file_url(file_url, path, user)