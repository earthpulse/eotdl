from ..repos import DatasetsAPIRepo
from ..auth import with_auth
from .retrieve import retrieve_dataset

def update_dataset(dataset_id, metadata, content, user):
    repo = DatasetsAPIRepo()
    data, error = repo.update_dataset(
        dataset_id,
        metadata.authors,
        metadata.source,
        metadata.license,
        metadata.thumbnail,
        content,
        user,
    )
    if error:
        raise Exception(error)
    return data

@with_auth
def deactivate_dataset(dataset_name, user):
    dataset = retrieve_dataset(dataset_name)
    repo = DatasetsAPIRepo()
    data, error = repo.deactivate_dataset(dataset['id'], user)
    if error:
        raise Exception(error)
    return data