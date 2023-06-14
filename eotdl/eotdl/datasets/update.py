from ..src.repos import APIRepo
from ..src.usecases.datasets import UpdateDataset
from ..auth import with_auth


@with_auth
def update_dataset(name, path, logger=None, user=None):
    api_repo = APIRepo()
    ingest = UpdateDataset(api_repo, logger)
    inputs = ingest.Inputs(name=name, path=path, user=user)
    outputs = ingest(inputs)
    return outputs.dataset
