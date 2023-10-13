from ..repos import DatasetsAPIRepo, FilesAPIRepo


def retrieve_datasets(name=None, limit=None):
    api_repo = DatasetsAPIRepo()
    data, error = api_repo.retrieve_datasets(name, limit)
    if data and not error:
        datasets = [d["name"] for d in data] if data else []
        return datasets
    return []


def retrieve_dataset(name):
    repo = DatasetsAPIRepo()
    data, error = repo.retrieve_dataset(name)
    if error:
        raise Exception(error)
    return data


def retrieve_dataset_files(dataset_id, version):
    repo = FilesAPIRepo()
    data, error = repo.retrieve_dataset_files(dataset_id, version)
    if error:
        raise Exception(error)
    return data


# def list_datasets(pattern=None):
#     datasets = retrieve_datasets()
#     if pattern:
#         regex = re.compile(rf".*{re.escape(pattern)}.*", re.IGNORECASE)
#         names = list(datasets.keys())
#         valid = [name for name in names if regex.search(name)]
#         return {name: datasets[name] for name in valid}
#     return datasets
