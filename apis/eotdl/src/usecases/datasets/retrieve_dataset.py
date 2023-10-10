from ...models import Dataset, STACDataset
from ...errors import DatasetDoesNotExistError, UserUnauthorizedError
from ...repos import DatasetsDBRepo, FilesDBRepo


def retrieve(data):
    if data is None:
        raise DatasetDoesNotExistError()
    return Dataset(**data) if data["quality"] == 0 else STACDataset(**data)


def retrieve_dataset(dataset_id):
    repo = DatasetsDBRepo()
    data = repo.retrieve_dataset(dataset_id)
    return retrieve(data)


def retrieve_dataset_by_name(name):
    repo = DatasetsDBRepo()
    data = repo.find_one_dataset_by_name(name)
    return retrieve(data)


def retrieve_file(files_id, file_id):
    repo = DatasetsDBRepo()
    data = repo.retrieve_file(files_id, file_id)
    return data


def retrieve_owned_dataset(dataset_id, uid):
    dataset = retrieve_dataset(dataset_id)
    if dataset.uid != uid:
        raise UserUnauthorizedError()
    return dataset


def retrieve_dataset_files(dataset_id, user, version=None):
    files_repo = FilesDBRepo()
    dataset = retrieve_dataset(dataset_id)
    versions = sorted(dataset.versions, key=lambda x: x.version_id)
    if version is None:
        version = versions[-1].version_id
    if version not in [v.version_id for v in versions]:
        raise Exception("Version not found")
    data = files_repo.retrieve_dataset_files(dataset.files, version)
    if len(data) != 1:
        raise Exception("No files found")
    files = (
        [{"filename": f["name"], "version": f["version"]} for f in data[0]["files"]]
        if len(data[0]["files"]) > 0
        else []
    )
    return files
