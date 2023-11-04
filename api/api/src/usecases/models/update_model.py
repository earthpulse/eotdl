from datetime import datetime


from ...repos import ModelsDBRepo
from .retrieve_model import retrieve_model, retrieve_model_by_name, retrieve_owned_model
from ..user import retrieve_user
from ...errors import ModelAlreadyExistsError, ModelDoesNotExistError, InvalidTagError
from ...models import Model


def toggle_like_model(model_id, user):
    repo = ModelsDBRepo()
    model = retrieve_model(model_id)
    user = retrieve_user(user.uid)
    if model.id in user.liked_models:
        repo.unlike_model(model_id, user.uid)
    else:
        repo.like_model(model_id, user.uid)
    return "done"


def update_model(model_id, user, name, authors, source, license, tags, description):
    model = retrieve_owned_model(model_id, user.uid)
    # validate name
    if name:
        try:
            _model = retrieve_model_by_name(name)
            if _model.id != model_id:
                raise ModelAlreadyExistsError()
        except ModelDoesNotExistError:
            pass
    # validate tags
    repo = ModelsDBRepo()
    if tags:
        tags_data = repo.retrieve_tags()
        all_tags = [tag["name"] for tag in tags_data]
        for tag in tags:
            if tag not in all_tags:
                raise InvalidTagError()
    # update model
    data = model.model_dump()
    data.update(
        updatedAt=datetime.now(),
        description=description if description is not None else model.description,
        tags=tags if tags is not None else model.tags,
    )
    if data["quality"] == 0:
        data.update(
            name=name if name is not None else model.name,
            authors=authors if authors is not None else model.authors,
            source=source if source is not None else model.source,
            license=license if license is not None else model.license,
        )
    updated_model = Model(**data)
    # update model in db
    repo.update_model(model_id, updated_model.model_dump())
    return updated_model
