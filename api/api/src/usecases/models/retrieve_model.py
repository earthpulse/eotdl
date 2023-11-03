from ...models import Model
from ...errors import ModelDoesNotExistError, UserUnauthorizedError
from ...repos import ModelsDBRepo
from ..files import retrieve_files


def retrieve(data):
    if data is None:
        raise ModelDoesNotExistError()
    return Model(**data)


def retrieve_model(model_id):
    repo = ModelsDBRepo()
    data = repo.retrieve_model(model_id)
    return retrieve(data)


def retrieve_model_by_name(name):
    repo = ModelsDBRepo()
    data = repo.find_one_model_by_name(name)
    return retrieve(data)


def retrieve_owned_model(model_id, uid):
    model = retrieve_model(model_id)
    if model.uid != uid:
        raise UserUnauthorizedError()
    return model


def retrieve_model_files(model_id, version=None):
    model = retrieve_model(model_id)
    return retrieve_files(model.versions, model.files, version)
