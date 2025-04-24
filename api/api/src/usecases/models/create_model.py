from ...models import Model, Metadata
from ...errors import (
    ModelAlreadyExistsError,
    ModelDoesNotExistError,
)
from ...repos import ModelsDBRepo, GeoDBRepo

from .retrieve_model import retrieve_model_by_name
from ..user import check_user_can_create_model


def create_model(user, name, authors, source, license, thumbnail, description, private):
    repo = ModelsDBRepo()
    try:
        retrieve_model_by_name(name)
        raise ModelAlreadyExistsError()
    except ModelDoesNotExistError:
        check_user_can_create_model(user)
        id = repo.generate_id()
        model = Model(
            uid=user.uid,
            id=id,
            name=name,
            metadata=Metadata(
                authors=authors,
                source=source,
                license=license,
                thumbnail=thumbnail,
                description=description,
            ),
            allowedUsers=[user.uid] if private else [],
        )
        repo.persist_model(model.model_dump(), model.id)
        repo.increase_user_model_count(user.uid)
        return model
