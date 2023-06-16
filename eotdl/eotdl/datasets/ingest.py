from ..src.repos import APIRepo
from ..src.usecases.datasets import IngestFile, IngestFolder
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
]


@with_auth
def ingest_file(file, dataset, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestFile(api_repo, allowed_extensions, logger)
    inputs = ingest.Inputs(file=file, dataset=dataset, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


@with_auth
def ingest_folder(folder, dataset, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestFolder(api_repo, ingest_file, allowed_extensions, logger)
    inputs = ingest.Inputs(folder=folder, dataset=dataset, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


# @with_auth
# def ingest_dataset(name, description, path, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestDataset(
#         api_repo,
#     )
#     inputs = ingest.Inputs(name=name, description=description, path=path, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset


# @with_auth
# def ingest_large_dataset(name, path, logger=None, user=None):
#     api_repo = APIRepo()
#     ingest = IngestLargeDataset(api_repo, logger)
#     inputs = ingest.Inputs(name=name, path=path, user=user)
#     outputs = ingest(inputs)
#     return outputs.dataset


# def ingest_q0(dataset, path):
#     return ingest_large_dataset(dataset, path)


# def ingest_q1(dataset, stac_catalog):
#     print("holas")
#     return
