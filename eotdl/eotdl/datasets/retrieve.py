from ..src.repos import APIRepo
from ..src.usecases.datasets import RetrieveDatasets, RetrieveDataset


def list_datasets():
    return retrieve_datasets()


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
