from ..src.repos import APIRepo
from ..src.usecases.datasets import IngestDataset, IngestLargeDataset
from ..auth import with_auth


@with_auth
def ingest_dataset(name, description, path, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestDataset(
        api_repo,
    )
    inputs = ingest.Inputs(name=name, description=description, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


@with_auth
def ingest_large_dataset(name, path, logger=None, user=None):
    api_repo = APIRepo()
    ingest = IngestLargeDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


def ingest_q0(dataset, path):
    return ingest_large_dataset(dataset, path)


def ingest_q1(dataset, stac_catalog):
    print("holas")
    return
