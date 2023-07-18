import os

from ..src.repos import APIRepo
from ..src.usecases.datasets import IngestFile, IngestFolder, IngestSTAC
from ..auth import with_auth


allowed_extensions = [
    ".zip",
    ".tar",
    ".tar.gz",
    ".csv",
    ".txt",
    ".json",
    ".pdf",
    ".md",
    ".yml",
]


def ingest_q1(dataset, stac_catalog):
    print("hola")
    return


@with_auth
def ingest_file(
    file, dataset_id, logger=None, allowed_extensions=allowed_extensions, user=None
):
    api_repo = APIRepo()
    ingest = IngestFile(api_repo, allowed_extensions, logger)
    inputs = ingest.Inputs(file=file, dataset_id=dataset_id, user=user)
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
def ingest_stac(stac_catalog, dataset, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestSTAC(api_repo, ingest_file, allowed_extensions)
    inputs = ingest.Inputs(stac_catalog=stac_catalog, dataset=dataset, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
