import re

from ..src.repos import APIRepo
from ..src.usecases.datasets import RetrieveDatasets, RetrieveDataset


def list_datasets(pattern=None):
    datasets = retrieve_datasets()
    if pattern:
        regex = re.compile(rf".*{re.escape(pattern)}.*", re.IGNORECASE)
        names = list(datasets.keys())
        valid = [name for name in names if regex.search(name)]
        return {name: datasets[name] for name in valid}
    return datasets


def retrieve_datasets():
    api_repo = APIRepo()
    retrieve = RetrieveDatasets(api_repo)
    inputs = retrieve.Inputs()
    outputs = retrieve(inputs)
    return outputs.datasets


def retrieve_dataset(name):
    api_repo = APIRepo()
    retrieve = RetrieveDataset(api_repo)
    inputs = retrieve.Inputs(name=name)
    outputs = retrieve(inputs)
    return outputs.dataset
