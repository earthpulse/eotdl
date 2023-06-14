from src.repos import APIRepo
from src.usecases.datasets.IngestDataset import IngestDataset
from src.usecases.datasets.IngestLargeDataset import IngestLargeDataset


def ingest_q0(dataset, file):
    print("hola")
    return


def ingest_q1(dataset, stac_catalog):
    print("hola")
    return


def ingest_dataset(name, description, path, user, logger):
    api_repo = APIRepo()
    ingest = IngestDataset(
        api_repo,
    )
    inputs = ingest.Inputs(name=name, description=description, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset


def ingest_large_dataset(name, path, user, logger):
    api_repo = APIRepo()
    ingest = IngestLargeDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
