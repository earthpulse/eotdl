from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ...errors import DatasetDoesNotExistError

def retrieve_stac_collection(collection_name):
    try:
        return retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        return retrieve_model_by_name(collection_name)