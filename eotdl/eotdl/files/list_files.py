from ..datasets import retrieve_dataset, retrieve_dataset_files
from ..models import retrieve_model, retrieve_model_files

def list_files(dataset_or_model_name, version=1):
	try:
		dataset = retrieve_dataset(dataset_or_model_name)
		return retrieve_dataset_files(dataset['id'], version)
	except Exception as e:
		try:
			model = retrieve_model(dataset_or_model_name)
			return retrieve_model_files(model['id'], version)
		except Exception as e:
			raise Exception(f"Dataset or model {dataset_or_model_name} not found.")