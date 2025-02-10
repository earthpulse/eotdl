import os
from pathlib import Path
from tqdm import tqdm

from ..auth import with_auth
from .retrieve import retrieve_model, retrieve_model_files
from ..shared import calculate_checksum
from ..repos import FilesAPIRepo, ModelsAPIRepo
from .metadata import generate_metadata
from ..curation.stac import STACDataFrame


@with_auth
def download_model(
    model_name,
    version=None,
    path=None,
    logger=None,
    assets=False,
    force=False,
    verbose=False,
    user=None,
    file=None,
):
    model = retrieve_model(model_name)
    if version is None:
        version = sorted(model["versions"], key=lambda v: v["version_id"])[-1][
            "version_id"
        ]
    else:
        assert version in [
            v["version_id"] for v in model["versions"]
        ], f"Version {version} not found"
    download_base_path = os.getenv(
        "EOTDL_DOWNLOAD_PATH", str(Path.home()) + "/.cache/eotdl/models"
    )
    if path is None:
        download_path = download_base_path + "/" + model_name + "/v" + str(version)
    else:
        download_path = path + "/" + model_name + "/v" + str(version)
    # check if model already exists
    if os.path.exists(download_path) and not force:
        os.makedirs(download_path, exist_ok=True)
        raise Exception(
            f"model `{model['name']} v{str(version)}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
        )
    if model["quality"] == 0:
        if file:
            raise NotImplementedError("Downloading a specific file is not implemented")
        model_files = retrieve_model_files(model["id"], version)
        repo = FilesAPIRepo()
        for file in tqdm(model_files, disable=verbose, unit="file"):
            filename, file_version = file["filename"], file["version"]
            if verbose:
                logger(f"Downloading {file['filename']}...")
            dst_path = repo.download_file(
                model["id"],
                filename,
                user,
                download_path,
                file_version,
                endpoint="models",
            )
            if verbose:
                logger("Generating README.md ...")
            generate_metadata(download_path, model)
    else:
        if verbose:
            logger("Downloading STAC metadata...")
        repo = ModelsAPIRepo()
        gdf, error = repo.download_stac(
            model["id"],
            user,
        )
        if error:
            raise Exception(error)
        # print(gdf)
        df = STACDataFrame(gdf)
        # df.geometry = df.geometry.apply(lambda x: Polygon() if x is None else x)
        df.to_stac(download_path)
        # print("----")
        # print(df)
        # download assets
        if assets:
            if verbose:
                logger("Downloading assets...")
            repo = FilesAPIRepo()
            df = df.dropna(subset=["assets"])
            for row in tqdm(df.iterrows(), total=len(df)):
                for k, v in row[1]["assets"].items():
                    href = v["href"]
                    _, filename = href.split("/download/")
                    # will overwrite assets with same name :(
                    repo.download_file_url(
                        href, filename, f"{download_path}/assets", user
                    )
        else:
            logger("To download assets, set assets=True or -a in the CLI.")
    if verbose:
        logger("Done")
    return download_path
