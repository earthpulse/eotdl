from ...repos import DatasetsDBRepo, OSRepo
from .retrieve_dataset import retrieve_dataset_by_name


def delete_dataset(name):
    db_repo, os_repo = DatasetsDBRepo(), OSRepo()
    dataset = retrieve_dataset_by_name(name)
    for file in db_repo.retrieve_files(dataset.files):
        os_repo.delete(dataset.id, file["id"])
    db_repo.delete_files(dataset.files)
    db_repo.decrease_user_dataset_count(dataset.uid)
    return "Dataset deleted successfully"
