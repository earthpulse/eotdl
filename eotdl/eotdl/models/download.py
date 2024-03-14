import os
from pathlib import Path
from tqdm import tqdm

from ..auth import with_auth
from .retrieve import retrieve_model, retrieve_model_files
from ..shared import calculate_checksum
from ..repos import FilesAPIRepo
from .metadata import generate_metadata


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
            # files = [f for f in model["files"] if f["name"] == file]
            # if not files:
            #     raise Exception(f"File {file} not found")
            # if len(files) > 1:
            #     raise Exception(f"Multiple files with name {file} found")
            # dst_path = download(
            #     model,
            #     model["id"],
            #     file,
            #     files[0]["checksum"],
            #     download_path,
            #     user,
            # )
            # return Outputs(dst_path=dst_path)
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
            # if calculate_checksum(dst_path) != checksum:
            #     logger(f"Checksum for {file} does not match")
    else:
        raise NotImplementedError("Downloading a STAC model is not implemented")
    #     logger("Downloading STAC metadata...")
    #     gdf, error = repo.download_stac(
    #         model["id"],
    #         user["id_token"],
    #     )
    #     if error:
    #         raise Exception(error)
    #     df = STACDataFrame(gdf)
    #     # df.geometry = df.geometry.apply(lambda x: Polygon() if x is None else x)
    #     path = path
    #     if path is None:
    #         path = download_base_path + "/" + model["name"]
    #     df.to_stac(path)
    #     # download assets
    #     if assets:
    #         logger("Downloading assets...")
    #         df = df.dropna(subset=["assets"])
    #         for row in tqdm(df.iterrows(), total=len(df)):
    #             id = row[1]["stac_id"]
    #             # print(row[1]["links"])
    #             for k, v in row[1]["assets"].items():
    #                 href = v["href"]
    #                 repo.download_file_url(
    #                     href, f"{path}/assets/{id}", user["id_token"]
    #                 )
    #     else:
    #         logger("To download assets, set assets=True or -a in the CLI.")
    #     return Outputs(dst_path=path)
    if verbose:
        logger("Generating README.md ...")
    generate_metadata(download_path, model)
    if verbose:
        logger("Done")
    return download_path
