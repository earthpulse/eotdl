from ..repos import ModelsAPIRepo
from ..auth import with_auth
from .retrieve import retrieve_model
def update_model(model_id, metadata, content, user):
    repo = ModelsAPIRepo()
    data, error = repo.update_model(
        model_id,
        metadata.authors,
        metadata.source,
        metadata.license,
        metadata.thumbnail,
        content,
        user,
    )
    if error:
        raise Exception(error)
    return data

@with_auth
def deactivate_model(model_name, user):
    model = retrieve_model(model_name)
    repo = ModelsAPIRepo()
    data, error = repo.deactivate_model(model['id'], user)
    if error:
        raise Exception(error)
    return data
