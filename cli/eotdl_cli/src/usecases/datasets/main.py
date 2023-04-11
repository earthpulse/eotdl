from ...repos import APIRepo
from .RetrieveDatasets import RetrieveDatasets
from .RetrieveDataset import RetrieveDataset
from .DownloadDataset import DownloadDataset
from .IngestDataset import IngestDataset

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

def download_dataset(name, path, user):
	dataset_id = retrieve_dataset(name)['id']
	api_repo = APIRepo()
	download = DownloadDataset(api_repo)
	inputs = download.Inputs(dataset=dataset_id, path=path, user=user)
	outputs = download(inputs)
	return outputs.dst_path

def ingest_dataset(name, description, path, user):
	api_repo = APIRepo()
	ingest = IngestDataset(api_repo)
	inputs = ingest.Inputs(name=name, description=description, path=path, user=user)
	outputs = ingest(inputs)
	return outputs.dataset