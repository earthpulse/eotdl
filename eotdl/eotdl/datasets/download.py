import os
from pathlib import Path
from tqdm import tqdm

from ..auth import with_auth
from .retrieve import retrieve_dataset, retrieve_dataset_files
from ..repos import FilesAPIRepo, DatasetsAPIRepo
from ..curation.stac import STACDataFrame
from .metadata import generate_metadata


@with_auth
def download_dataset(
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
    cache_base_path = os.getenv(
        "EOTDL_CACHE_PATH", str(Path.home()) + "-"
    )
    if path is None:
        download_path = download_base_path + "/" + dataset_name + "/v" + str(version)
    else:
        download_path = path + "/" + dataset_name + "/v" + str(version)
    # check if dataset already exists
    if os.path.exists(download_path) and not force:
        os.makedirs(download_path, exist_ok=True)
        raise Exception(
            f"Dataset `{dataset['name']} v{str(version)}` already exists at {download_path}. To force download, use force=True or -f in the CLI."
        )
    if dataset["quality"] == 0:
        if file:
            raise NotImplementedError("Downloading a specific file is not implemented")
        dataset_files = retrieve_dataset_files(dataset["id"], version)
        repo = FilesAPIRepo()
        for file in tqdm(dataset_files, disable=verbose, unit="file", position=0):
            filename, file_version = file["filename"], file["version"]
            cache_path = Path(
                f"{cache_base_path}/{dataset['id']}/{filename}_{file_version}")
            if cache_base_path != "-" and cache_path.exists():
                file_path = Path(download_path + "/" + filename)
                if verbose:
                    logger(f"Symlinking {filename}...")
                if file_path.exists():
                    file_path.unlink()
                else:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                if verbose:
                    logger(f"Symlinking {filename}...")                
                file_path.symlink_to(cache_path)
            else:
                if verbose:
                    logger(f"Downloading {filename}...")
                repo.download_file(
                    dataset["id"],
                    filename,
                    user,
                    download_path,
                    file_version,
                    progress=True,
                )
            if verbose:
                logger("Generating README.md ...")
            generate_metadata(download_path, dataset)
    else:
        if verbose:
            logger("Downloading STAC metadata...")
        repo = DatasetsAPIRepo()
        gdf, error = repo.download_stac(
            dataset["id"],
            user,
        )
        if error:
            raise Exception(error)
        df = STACDataFrame(gdf)
        # df.geometry = df.geometry.apply(lambda x: Polygon() if x is None else x)
        df.to_stac(download_path)
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


@with_auth
def download_file_url(url, path, progress=True, logger=print, user=None):
    repo = FilesAPIRepo()
    _, filename = url.split("/download/")
    return repo.download_file_url(url, filename, f"{path}/assets", user, progress)
