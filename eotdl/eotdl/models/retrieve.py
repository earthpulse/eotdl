from ..repos import ModelsAPIRepo, FilesAPIRepo


def retrieve_models(name=None, limit=None):
    api_repo = ModelsAPIRepo()
    data, error = api_repo.retrieve_models(name, limit)
    if data and not error:
        models = [d["name"] for d in data] if data else []
        return models
    return []


def retrieve_model(name):
    repo = ModelsAPIRepo()
    data, error = repo.retrieve_model(name)
    if error:
        raise Exception(error)
    return data


def retrieve_model_files(model_id, version):
    repo = FilesAPIRepo()
    data, error = repo.retrieve_files(model_id, "models", version)
    if error:
        raise Exception(error)
    return data
