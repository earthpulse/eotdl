from ..auth import with_auth
from ..repos import FilesAPIRepo
from ..datasets.retrieve import retrieve_dataset
from ..models.retrieve import retrieve_model
from ..fe.retrieve import retrieve_pipeline

@with_auth
def get_file_content_url(filename, dataset_or_model_name, endpoint, user):
    if endpoint == "datasets":
        dataset_or_model_id = retrieve_dataset(dataset_or_model_name)['id']
    elif endpoint == "models":
        dataset_or_model_id = retrieve_model(dataset_or_model_name)['id']
    elif endpoint == "pipelines":
        dataset_or_model_id = retrieve_pipeline(dataset_or_model_name)['id']
    else:
        raise Exception("Invalid endpoint (datasets, models or pipelines)")
    repo = FilesAPIRepo()
    return repo.generate_file_content_url(filename, dataset_or_model_id, user, endpoint)