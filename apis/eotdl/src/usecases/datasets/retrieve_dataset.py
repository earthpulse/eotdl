from ...models import Dataset, STACDataset
from ...errors import DatasetDoesNotExistError
from ...repos import DatasetsDBRepo

def retrieve(data):
    if data is None:
        raise DatasetDoesNotExistError()
    return Dataset(**data) if data['quality'] == 0 else STACDataset(**data)


def retrieve_dataset(dataset_id):
    repo = DatasetsDBRepo()
    data = repo.retrieve_dataset(dataset_id)
    return retrieve(data)


def retrieve_dataset_by_name(name):
    repo = DatasetsDBRepo()
    data = repo.find_one_dataset_by_name(name)
    return retrieve(data)
