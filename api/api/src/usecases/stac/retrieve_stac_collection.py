from ..datasets.retrieve_dataset import retrieve_dataset_by_name
from ..models.retrieve_model import retrieve_model_by_name
from ..pipelines.retrieve_pipeline import retrieve_pipeline_by_name
from ...errors import DatasetDoesNotExistError, ModelDoesNotExistError

def retrieve_stac_collection(collection_name):
    try:
        return retrieve_dataset_by_name(collection_name)
    except DatasetDoesNotExistError:
        try:
            return retrieve_model_by_name(collection_name)
        except ModelDoesNotExistError:
            return retrieve_pipeline_by_name(collection_name)