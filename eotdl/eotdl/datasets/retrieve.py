from ..repos import DatasetsAPIRepo, FilesAPIRepo
from ..auth import with_auth


def retrieve_datasets(name=None, limit=None):
    api_repo = DatasetsAPIRepo()
    data, error = api_repo.retrieve_datasets(name, limit)
    if data and not error:
        datasets = [d["name"] for d in data] if data else []
        return datasets
    return []


def retrieve_dataset(name, user=None):
    repo = DatasetsAPIRepo()
    data, error = repo.retrieve_dataset(name)
    if error:
        if error == "NoAccessToPrivateError" and user is not None:
            data, error = repo.retrieve_private_dataset(name, user)
            if error:
                raise Exception(error)
        else:
            raise Exception(error)
    return data


def retrieve_dataset_files(dataset_id, version):
    repo = FilesAPIRepo()
    data, error = repo.retrieve_files(dataset_id, "datasets", version)
    if error:
        raise Exception(error)
    return data

@with_auth
def retrieve_private_datasets(user):
    api_repo = DatasetsAPIRepo()
    data, error = api_repo.retrieve_private_datasets(user)
    if data and not error:
        datasets = [d["name"] for d in data] if data else []
        return datasets
    return []