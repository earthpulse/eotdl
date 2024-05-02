from ...repos import DatasetsDBRepo, OSRepo, FilesDBRepo
from .retrieve_dataset import retrieve_dataset_by_name


def delete_dataset(name):
    db_repo, files_repo, os_repo = DatasetsDBRepo(), FilesDBRepo(), OSRepo()
    dataset = retrieve_dataset_by_name(name)
    # BUG: this throws an error if dataset has no files
    for file in files_repo.retrieve_files(dataset.files)[0]["files"]:
        os_repo.delete(dataset.id, f"{file['name']}_{file['version']}")
    db_repo.delete_files(dataset.files)
    db_repo.delete_dataset(dataset.id)
    db_repo.decrease_user_dataset_count(dataset.uid)
    # TODO: delete from GeoDB (get user creds from db)
    return "Dataset deleted successfully"
