from ...models import Dataset
from ...errors import DatasetDoesNotExistError, UserUnauthorizedError, DatasetNotActiveError, NoAccessToPrivateError
from ...repos import DatasetsDBRepo
# from ..files import retrieve_files


def retrieve(data):
    if data is None:
        raise DatasetDoesNotExistError()
    if 'active' in data and data['active'] is False:
        raise DatasetNotActiveError()
    return Dataset(**data)


def retrieve_dataset(dataset_id):
    repo = DatasetsDBRepo()
    data = repo.retrieve_dataset(dataset_id)
    return retrieve(data)


def retrieve_dataset_by_name(name):
    repo = DatasetsDBRepo()
    data = repo.find_one_dataset_by_name(name)
    return retrieve(data)


def retrieve_owned_dataset(dataset_id, uid):
    dataset = retrieve_dataset(dataset_id)
    if dataset.uid != uid:
        raise UserUnauthorizedError()
    if dataset.allowed_users and uid not in dataset.allowed_users:
        raise NoAccessToPrivateError()
    return dataset


# def retrieve_dataset_files(dataset_id, version=None):
#     dataset = retrieve_dataset(dataset_id)
#     return retrieve_files(dataset.versions, dataset.files, version)