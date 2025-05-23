from ..repos import FEAPIRepo


def retrieve_pipelines(name=None, limit=None):
    api_repo = FEAPIRepo()
    data, error = api_repo.retrieve_pipelines(name, limit)
    if data and not error:
        models = [d["name"] for d in data] if data else []
        return models
    return []


def retrieve_pipeline(name):
    repo = FEAPIRepo()
    data, error = repo.retrieve_pipeline(name)
    if error:
        raise Exception(error)
    return data