from ..repos import ModelsAPIRepo


def retrieve_models(name=None, limit=None):
    api_repo = ModelsAPIRepo()
    data, error = api_repo.retrieve_models(name, limit)
    if data and not error:
        models = [d["name"] for d in data] if data else []
        return models
    return []


# def retrieve_dataset(name):
#     repo = DatasetsAPIRepo()
#     data, error = repo.retrieve_dataset(name)
#     if error:
#         raise Exception(error)
#     return data


# def retrieve_dataset_files(dataset_id, version):
#     repo = FilesAPIRepo()
#     data, error = repo.retrieve_dataset_files(dataset_id, version)
#     if error:
#         raise Exception(error)
#     return data
