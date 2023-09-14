from pathlib import Path

from ..src.repos import APIRepo
from ..src.usecases.datasets import IngestFile, IngestFolder, IngestSTAC
from ..auth import with_auth


allowed_extensions = [
    ".zip",
    ".tar",
    ".gz",
    ".csv",
    ".txt",
    ".json",
    ".geojson",
    ".pdf",
    ".md",
    ".yml",
]


def ingest_dataset(path, f=False, d=False, logger=print):
    path = Path(path)
    if not path.is_dir():
        raise Exception("Path must be a folder")
    if "catalog.json" in [f.name for f in path.iterdir()]:
        return ingest_stac(path / "catalog.json", logger)
    return ingest_folder(path, f, d, logger)


@with_auth
def ingest_file(
    file,
    dataset_id,
    logger=None,
    allowed_extensions=allowed_extensions,
    verbose=True,
    root=None,
    user=None,
):
    api_repo = APIRepo()
    ingest = IngestFile(api_repo, allowed_extensions, logger, verbose)
    inputs = ingest.Inputs(file=file, dataset_id=dataset_id, user=user, root=root)
    outputs = ingest(inputs)
    return outputs.data


@with_auth
def ingest_folder(folder, force, delete, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestFolder(api_repo, ingest_file, allowed_extensions, logger)
    inputs = ingest.Inputs(folder=folder, user=user, force=force, delete=delete)
    outputs = ingest(inputs)
    return outputs.dataset


@with_auth
def ingest_stac(stac_catalog, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestSTAC(api_repo, ingest_file, allowed_extensions, logger)
    inputs = ingest.Inputs(stac_catalog=stac_catalog, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
