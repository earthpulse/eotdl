from ...repos import DatasetsDBRepo

from .retrieve_dataset import retrieve_owned_dataset

def deactivate_dataset(dataset_id, user):
    dataset = retrieve_owned_dataset(dataset_id, user)
    repo = DatasetsDBRepo()
    repo.deactivate_dataset(dataset_id)
    return f"Dataset {dataset.name} has been deactivated."
