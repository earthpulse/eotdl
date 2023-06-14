from ..src.repos import APIRepo
from ..src.usecases.datasets.UpdateDataset import UpdateDataset


def update_dataset(name, path, user, logger):
    api_repo = APIRepo()
    ingest = UpdateDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
