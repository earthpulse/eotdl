from ..datasets.retrieve_dataset import retrieve_dataset
from ..models.retrieve_model import retrieve_model
from ...errors import DatasetDoesNotExistError

def retrieve_stac_collection(collection_id):
    try:
        return retrieve_dataset(collection_id)
    except DatasetDoesNotExistError:
        return retrieve_model(collection_id)