from ..repos import DatasetsAPIRepo


def update_dataset(dataset_id, content, user):
    repo = DatasetsAPIRepo()
    data, error = repo.update_dataset(dataset_id, content, user)
    if error:
        raise Exception(error)
    return data
