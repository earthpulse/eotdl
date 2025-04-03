from ..repos import ModelsAPIRepo


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

def deactivate_model(model_id):
    repo = ModelsAPIRepo()
    data, error = repo.deactivate_model(model_id)
    if error:
        raise Exception(error)
    return data
