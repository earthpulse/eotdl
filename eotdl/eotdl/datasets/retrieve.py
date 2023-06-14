from ..src.repos import APIRepo
from ..src.usecases.datasets.RetrieveDatasets import RetrieveDatasets
from ..src.usecases.datasets.RetrieveDataset import RetrieveDataset


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
