from ...repos import DatasetsDBRepo
from ...errors import DatasetDoesNotExistError, DatasetNotActiveError


def deactivate_dataset(dataset_id: str):
    repo = DatasetsDBRepo()
    dataset = repo.find_one_by_field('datasets', 'id', dataset_id, limit=None)
    if dataset is None:
        raise DatasetDoesNotExistError()
    if dataset.get("active") is False:
        raise DatasetNotActiveError()
    repo.deactivate_dataset(dataset_id)
    return f"Dataset {dataset_id} has been deactivated."